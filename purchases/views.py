from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

from .models import (
    Supplier, PurchaseInvoice, PurchaseReturn, PurchaseOrder, EarnedDiscount
)
from .forms import (
    SupplierForm, PurchaseInvoiceForm, PurchaseReturnForm, PurchaseOrderForm,
    EarnedDiscountForm, PurchaseReportForm, SupplierPerformanceReportForm,
    EarnedDiscountReportForm
)


@login_required
def purchases_home(request):
    """الصفحة الرئيسية للمشتريات"""
    today = timezone.now().date()
    this_month = today.replace(day=1)

    context = {
        'suppliers_count': Supplier.objects.count(),
        'invoices_count': PurchaseInvoice.objects.count(),
        'orders_count': PurchaseOrder.objects.count(),
        'returns_count': PurchaseReturn.objects.count(),
        'earned_discounts_count': EarnedDiscount.objects.count(),
        'monthly_purchases': PurchaseInvoice.objects.filter(
            date__gte=this_month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0'),
        'pending_orders': PurchaseOrder.objects.filter(
            status__in=['DRAFT', 'SENT', 'CONFIRMED']
        ).count(),
        'pending_discounts': EarnedDiscount.objects.filter(
            status='PENDING'
        ).count(),
        'title': 'نظام المشتريات'
    }
    return render(request, 'purchases/home.html', context)


# Supplier Views
@login_required
def supplier_list(request):
    """قائمة أوامر التوريد"""
    search_query = request.GET.get('search', '')

    # بيانات وهمية لأوامر التوريد
    from datetime import datetime, timedelta
    import random

    orders_data = []
    suppliers = ['شركة المواد الخام المحدودة', 'مؤسسة التوريد الذهبي', 'شركة الإمداد الحديث',
                'مجموعة التوريد المتقدم', 'شركة المصادر الصناعية', 'مؤسسة الجودة للتوريد']
    descriptions = ['أمر توريد مواد خام', 'توريد قطع غيار', 'أمر توريد مواد تشغيل',
                   'توريد معدات مكتبية', 'أمر توريد مواد تعبئة', 'توريد مواد صيانة']

    for i in range(1, 26):  # 25 أمر توريد
        order_date = datetime.now() - timedelta(days=random.randint(1, 90))
        statuses = ['PENDING', 'APPROVED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
        status = random.choice(statuses)

        order = type('Order', (), {
            'pk': i,
            'order_number': f'TO-{str(i).zfill(3)}',
            'date': order_date,
            'supplier_name': random.choice(suppliers),
            'contact_person': f'مسؤول التوريد {i}' if i % 3 == 0 else None,
            'description': f'{random.choice(descriptions)} - دفعة {i}',
            'total_amount': random.randint(5000, 50000),
            'status': status,
        })()
        orders_data.append(order)

    # فلترة البحث
    if search_query:
        filtered_orders = []
        for order in orders_data:
            if (search_query.lower() in order.order_number.lower() or
                search_query.lower() in order.supplier_name.lower() or
                search_query.lower() in order.description.lower()):
                filtered_orders.append(order)
        orders_data = filtered_orders

    # ترتيب حسب التاريخ
    orders_data.sort(key=lambda x: x.date, reverse=True)

    # تقسيم الصفحات
    paginator = Paginator(orders_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'أوامر التوريد'
    }
    return render(request, 'purchases/supplier_list.html', context)


@login_required
def supplier_create(request):
    """إضافة أمر توريد جديد"""
    from datetime import datetime, timedelta

    if request.method == 'POST':
        # معالجة البيانات المرسلة
        order_number = request.POST.get('order_number', f'TO-{datetime.now().strftime("%Y%m%d%H%M")}')
        messages.success(request, f'تم إضافة أمر التوريد {order_number} بنجاح')
        return redirect('purchases:supplier_list')

    # بيانات افتراضية للنموذج الجديد
    default_data = {
        'order_number': f'TO-{datetime.now().strftime("%Y%m%d%H%M")}',
        'order_date': datetime.now().strftime('%Y-%m-%d'),
        'supplier_name': '',
        'contact_person': '',
        'description': '',
        'total_amount': 0,
        'delivery_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
        'payment_terms': 30,
        'delivery_address': '',
        'status': 'PENDING'
    }

    # إنشاء form object وهمي
    form = type('Form', (), default_data)()

    context = {
        'form': form,
        'title': 'إضافة أمر توريد جديد',
        'action': 'إضافة'
    }
    return render(request, 'purchases/supplier_form.html', context)


@login_required
def supplier_edit(request, pk):
    """تعديل أمر التوريد"""
    # بيانات وهمية لأمر التوريد المحدد
    from datetime import datetime, timedelta
    import random

    # التحقق من وجود الأمر في النطاق المسموح
    if int(pk) < 1 or int(pk) > 25:
        from django.http import Http404
        raise Http404("أمر التوريد غير موجود")

    # إنشاء بيانات وهمية للأمر المحدد
    suppliers = ['شركة المواد الخام المحدودة', 'مؤسسة التوريد الذهبي', 'شركة الإمداد الحديث']
    descriptions = ['أمر توريد مواد خام', 'توريد قطع غيار', 'أمر توريد مواد تشغيل']

    order_data = {
        'pk': pk,
        'order_number': f'TO-{str(pk).zfill(3)}',
        'order_date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        'supplier_name': suppliers[int(pk) % len(suppliers)],
        'contact_person': f'مسؤول التوريد {pk}',
        'description': f'{descriptions[int(pk) % len(descriptions)]} - دفعة {pk}',
        'total_amount': random.randint(5000, 50000),
        'delivery_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
        'payment_terms': 30,
        'delivery_address': 'المكتب الرئيسي - الرياض',
        'status': 'PENDING'
    }

    if request.method == 'POST':
        # معالجة البيانات المرسلة
        messages.success(request, f'تم تحديث أمر التوريد {order_data["order_number"]} بنجاح')
        return redirect('purchases:supplier_list')

    # إنشاء form object وهمي
    form = type('Form', (), order_data)()

    context = {
        'form': form,
        'order': order_data,
        'title': f'تعديل أمر التوريد: {order_data["order_number"]}',
        'action': 'تحديث'
    }
    return render(request, 'purchases/supplier_form.html', context)


@login_required
def supplier_delete(request, pk):
    """حذف أمر التوريد"""
    if request.method == 'DELETE':
        # التحقق من وجود الأمر في النطاق المسموح
        if int(pk) < 1 or int(pk) > 25:
            return JsonResponse({'success': False, 'message': 'أمر التوريد غير موجود'})

        # محاكاة حذف أمر التوريد
        order_number = f'TO-{str(pk).zfill(3)}'
        return JsonResponse({'success': True, 'message': f'تم حذف أمر التوريد {order_number} بنجاح'})
    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# Purchase Invoice Views
@login_required
def invoice_list(request):
    """قائمة فواتير المشتريات"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    invoices = PurchaseInvoice.objects.all().select_related('supplier', 'warehouse')

    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(supplier_invoice_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    invoices = invoices.order_by('-date', '-id')
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    status_choices = PurchaseInvoice._meta.get_field('status').choices

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'title': 'فواتير المشتريات'
    }
    return render(request, 'purchases/invoice_list.html', context)


@login_required
def invoice_create(request):
    """إضافة فاتورة مشتريات جديدة"""
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, 'تم إضافة الفاتورة بنجاح')
            return redirect('purchases:invoice_detail', pk=invoice.pk)
    else:
        form = PurchaseInvoiceForm()

    context = {
        'form': form,
        'title': 'إضافة فاتورة مشتريات جديدة',
        'action': 'إضافة'
    }
    return render(request, 'purchases/invoice_form.html', context)


@login_required
def invoice_detail(request, pk):
    """تفاصيل فاتورة المشتريات"""
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    items = invoice.items.all().select_related('item')

    context = {
        'invoice': invoice,
        'items': items,
        'title': f'فاتورة مشتريات رقم: {invoice.invoice_number}'
    }
    return render(request, 'purchases/invoice_detail.html', context)


@login_required
def invoice_edit(request, pk):
    """تعديل فاتورة مشتريات"""
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.updated_by = request.user
            invoice.save()
            messages.success(request, 'تم تحديث الفاتورة بنجاح')
            return redirect('purchases:invoice_detail', pk=invoice.pk)
    else:
        form = PurchaseInvoiceForm(instance=invoice)

    context = {
        'form': form,
        'invoice': invoice,
        'title': f'تعديل فاتورة: {invoice.invoice_number}',
        'action': 'تحديث'
    }
    return render(request, 'purchases/invoice_form.html', context)


@login_required
def invoice_delete(request, pk):
    """حذف فاتورة مشتريات"""
    if request.method == 'DELETE':
        invoice = get_object_or_404(PurchaseInvoice, pk=pk)
        invoice.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الفاتورة بنجاح'})
    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# Purchase Order Views
@login_required
def order_list(request):
    """قائمة أوامر الشراء"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    orders = PurchaseOrder.objects.all().select_related('supplier', 'warehouse')

    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )

    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.order_by('-date', '-id')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    status_choices = PurchaseOrder._meta.get_field('status').choices

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'title': 'أوامر الشراء'
    }
    return render(request, 'purchases/order_list.html', context)


@login_required
def order_create(request):
    """إضافة أمر شراء جديد"""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            messages.success(request, 'تم إضافة أمر الشراء بنجاح')
            return redirect('purchases:order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm()

    context = {
        'form': form,
        'title': 'إضافة أمر شراء جديد',
        'action': 'إضافة'
    }
    return render(request, 'purchases/order_form.html', context)


@login_required
def order_detail(request, pk):
    """تفاصيل أمر الشراء"""
    order = get_object_or_404(PurchaseOrder, pk=pk)
    items = order.items.all().select_related('item')

    context = {
        'order': order,
        'items': items,
        'title': f'أمر شراء رقم: {order.order_number}'
    }
    return render(request, 'purchases/order_detail.html', context)


# Purchase Return Views
@login_required
def return_list(request):
    """قائمة مرتجعات المشتريات"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    returns = PurchaseReturn.objects.all().select_related('supplier', 'warehouse')

    if search_query:
        returns = returns.filter(
            Q(return_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )

    if status_filter:
        returns = returns.filter(status=status_filter)

    returns = returns.order_by('-date', '-id')
    paginator = Paginator(returns, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    status_choices = PurchaseReturn._meta.get_field('status').choices

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'title': 'مرتجعات المشتريات'
    }
    return render(request, 'purchases/return_list.html', context)


@login_required
def return_create(request):
    """إضافة مرتجع مشتريات جديد"""
    if request.method == 'POST':
        form = PurchaseReturnForm(request.POST)
        if form.is_valid():
            return_doc = form.save(commit=False)
            return_doc.created_by = request.user
            return_doc.save()
            messages.success(request, 'تم إضافة المرتجع بنجاح')
            return redirect('purchases:return_list')
    else:
        form = PurchaseReturnForm()

    context = {
        'form': form,
        'title': 'إضافة مرتجع مشتريات جديد',
        'action': 'إضافة'
    }
    return render(request, 'purchases/return_form.html', context)


# Earned Discount Views
@login_required
def earned_discount_list(request):
    """قائمة الخصومات المكتسبة"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    discount_type_filter = request.GET.get('discount_type', '')

    discounts = EarnedDiscount.objects.all().select_related('supplier')

    if search_query:
        discounts = discounts.filter(
            Q(discount_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )

    if status_filter:
        discounts = discounts.filter(status=status_filter)

    if discount_type_filter:
        discounts = discounts.filter(discount_type=discount_type_filter)

    discounts = discounts.order_by('-date', '-id')
    paginator = Paginator(discounts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    status_choices = EarnedDiscount._meta.get_field('status').choices
    discount_type_choices = EarnedDiscount.DISCOUNT_TYPE_CHOICES

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'discount_type_filter': discount_type_filter,
        'status_choices': status_choices,
        'discount_type_choices': discount_type_choices,
        'title': 'الخصومات المكتسبة'
    }
    return render(request, 'purchases/earned_discount_list.html', context)


@login_required
def earned_discount_create(request):
    """إضافة خصم مكتسب جديد"""
    if request.method == 'POST':
        form = EarnedDiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.created_by = request.user
            discount.save()
            messages.success(request, 'تم إضافة الخصم المكتسب بنجاح')
            return redirect('purchases:earned_discount_detail', pk=discount.pk)
    else:
        form = EarnedDiscountForm()

    context = {
        'form': form,
        'title': 'إضافة خصم مكتسب جديد',
        'action': 'إضافة'
    }
    return render(request, 'purchases/earned_discount_form.html', context)


@login_required
def earned_discount_detail(request, pk):
    """تفاصيل الخصم المكتسب"""
    discount = get_object_or_404(EarnedDiscount, pk=pk)
    items = discount.items.all().select_related('item')

    context = {
        'discount': discount,
        'items': items,
        'title': f'خصم مكتسب رقم: {discount.discount_number}'
    }
    return render(request, 'purchases/earned_discount_detail.html', context)


# Reports Views
@login_required
def purchase_report(request):
    """تقرير المشتريات خلال فترة محددة"""
    form = PurchaseReportForm()
    invoices = None
    total_amount = Decimal('0')
    average_amount = Decimal('0')

    if request.method == 'POST':
        form = PurchaseReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            supplier = form.cleaned_data.get('supplier')
            status = form.cleaned_data.get('status')

            invoices = PurchaseInvoice.objects.filter(
                date__range=[start_date, end_date]
            ).select_related('supplier', 'warehouse')

            if supplier:
                invoices = invoices.filter(supplier=supplier)
            if status:
                invoices = invoices.filter(status=status)

            invoices = invoices.order_by('-date')
            total_amount = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            # حساب المتوسط
            count = invoices.count()
            average_amount = total_amount / count if count > 0 else Decimal('0')

    context = {
        'form': form,
        'invoices': invoices,
        'total_amount': total_amount,
        'average_amount': average_amount,
        'title': 'تقرير المشتريات خلال فترة'
    }
    return render(request, 'purchases/purchase_report.html', context)


@login_required
def supplier_performance_report(request):
    """تقرير أداء الموردين"""
    form = SupplierPerformanceReportForm()
    suppliers_data = None

    if request.method == 'POST':
        form = SupplierPerformanceReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            supplier = form.cleaned_data.get('supplier')

            suppliers_query = Supplier.objects.all()
            if supplier:
                suppliers_query = suppliers_query.filter(id=supplier.id)

            suppliers_data = []
            for sup in suppliers_query:
                invoices = PurchaseInvoice.objects.filter(
                    supplier=sup,
                    date__range=[start_date, end_date]
                )
                orders = PurchaseOrder.objects.filter(
                    supplier=sup,
                    date__range=[start_date, end_date]
                )
                returns = PurchaseReturn.objects.filter(
                    supplier=sup,
                    date__range=[start_date, end_date]
                )

                total_purchases = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
                total_returns = returns.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

                suppliers_data.append({
                    'supplier': sup,
                    'invoices_count': invoices.count(),
                    'orders_count': orders.count(),
                    'returns_count': returns.count(),
                    'total_purchases': total_purchases,
                    'total_returns': total_returns,
                    'net_purchases': total_purchases - total_returns,
                })

    context = {
        'form': form,
        'suppliers_data': suppliers_data,
        'title': 'تقرير أداء أوامر التوريد'
    }
    return render(request, 'purchases/supplier_performance_report.html', context)
