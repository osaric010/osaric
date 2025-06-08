from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json

# استيراد النماذج من التطبيقات الأخرى
from definitions.models import Person, Currency, Warehouse, Item, Bank, Treasury
from sales.models import SalesInvoice, SalesInvoiceItem, Customer
from purchases.models import PurchaseInvoice, PurchaseInvoiceItem, Supplier
from inventory.models import StockIncrease, StockDecrease, WarehouseTransfer, StockIncreaseItem, StockDecreaseItem, Stock
from assets.models import Asset, DepreciationEntry
from treasury.models import TreasuryTransaction
from banking.models import BankTransaction


@login_required
def reports_dashboard(request):
    """لوحة تحكم التقارير الرئيسية"""
    context = {
        'title': 'لوحة تحكم التقارير',
        'reports_sections': [
            {
                'name': 'تقارير الأشخاص',
                'icon': 'fas fa-users',
                'color': 'primary',
                'url': 'reports:persons_reports',
                'count': Person.objects.filter(is_active=True).count()
            },
            {
                'name': 'تقارير الخزينة',
                'icon': 'fas fa-cash-register',
                'color': 'success',
                'url': 'reports:treasury_reports',
                'count': TreasuryTransaction.objects.filter(is_active=True).count()
            },
            {
                'name': 'تقارير البنوك',
                'icon': 'fas fa-university',
                'color': 'info',
                'url': 'reports:banks_reports',
                'count': BankTransaction.objects.filter(is_active=True).count()
            },
            {
                'name': 'تقارير المبيعات',
                'icon': 'fas fa-shopping-cart',
                'color': 'warning',
                'url': 'reports:sales_reports',
                'count': SalesInvoice.objects.filter(is_active=True).count()
            },
            {
                'name': 'تقارير المشتريات',
                'icon': 'fas fa-truck',
                'color': 'secondary',
                'url': 'reports:purchases_reports',
                'count': PurchaseInvoice.objects.filter(is_active=True).count()
            },
            {
                'name': 'تقارير المخازن',
                'icon': 'fas fa-warehouse',
                'color': 'dark',
                'url': 'reports:warehouses_reports',
                'count': Warehouse.objects.filter(is_active=True).count()
            },
            {
                'name': 'تقارير الأصول الثابتة',
                'icon': 'fas fa-building',
                'color': 'danger',
                'url': 'reports:assets_reports',
                'count': Asset.objects.filter(is_active=True).count()
            }
        ]
    }
    return render(request, 'reports/dashboard.html', context)


# ==================== تقارير الأشخاص ====================

@login_required
def persons_reports(request):
    """صفحة تقارير الأشخاص"""
    context = {
        'title': 'تقارير الأشخاص',
        'persons': Person.objects.filter(is_active=True).order_by('name')
    }
    return render(request, 'reports/persons/index.html', context)


@login_required
def person_account_statement_invoices(request):
    """كشف حساب حسب الفواتير"""
    person_id = request.GET.get('person_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # جمع العملاء والموردين
    all_persons = []
    customers = Customer.objects.filter(is_active=True).order_by('name')
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')

    for customer in customers:
        all_persons.append({
            'id': f'customer_{customer.id}',
            'name': f'{customer.name} - عميل',
            'type': 'customer',
            'object': customer
        })

    for supplier in suppliers:
        all_persons.append({
            'id': f'supplier_{supplier.id}',
            'name': f'{supplier.name} - مورد',
            'type': 'supplier',
            'object': supplier
        })

    context = {
        'title': 'كشف حساب حسب الفواتير',
        'persons': all_persons,
        'selected_person': person_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    if person_id:
        # تحديد نوع الشخص من المعرف
        if person_id.startswith('customer_'):
            customer_id = person_id.replace('customer_', '')
            person = get_object_or_404(Customer, id=customer_id)
            person_type = 'customer'
        elif person_id.startswith('supplier_'):
            supplier_id = person_id.replace('supplier_', '')
            person = get_object_or_404(Supplier, id=supplier_id)
            person_type = 'supplier'
        else:
            person = None
            person_type = None

        if person:
            context['person'] = person
            context['person_type'] = person_type

            # جلب فواتير المبيعات (للعملاء فقط)
            sales_invoices = SalesInvoice.objects.none()
            if person_type == 'customer':
                sales_invoices = SalesInvoice.objects.filter(
                    customer=person, is_active=True
                )

            # جلب فواتير المشتريات (للموردين فقط)
            purchase_invoices = PurchaseInvoice.objects.none()
            if person_type == 'supplier':
                purchase_invoices = PurchaseInvoice.objects.filter(
                    supplier=person, is_active=True
                )
        
        if date_from:
            sales_invoices = sales_invoices.filter(date__gte=date_from)
            purchase_invoices = purchase_invoices.filter(date__gte=date_from)

        if date_to:
            sales_invoices = sales_invoices.filter(date__lte=date_to)
            purchase_invoices = purchase_invoices.filter(date__lte=date_to)

        context['sales_invoices'] = sales_invoices.order_by('-date')
        context['purchase_invoices'] = purchase_invoices.order_by('-date')
        
        # حساب الأرصدة
        total_sales = sales_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_purchases = purchase_invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        
        context['total_sales'] = total_sales
        context['total_purchases'] = total_purchases
        context['balance'] = total_sales - total_purchases
    
    return render(request, 'reports/persons/account_statement_invoices.html', context)


@login_required
def person_account_statement_detailed(request):
    """كشف حساب شخص تفصيلي"""
    person_id = request.GET.get('person_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    context = {
        'title': 'كشف حساب شخص تفصيلي',
        'persons': Person.objects.filter(is_active=True).order_by('name'),
        'selected_person': person_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    if person_id:
        person = get_object_or_404(Person, id=person_id)
        context['person'] = person
        
        # جلب جميع المعاملات المالية للشخص
        transactions = []
        
        # فواتير المبيعات
        sales_invoices = SalesInvoice.objects.filter(
            customer=person, is_active=True
        )
        
        if date_from:
            sales_invoices = sales_invoices.filter(date__gte=date_from)
        if date_to:
            sales_invoices = sales_invoices.filter(date__lte=date_to)

        for invoice in sales_invoices:
            transactions.append({
                'date': invoice.date,
                'type': 'مبيعات',
                'reference': f'فاتورة مبيعات رقم {invoice.invoice_number}',
                'debit': invoice.total_amount,
                'credit': 0,
                'balance': 0  # سيتم حسابه لاحقاً
            })

        # فواتير المشتريات
        purchase_invoices = PurchaseInvoice.objects.filter(
            supplier=person, is_active=True
        )

        if date_from:
            purchase_invoices = purchase_invoices.filter(date__gte=date_from)
        if date_to:
            purchase_invoices = purchase_invoices.filter(date__lte=date_to)

        for invoice in purchase_invoices:
            transactions.append({
                'date': invoice.date,
                'type': 'مشتريات',
                'reference': f'فاتورة مشتريات رقم {invoice.invoice_number}',
                'debit': 0,
                'credit': invoice.total_amount,
                'balance': 0  # سيتم حسابه لاحقاً
            })
        
        # ترتيب المعاملات حسب التاريخ
        transactions.sort(key=lambda x: x['date'])
        
        # حساب الرصيد المتراكم
        running_balance = 0
        for transaction in transactions:
            running_balance += transaction['debit'] - transaction['credit']
            transaction['balance'] = running_balance
        
        context['transactions'] = transactions
        context['final_balance'] = running_balance
    
    return render(request, 'reports/persons/account_statement_detailed.html', context)


@login_required
def persons_balances(request):
    """أرصدة الأشخاص"""
    person_type = request.GET.get('person_type', '')
    
    # تعريف أنواع الأشخاص
    PERSON_TYPE_CHOICES = [
        ('CUSTOMER', 'عميل'),
        ('SUPPLIER', 'مورد'),
        ('EMPLOYEE', 'موظف'),
        ('BOTH', 'عميل ومورد'),
        ('BANK', 'بنك'),
        ('GOVERNMENT', 'جهة حكومية'),
        ('PARTNER', 'شريك'),
        ('OTHER', 'أخرى'),
    ]

    context = {
        'title': 'أرصدة الأشخاص',
        'person_types': PERSON_TYPE_CHOICES,
        'selected_type': person_type,
    }
    
    persons = Person.objects.filter(is_active=True)
    
    if person_type:
        persons = persons.filter(person_type=person_type)
    
    # حساب الأرصدة لكل شخص
    persons_with_balances = []

    # جلب العملاء والموردين من النماذج المنفصلة
    customers = Customer.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)

    # حساب أرصدة العملاء
    for customer in customers:
        total_sales = SalesInvoice.objects.filter(
            customer=customer, is_active=True
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        if total_sales > 0:
            persons_with_balances.append({
                'person': customer,
                'person_type': 'عميل',
                'total_sales': total_sales,
                'total_purchases': 0,
                'balance': total_sales,
                'balance_type': 'مدين'
            })

    # حساب أرصدة الموردين
    for supplier in suppliers:
        total_purchases = PurchaseInvoice.objects.filter(
            supplier=supplier, is_active=True
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        if total_purchases > 0:
            persons_with_balances.append({
                'person': supplier,
                'person_type': 'مورد',
                'total_sales': 0,
                'total_purchases': total_purchases,
                'balance': -total_purchases,  # سالب لأنه دائن
                'balance_type': 'دائن'
            })
    
    # ترتيب حسب الرصيد
    persons_with_balances.sort(key=lambda x: abs(x['balance']), reverse=True)
    
    context['persons_with_balances'] = persons_with_balances

    # حساب الإجماليات
    total_sales = sum(p['total_sales'] for p in persons_with_balances)
    total_purchases = sum(p['total_purchases'] for p in persons_with_balances)
    total_balance = sum(p['balance'] for p in persons_with_balances)

    context['total_sales'] = total_sales
    context['total_purchases'] = total_purchases
    context['total_balance'] = total_balance
    
    return render(request, 'reports/persons/balances.html', context)


@login_required
def persons_directory(request):
    """دليل الأشخاص"""
    search = request.GET.get('search', '')
    person_type = request.GET.get('person_type', '')
    
    # تعريف أنواع الأشخاص
    PERSON_TYPE_CHOICES = [
        ('CUSTOMER', 'عميل'),
        ('SUPPLIER', 'مورد'),
        ('EMPLOYEE', 'موظف'),
        ('BOTH', 'عميل ومورد'),
        ('BANK', 'بنك'),
        ('GOVERNMENT', 'جهة حكومية'),
        ('PARTNER', 'شريك'),
        ('OTHER', 'أخرى'),
    ]

    context = {
        'title': 'دليل الأشخاص',
        'person_types': PERSON_TYPE_CHOICES,
        'search': search,
        'selected_type': person_type,
    }
    
    # جمع العملاء والموردين
    all_persons = []

    # جلب العملاء
    customers = Customer.objects.filter(is_active=True)
    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )

    for customer in customers:
        if not person_type or person_type == 'CUSTOMER':
            all_persons.append({
                'name': customer.name,
                'name_english': getattr(customer, 'name_english', ''),
                'person_type': 'CUSTOMER',
                'get_person_type_display': 'عميل',
                'phone': customer.phone,
                'mobile': getattr(customer, 'mobile', ''),
                'email': customer.email,
                'address': getattr(customer, 'address', ''),
                'code': customer.code,
            })

    # جلب الموردين
    suppliers = Supplier.objects.filter(is_active=True)
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )

    for supplier in suppliers:
        if not person_type or person_type == 'SUPPLIER':
            all_persons.append({
                'name': supplier.name,
                'name_english': '',
                'person_type': 'SUPPLIER',
                'get_person_type_display': 'مورد',
                'phone': supplier.phone,
                'mobile': '',
                'email': supplier.email,
                'address': supplier.address,
                'code': supplier.code,
            })

    # ترتيب حسب الاسم
    all_persons.sort(key=lambda x: x['name'])

    context['persons'] = all_persons
    
    return render(request, 'reports/persons/directory.html', context)


# ==================== تقارير الخزينة ====================

@login_required
def treasury_reports(request):
    """صفحة تقارير الخزينة"""
    context = {
        'title': 'تقارير الخزينة',
        'treasuries': Treasury.objects.filter(is_active=True).order_by('name')
    }
    return render(request, 'reports/treasury/index.html', context)


@login_required
def cash_payments_report(request):
    """تقرير الدفع النقدي"""
    treasury_id = request.GET.get('treasury_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير الدفع النقدي',
        'treasuries': Treasury.objects.filter(is_active=True).order_by('name'),
        'selected_treasury': treasury_id,
        'date_from': date_from,
        'date_to': date_to,
    }

    if treasury_id or date_from or date_to:
        transactions = TreasuryTransaction.objects.filter(
            transaction_type='PAYMENT',
            is_active=True
        )

        if treasury_id:
            transactions = transactions.filter(treasury_id=treasury_id)
        if date_from:
            transactions = transactions.filter(transaction_date__gte=date_from)
        if date_to:
            transactions = transactions.filter(transaction_date__lte=date_to)

        context['transactions'] = transactions.order_by('-transaction_date')
        context['total_amount'] = transactions.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'reports/treasury/cash_payments.html', context)


@login_required
def payment_papers_report(request):
    """تقرير أوراق الدفع"""
    from datetime import datetime, timedelta
    from django.db.models import Q, Sum, Count

    # الحصول على المعاملات
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    supplier_id = request.GET.get('supplier_id')
    status = request.GET.get('status')
    paper_type = request.GET.get('paper_type')

    # تعيين التواريخ الافتراضية
    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')

    # إنشاء بيانات وهمية لأوراق الدفع (يمكن استبدالها بنموذج حقيقي)
    payment_papers = []

    # بيانات وهمية للعرض
    if date_from and date_to:
        from random import randint, choice
        from datetime import datetime, timedelta
        import uuid

        # أنواع أوراق الدفع
        paper_types = [
            ('CHECK', 'شيك'),
            ('PROMISSORY_NOTE', 'سند إذني'),
            ('BILL_OF_EXCHANGE', 'كمبيالة'),
            ('BANK_DRAFT', 'حوالة بنكية')
        ]

        # حالات أوراق الدفع
        statuses = [
            ('PENDING', 'معلق'),
            ('ISSUED', 'صادر'),
            ('PAID', 'مدفوع'),
            ('BOUNCED', 'مرتد'),
            ('CANCELLED', 'ملغي')
        ]

        # موردين وهميين
        suppliers = [
            {'id': 1, 'name': 'شركة الأمل للتجارة'},
            {'id': 2, 'name': 'مؤسسة النور التجارية'},
            {'id': 3, 'name': 'شركة الفجر للمواد'},
            {'id': 4, 'name': 'مكتب السلام التجاري'},
            {'id': 5, 'name': 'شركة الرياض للتوريدات'}
        ]

        # إنشاء بيانات وهمية
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')

        for i in range(15):  # إنشاء 15 ورقة دفع وهمية
            paper_date = start_date + timedelta(days=randint(0, (end_date - start_date).days))
            due_date = paper_date + timedelta(days=randint(30, 90))
            supplier = choice(suppliers)
            paper_type_choice = choice(paper_types)
            status_choice = choice(statuses)
            amount = randint(5000, 50000)

            # تطبيق الفلاتر
            if supplier_id and str(supplier['id']) != supplier_id:
                continue
            if paper_type and paper_type_choice[0] != paper_type:
                continue
            if status and status_choice[0] != status:
                continue

            payment_papers.append({
                'id': i + 1,
                'paper_number': f'PP-{2024}-{str(i+1).zfill(4)}',
                'paper_type': paper_type_choice[0],
                'paper_type_display': paper_type_choice[1],
                'supplier_id': supplier['id'],
                'supplier_name': supplier['name'],
                'amount': amount,
                'issue_date': paper_date,
                'due_date': due_date,
                'status': status_choice[0],
                'status_display': status_choice[1],
                'bank_name': choice(['البنك الأهلي', 'بنك الرياض', 'بنك ساب', 'البنك السعودي الفرنسي']),
                'notes': f'ملاحظات ورقة الدفع رقم {i+1}' if randint(1, 3) == 1 else None
            })

    # حساب الإحصائيات
    total_papers = len(payment_papers)
    total_amount = sum(paper['amount'] for paper in payment_papers)
    pending_papers = len([p for p in payment_papers if p['status'] == 'PENDING'])
    paid_papers = len([p for p in payment_papers if p['status'] == 'PAID'])
    bounced_papers = len([p for p in payment_papers if p['status'] == 'BOUNCED'])

    # الحصول على قوائم للفلاتر
    suppliers = [
        {'id': 1, 'name': 'شركة الأمل للتجارة'},
        {'id': 2, 'name': 'مؤسسة النور التجارية'},
        {'id': 3, 'name': 'شركة الفجر للمواد'},
        {'id': 4, 'name': 'مكتب السلام التجاري'},
        {'id': 5, 'name': 'شركة الرياض للتوريدات'}
    ]

    context = {
        'title': 'تقرير أوراق الدفع',
        'payment_papers': payment_papers,
        'suppliers': suppliers,
        'date_from': date_from,
        'date_to': date_to,
        'selected_supplier': supplier_id,
        'selected_status': status,
        'selected_paper_type': paper_type,
        'total_papers': total_papers,
        'total_amount': total_amount,
        'pending_papers': pending_papers,
        'paid_papers': paid_papers,
        'bounced_papers': bounced_papers,
    }

    return render(request, 'reports/treasury/payment_papers.html', context)


@login_required
def outgoing_custody_receipts_report(request):
    """تقرير إيصالات الأمانة الصادرة"""
    context = {
        'title': 'تقرير إيصالات الأمانة الصادرة',
    }
    return render(request, 'reports/treasury/outgoing_custody_receipts.html', context)


@login_required
def expenses_report(request):
    """تقرير المصروفات"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير المصروفات',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        transactions = TreasuryTransaction.objects.filter(
            transaction_type='EXPENSE',
            is_active=True
        )

        if date_from:
            transactions = transactions.filter(transaction_date__gte=date_from)
        if date_to:
            transactions = transactions.filter(transaction_date__lte=date_to)

        context['transactions'] = transactions.order_by('-transaction_date')
        context['total_amount'] = transactions.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'reports/treasury/expenses.html', context)


@login_required
def monthly_expenses_report(request):
    """تقرير المصروفات الشهرية"""
    year = request.GET.get('year', timezone.now().year)

    context = {
        'title': 'تقرير المصروفات الشهرية',
        'year': year,
        'years': range(2020, timezone.now().year + 2),
    }

    # حساب المصروفات لكل شهر
    monthly_expenses = []
    for month in range(1, 13):
        month_expenses = TreasuryTransaction.objects.filter(
            transaction_type='EXPENSE',
            transaction_date__year=year,
            transaction_date__month=month,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_expenses.append({
            'month': month,
            'month_name': [
                'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
            ][month - 1],
            'amount': month_expenses
        })

    context['monthly_expenses'] = monthly_expenses
    context['total_year_expenses'] = sum(item['amount'] for item in monthly_expenses)

    return render(request, 'reports/treasury/monthly_expenses.html', context)


@login_required
def cash_collections_report(request):
    """تقرير التحصيل النقدي"""
    treasury_id = request.GET.get('treasury_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير التحصيل النقدي',
        'treasuries': Treasury.objects.filter(is_active=True).order_by('name'),
        'selected_treasury': treasury_id,
        'date_from': date_from,
        'date_to': date_to,
    }

    if treasury_id or date_from or date_to:
        transactions = TreasuryTransaction.objects.filter(
            transaction_type='RECEIPT',
            is_active=True
        )

        if treasury_id:
            transactions = transactions.filter(treasury_id=treasury_id)
        if date_from:
            transactions = transactions.filter(transaction_date__gte=date_from)
        if date_to:
            transactions = transactions.filter(transaction_date__lte=date_to)

        context['transactions'] = transactions.order_by('-transaction_date')
        context['total_amount'] = transactions.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'reports/treasury/cash_collections.html', context)


@login_required
def collection_papers_report(request):
    """تقرير أوراق القبض"""
    context = {
        'title': 'تقرير أوراق القبض',
    }
    return render(request, 'reports/treasury/collection_papers.html', context)


@login_required
def incoming_custody_receipts_report(request):
    """تقرير إيصالات الأمانة الواردة"""
    context = {
        'title': 'تقرير إيصالات الأمانة الواردة',
    }
    return render(request, 'reports/treasury/incoming_custody_receipts.html', context)


@login_required
def revenues_report(request):
    """تقرير الإيرادات"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير الإيرادات',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        transactions = TreasuryTransaction.objects.filter(
            transaction_type='REVENUE',
            is_active=True
        )

        if date_from:
            transactions = transactions.filter(transaction_date__gte=date_from)
        if date_to:
            transactions = transactions.filter(transaction_date__lte=date_to)

        context['transactions'] = transactions.order_by('-transaction_date')
        context['total_amount'] = transactions.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'reports/treasury/revenues.html', context)


@login_required
def monthly_revenues_report(request):
    """تقرير الإيرادات الشهرية"""
    year = request.GET.get('year', timezone.now().year)

    context = {
        'title': 'تقرير الإيرادات الشهرية',
        'year': year,
        'years': range(2020, timezone.now().year + 2),
    }

    # حساب الإيرادات لكل شهر
    monthly_revenues = []
    for month in range(1, 13):
        month_revenues = TreasuryTransaction.objects.filter(
            transaction_type='REVENUE',
            transaction_date__year=year,
            transaction_date__month=month,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_revenues.append({
            'month': month,
            'month_name': [
                'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
            ][month - 1],
            'amount': month_revenues
        })

    context['monthly_revenues'] = monthly_revenues
    context['total_year_revenues'] = sum(item['amount'] for item in monthly_revenues)

    return render(request, 'reports/treasury/monthly_revenues.html', context)


@login_required
def treasury_account_statement(request):
    """كشف حساب الخزينة"""
    from datetime import datetime, timedelta
    from random import randint, choice

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # تعيين التواريخ الافتراضية
    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')

    context = {
        'title': 'كشف حساب الخزينة',
        'date_from': date_from,
        'date_to': date_to,
    }

    # إنشاء بيانات وهمية للمعاملات
    transactions = []

    if date_from and date_to:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')

        # أنواع المعاملات
        transaction_types = [
            ('RECEIPT', 'إيراد', 'credit'),
            ('PAYMENT', 'مصروف', 'debit'),
            ('COLLECTION', 'تحصيل', 'credit'),
            ('TRANSFER_IN', 'تحويل داخل', 'credit'),
            ('TRANSFER_OUT', 'تحويل خارج', 'debit')
        ]

        # أوصاف المعاملات
        descriptions = [
            'مبيعات نقدية',
            'تحصيل من عميل',
            'إيراد متنوع',
            'مصروفات إدارية',
            'مصروفات تشغيلية',
            'رواتب وأجور',
            'إيجار المكتب',
            'فواتير كهرباء',
            'مصروفات صيانة',
            'تحويل من البنك'
        ]

        # الأطراف
        parties = [
            'شركة الأمل للتجارة',
            'مؤسسة النور التجارية',
            'شركة الفجر للمواد',
            'مكتب السلام التجاري',
            'شركة الرياض للتوريدات',
            'عميل نقدي',
            'مورد محلي'
        ]

        # إنشاء المعاملات
        running_balance = 50000  # رصيد افتتاحي

        for i in range(20):  # إنشاء 20 معاملة
            transaction_date = start_date + timedelta(days=randint(0, (end_date - start_date).days))
            transaction_type = choice(transaction_types)
            amount = randint(1000, 15000)

            if transaction_type[2] == 'credit':
                debit_amount = 0
                credit_amount = amount
                running_balance += amount
            else:
                debit_amount = amount
                credit_amount = 0
                running_balance -= amount

            transactions.append({
                'date': transaction_date,
                'reference_number': f'TR-{2024}-{str(i+1).zfill(4)}',
                'type': transaction_type[0],
                'type_display': transaction_type[1],
                'description': choice(descriptions),
                'party': choice(parties) if randint(1, 3) == 1 else None,
                'debit_amount': debit_amount,
                'credit_amount': credit_amount,
                'balance': running_balance,
                'notes': f'ملاحظات المعاملة رقم {i+1}' if randint(1, 4) == 1 else None
            })

        # ترتيب المعاملات حسب التاريخ
        transactions.sort(key=lambda x: x['date'])

        # إعادة حساب الأرصدة بالترتيب الصحيح
        running_balance = 50000
        for transaction in transactions:
            if transaction['credit_amount'] > 0:
                running_balance += transaction['credit_amount']
            else:
                running_balance -= transaction['debit_amount']
            transaction['balance'] = running_balance

    # حساب الإحصائيات
    opening_balance = 50000
    total_receipts = sum(t['credit_amount'] for t in transactions)
    total_payments = sum(t['debit_amount'] for t in transactions)
    closing_balance = opening_balance + total_receipts - total_payments
    total_transactions = len(transactions)

    context.update({
        'transactions': transactions,
        'opening_balance': opening_balance,
        'total_receipts': total_receipts,
        'total_payments': total_payments,
        'closing_balance': closing_balance,
        'total_transactions': total_transactions,
    })

    return render(request, 'reports/treasury/account_statement.html', context)


# ==================== تقارير البنوك ====================

@login_required
def banks_reports(request):
    """صفحة تقارير البنوك"""
    context = {
        'title': 'تقارير البنوك',
        'banks': Bank.objects.filter(is_active=True).order_by('name')
    }
    return render(request, 'reports/banks/index.html', context)


@login_required
def bank_account_statement(request):
    """كشف حساب البنك"""
    from datetime import datetime, timedelta
    from random import randint, choice

    bank_id = request.GET.get('bank_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # تعيين التواريخ الافتراضية
    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')

    # بنوك وهمية
    banks = [
        {'id': 1, 'name': 'البنك الأهلي السعودي', 'account_number': '123456789', 'branch': 'الرياض الرئيسي'},
        {'id': 2, 'name': 'بنك الرياض', 'account_number': '987654321', 'branch': 'فرع الملك فهد'},
        {'id': 3, 'name': 'البنك السعودي الفرنسي', 'account_number': '456789123', 'branch': 'فرع العليا'},
        {'id': 4, 'name': 'بنك ساب', 'account_number': '789123456', 'branch': 'فرع الملز'},
        {'id': 5, 'name': 'البنك السعودي للاستثمار', 'account_number': '321654987', 'branch': 'فرع النخيل'}
    ]

    context = {
        'title': 'كشف حساب البنك',
        'banks': banks,
        'selected_bank': bank_id,
        'date_from': date_from,
        'date_to': date_to,
    }

    if bank_id:
        # العثور على البنك المحدد
        selected_bank = next((bank for bank in banks if str(bank['id']) == bank_id), None)
        if selected_bank:
            context['bank'] = selected_bank

            # إنشاء معاملات وهمية
            transactions = []

            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')

            # أوصاف المعاملات
            deposit_descriptions = [
                'إيداع نقدي',
                'تحويل من حساب آخر',
                'إيداع شيك',
                'تحصيل فاتورة',
                'إيراد مبيعات',
                'عائد استثمار',
                'تحويل من عميل'
            ]

            withdrawal_descriptions = [
                'سحب نقدي',
                'تحويل لحساب آخر',
                'دفع فاتورة',
                'سداد قرض',
                'مصروفات إدارية',
                'رسوم بنكية',
                'دفع لمورد'
            ]

            # إنشاء المعاملات
            for i in range(15):  # إنشاء 15 معاملة
                transaction_date = start_date + timedelta(days=randint(0, (end_date - start_date).days))
                transaction_type = choice(['DEPOSIT', 'WITHDRAWAL'])
                amount = randint(5000, 50000)

                if transaction_type == 'DEPOSIT':
                    description = choice(deposit_descriptions)
                else:
                    description = choice(withdrawal_descriptions)

                transactions.append({
                    'transaction_date': transaction_date,
                    'transaction_type': transaction_type,
                    'amount': amount,
                    'description': description,
                    'reference_number': f'BT-{2024}-{str(i+1).zfill(4)}'
                })

            # ترتيب المعاملات حسب التاريخ
            transactions.sort(key=lambda x: x['transaction_date'])

            context['transactions'] = transactions

            # حساب الأرصدة
            total_deposits = sum(t['amount'] for t in transactions if t['transaction_type'] == 'DEPOSIT')
            total_withdrawals = sum(t['amount'] for t in transactions if t['transaction_type'] == 'WITHDRAWAL')
            balance = total_deposits - total_withdrawals

            context['total_deposits'] = total_deposits
            context['total_withdrawals'] = total_withdrawals
            context['balance'] = balance

    return render(request, 'reports/banks/account_statement.html', context)


# ==================== تقارير المبيعات ====================

@login_required
def sales_reports(request):
    """صفحة تقارير المبيعات"""
    context = {
        'title': 'تقارير المبيعات',
    }
    return render(request, 'reports/sales/index.html', context)


@login_required
def sales_detailed_report(request):
    """تقرير المبيعات التفصيلي"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    customer_id = request.GET.get('customer_id')

    context = {
        'title': 'تقرير المبيعات التفصيلي',
        'customers': Customer.objects.filter(is_active=True).order_by('name'),
        'date_from': date_from,
        'date_to': date_to,
        'selected_customer': customer_id,
    }

    if date_from or date_to or customer_id:
        invoices = SalesInvoice.objects.filter(is_active=True)

        if date_from:
            invoices = invoices.filter(date__gte=date_from)
        if date_to:
            invoices = invoices.filter(date__lte=date_to)
        if customer_id:
            invoices = invoices.filter(customer_id=customer_id)

        context['invoices'] = invoices.order_by('-date')
        total_amount = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_invoices = invoices.count()
        context['total_amount'] = total_amount
        context['total_invoices'] = total_invoices
        context['average_invoice'] = total_amount / total_invoices if total_invoices > 0 else 0

    return render(request, 'reports/sales/detailed.html', context)


@login_required
def sales_monthly_report(request):
    """تقرير المبيعات الشهرية"""
    year = request.GET.get('year', timezone.now().year)

    context = {
        'title': 'تقرير المبيعات الشهرية',
        'year': year,
        'years': range(2020, timezone.now().year + 2),
    }

    # حساب المبيعات لكل شهر
    monthly_sales = []
    for month in range(1, 13):
        month_sales = SalesInvoice.objects.filter(
            date__year=year,
            date__month=month,
            is_active=True
        ).aggregate(
            total_amount=Sum('total_amount'),
            count=Count('id')
        )

        amount = month_sales['total_amount'] or 0
        count = month_sales['count'] or 0
        average = amount / count if count > 0 else 0

        monthly_sales.append({
            'month': month,
            'month_name': [
                'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
            ][month - 1],
            'amount': amount,
            'count': count,
            'average': average
        })

    context['monthly_sales'] = monthly_sales
    total_year_sales = sum(item['amount'] for item in monthly_sales)
    total_year_invoices = sum(item['count'] for item in monthly_sales)
    context['total_year_sales'] = total_year_sales
    context['total_year_invoices'] = total_year_invoices
    context['average_year_invoice'] = total_year_sales / total_year_invoices if total_year_invoices > 0 else 0

    return render(request, 'reports/sales/monthly.html', context)


@login_required
def sales_summary_report(request):
    """تقرير المبيعات الإجمالي"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير المبيعات الإجمالي',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        invoices = SalesInvoice.objects.filter(is_active=True)

        if date_from:
            invoices = invoices.filter(date__gte=date_from)
        if date_to:
            invoices = invoices.filter(date__lte=date_to)

        # إحصائيات عامة
        stats = invoices.aggregate(
            total_amount=Sum('total_amount'),
            total_discount=Sum('discount_amount'),
            total_tax=Sum('tax_amount'),
            count=Count('id'),
            avg_amount=Avg('total_amount')
        )

        # المبيعات حسب العملاء
        customer_sales = invoices.values(
            'customer__name'
        ).annotate(
            total_amount=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total_amount')[:10]

        context['stats'] = stats
        context['customer_sales'] = customer_sales

    return render(request, 'reports/sales/summary.html', context)


@login_required
def sales_profit_report(request):
    """تقرير ربح المبيعات"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير ربح المبيعات',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        invoice_items = SalesInvoiceItem.objects.filter(
            invoice__is_active=True
        )

        if date_from:
            invoice_items = invoice_items.filter(invoice__date__gte=date_from)
        if date_to:
            invoice_items = invoice_items.filter(invoice__date__lte=date_to)

        # حساب الربح لكل صنف
        profit_items = []
        items_dict = {}

        for item in invoice_items:
            item_key = item.item.id
            cost_price = getattr(item.item, 'cost_price', 0) or 0

            if item_key not in items_dict:
                items_dict[item_key] = {
                    'item_name': item.item.name,
                    'item_code': item.item.code,
                    'quantity': 0,
                    'unit_price': 0,
                    'cost_price': cost_price,
                    'total_sales': 0,
                    'total_cost': 0
                }

            items_dict[item_key]['quantity'] += item.quantity
            items_dict[item_key]['total_sales'] += item.total_amount
            items_dict[item_key]['total_cost'] += cost_price * item.quantity
            items_dict[item_key]['unit_price'] = item.unit_price

        for item_data in items_dict.values():
            profit = item_data['total_sales'] - item_data['total_cost']
            profit_margin = (profit / item_data['total_sales'] * 100) if item_data['total_sales'] > 0 else 0

            profit_items.append({
                'item_name': item_data['item_name'],
                'item_code': item_data['item_code'],
                'quantity': item_data['quantity'],
                'unit_price': item_data['unit_price'],
                'cost_price': item_data['cost_price'],
                'total_sales': item_data['total_sales'],
                'total_cost': item_data['total_cost'],
                'profit': profit,
                'profit_margin': profit_margin
            })

        context['profit_items'] = profit_items
        total_sales = sum(item['total_sales'] for item in profit_items)
        total_cost = sum(item['total_cost'] for item in profit_items)
        total_profit = sum(item['profit'] for item in profit_items)
        profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

        context['total_sales'] = total_sales
        context['total_cost'] = total_cost
        context['total_profit'] = total_profit
        context['profit_margin'] = profit_margin

    return render(request, 'reports/sales/profits.html', context)


@login_required
def sales_discounts_report(request):
    """تقرير خصومات المبيعات"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير خصومات المبيعات',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        invoices = SalesInvoice.objects.filter(
            is_active=True,
            discount_amount__gt=0
        )

        if date_from:
            invoices = invoices.filter(date__gte=date_from)
        if date_to:
            invoices = invoices.filter(date__lte=date_to)

        # إضافة حسابات إضافية لكل فاتورة
        invoices_list = []
        for invoice in invoices.order_by('-date'):
            discount_percentage = 0
            amount_after_discount = invoice.subtotal
            if invoice.subtotal > 0:
                discount_percentage = (invoice.discount_amount / invoice.subtotal) * 100
                amount_after_discount = invoice.subtotal - invoice.discount_amount

            invoices_list.append({
                'invoice': invoice,
                'discount_percentage': discount_percentage,
                'amount_after_discount': amount_after_discount
            })

        context['invoices'] = invoices_list
        total_discount = invoices.aggregate(total=Sum('discount_amount'))['total'] or 0
        total_invoices = invoices.count()
        context['total_discount'] = total_discount
        context['total_invoices'] = total_invoices
        context['average_discount'] = total_discount / total_invoices if total_invoices > 0 else 0

    return render(request, 'reports/sales/discounts.html', context)


@login_required
def representative_commission_report(request):
    """تقرير عمولة المندوب"""
    context = {
        'title': 'تقرير عمولة المندوب',
    }
    return render(request, 'reports/sales/representative_commission.html', context)


@login_required
def employee_commission_report(request):
    """تقرير عمولة الموظف"""
    context = {
        'title': 'تقرير عمولة الموظف',
    }
    return render(request, 'reports/sales/employee_commission.html', context)


@login_required
def quotations_detailed_report(request):
    """تقرير عروض الأسعار التفصيلي"""
    context = {
        'title': 'تقرير عروض الأسعار التفصيلي',
    }
    return render(request, 'reports/sales/quotations_detailed.html', context)


@login_required
def quotations_summary_report(request):
    """تقرير عروض الأسعار الإجمالي"""
    context = {
        'title': 'تقرير عروض الأسعار الإجمالي',
    }
    return render(request, 'reports/sales/quotations_summary.html', context)


# ==================== تقارير المشتريات ====================

@login_required
def purchases_reports(request):
    """صفحة تقارير المشتريات"""
    context = {
        'title': 'تقارير المشتريات',
    }
    return render(request, 'reports/purchases/index.html', context)


@login_required
def purchases_detailed_report(request):
    """تقرير المشتريات التفصيلي"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    supplier_id = request.GET.get('supplier_id')

    context = {
        'title': 'تقرير المشتريات التفصيلي',
        'suppliers': Supplier.objects.filter(is_active=True).order_by('name'),
        'date_from': date_from,
        'date_to': date_to,
        'selected_supplier': supplier_id,
    }

    if date_from or date_to or supplier_id:
        invoices = PurchaseInvoice.objects.filter(is_active=True)

        if date_from:
            invoices = invoices.filter(date__gte=date_from)
        if date_to:
            invoices = invoices.filter(date__lte=date_to)
        if supplier_id:
            invoices = invoices.filter(supplier_id=supplier_id)

        context['invoices'] = invoices.order_by('-date')
        total_amount = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_invoices = invoices.count()
        context['total_amount'] = total_amount
        context['total_invoices'] = total_invoices
        context['average_invoice'] = total_amount / total_invoices if total_invoices > 0 else 0

    return render(request, 'reports/purchases/detailed.html', context)


@login_required
def purchases_monthly_report(request):
    """تقرير المشتريات الشهرية"""
    year = request.GET.get('year', timezone.now().year)

    context = {
        'title': 'تقرير المشتريات الشهرية',
        'year': year,
        'years': range(2020, timezone.now().year + 2),
    }

    # حساب المشتريات لكل شهر
    monthly_purchases = []
    for month in range(1, 13):
        month_purchases = PurchaseInvoice.objects.filter(
            date__year=year,
            date__month=month,
            is_active=True
        ).aggregate(
            total_amount=Sum('total_amount'),
            count=Count('id')
        )

        amount = month_purchases['total_amount'] or 0
        count = month_purchases['count'] or 0
        average = amount / count if count > 0 else 0

        monthly_purchases.append({
            'month': month,
            'month_name': [
                'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
            ][month - 1],
            'amount': amount,
            'count': count,
            'average': average
        })

    context['monthly_purchases'] = monthly_purchases
    total_year_purchases = sum(item['amount'] for item in monthly_purchases)
    total_year_invoices = sum(item['count'] for item in monthly_purchases)
    context['total_year_purchases'] = total_year_purchases
    context['total_year_invoices'] = total_year_invoices
    context['average_year_invoice'] = total_year_purchases / total_year_invoices if total_year_invoices > 0 else 0

    return render(request, 'reports/purchases/monthly.html', context)


@login_required
def purchases_summary_report(request):
    """تقرير المشتريات الإجمالي"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير المشتريات الإجمالي',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        invoices = PurchaseInvoice.objects.filter(is_active=True)

        if date_from:
            invoices = invoices.filter(date__gte=date_from)
        if date_to:
            invoices = invoices.filter(date__lte=date_to)

        # إحصائيات عامة
        stats = invoices.aggregate(
            total_amount=Sum('total_amount'),
            total_discount=Sum('discount_amount'),
            total_tax=Sum('tax_amount'),
            count=Count('id'),
            avg_amount=Avg('total_amount')
        )

        # المشتريات حسب الموردين
        supplier_purchases = invoices.values(
            'supplier__name'
        ).annotate(
            total_amount=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total_amount')[:10]

        context['stats'] = stats
        context['supplier_purchases'] = supplier_purchases

    return render(request, 'reports/purchases/summary.html', context)


@login_required
def purchases_discounts_report(request):
    """تقرير خصومات المشتريات"""
    from datetime import datetime, timedelta
    from random import randint, choice

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    supplier_id = request.GET.get('supplier_id')

    # تعيين التواريخ الافتراضية
    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')

    # موردين وهميين
    suppliers = [
        {'id': 1, 'name': 'شركة الأمل للتجارة', 'phone': '0112345678'},
        {'id': 2, 'name': 'مؤسسة النور التجارية', 'phone': '0112345679'},
        {'id': 3, 'name': 'شركة الفجر للمواد', 'phone': '0112345680'},
        {'id': 4, 'name': 'مكتب السلام التجاري', 'phone': '0112345681'},
        {'id': 5, 'name': 'شركة الرياض للتوريدات', 'phone': '0112345682'}
    ]

    context = {
        'title': 'تقرير خصومات المشتريات',
        'suppliers': suppliers,
        'date_from': date_from,
        'date_to': date_to,
        'selected_supplier': supplier_id,
    }

    # إنشاء بيانات وهمية للفواتير مع خصومات
    invoices = []

    if date_from and date_to:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')

        # إنشاء فواتير مع خصومات
        for i in range(10):  # إنشاء 10 فواتير
            invoice_date = start_date + timedelta(days=randint(0, (end_date - start_date).days))
            supplier = choice(suppliers)
            subtotal = randint(20000, 80000)
            discount_amount = randint(1000, 5000)
            tax_amount = randint(500, 2000)
            total_amount = subtotal - discount_amount + tax_amount

            # تطبيق فلتر المورد
            if supplier_id and str(supplier['id']) != supplier_id:
                continue

            # حساب النسب
            discount_percentage = (discount_amount / subtotal * 100) if subtotal > 0 else 0
            amount_after_discount = subtotal - discount_amount

            invoices.append({
                'invoice': {
                    'invoice_number': f'PI-{2024}-{str(i+1).zfill(4)}',
                    'date': invoice_date,
                    'supplier': supplier,
                    'subtotal': subtotal,
                    'discount_amount': discount_amount,
                    'tax_amount': tax_amount,
                    'total_amount': total_amount
                },
                'discount_percentage': discount_percentage,
                'amount_after_discount': amount_after_discount
            })

    # حساب الإحصائيات
    total_discount = sum(inv['invoice']['discount_amount'] for inv in invoices)
    total_invoices = len(invoices)
    average_discount = total_discount / total_invoices if total_invoices > 0 else 0
    total_subtotal = sum(inv['invoice']['subtotal'] for inv in invoices)
    average_discount_percentage = (total_discount / total_subtotal * 100) if total_subtotal > 0 else 0
    total_after_discount = sum(inv['amount_after_discount'] for inv in invoices)
    total_final_amount = sum(inv['invoice']['total_amount'] for inv in invoices)

    context.update({
        'invoices': invoices,
        'total_discount': total_discount,
        'total_invoices': total_invoices,
        'average_discount': average_discount,
        'average_discount_percentage': average_discount_percentage,
        'total_after_discount': total_after_discount,
        'total_final_amount': total_final_amount,
    })

    return render(request, 'reports/purchases/discounts.html', context)


@login_required
def supply_orders_report(request):
    """تقرير أوامر التوريد"""
    from datetime import datetime, timedelta
    from random import randint, choice

    # الحصول على المعاملات
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    supplier_id = request.GET.get('supplier_id')
    status = request.GET.get('status')

    # تعيين التواريخ الافتراضية
    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')

    # موردين وهميين
    suppliers = [
        {'id': 1, 'name': 'شركة الأمل للتجارة', 'phone': '0112345678'},
        {'id': 2, 'name': 'مؤسسة النور التجارية', 'phone': '0112345679'},
        {'id': 3, 'name': 'شركة الفجر للمواد', 'phone': '0112345680'},
        {'id': 4, 'name': 'مكتب السلام التجاري', 'phone': '0112345681'},
        {'id': 5, 'name': 'شركة الرياض للتوريدات', 'phone': '0112345682'}
    ]

    # إنشاء بيانات وهمية لأوامر التوريد
    orders = []

    if date_from and date_to:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')

        # حالات أوامر التوريد
        statuses = [
            ('PENDING', 'معلق'),
            ('APPROVED', 'معتمد'),
            ('ORDERED', 'مطلوب'),
            ('RECEIVED', 'مستلم'),
            ('CANCELLED', 'ملغي')
        ]

        # أسماء المعتمدين
        approvers = [
            'أحمد محمد',
            'فاطمة علي',
            'محمد سالم',
            'نورا أحمد',
            'خالد عبدالله'
        ]

        # إنشاء أوامر التوريد
        for i in range(12):  # إنشاء 12 أمر توريد
            order_date = start_date + timedelta(days=randint(0, (end_date - start_date).days))
            delivery_date = order_date + timedelta(days=randint(7, 30))
            supplier = choice(suppliers)
            status_choice = choice(statuses)
            amount = randint(10000, 100000)

            # تطبيق الفلاتر
            if supplier_id and str(supplier['id']) != supplier_id:
                continue
            if status and status_choice[0] != status:
                continue

            orders.append({
                'id': i + 1,
                'order_number': f'SO-{2024}-{str(i+1).zfill(4)}',
                'order_date': order_date,
                'supplier_id': supplier['id'],
                'supplier_name': supplier['name'],
                'supplier_phone': supplier['phone'],
                'total_amount': amount,
                'expected_delivery_date': delivery_date,
                'status': status_choice[0],
                'status_display': status_choice[1],
                'approved_by': choice(approvers) if status_choice[0] != 'PENDING' else None,
                'approved_date': order_date + timedelta(days=1) if status_choice[0] != 'PENDING' else None,
                'notes': f'ملاحظات أمر التوريد رقم {i+1}' if randint(1, 3) == 1 else None
            })

    # حساب الإحصائيات
    total_orders = len(orders)
    total_amount = sum(order['total_amount'] for order in orders)
    pending_orders = len([o for o in orders if o['status'] == 'PENDING'])
    received_orders = len([o for o in orders if o['status'] == 'RECEIVED'])

    context = {
        'title': 'تقرير أوامر التوريد',
        'orders': orders,
        'suppliers': suppliers,
        'date_from': date_from,
        'date_to': date_to,
        'selected_supplier': supplier_id,
        'selected_status': status,
        'total_orders': total_orders,
        'total_amount': total_amount,
        'pending_orders': pending_orders,
        'received_orders': received_orders,
    }

    return render(request, 'reports/purchases/supply_orders.html', context)


# ==================== اليوميات الإجمالية ====================

@login_required
def general_journals_report(request):
    """تقرير اليوميات الإجمالية"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير اليوميات الإجمالية',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        # جمع جميع المعاملات من مختلف الأنظمة
        transactions = []

        # معاملات المبيعات
        sales_invoices = SalesInvoice.objects.filter(is_active=True)
        if date_from:
            sales_invoices = sales_invoices.filter(date__gte=date_from)
        if date_to:
            sales_invoices = sales_invoices.filter(date__lte=date_to)

        for invoice in sales_invoices:
            transactions.append({
                'date': invoice.date,
                'type': 'مبيعات',
                'reference': f'فاتورة مبيعات رقم {invoice.invoice_number}',
                'debit': invoice.total_amount,
                'credit': 0,
                'description': f'مبيعات للعميل: {invoice.customer.name}'
            })

        # معاملات المشتريات
        purchase_invoices = PurchaseInvoice.objects.filter(is_active=True)
        if date_from:
            purchase_invoices = purchase_invoices.filter(date__gte=date_from)
        if date_to:
            purchase_invoices = purchase_invoices.filter(date__lte=date_to)

        for invoice in purchase_invoices:
            transactions.append({
                'date': invoice.date,
                'type': 'مشتريات',
                'reference': f'فاتورة مشتريات رقم {invoice.invoice_number}',
                'debit': 0,
                'credit': invoice.total_amount,
                'description': f'مشتريات من المورد: {invoice.supplier.name}'
            })

        # معاملات الخزينة
        treasury_transactions = TreasuryTransaction.objects.filter(is_active=True)
        if date_from:
            treasury_transactions = treasury_transactions.filter(transaction_date__gte=date_from)
        if date_to:
            treasury_transactions = treasury_transactions.filter(transaction_date__lte=date_to)

        for transaction in treasury_transactions:
            if transaction.transaction_type in ['RECEIPT', 'REVENUE']:
                debit, credit = transaction.amount, 0
            else:
                debit, credit = 0, transaction.amount

            transactions.append({
                'date': transaction.transaction_date,
                'type': 'خزينة',
                'reference': f'معاملة خزينة رقم {transaction.id}',
                'debit': debit,
                'credit': credit,
                'description': transaction.description or transaction.get_transaction_type_display()
            })

        # ترتيب المعاملات حسب التاريخ
        transactions.sort(key=lambda x: x['date'])

        context['transactions'] = transactions
        context['total_debit'] = sum(t['debit'] for t in transactions)
        context['total_credit'] = sum(t['credit'] for t in transactions)

    return render(request, 'reports/general_journals.html', context)


# ==================== تقارير المخازن ====================

@login_required
def warehouses_reports(request):
    """صفحة تقارير المخازن"""
    context = {
        'title': 'تقارير المخازن',
        'warehouses': Warehouse.objects.filter(is_active=True).order_by('name')
    }
    return render(request, 'reports/warehouses/index.html', context)


@login_required
def stock_increases_report(request):
    """تقرير أذون إضافة الزيادات"""
    warehouse_id = request.GET.get('warehouse_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير أذون إضافة الزيادات',
        'warehouses': Warehouse.objects.filter(is_active=True).order_by('name'),
        'selected_warehouse': warehouse_id,
        'date_from': date_from,
        'date_to': date_to,
    }

    if warehouse_id or date_from or date_to:
        increases = StockIncrease.objects.filter(is_active=True)

        if warehouse_id:
            increases = increases.filter(warehouse_id=warehouse_id)
        if date_from:
            increases = increases.filter(date__gte=date_from)
        if date_to:
            increases = increases.filter(date__lte=date_to)

        context['increases'] = increases.order_by('-date')
        context['total_increases'] = increases.count()

    return render(request, 'reports/warehouses/stock_increases.html', context)


@login_required
def stock_decreases_detailed_report(request):
    """تقرير أذون صرف النواقص التفصيلي"""
    warehouse_id = request.GET.get('warehouse_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير أذون صرف النواقص التفصيلي',
        'warehouses': Warehouse.objects.filter(is_active=True).order_by('name'),
        'selected_warehouse': warehouse_id,
        'date_from': date_from,
        'date_to': date_to,
    }

    if warehouse_id or date_from or date_to:
        decreases = StockDecrease.objects.filter(is_active=True)

        if warehouse_id:
            decreases = decreases.filter(warehouse_id=warehouse_id)
        if date_from:
            decreases = decreases.filter(date__gte=date_from)
        if date_to:
            decreases = decreases.filter(date__lte=date_to)

        context['decreases'] = decreases.order_by('-date')
        context['total_decreases'] = decreases.count()

    return render(request, 'reports/warehouses/stock_decreases_detailed.html', context)


@login_required
def stock_decreases_monthly_report(request):
    """تقرير أذون صرف النواقص الشهري"""
    year = request.GET.get('year', timezone.now().year)
    warehouse_id = request.GET.get('warehouse_id')

    context = {
        'title': 'تقرير أذون صرف النواقص الشهري',
        'year': year,
        'years': range(2020, timezone.now().year + 2),
        'warehouses': Warehouse.objects.filter(is_active=True).order_by('name'),
        'selected_warehouse': warehouse_id,
    }

    # حساب الصرف لكل شهر
    monthly_decreases = []
    for month in range(1, 13):
        decreases = StockDecrease.objects.filter(
            transaction_date__year=year,
            transaction_date__month=month,
            is_active=True
        )

        if warehouse_id:
            decreases = decreases.filter(warehouse_id=warehouse_id)

        monthly_decreases.append({
            'month': month,
            'month_name': [
                'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
            ][month - 1],
            'count': decreases.count()
        })

    context['monthly_decreases'] = monthly_decreases
    context['total_year_decreases'] = sum(item['count'] for item in monthly_decreases)

    return render(request, 'reports/warehouses/stock_decreases_monthly.html', context)


@login_required
def stock_decreases_renewal_report(request):
    """تقرير أذون صرف النواقص - تاريخ التجديد"""
    context = {
        'title': 'تقرير أذون صرف النواقص - تاريخ التجديد',
    }
    return render(request, 'reports/warehouses/stock_decreases_renewal.html', context)


@login_required
def warehouse_transfers_detailed_report(request):
    """تقرير التحويلات بين المخازن التفصيلي"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    from_warehouse_id = request.GET.get('from_warehouse_id')
    to_warehouse_id = request.GET.get('to_warehouse_id')

    context = {
        'title': 'تقرير التحويلات بين المخازن التفصيلي',
        'warehouses': Warehouse.objects.filter(is_active=True).order_by('name'),
        'date_from': date_from,
        'date_to': date_to,
        'selected_from_warehouse': from_warehouse_id,
        'selected_to_warehouse': to_warehouse_id,
    }

    if date_from or date_to or from_warehouse_id or to_warehouse_id:
        transfers = WarehouseTransfer.objects.filter(is_active=True)

        if date_from:
            transfers = transfers.filter(date__gte=date_from)
        if date_to:
            transfers = transfers.filter(date__lte=date_to)
        if from_warehouse_id:
            transfers = transfers.filter(from_warehouse_id=from_warehouse_id)
        if to_warehouse_id:
            transfers = transfers.filter(to_warehouse_id=to_warehouse_id)

        context['transfers'] = transfers.order_by('-date')
        context['total_transfers'] = transfers.count()

    return render(request, 'reports/warehouses/transfers_detailed.html', context)


@login_required
def warehouse_transfers_summary_report(request):
    """تقرير التحويلات بين المخازن الإجمالي"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير التحويلات بين المخازن الإجمالي',
        'date_from': date_from,
        'date_to': date_to,
    }

    if date_from or date_to:
        transfers = WarehouseTransfer.objects.filter(is_active=True)

        if date_from:
            transfers = transfers.filter(date__gte=date_from)
        if date_to:
            transfers = transfers.filter(date__lte=date_to)

        # إحصائيات حسب المخازن
        warehouse_stats = transfers.values(
            'from_warehouse__name',
            'to_warehouse__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        context['warehouse_stats'] = warehouse_stats
        context['total_transfers'] = transfers.count()

    return render(request, 'reports/warehouses/transfers_summary.html', context)


@login_required
def production_report(request):
    """تقرير الإنتاج التام أو تحت التشغيل"""
    context = {
        'title': 'تقرير الإنتاج التام أو تحت التشغيل',
    }
    return render(request, 'reports/warehouses/production.html', context)


@login_required
def items_prices_report(request):
    """تقرير الأصناف وأسعارها"""
    category_id = request.GET.get('category_id')

    context = {
        'title': 'تقرير الأصناف وأسعارها',
        'categories': Item.objects.values_list('category', flat=True).distinct(),
        'selected_category': category_id,
    }

    items = Item.objects.filter(is_active=True)

    if category_id:
        items = items.filter(category_id=category_id)

    context['items'] = items.order_by('name')

    return render(request, 'reports/warehouses/items_prices.html', context)


@login_required
def item_movement_report(request):
    """تقرير حركة صنف"""
    item_id = request.GET.get('item_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير حركة صنف',
        'items': Item.objects.filter(is_active=True).order_by('name'),
        'selected_item': item_id,
        'date_from': date_from,
        'date_to': date_to,
    }

    if item_id:
        item = get_object_or_404(Item, id=item_id)
        context['item'] = item

        # جمع حركات الصنف من مختلف المصادر
        movements = []

        # حركات المبيعات
        sales_items = SalesInvoiceItem.objects.filter(
            item=item,
            invoice__is_active=True
        )

        if date_from:
            sales_items = sales_items.filter(invoice__date__gte=date_from)
        if date_to:
            sales_items = sales_items.filter(invoice__date__lte=date_to)

        for sale_item in sales_items:
            movements.append({
                'date': sale_item.invoice.date,
                'type': 'مبيعات',
                'reference': f'فاتورة مبيعات {sale_item.invoice.invoice_number}',
                'quantity_out': sale_item.quantity,
                'quantity_in': 0,
                'unit_price': sale_item.unit_price
            })

        # حركات المشتريات
        purchase_items = PurchaseInvoiceItem.objects.filter(
            item=item,
            invoice__is_active=True
        )

        if date_from:
            purchase_items = purchase_items.filter(invoice__date__gte=date_from)
        if date_to:
            purchase_items = purchase_items.filter(invoice__date__lte=date_to)

        for purchase_item in purchase_items:
            movements.append({
                'date': purchase_item.invoice.date,
                'type': 'مشتريات',
                'reference': f'فاتورة مشتريات {purchase_item.invoice.invoice_number}',
                'quantity_out': 0,
                'quantity_in': purchase_item.quantity,
                'unit_price': purchase_item.unit_price
            })

        # ترتيب الحركات حسب التاريخ
        movements.sort(key=lambda x: x['date'])

        context['movements'] = movements
        context['total_in'] = sum(m['quantity_in'] for m in movements)
        context['total_out'] = sum(m['quantity_out'] for m in movements)
        context['balance'] = context['total_in'] - context['total_out']

    return render(request, 'reports/warehouses/item_movement.html', context)


@login_required
def inventory_report(request):
    """تقرير جرد البضاعة"""
    warehouse_id = request.GET.get('warehouse_id')

    context = {
        'title': 'تقرير جرد البضاعة',
        'warehouses': Warehouse.objects.filter(is_active=True).order_by('name'),
        'selected_warehouse': warehouse_id,
    }

    # حساب المخزون الحالي لكل صنف
    items_inventory = []

    # استخدام نموذج Stock المباشر إذا كان متاحاً
    stocks = Stock.objects.filter(is_active=True)
    if warehouse_id:
        stocks = stocks.filter(warehouse_id=warehouse_id)

    for stock in stocks:
        if stock.quantity > 0:  # عرض الأصناف التي لها رصيد فقط
            items_inventory.append({
                'item': stock.item,
                'warehouse': stock.warehouse,
                'total_in': 0,  # سيتم حسابه لاحقاً إذا لزم الأمر
                'total_out': 0,  # سيتم حسابه لاحقاً إذا لزم الأمر
                'current_balance': stock.quantity,
                'available_quantity': stock.available_quantity,
                'reserved_quantity': stock.reserved_quantity,
                'average_cost': stock.average_cost,
                'value': stock.quantity * stock.average_cost
            })

    # إذا لم توجد أرصدة في نموذج Stock، احسب من الحركات
    if not items_inventory:
        items = Item.objects.filter(is_active=True)

        for item in items:
            # حساب الكمية الداخلة من إضافات المخزون
            increase_qty = StockIncreaseItem.objects.filter(
                item=item,
                increase__is_active=True
            ).aggregate(total=Sum('quantity'))['total'] or 0

            # حساب الكمية الخارجة من صرف المخزون
            decrease_qty = StockDecreaseItem.objects.filter(
                item=item,
                decrease__is_active=True
            ).aggregate(total=Sum('quantity'))['total'] or 0

            # من المبيعات
            sales_qty = SalesInvoiceItem.objects.filter(
                item=item,
                invoice__is_active=True
            ).aggregate(total=Sum('quantity'))['total'] or 0

            # من المشتريات
            purchase_qty = PurchaseInvoiceItem.objects.filter(
                item=item,
                invoice__is_active=True
            ).aggregate(total=Sum('quantity'))['total'] or 0

            total_in = increase_qty + purchase_qty
            total_out = decrease_qty + sales_qty
            current_balance = total_in - total_out

            if current_balance != 0:  # عرض الأصناف التي لها رصيد فقط
                items_inventory.append({
                    'item': item,
                    'total_in': total_in,
                    'total_out': total_out,
                    'current_balance': current_balance,
                    'value': current_balance * (item.cost_price if hasattr(item, 'cost_price') else 0)
                })

    # ترتيب حسب القيمة
    items_inventory.sort(key=lambda x: x['value'], reverse=True)

    context['items_inventory'] = items_inventory
    context['total_value'] = sum(item['value'] for item in items_inventory)

    return render(request, 'reports/warehouses/inventory.html', context)


# ==================== تقارير الأصول الثابتة ====================

@login_required
def assets_reports(request):
    """صفحة تقارير الأصول الثابتة"""
    context = {
        'title': 'تقارير الأصول الثابتة',
    }
    return render(request, 'reports/assets/index.html', context)


@login_required
def current_year_depreciation_report(request):
    """تقرير إهلاك السنة الحالية"""
    year = request.GET.get('year', timezone.now().year)

    context = {
        'title': 'تقرير إهلاك السنة الحالية',
        'year': year,
        'years': range(2020, timezone.now().year + 2),
    }

    # جلب إهلاكات السنة المحددة
    depreciations = DepreciationEntry.objects.filter(
        entry_date__year=year,
        is_active=True
    ).select_related('asset')

    # تجميع الإهلاكات حسب الأصل
    assets_depreciation = {}
    for depreciation in depreciations:
        asset_id = depreciation.asset.id
        if asset_id not in assets_depreciation:
            assets_depreciation[asset_id] = {
                'asset': depreciation.asset,
                'total_depreciation': 0,
                'depreciations': []
            }

        assets_depreciation[asset_id]['total_depreciation'] += depreciation.depreciation_amount
        assets_depreciation[asset_id]['depreciations'].append(depreciation)

    context['assets_depreciation'] = list(assets_depreciation.values())
    context['total_year_depreciation'] = sum(
        item['total_depreciation'] for item in assets_depreciation.values()
    )

    return render(request, 'reports/assets/current_year_depreciation.html', context)


@login_required
def assets_detailed_report(request):
    """تقرير الأصول التفصيلي"""
    asset_group_id = request.GET.get('asset_group_id')

    context = {
        'title': 'تقرير الأصول التفصيلي',
        'asset_groups': Asset.objects.values_list('asset_group', flat=True).distinct(),
        'selected_group': asset_group_id,
    }

    assets = Asset.objects.filter(is_active=True).select_related('asset_group')

    if asset_group_id:
        assets = assets.filter(asset_group_id=asset_group_id)

    # حساب الإهلاك المتراكم لكل أصل
    assets_with_depreciation = []
    for asset in assets:
        total_depreciation = DepreciationEntry.objects.filter(
            asset=asset,
            is_active=True
        ).aggregate(total=Sum('depreciation_amount'))['total'] or 0

        net_value = asset.purchase_price - total_depreciation

        assets_with_depreciation.append({
            'asset': asset,
            'total_depreciation': total_depreciation,
            'net_value': net_value,
            'depreciation_percentage': (total_depreciation / asset.purchase_price * 100) if asset.purchase_price > 0 else 0
        })

    context['assets_with_depreciation'] = assets_with_depreciation
    context['total_purchase_value'] = sum(item['asset'].purchase_price for item in assets_with_depreciation)
    context['total_depreciation'] = sum(item['total_depreciation'] for item in assets_with_depreciation)
    context['total_net_value'] = sum(item['net_value'] for item in assets_with_depreciation)

    return render(request, 'reports/assets/detailed.html', context)


@login_required
def assets_summary_report(request):
    """تقرير الأصول الإجمالي"""
    context = {
        'title': 'تقرير الأصول الإجمالي',
    }

    # إحصائيات عامة
    assets = Asset.objects.filter(is_active=True)

    stats = {
        'total_assets': assets.count(),
        'total_purchase_value': assets.aggregate(total=Sum('purchase_price'))['total'] or 0,
        'total_depreciation': DepreciationEntry.objects.filter(
            is_active=True
        ).aggregate(total=Sum('depreciation_amount'))['total'] or 0,
    }

    stats['total_net_value'] = stats['total_purchase_value'] - stats['total_depreciation']

    # الأصول حسب المجموعات
    group_stats = assets.values(
        'asset_group__name'
    ).annotate(
        count=Count('id'),
        total_value=Sum('purchase_price')
    ).order_by('-total_value')

    # الأصول حسب السنة
    year_stats = assets.values(
        'purchase_date__year'
    ).annotate(
        count=Count('id'),
        total_value=Sum('purchase_price')
    ).order_by('-purchase_date__year')

    context['stats'] = stats
    context['group_stats'] = group_stats
    context['year_stats'] = year_stats

    return render(request, 'reports/assets/summary.html', context)


@login_required
def assets_sale_profits_report(request):
    """تقرير أرباح بيع الأصول"""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    context = {
        'title': 'تقرير أرباح بيع الأصول',
        'date_from': date_from,
        'date_to': date_to,
    }

    # جلب الأصول المباعة
    sold_assets = Asset.objects.filter(
        is_active=False,  # الأصول المباعة أو المستبعدة
        sale_date__isnull=False
    )

    if date_from:
        sold_assets = sold_assets.filter(sale_date__gte=date_from)
    if date_to:
        sold_assets = sold_assets.filter(sale_date__lte=date_to)

    # حساب الربح/الخسارة لكل أصل
    assets_with_profit = []
    for asset in sold_assets:
        # حساب الإهلاك المتراكم
        total_depreciation = DepreciationEntry.objects.filter(
            asset=asset,
            entry_date__lte=asset.sale_date,
            is_active=True
        ).aggregate(total=Sum('depreciation_amount'))['total'] or 0

        # القيمة الدفترية
        book_value = asset.purchase_price - total_depreciation

        # ربح/خسارة البيع
        sale_profit = (asset.sale_price or 0) - book_value

        assets_with_profit.append({
            'asset': asset,
            'purchase_price': asset.purchase_price,
            'total_depreciation': total_depreciation,
            'book_value': book_value,
            'sale_price': asset.sale_price or 0,
            'sale_profit': sale_profit,
            'profit_type': 'ربح' if sale_profit > 0 else 'خسارة' if sale_profit < 0 else 'تعادل'
        })

    context['assets_with_profit'] = assets_with_profit
    context['total_sale_profit'] = sum(item['sale_profit'] for item in assets_with_profit)
    context['total_sold_assets'] = len(assets_with_profit)

    return render(request, 'reports/assets/sale_profits.html', context)
