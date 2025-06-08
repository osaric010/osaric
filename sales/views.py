from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from decimal import Decimal

from .models import (
    Customer, SalesInvoice, SalesInvoiceItem, SalesReturn, SalesReturnItem,
    PriceList, PriceListItem, Quotation, QuotationItem, DiscountPolicy
)
from .forms import (
    CustomerForm, SalesInvoiceForm, SalesReturnForm, PriceListForm,
    QuotationForm, DiscountPolicyForm, PriceDisplayForm, QuotationPeriodReportForm
)


@login_required
def sales_home(request):
    """الصفحة الرئيسية للمبيعات"""
    # إحصائيات المبيعات
    today = timezone.now().date()
    this_month = today.replace(day=1)

    context = {
        'title': 'المبيعات',
        'customers_count': Customer.objects.count(),
        'invoices_count': SalesInvoice.objects.count(),
        'quotations_count': Quotation.objects.count(),
        'returns_count': SalesReturn.objects.count(),
        'price_lists_count': PriceList.objects.count(),
        'monthly_sales': SalesInvoice.objects.filter(
            date__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0'),
        'pending_quotations': Quotation.objects.filter(
            status='SENT', valid_until__gte=today
        ).count(),
    }
    return render(request, 'sales/home.html', context)


# Customer Views
@login_required
def customer_list(request):
    """قائمة العملاء"""
    search_query = request.GET.get('search', '')
    customers = Customer.objects.all()

    if search_query:
        customers = customers.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    customers = customers.order_by('name')
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'العملاء'
    }
    return render(request, 'sales/customer_list.html', context)


@login_required
def customer_create(request):
    """إضافة عميل جديد"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, 'تم إضافة العميل بنجاح')
            return redirect('sales:customer_list')
    else:
        form = CustomerForm()

    context = {
        'form': form,
        'title': 'إضافة عميل جديد',
        'action': 'إضافة'
    }
    return render(request, 'sales/customer_form.html', context)


@login_required
def customer_edit(request, pk):
    """تعديل عميل"""
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_by = request.user
            customer.save()
            messages.success(request, 'تم تحديث العميل بنجاح')
            return redirect('sales:customer_list')
    else:
        form = CustomerForm(instance=customer)

    context = {
        'form': form,
        'customer': customer,
        'title': f'تعديل العميل: {customer.name}',
        'action': 'تحديث'
    }
    return render(request, 'sales/customer_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def customer_delete(request, pk):
    """حذف عميل"""
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    customer.updated_by = request.user
    customer.save()
    return JsonResponse({'success': True, 'message': 'تم حذف العميل بنجاح'})


# Sales Invoice Views
@login_required
def invoice_list(request):
    """قائمة فواتير المبيعات"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    invoices = SalesInvoice.objects.all().select_related('customer', 'warehouse')

    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    invoices = invoices.order_by('-date', '-id')
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    status_choices = SalesInvoice._meta.get_field('status').choices

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'title': 'فواتير المبيعات'
    }
    return render(request, 'sales/invoice_list.html', context)


@login_required
def invoice_create(request):
    """إضافة فاتورة مبيعات جديدة"""
    if request.method == 'POST':
        form = SalesInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, 'تم إضافة الفاتورة بنجاح')
            return redirect('sales:invoice_detail', pk=invoice.pk)
    else:
        form = SalesInvoiceForm()

    context = {
        'form': form,
        'title': 'إضافة فاتورة مبيعات جديدة',
        'action': 'إضافة'
    }
    return render(request, 'sales/invoice_form.html', context)


@login_required
def invoice_detail(request, pk):
    """تفاصيل فاتورة المبيعات"""
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    items = invoice.items.all().select_related('item')

    context = {
        'invoice': invoice,
        'items': items,
        'title': f'فاتورة رقم: {invoice.invoice_number}'
    }
    return render(request, 'sales/invoice_detail.html', context)


@login_required
def invoice_edit(request, pk):
    """تعديل فاتورة مبيعات"""
    invoice = get_object_or_404(SalesInvoice, pk=pk)

    if request.method == 'POST':
        form = SalesInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.updated_by = request.user
            invoice.save()
            messages.success(request, 'تم تحديث الفاتورة بنجاح')
            return redirect('sales:invoice_detail', pk=invoice.pk)
    else:
        form = SalesInvoiceForm(instance=invoice)

    context = {
        'form': form,
        'invoice': invoice,
        'title': f'تعديل الفاتورة: {invoice.invoice_number}',
        'action': 'تحديث'
    }
    return render(request, 'sales/invoice_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def invoice_delete(request, pk):
    """حذف فاتورة مبيعات"""
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    invoice.delete()
    invoice.updated_by = request.user
    invoice.save()
    return JsonResponse({'success': True, 'message': 'تم حذف الفاتورة بنجاح'})


# Sales Return Views
@login_required
def return_list(request):
    """قائمة مرتجعات المبيعات"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    returns = SalesReturn.objects.all().select_related('customer', 'warehouse')

    if search_query:
        returns = returns.filter(
            Q(return_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    if status_filter:
        returns = returns.filter(status=status_filter)

    returns = returns.order_by('-date', '-id')
    paginator = Paginator(returns, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    status_choices = SalesReturn._meta.get_field('status').choices

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'title': 'مرتجعات المبيعات'
    }
    return render(request, 'sales/return_list.html', context)


@login_required
def return_create(request):
    """إضافة مرتجع مبيعات جديد"""
    if request.method == 'POST':
        form = SalesReturnForm(request.POST)
        if form.is_valid():
            return_doc = form.save(commit=False)
            return_doc.created_by = request.user
            return_doc.save()
            messages.success(request, 'تم إضافة المرتجع بنجاح')
            return redirect('sales:return_list')
    else:
        form = SalesReturnForm()

    context = {
        'form': form,
        'title': 'إضافة مرتجع مبيعات جديد',
        'action': 'إضافة'
    }
    return render(request, 'sales/return_form.html', context)


# Quotation Views
@login_required
def quotation_list(request):
    """قائمة عروض الأسعار"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    quotations = Quotation.objects.all().select_related('customer')

    if search_query:
        quotations = quotations.filter(
            Q(quotation_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    if status_filter:
        quotations = quotations.filter(status=status_filter)

    quotations = quotations.order_by('-date', '-id')
    paginator = Paginator(quotations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    status_choices = Quotation._meta.get_field('status').choices

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'title': 'عروض الأسعار'
    }
    return render(request, 'sales/quotation_list.html', context)


@login_required
def quotation_create(request):
    """إضافة عرض سعر جديد"""
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            quotation = form.save(commit=False)
            quotation.created_by = request.user
            quotation.save()
            messages.success(request, 'تم إضافة عرض السعر بنجاح')
            return redirect('sales:quotation_detail', pk=quotation.pk)
    else:
        form = QuotationForm()

    context = {
        'form': form,
        'title': 'إضافة عرض سعر جديد',
        'action': 'إضافة'
    }
    return render(request, 'sales/quotation_form.html', context)


@login_required
def quotation_detail(request, pk):
    """تفاصيل عرض السعر"""
    quotation = get_object_or_404(Quotation, pk=pk)
    items = quotation.items.all().select_related('item')

    context = {
        'quotation': quotation,
        'items': items,
        'title': f'عرض سعر رقم: {quotation.quotation_number}'
    }
    return render(request, 'sales/quotation_detail.html', context)


# Price List Views
@login_required
def price_list_list(request):
    """قائمة قوائم الأسعار"""
    search_query = request.GET.get('search', '')
    price_lists = PriceList.objects.all()

    if search_query:
        price_lists = price_lists.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    price_lists = price_lists.order_by('name')
    paginator = Paginator(price_lists, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'قوائم الأسعار'
    }
    return render(request, 'sales/price_list_list.html', context)


@login_required
def price_list_create(request):
    """إضافة قائمة أسعار جديدة"""
    if request.method == 'POST':
        form = PriceListForm(request.POST)
        if form.is_valid():
            price_list = form.save(commit=False)
            price_list.created_by = request.user
            price_list.save()
            messages.success(request, 'تم إضافة قائمة الأسعار بنجاح')
            return redirect('sales:price_list_list')
    else:
        form = PriceListForm()

    context = {
        'form': form,
        'title': 'إضافة قائمة أسعار جديدة',
        'action': 'إضافة'
    }
    return render(request, 'sales/price_list_form.html', context)


# Price Display Views
@login_required
def price_display(request):
    """شاشة عرض أسعار البيع"""
    form = PriceDisplayForm()
    price_info = None

    if request.method == 'POST':
        form = PriceDisplayForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data['item']
            price_list = form.cleaned_data.get('price_list')
            customer = form.cleaned_data.get('customer')
            quantity = form.cleaned_data['quantity']

            # البحث عن السعر
            price_info = get_item_price(item, price_list, customer, quantity)

    context = {
        'form': form,
        'price_info': price_info,
        'title': 'عرض أسعار البيع'
    }
    return render(request, 'sales/price_display.html', context)


@login_required
def quotation_period_report(request):
    """تقرير عروض الأسعار خلال فترة محددة"""
    form = QuotationPeriodReportForm()
    quotations = None
    total_amount = Decimal('0')

    if request.method == 'POST':
        form = QuotationPeriodReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            customer = form.cleaned_data.get('customer')
            status = form.cleaned_data.get('status')
            salesperson = form.cleaned_data.get('salesperson')

            quotations = Quotation.objects.filter(
                date__range=[start_date, end_date]
            ).select_related('customer', 'salesperson')

            if customer:
                quotations = quotations.filter(customer=customer)
            if status:
                quotations = quotations.filter(status=status)
            if salesperson:
                quotations = quotations.filter(salesperson=salesperson)

            quotations = quotations.order_by('-date')
            total_amount = quotations.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            # حساب المتوسط
            count = quotations.count()
            average_amount = total_amount / count if count > 0 else Decimal('0')

    context = {
        'form': form,
        'quotations': quotations,
        'total_amount': total_amount,
        'average_amount': average_amount,
        'title': 'تقرير عروض الأسعار خلال فترة'
    }
    return render(request, 'sales/quotation_period_report.html', context)


@login_required
def discount_policy_list(request):
    """قائمة سياسات الخصم"""
    search_query = request.GET.get('search', '')
    policies = DiscountPolicy.objects.all()

    if search_query:
        policies = policies.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    policies = policies.order_by('name')
    paginator = Paginator(policies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'سياسات الخصم المسموح به'
    }
    return render(request, 'sales/discount_policy_list.html', context)


def get_item_price(item, price_list=None, customer=None, quantity=1):
    """الحصول على سعر الصنف"""
    quantity = Decimal(str(quantity))

    price_info = {
        'item': item,
        'quantity': quantity,
        'base_price': item.selling_price or Decimal('0'),
        'final_price': item.selling_price or Decimal('0'),
        'discount_percentage': Decimal('0'),
        'discount_amount': Decimal('0'),
        'price_source': 'سعر الصنف الأساسي'
    }

    # البحث في قائمة الأسعار
    if price_list:
        try:
            price_item = PriceListItem.objects.get(
                price_list=price_list,
                item=item,
                min_quantity__lte=quantity
            )
            price_info['base_price'] = price_item.unit_price
            price_info['final_price'] = price_item.unit_price
            price_info['price_source'] = f'قائمة الأسعار: {price_list.name}'
        except PriceListItem.DoesNotExist:
            pass

    # تطبيق خصم العميل
    if customer and customer.default_discount_percentage > 0:
        discount_percentage = customer.default_discount_percentage
        discount_amount = price_info['base_price'] * (discount_percentage / Decimal('100'))
        price_info['discount_percentage'] = discount_percentage
        price_info['discount_amount'] = discount_amount
        price_info['final_price'] = price_info['base_price'] - discount_amount

    # حساب الإجمالي
    price_info['total_amount'] = price_info['final_price'] * quantity

    return price_info
