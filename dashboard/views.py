from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q, Avg
from django.db import models
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal

# Import models from other apps
from sales.models import SalesInvoice, Customer
from purchases.models import PurchaseInvoice, Supplier
from inventory.models import Stock, StockMovement
from treasury.models import TreasuryTransaction, Receipt, Payment
from banking.models import BankTransaction
from definitions.models import Item, Warehouse, Bank, Treasury, Currency, EgyptianBankRate


def get_currency_rates_data():
    """جلب بيانات أسعار العملات للصفحة الرئيسية"""
    try:
        # العملات الرئيسية
        main_currencies = ['USD', 'EUR', 'GBP', 'SAR', 'AED']

        currency_data = []

        for currency_code in main_currencies:
            try:
                currency = Currency.objects.get(code=currency_code, is_active=True)

                # جلب أحدث الأسعار من البنوك
                latest_rates = EgyptianBankRate.objects.filter(
                    currency=currency,
                    is_active=True
                ).order_by('-last_updated')[:5]  # أحدث 5 بنوك

                if latest_rates:
                    # حساب المتوسطات
                    avg_buy = latest_rates.aggregate(avg=Avg('buy_rate'))['avg'] or 0
                    avg_sell = latest_rates.aggregate(avg=Avg('sell_rate'))['avg'] or 0

                    # أفضل الأسعار
                    best_buy = latest_rates.order_by('-buy_rate').first()
                    best_sell = latest_rates.order_by('sell_rate').first()

                    currency_info = {
                        'code': currency_code,
                        'name': currency.name,
                        'symbol': currency.symbol,
                        'avg_buy': round(float(avg_buy), 4),
                        'avg_sell': round(float(avg_sell), 4),
                        'best_buy': {
                            'rate': float(best_buy.buy_rate),
                            'bank': best_buy.bank_name
                        } if best_buy else None,
                        'best_sell': {
                            'rate': float(best_sell.sell_rate),
                            'bank': best_sell.bank_name
                        } if best_sell else None,
                        'rates': [
                            {
                                'bank': rate.bank_name,
                                'buy': float(rate.buy_rate),
                                'sell': float(rate.sell_rate),
                                'last_updated': rate.last_updated.strftime('%H:%M')
                            }
                            for rate in latest_rates
                        ],
                        'last_updated': latest_rates.first().last_updated if latest_rates else None
                    }
                    currency_data.append(currency_info)

            except Currency.DoesNotExist:
                continue

        return {
            'currencies': currency_data,
            'last_update': timezone.now(),
            'update_frequency': '15 دقيقة'
        }

    except Exception as e:
        # في حالة حدوث خطأ، إرجاع بيانات فارغة
        return {
            'currencies': [],
            'last_update': timezone.now(),
            'update_frequency': '15 دقيقة'
        }


@login_required
def dashboard_home(request):
    """لوحة التحكم الرئيسية"""

    # Get current date and date ranges
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    current_year_start = today.replace(month=1, day=1)

    # Sales Statistics
    sales_today = SalesInvoice.objects.filter(
        date=today,
        status__in=['CONFIRMED', 'DELIVERED', 'PAID']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    sales_this_month = SalesInvoice.objects.filter(
        date__gte=current_month_start,
        status__in=['CONFIRMED', 'DELIVERED', 'PAID']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    sales_this_year = SalesInvoice.objects.filter(
        date__gte=current_year_start,
        status__in=['CONFIRMED', 'DELIVERED', 'PAID']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    # Purchase Statistics
    purchases_today = PurchaseInvoice.objects.filter(
        date=today,
        status__in=['CONFIRMED', 'RECEIVED', 'PAID']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    purchases_this_month = PurchaseInvoice.objects.filter(
        date__gte=current_month_start,
        status__in=['CONFIRMED', 'RECEIVED', 'PAID']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    # Inventory Statistics
    total_items = Item.objects.filter(is_active=True).count()
    low_stock_items = Stock.objects.filter(
        quantity__lte=models.F('item__min_stock'),
        item__is_active=True
    ).count()

    # Treasury and Bank Balances
    treasury_balance = Treasury.objects.filter(is_active=True).aggregate(
        total=Sum('balance')
    )['total'] or Decimal('0')

    bank_balance = Bank.objects.filter(is_active=True).aggregate(
        total=Sum('balance')
    )['total'] or Decimal('0')

    # Customer and Supplier counts
    total_customers = Customer.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()

    # Recent transactions
    recent_sales = SalesInvoice.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]

    recent_purchases = PurchaseInvoice.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]

    recent_stock_movements = StockMovement.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]

    # Chart data for sales trend (last 7 days)
    sales_chart_data = []
    sales_chart_labels = []

    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        daily_sales = SalesInvoice.objects.filter(
            date=date,
            status__in=['CONFIRMED', 'DELIVERED', 'PAID']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        sales_chart_data.append(float(daily_sales))
        sales_chart_labels.append(date.strftime('%Y-%m-%d'))

    # Monthly comparison data
    monthly_sales = []
    monthly_purchases = []
    monthly_labels = []

    for i in range(5, -1, -1):
        month_start = (current_month_start - timedelta(days=32*i)).replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)

        month_sales = SalesInvoice.objects.filter(
            date__gte=month_start,
            date__lt=next_month,
            status__in=['CONFIRMED', 'DELIVERED', 'PAID']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        month_purchases = PurchaseInvoice.objects.filter(
            date__gte=month_start,
            date__lt=next_month,
            status__in=['CONFIRMED', 'RECEIVED', 'PAID']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        monthly_sales.append(float(month_sales))
        monthly_purchases.append(float(month_purchases))
        monthly_labels.append(month_start.strftime('%Y-%m'))

    # Currency rates data
    currency_data = get_currency_rates_data()

    context = {
        'sales_today': sales_today,
        'sales_this_month': sales_this_month,
        'sales_this_year': sales_this_year,
        'purchases_today': purchases_today,
        'purchases_this_month': purchases_this_month,
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'treasury_balance': treasury_balance,
        'bank_balance': bank_balance,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
        'recent_stock_movements': recent_stock_movements,
        'sales_chart_data': sales_chart_data,
        'sales_chart_labels': sales_chart_labels,
        'monthly_sales': monthly_sales,
        'monthly_purchases': monthly_purchases,
        'monthly_labels': monthly_labels,
        # Currency rates
        'currencies': currency_data.get('currencies', []),
        'last_update': currency_data.get('last_update'),
        'update_frequency': currency_data.get('update_frequency', '15 دقيقة'),
    }

    return render(request, 'dashboard/home.html', context)


@login_required
def currency_rates_widget(request):
    """عرض أسعار العملات للشاشة الرئيسية"""
    from definitions.models import EgyptianBankRate, Currency
    from services.currency_rates import currency_service

    # العملات الرئيسية
    main_currencies = ['USD', 'EUR', 'GBP', 'SAR', 'AED']

    currency_data = []

    for currency_code in main_currencies:
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)

            # جلب أحدث الأسعار من البنوك
            latest_rates = EgyptianBankRate.objects.filter(
                currency=currency,
                is_active=True
            ).order_by('-last_updated')[:5]  # أحدث 5 بنوك

            if latest_rates:
                # حساب المتوسطات
                avg_buy = latest_rates.aggregate(avg=Avg('buy_rate'))['avg'] or 0
                avg_sell = latest_rates.aggregate(avg=Avg('sell_rate'))['avg'] or 0

                # أفضل الأسعار
                best_buy = latest_rates.order_by('-buy_rate').first()
                best_sell = latest_rates.order_by('sell_rate').first()

                currency_info = {
                    'code': currency_code,
                    'name': currency.name,
                    'symbol': currency.symbol,
                    'avg_buy': round(float(avg_buy), 4),
                    'avg_sell': round(float(avg_sell), 4),
                    'best_buy': {
                        'rate': float(best_buy.buy_rate),
                        'bank': best_buy.bank_name
                    } if best_buy else None,
                    'best_sell': {
                        'rate': float(best_sell.sell_rate),
                        'bank': best_sell.bank_name
                    } if best_sell else None,
                    'rates': [
                        {
                            'bank': rate.bank_name,
                            'buy': float(rate.buy_rate),
                            'sell': float(rate.sell_rate),
                            'last_updated': rate.last_updated.strftime('%H:%M')
                        }
                        for rate in latest_rates
                    ],
                    'last_updated': latest_rates.first().last_updated if latest_rates else None
                }
                currency_data.append(currency_info)

        except Currency.DoesNotExist:
            continue

    context = {
        'currencies': currency_data,
        'last_update': timezone.now(),
        'update_frequency': '15 دقيقة'  # تردد التحديث
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context, safe=False)

    return render(request, 'dashboard/currency_rates_widget.html', context)


@login_required
def update_currency_rates_ajax(request):
    """تحديث أسعار العملات عبر AJAX"""
    if request.method == 'POST':
        try:
            from services.currency_rates import currency_service

            # تحديث الأسعار
            result = currency_service.update_all_rates()

            return JsonResponse({
                'success': True,
                'message': f'تم تحديث {result["success"]} بنك بنجاح',
                'data': result
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'حدث خطأ: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'طريقة غير مدعومة'})


@login_required
def currency_rates_full(request):
    """صفحة كاملة لعرض أسعار العملات"""
    currency_data = get_currency_rates_data()

    context = {
        'title': 'أسعار العملات - البنوك المصرية',
        'currencies': currency_data.get('currencies', []),
        'last_update': currency_data.get('last_update'),
        'update_frequency': currency_data.get('update_frequency', '15 دقيقة'),
    }

    return render(request, 'dashboard/currency_rates_full.html', context)
