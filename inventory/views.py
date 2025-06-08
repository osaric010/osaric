from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F, Avg
from django.utils import timezone
from decimal import Decimal
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from django import forms
from datetime import datetime, date
from .models import (StockIncrease, StockIncreaseItem, StockDecrease, StockDecreaseItem,
                    GoodsReceivedOnLoan, GoodsReceivedOnLoanItem,
                    GoodsIssuedOnLoan, GoodsIssuedOnLoanItem,
                    WarehouseTransfer, WarehouseTransferItem,
                    ItemTransformation, ItemTransformationInput, ItemTransformationOutput,
                    ManufacturingOrder, ManufacturingOrderMaterial,
                    PhysicalInventory, PhysicalInventoryItem, Stock)
from definitions.models import Warehouse, Item
from .forms import (StockIncreaseForm, StockIncreaseItemFormSet, StockIncreaseFilterForm,
                    StockDecreaseForm, StockDecreaseItemFormSet, StockDecreaseFilterForm,
                    GoodsReceivedOnLoanForm, GoodsReceivedOnLoanItemFormSet, GoodsReceivedOnLoanFilterForm,
                    GoodsIssuedOnLoanForm, GoodsIssuedOnLoanItemFormSet, GoodsIssuedOnLoanFilterForm,
                    WarehouseTransferForm, WarehouseTransferItemFormSet, WarehouseTransferFilterForm,
                    ItemTransformationForm, ItemTransformationInputFormSet, ItemTransformationOutputFormSet,
                    ItemTransformationFilterForm, ManufacturingOrderForm, ManufacturingOrderMaterialFormSet,
                    ManufacturingOrderFilterForm, PhysicalInventoryForm, PhysicalInventoryItemFormSet,
                    PhysicalInventoryFilterForm, CountItemForm)


@login_required
def stock_increase_list(request):
    """قائمة أذون إضافة الزيادات"""
    form = StockIncreaseFilterForm(request.GET)
    increases = StockIncrease.objects.all().select_related('warehouse', 'created_by')

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        warehouse = form.cleaned_data.get('warehouse')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            increases = increases.filter(
                Q(increase_number__icontains=search) |
                Q(warehouse__name__icontains=search) |
                Q(reason__icontains=search)
            )

        if warehouse:
            increases = increases.filter(warehouse=warehouse)

        if status:
            increases = increases.filter(status=status)

        if date_from:
            increases = increases.filter(date__gte=date_from)

        if date_to:
            increases = increases.filter(date__lte=date_to)

    increases = increases.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(increases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_increases = increases.count()
    pending_increases = increases.filter(status='DRAFT').count()
    approved_increases = increases.filter(status='APPROVED').count()
    applied_increases = increases.filter(status='APPLIED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_increases': total_increases,
        'pending_increases': pending_increases,
        'approved_increases': approved_increases,
        'applied_increases': applied_increases,
        'title': 'أذون إضافة الزيادات'
    }
    return render(request, 'inventory/stock_increase_list.html', context)


@login_required
def stock_increase_create(request):
    """إضافة إذن زيادة جديد"""
    if request.method == 'POST':
        form = StockIncreaseForm(request.POST)
        formset = StockIncreaseItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                increase = form.save(commit=False)
                increase.created_by = request.user
                increase.save()

                formset.instance = increase
                items = formset.save()

                # حساب الإجمالي
                total_amount = sum(item.total_cost for item in items)
                increase.total_amount = total_amount
                increase.save()

                messages.success(request, f'تم إنشاء إذن الزيادة {increase.increase_number} بنجاح')
                return redirect('inventory:stock_increase_detail', pk=increase.pk)
    else:
        form = StockIncreaseForm()
        formset = StockIncreaseItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'إضافة إذن زيادة جديد',
        'action': 'إضافة'
    }
    return render(request, 'inventory/stock_increase_form.html', context)


@login_required
def stock_increase_detail(request, pk):
    """تفاصيل إذن الزيادة"""
    increase = get_object_or_404(StockIncrease, pk=pk)
    items = increase.items.all().select_related('item')

    context = {
        'increase': increase,
        'items': items,
        'title': f'إذن زيادة رقم: {increase.increase_number}'
    }
    return render(request, 'inventory/stock_increase_detail.html', context)


@login_required
def stock_increase_edit(request, pk):
    """تعديل إذن الزيادة"""
    increase = get_object_or_404(StockIncrease, pk=pk)

    # التحقق من إمكانية التعديل
    if increase.status not in ['DRAFT']:
        messages.error(request, 'لا يمكن تعديل إذن الزيادة بعد اعتماده')
        return redirect('inventory:stock_increase_detail', pk=pk)

    if request.method == 'POST':
        form = StockIncreaseForm(request.POST, instance=increase)
        formset = StockIncreaseItemFormSet(request.POST, instance=increase)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                increase = form.save(commit=False)
                increase.updated_by = request.user
                increase.save()

                items = formset.save()

                # حساب الإجمالي
                total_amount = sum(item.total_cost for item in items)
                increase.total_amount = total_amount
                increase.save()

                messages.success(request, f'تم تحديث إذن الزيادة {increase.increase_number} بنجاح')
                return redirect('inventory:stock_increase_detail', pk=increase.pk)
    else:
        form = StockIncreaseForm(instance=increase)
        formset = StockIncreaseItemFormSet(instance=increase)

    context = {
        'form': form,
        'formset': formset,
        'increase': increase,
        'title': f'تعديل إذن الزيادة: {increase.increase_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/stock_increase_form.html', context)


@login_required
def stock_increase_approve(request, pk):
    """اعتماد إذن الزيادة"""
    if request.method == 'POST':
        increase = get_object_or_404(StockIncrease, pk=pk)

        if increase.status != 'DRAFT':
            return JsonResponse({'success': False, 'message': 'الإذن معتمد مسبقاً أو ملغي'})

        increase.status = 'APPROVED'
        increase.approved_by = request.user
        increase.approved_date = datetime.now()
        increase.save()

        return JsonResponse({
            'success': True,
            'message': f'تم اعتماد إذن الزيادة {increase.increase_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def stock_increase_apply(request, pk):
    """تطبيق إذن الزيادة على المخزون"""
    if request.method == 'POST':
        increase = get_object_or_404(StockIncrease, pk=pk)

        if increase.status != 'APPROVED':
            return JsonResponse({'success': False, 'message': 'يجب اعتماد الإذن أولاً'})

        with transaction.atomic():
            # تطبيق الزيادات على المخزون
            from .models import Stock, StockMovement, StockMovementItem

            # إنشاء حركة مخزون
            movement = StockMovement.objects.create(
                movement_type='IN',
                reference_number=increase.increase_number,
                date=increase.date,
                warehouse=increase.warehouse,
                notes=f'إذن زيادة: {increase.reason}',
                total_amount=increase.total_amount,
                created_by=request.user
            )

            # تطبيق كل صنف
            for item in increase.items.all():
                # إنشاء حركة للصنف
                StockMovementItem.objects.create(
                    movement=movement,
                    item=item.item,
                    quantity=item.quantity,
                    unit_cost=item.unit_cost,
                    total_cost=item.total_cost,
                    expiry_date=item.expiry_date,
                    batch_number=item.batch_number
                )

                # تحديث رصيد المخزون
                stock, created = Stock.objects.get_or_create(
                    warehouse=increase.warehouse,
                    item=item.item,
                    defaults={
                        'quantity': 0,
                        'average_cost': item.unit_cost
                    }
                )

                # حساب المتوسط المرجح للتكلفة
                total_value = (stock.quantity * stock.average_cost) + item.total_cost
                stock.quantity += item.quantity
                stock.average_cost = total_value / stock.quantity if stock.quantity > 0 else 0
                stock.last_movement_date = datetime.now()
                stock.save()

            # تحديث حالة الإذن
            increase.status = 'APPLIED'
            increase.save()

        return JsonResponse({
            'success': True,
            'message': f'تم تطبيق إذن الزيادة {increase.increase_number} على المخزون بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def stock_increase_delete(request, pk):
    """حذف إذن الزيادة"""
    if request.method == 'DELETE':
        increase = get_object_or_404(StockIncrease, pk=pk)

        if increase.status not in ['DRAFT']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف إذن معتمد أو مطبق'})

        increase_number = increase.increase_number
        increase.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف إذن الزيادة {increase_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# ==================== Stock Decrease Views ====================

@login_required
def stock_decrease_list(request):
    """قائمة أذون صرف النواقص"""
    form = StockDecreaseFilterForm(request.GET)
    decreases = StockDecrease.objects.all().select_related('warehouse', 'created_by')

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        warehouse = form.cleaned_data.get('warehouse')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            decreases = decreases.filter(
                Q(decrease_number__icontains=search) |
                Q(warehouse__name__icontains=search) |
                Q(reason__icontains=search)
            )

        if warehouse:
            decreases = decreases.filter(warehouse=warehouse)

        if status:
            decreases = decreases.filter(status=status)

        if date_from:
            decreases = decreases.filter(date__gte=date_from)

        if date_to:
            decreases = decreases.filter(date__lte=date_to)

    decreases = decreases.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(decreases, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_decreases = decreases.count()
    pending_decreases = decreases.filter(status='DRAFT').count()
    approved_decreases = decreases.filter(status='APPROVED').count()
    applied_decreases = decreases.filter(status='APPLIED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_decreases': total_decreases,
        'pending_decreases': pending_decreases,
        'approved_decreases': approved_decreases,
        'applied_decreases': applied_decreases,
        'title': 'أذون صرف النواقص'
    }
    return render(request, 'inventory/stock_decrease_list.html', context)


@login_required
def stock_decrease_create(request):
    """إضافة إذن نقص جديد"""
    if request.method == 'POST':
        form = StockDecreaseForm(request.POST)
        formset = StockDecreaseItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                decrease = form.save(commit=False)
                decrease.created_by = request.user
                decrease.save()

                formset.instance = decrease
                items = formset.save()

                # حساب الإجمالي
                total_amount = sum(item.total_cost for item in items)
                decrease.total_amount = total_amount
                decrease.save()

                messages.success(request, f'تم إنشاء إذن النقص {decrease.decrease_number} بنجاح')
                return redirect('inventory:stock_decrease_detail', pk=decrease.pk)
    else:
        form = StockDecreaseForm()
        formset = StockDecreaseItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'إضافة إذن نقص جديد',
        'action': 'إضافة'
    }
    return render(request, 'inventory/stock_decrease_form.html', context)


@login_required
def stock_decrease_detail(request, pk):
    """تفاصيل إذن النقص"""
    decrease = get_object_or_404(StockDecrease, pk=pk)
    items = decrease.items.all().select_related('item')

    context = {
        'decrease': decrease,
        'items': items,
        'title': f'إذن نقص رقم: {decrease.decrease_number}'
    }
    return render(request, 'inventory/stock_decrease_detail.html', context)


@login_required
def stock_decrease_edit(request, pk):
    """تعديل إذن النقص"""
    decrease = get_object_or_404(StockDecrease, pk=pk)

    # التحقق من إمكانية التعديل
    if decrease.status not in ['DRAFT']:
        messages.error(request, 'لا يمكن تعديل إذن النقص بعد اعتماده')
        return redirect('inventory:stock_decrease_detail', pk=pk)

    if request.method == 'POST':
        form = StockDecreaseForm(request.POST, instance=decrease)
        formset = StockDecreaseItemFormSet(request.POST, instance=decrease)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                decrease = form.save(commit=False)
                decrease.updated_by = request.user
                decrease.save()

                items = formset.save()

                # حساب الإجمالي
                total_amount = sum(item.total_cost for item in items)
                decrease.total_amount = total_amount
                decrease.save()

                messages.success(request, f'تم تحديث إذن النقص {decrease.decrease_number} بنجاح')
                return redirect('inventory:stock_decrease_detail', pk=decrease.pk)
    else:
        form = StockDecreaseForm(instance=decrease)
        formset = StockDecreaseItemFormSet(instance=decrease)

    context = {
        'form': form,
        'formset': formset,
        'decrease': decrease,
        'title': f'تعديل إذن النقص: {decrease.decrease_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/stock_decrease_form.html', context)


@login_required
def stock_decrease_approve(request, pk):
    """اعتماد إذن النقص"""
    if request.method == 'POST':
        decrease = get_object_or_404(StockDecrease, pk=pk)

        if decrease.status != 'DRAFT':
            return JsonResponse({'success': False, 'message': 'الإذن معتمد مسبقاً أو ملغي'})

        decrease.status = 'APPROVED'
        decrease.approved_by = request.user
        decrease.approved_date = datetime.now()
        decrease.save()

        return JsonResponse({
            'success': True,
            'message': f'تم اعتماد إذن النقص {decrease.decrease_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def stock_decrease_apply(request, pk):
    """تطبيق إذن النقص على المخزون"""
    if request.method == 'POST':
        decrease = get_object_or_404(StockDecrease, pk=pk)

        if decrease.status != 'APPROVED':
            return JsonResponse({'success': False, 'message': 'يجب اعتماد الإذن أولاً'})

        with transaction.atomic():
            # التحقق من توفر الكميات في المخزون
            from .models import Stock

            for item in decrease.items.all():
                try:
                    stock = Stock.objects.get(warehouse=decrease.warehouse, item=item.item)
                    if stock.quantity < item.quantity:
                        return JsonResponse({
                            'success': False,
                            'message': f'الكمية المتاحة من {item.item.name} غير كافية. المتاح: {stock.quantity}'
                        })
                except Stock.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'الصنف {item.item.name} غير متوفر في المخزون'
                    })

            # تطبيق النواقص على المخزون
            from .models import StockMovement, StockMovementItem

            # إنشاء حركة مخزون
            movement = StockMovement.objects.create(
                movement_type='OUT',
                reference_number=decrease.decrease_number,
                date=decrease.date,
                warehouse=decrease.warehouse,
                notes=f'إذن نقص: {decrease.reason}',
                total_amount=decrease.total_amount,
                created_by=request.user
            )

            # تطبيق كل صنف
            for item in decrease.items.all():
                # إنشاء حركة للصنف
                StockMovementItem.objects.create(
                    movement=movement,
                    item=item.item,
                    quantity=-item.quantity,  # كمية سالبة للنقص
                    unit_cost=item.unit_cost,
                    total_cost=-item.total_cost,  # مبلغ سالب للنقص
                    batch_number=item.batch_number
                )

                # تحديث رصيد المخزون
                stock = Stock.objects.get(warehouse=decrease.warehouse, item=item.item)
                stock.quantity -= item.quantity
                stock.last_movement_date = datetime.now()
                stock.save()

            # تحديث حالة الإذن
            decrease.status = 'APPLIED'
            decrease.save()

        return JsonResponse({
            'success': True,
            'message': f'تم تطبيق إذن النقص {decrease.decrease_number} على المخزون بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def stock_decrease_delete(request, pk):
    """حذف إذن النقص"""
    if request.method == 'DELETE':
        decrease = get_object_or_404(StockDecrease, pk=pk)

        if decrease.status not in ['DRAFT']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف إذن معتمد أو مطبق'})

        decrease_number = decrease.decrease_number
        decrease.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف إذن النقص {decrease_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# ==================== Goods Received On Loan Views ====================

@login_required
def goods_received_on_loan_list(request):
    """قائمة البضائع المضافة سلفة من الغير"""
    form = GoodsReceivedOnLoanFilterForm(request.GET)
    loans = GoodsReceivedOnLoan.objects.all().select_related('warehouse', 'created_by')

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        warehouse = form.cleaned_data.get('warehouse')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        overdue_only = form.cleaned_data.get('overdue_only')

        if search:
            loans = loans.filter(
                Q(loan_number__icontains=search) |
                Q(lender_name__icontains=search) |
                Q(loan_reason__icontains=search)
            )

        if warehouse:
            loans = loans.filter(warehouse=warehouse)

        if status:
            loans = loans.filter(status=status)

        if date_from:
            loans = loans.filter(date__gte=date_from)

        if date_to:
            loans = loans.filter(date__lte=date_to)

        if overdue_only:
            from datetime import date
            loans = loans.filter(
                expected_return_date__lt=date.today(),
                status__in=['RECEIVED', 'PARTIAL_RETURNED']
            )

    loans = loans.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(loans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_loans = loans.count()
    active_loans = loans.filter(status__in=['RECEIVED', 'PARTIAL_RETURNED']).count()
    overdue_loans = loans.filter(
        expected_return_date__lt=datetime.now().date(),
        status__in=['RECEIVED', 'PARTIAL_RETURNED']
    ).count()
    returned_loans = loans.filter(status='RETURNED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'returned_loans': returned_loans,
        'title': 'بضائع مضافة سلفة من الغير'
    }
    return render(request, 'inventory/goods_received_on_loan_list.html', context)


@login_required
def goods_received_on_loan_create(request):
    """إضافة بضاعة سلفة جديدة"""
    if request.method == 'POST':
        form = GoodsReceivedOnLoanForm(request.POST)
        formset = GoodsReceivedOnLoanItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                loan = form.save(commit=False)
                loan.created_by = request.user
                loan.save()

                formset.instance = loan
                items = formset.save()

                # حساب الإجمالي
                total_value = sum(item.total_estimated_value for item in items)
                loan.total_estimated_value = total_value
                loan.save()

                messages.success(request, f'تم إنشاء سلفة البضاعة {loan.loan_number} بنجاح')
                return redirect('inventory:goods_received_on_loan_detail', pk=loan.pk)
    else:
        form = GoodsReceivedOnLoanForm()
        formset = GoodsReceivedOnLoanItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'إضافة بضاعة سلفة جديدة',
        'action': 'إضافة'
    }
    return render(request, 'inventory/goods_received_on_loan_form.html', context)


@login_required
def goods_received_on_loan_detail(request, pk):
    """تفاصيل بضاعة السلفة"""
    loan = get_object_or_404(GoodsReceivedOnLoan, pk=pk)
    items = loan.items.all().select_related('item')

    context = {
        'loan': loan,
        'items': items,
        'title': f'سلفة بضاعة رقم: {loan.loan_number}'
    }
    return render(request, 'inventory/goods_received_on_loan_detail.html', context)


@login_required
def goods_received_on_loan_edit(request, pk):
    """تعديل بضاعة السلفة"""
    loan = get_object_or_404(GoodsReceivedOnLoan, pk=pk)

    # التحقق من إمكانية التعديل
    if loan.status not in ['RECEIVED']:
        messages.error(request, 'لا يمكن تعديل السلفة بعد إرجاعها أو إلغائها')
        return redirect('inventory:goods_received_on_loan_detail', pk=pk)

    if request.method == 'POST':
        form = GoodsReceivedOnLoanForm(request.POST, instance=loan)
        formset = GoodsReceivedOnLoanItemFormSet(request.POST, instance=loan)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                loan = form.save(commit=False)
                loan.updated_by = request.user
                loan.save()

                items = formset.save()

                # حساب الإجمالي
                total_value = sum(item.total_estimated_value for item in items)
                loan.total_estimated_value = total_value
                loan.save()

                messages.success(request, f'تم تحديث سلفة البضاعة {loan.loan_number} بنجاح')
                return redirect('inventory:goods_received_on_loan_detail', pk=loan.pk)
    else:
        form = GoodsReceivedOnLoanForm(instance=loan)
        formset = GoodsReceivedOnLoanItemFormSet(instance=loan)

    context = {
        'form': form,
        'formset': formset,
        'loan': loan,
        'title': f'تعديل سلفة البضاعة: {loan.loan_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/goods_received_on_loan_form.html', context)


@login_required
def goods_received_on_loan_return(request, pk):
    """إرجاع بضاعة السلفة"""
    if request.method == 'POST':
        loan = get_object_or_404(GoodsReceivedOnLoan, pk=pk)

        if loan.status not in ['RECEIVED', 'PARTIAL_RETURNED']:
            return JsonResponse({'success': False, 'message': 'السلفة مرتجعة مسبقاً أو ملغاة'})

        # تحديث حالة السلفة
        loan.status = 'RETURNED'
        loan.save()

        # تحديث كميات الإرجاع لجميع الأصناف
        for item in loan.items.all():
            item.quantity_returned = item.quantity_received
            item.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إرجاع سلفة البضاعة {loan.loan_number} بالكامل'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def goods_received_on_loan_partial_return(request, pk):
    """إرجاع جزئي لبضاعة السلفة"""
    if request.method == 'POST':
        loan = get_object_or_404(GoodsReceivedOnLoan, pk=pk)

        if loan.status not in ['RECEIVED', 'PARTIAL_RETURNED']:
            return JsonResponse({'success': False, 'message': 'السلفة مرتجعة مسبقاً أو ملغاة'})

        # هنا يمكن إضافة نموذج للإرجاع الجزئي
        # للبساطة، سنقوم بتحديث الحالة فقط
        loan.status = 'PARTIAL_RETURNED'
        loan.save()

        return JsonResponse({
            'success': True,
            'message': f'تم تسجيل إرجاع جزئي لسلفة البضاعة {loan.loan_number}'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def goods_received_on_loan_cancel(request, pk):
    """إلغاء سلفة البضاعة"""
    if request.method == 'POST':
        loan = get_object_or_404(GoodsReceivedOnLoan, pk=pk)

        if loan.status in ['RETURNED', 'CANCELLED']:
            return JsonResponse({'success': False, 'message': 'السلفة مرتجعة أو ملغاة مسبقاً'})

        loan.status = 'CANCELLED'
        loan.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إلغاء سلفة البضاعة {loan.loan_number}'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def goods_received_on_loan_delete(request, pk):
    """حذف سلفة البضاعة"""
    if request.method == 'DELETE':
        loan = get_object_or_404(GoodsReceivedOnLoan, pk=pk)

        if loan.status not in ['RECEIVED']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف سلفة مرتجعة أو ملغاة'})

        loan_number = loan.loan_number
        loan.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف سلفة البضاعة {loan_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# ==================== Goods Issued On Loan Views ====================

@login_required
def goods_issued_on_loan_list(request):
    """قائمة البضائع المنصرفة سلفة لدى الغير"""
    form = GoodsIssuedOnLoanFilterForm(request.GET)
    loans = GoodsIssuedOnLoan.objects.all().select_related('warehouse', 'created_by')

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        warehouse = form.cleaned_data.get('warehouse')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        overdue_only = form.cleaned_data.get('overdue_only')

        if search:
            loans = loans.filter(
                Q(loan_number__icontains=search) |
                Q(borrower_name__icontains=search) |
                Q(loan_reason__icontains=search)
            )

        if warehouse:
            loans = loans.filter(warehouse=warehouse)

        if status:
            loans = loans.filter(status=status)

        if date_from:
            loans = loans.filter(date__gte=date_from)

        if date_to:
            loans = loans.filter(date__lte=date_to)

        if overdue_only:
            from datetime import date
            loans = loans.filter(
                expected_return_date__lt=date.today(),
                status__in=['ISSUED', 'PARTIAL_RETURNED']
            )

    loans = loans.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(loans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_loans = loans.count()
    active_loans = loans.filter(status__in=['ISSUED', 'PARTIAL_RETURNED']).count()
    overdue_loans = loans.filter(
        expected_return_date__lt=datetime.now().date(),
        status__in=['ISSUED', 'PARTIAL_RETURNED']
    ).count()
    returned_loans = loans.filter(status='RETURNED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'returned_loans': returned_loans,
        'title': 'بضائع منصرفة سلفة لدى الغير'
    }
    return render(request, 'inventory/goods_issued_on_loan_list.html', context)


@login_required
def goods_issued_on_loan_create(request):
    """إضافة بضاعة سلفة منصرفة جديدة"""
    if request.method == 'POST':
        form = GoodsIssuedOnLoanForm(request.POST)
        formset = GoodsIssuedOnLoanItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # التحقق من توفر الكميات في المخزون
                warehouse = form.cleaned_data['warehouse']
                from .models import Stock

                for item_form in formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                        item = item_form.cleaned_data['item']
                        quantity = item_form.cleaned_data['quantity_issued']

                        try:
                            stock = Stock.objects.get(warehouse=warehouse, item=item)
                            if stock.quantity < quantity:
                                messages.error(request, f'الكمية المتاحة من {item.name} غير كافية. المتاح: {stock.quantity}')
                                return render(request, 'inventory/goods_issued_on_loan_form.html', {
                                    'form': form, 'formset': formset, 'title': 'إضافة بضاعة سلفة منصرفة جديدة', 'action': 'إضافة'
                                })
                        except Stock.DoesNotExist:
                            messages.error(request, f'الصنف {item.name} غير متوفر في المخزون')
                            return render(request, 'inventory/goods_issued_on_loan_form.html', {
                                'form': form, 'formset': formset, 'title': 'إضافة بضاعة سلفة منصرفة جديدة', 'action': 'إضافة'
                            })

                loan = form.save(commit=False)
                loan.created_by = request.user
                loan.save()

                formset.instance = loan
                items = formset.save()

                # حساب الإجمالي
                total_value = sum(item.total_estimated_value for item in items)
                loan.total_estimated_value = total_value
                loan.save()

                # خصم الكميات من المخزون
                from .models import StockMovement, StockMovementItem

                # إنشاء حركة مخزون
                movement = StockMovement.objects.create(
                    movement_type='OUT',
                    reference_number=loan.loan_number,
                    date=loan.date,
                    warehouse=loan.warehouse,
                    notes=f'سلفة منصرفة: {loan.loan_reason}',
                    total_amount=loan.total_estimated_value,
                    created_by=request.user
                )

                # تطبيق كل صنف
                for item in items:
                    # إنشاء حركة للصنف
                    StockMovementItem.objects.create(
                        movement=movement,
                        item=item.item,
                        quantity=-item.quantity_issued,  # كمية سالبة للصرف
                        unit_cost=item.estimated_unit_value,
                        total_cost=-item.total_estimated_value,  # مبلغ سالب للصرف
                        batch_number=item.batch_number
                    )

                    # تحديث رصيد المخزون
                    stock = Stock.objects.get(warehouse=loan.warehouse, item=item.item)
                    stock.quantity -= item.quantity_issued
                    stock.last_movement_date = datetime.now()
                    stock.save()

                messages.success(request, f'تم إنشاء سلفة البضاعة المنصرفة {loan.loan_number} بنجاح')
                return redirect('inventory:goods_issued_on_loan_detail', pk=loan.pk)
    else:
        form = GoodsIssuedOnLoanForm()
        formset = GoodsIssuedOnLoanItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'إضافة بضاعة سلفة منصرفة جديدة',
        'action': 'إضافة'
    }
    return render(request, 'inventory/goods_issued_on_loan_form.html', context)


@login_required
def goods_issued_on_loan_detail(request, pk):
    """تفاصيل بضاعة السلفة المنصرفة"""
    loan = get_object_or_404(GoodsIssuedOnLoan, pk=pk)
    items = loan.items.all().select_related('item')

    context = {
        'loan': loan,
        'items': items,
        'title': f'سلفة بضاعة منصرفة رقم: {loan.loan_number}'
    }
    return render(request, 'inventory/goods_issued_on_loan_detail.html', context)


@login_required
def goods_issued_on_loan_edit(request, pk):
    """تعديل بضاعة السلفة المنصرفة"""
    loan = get_object_or_404(GoodsIssuedOnLoan, pk=pk)

    # التحقق من إمكانية التعديل
    if loan.status not in ['ISSUED']:
        messages.error(request, 'لا يمكن تعديل السلفة بعد إرجاعها أو إلغائها')
        return redirect('inventory:goods_issued_on_loan_detail', pk=pk)

    if request.method == 'POST':
        form = GoodsIssuedOnLoanForm(request.POST, instance=loan)
        formset = GoodsIssuedOnLoanItemFormSet(request.POST, instance=loan)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                loan = form.save(commit=False)
                loan.updated_by = request.user
                loan.save()

                items = formset.save()

                # حساب الإجمالي
                total_value = sum(item.total_estimated_value for item in items)
                loan.total_estimated_value = total_value
                loan.save()

                messages.success(request, f'تم تحديث سلفة البضاعة المنصرفة {loan.loan_number} بنجاح')
                return redirect('inventory:goods_issued_on_loan_detail', pk=loan.pk)
    else:
        form = GoodsIssuedOnLoanForm(instance=loan)
        formset = GoodsIssuedOnLoanItemFormSet(instance=loan)

    context = {
        'form': form,
        'formset': formset,
        'loan': loan,
        'title': f'تعديل سلفة البضاعة المنصرفة: {loan.loan_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/goods_issued_on_loan_form.html', context)


@login_required
def goods_issued_on_loan_return(request, pk):
    """إرجاع بضاعة السلفة المنصرفة"""
    if request.method == 'POST':
        loan = get_object_or_404(GoodsIssuedOnLoan, pk=pk)

        if loan.status not in ['ISSUED', 'PARTIAL_RETURNED']:
            return JsonResponse({'success': False, 'message': 'السلفة مرتجعة مسبقاً أو ملغاة'})

        with transaction.atomic():
            # تحديث حالة السلفة
            loan.status = 'RETURNED'
            loan.save()

            # تحديث كميات الإرجاع لجميع الأصناف وإرجاعها للمخزون
            from .models import Stock, StockMovement, StockMovementItem

            # إنشاء حركة مخزون للإرجاع
            movement = StockMovement.objects.create(
                movement_type='IN',
                reference_number=f'{loan.loan_number}-RETURN',
                date=datetime.now().date(),
                warehouse=loan.warehouse,
                notes=f'إرجاع سلفة منصرفة: {loan.loan_reason}',
                total_amount=loan.total_estimated_value,
                created_by=request.user
            )

            for item in loan.items.all():
                remaining_qty = item.quantity_issued - item.quantity_returned
                if remaining_qty > 0:
                    # تحديث كمية الإرجاع
                    item.quantity_returned = item.quantity_issued
                    item.save()

                    # إنشاء حركة للصنف
                    StockMovementItem.objects.create(
                        movement=movement,
                        item=item.item,
                        quantity=remaining_qty,  # كمية موجبة للإرجاع
                        unit_cost=item.estimated_unit_value,
                        total_cost=remaining_qty * item.estimated_unit_value,
                        batch_number=item.batch_number
                    )

                    # إرجاع الكمية للمخزون
                    stock, created = Stock.objects.get_or_create(
                        warehouse=loan.warehouse,
                        item=item.item,
                        defaults={'quantity': 0, 'average_cost': item.estimated_unit_value}
                    )
                    stock.quantity += remaining_qty
                    stock.last_movement_date = datetime.now()
                    stock.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إرجاع سلفة البضاعة المنصرفة {loan.loan_number} بالكامل'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def goods_issued_on_loan_partial_return(request, pk):
    """إرجاع جزئي لبضاعة السلفة المنصرفة"""
    if request.method == 'POST':
        loan = get_object_or_404(GoodsIssuedOnLoan, pk=pk)

        if loan.status not in ['ISSUED', 'PARTIAL_RETURNED']:
            return JsonResponse({'success': False, 'message': 'السلفة مرتجعة مسبقاً أو ملغاة'})

        # هنا يمكن إضافة نموذج للإرجاع الجزئي
        # للبساطة، سنقوم بتحديث الحالة فقط
        loan.status = 'PARTIAL_RETURNED'
        loan.save()

        return JsonResponse({
            'success': True,
            'message': f'تم تسجيل إرجاع جزئي لسلفة البضاعة المنصرفة {loan.loan_number}'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def goods_issued_on_loan_cancel(request, pk):
    """إلغاء سلفة البضاعة المنصرفة"""
    if request.method == 'POST':
        loan = get_object_or_404(GoodsIssuedOnLoan, pk=pk)

        if loan.status in ['RETURNED', 'CANCELLED']:
            return JsonResponse({'success': False, 'message': 'السلفة مرتجعة أو ملغاة مسبقاً'})

        with transaction.atomic():
            # إلغاء السلفة وإرجاع البضاعة للمخزون
            loan.status = 'CANCELLED'
            loan.save()

            # إرجاع البضاعة للمخزون
            from .models import Stock, StockMovement, StockMovementItem

            # إنشاء حركة مخزون للإلغاء
            movement = StockMovement.objects.create(
                movement_type='IN',
                reference_number=f'{loan.loan_number}-CANCEL',
                date=datetime.now().date(),
                warehouse=loan.warehouse,
                notes=f'إلغاء سلفة منصرفة: {loan.loan_reason}',
                total_amount=loan.total_estimated_value,
                created_by=request.user
            )

            for item in loan.items.all():
                remaining_qty = item.quantity_issued - item.quantity_returned
                if remaining_qty > 0:
                    # إنشاء حركة للصنف
                    StockMovementItem.objects.create(
                        movement=movement,
                        item=item.item,
                        quantity=remaining_qty,
                        unit_cost=item.estimated_unit_value,
                        total_cost=remaining_qty * item.estimated_unit_value,
                        batch_number=item.batch_number
                    )

                    # إرجاع الكمية للمخزون
                    stock, created = Stock.objects.get_or_create(
                        warehouse=loan.warehouse,
                        item=item.item,
                        defaults={'quantity': 0, 'average_cost': item.estimated_unit_value}
                    )
                    stock.quantity += remaining_qty
                    stock.last_movement_date = datetime.now()
                    stock.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إلغاء سلفة البضاعة المنصرفة {loan.loan_number} وإرجاع البضاعة للمخزون'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def goods_issued_on_loan_delete(request, pk):
    """حذف سلفة البضاعة المنصرفة"""
    if request.method == 'DELETE':
        loan = get_object_or_404(GoodsIssuedOnLoan, pk=pk)

        if loan.status not in ['CANCELLED']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف سلفة نشطة. يجب إلغاؤها أولاً'})

        loan_number = loan.loan_number
        loan.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف سلفة البضاعة المنصرفة {loan_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# ==================== Warehouse Transfer Views ====================

@login_required
def warehouse_transfer_list(request):
    """قائمة تحويلات المخازن"""
    form = WarehouseTransferFilterForm(request.GET)
    transfers = WarehouseTransfer.objects.all().select_related(
        'from_warehouse', 'to_warehouse', 'created_by'
    )

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        from_warehouse = form.cleaned_data.get('from_warehouse')
        to_warehouse = form.cleaned_data.get('to_warehouse')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            transfers = transfers.filter(
                Q(transfer_number__icontains=search) |
                Q(transfer_reason__icontains=search)
            )

        if from_warehouse:
            transfers = transfers.filter(from_warehouse=from_warehouse)

        if to_warehouse:
            transfers = transfers.filter(to_warehouse=to_warehouse)

        if status:
            transfers = transfers.filter(status=status)

        if date_from:
            transfers = transfers.filter(date__gte=date_from)

        if date_to:
            transfers = transfers.filter(date__lte=date_to)

    transfers = transfers.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(transfers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_transfers = transfers.count()
    draft_transfers = transfers.filter(status='DRAFT').count()
    approved_transfers = transfers.filter(status='APPROVED').count()
    in_transit_transfers = transfers.filter(status='IN_TRANSIT').count()
    completed_transfers = transfers.filter(status='COMPLETED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_transfers': total_transfers,
        'draft_transfers': draft_transfers,
        'approved_transfers': approved_transfers,
        'in_transit_transfers': in_transit_transfers,
        'completed_transfers': completed_transfers,
        'title': 'تحويلات بين المخازن'
    }
    return render(request, 'inventory/warehouse_transfer_list.html', context)


@login_required
def warehouse_transfer_create(request):
    """إضافة تحويل جديد بين المخازن"""
    if request.method == 'POST':
        form = WarehouseTransferForm(request.POST)
        formset = WarehouseTransferItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                transfer = form.save(commit=False)
                transfer.created_by = request.user
                transfer.save()

                formset.instance = transfer
                items = formset.save()

                # حساب الإجمالي
                total_value = sum(item.total_cost for item in items)
                transfer.total_estimated_value = total_value
                transfer.save()

                messages.success(request, f'تم إنشاء التحويل {transfer.transfer_number} بنجاح')
                return redirect('inventory:warehouse_transfer_detail', pk=transfer.pk)
    else:
        form = WarehouseTransferForm()
        formset = WarehouseTransferItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'إضافة تحويل جديد بين المخازن',
        'action': 'إضافة'
    }
    return render(request, 'inventory/warehouse_transfer_form.html', context)


@login_required
def warehouse_transfer_detail(request, pk):
    """تفاصيل التحويل"""
    transfer = get_object_or_404(WarehouseTransfer, pk=pk)
    items = transfer.items.all().select_related('item')

    context = {
        'transfer': transfer,
        'items': items,
        'title': f'تحويل رقم: {transfer.transfer_number}'
    }
    return render(request, 'inventory/warehouse_transfer_detail.html', context)


@login_required
def warehouse_transfer_edit(request, pk):
    """تعديل التحويل"""
    transfer = get_object_or_404(WarehouseTransfer, pk=pk)

    # التحقق من إمكانية التعديل
    if not transfer.can_be_edited:
        messages.error(request, 'لا يمكن تعديل التحويل بعد اعتماده')
        return redirect('inventory:warehouse_transfer_detail', pk=pk)

    if request.method == 'POST':
        form = WarehouseTransferForm(request.POST, instance=transfer)
        formset = WarehouseTransferItemFormSet(request.POST, instance=transfer)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                transfer = form.save(commit=False)
                transfer.updated_by = request.user
                transfer.save()

                items = formset.save()

                # حساب الإجمالي
                total_value = sum(item.total_cost for item in items)
                transfer.total_estimated_value = total_value
                transfer.save()

                messages.success(request, f'تم تحديث التحويل {transfer.transfer_number} بنجاح')
                return redirect('inventory:warehouse_transfer_detail', pk=transfer.pk)
    else:
        form = WarehouseTransferForm(instance=transfer)
        formset = WarehouseTransferItemFormSet(instance=transfer)

    context = {
        'form': form,
        'formset': formset,
        'transfer': transfer,
        'title': f'تعديل التحويل: {transfer.transfer_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/warehouse_transfer_form.html', context)


@login_required
def warehouse_transfer_approve(request, pk):
    """اعتماد التحويل"""
    if request.method == 'POST':
        transfer = get_object_or_404(WarehouseTransfer, pk=pk)

        if not transfer.can_be_approved:
            return JsonResponse({'success': False, 'message': 'التحويل معتمد مسبقاً أو ملغي'})

        transfer.status = 'APPROVED'
        transfer.approved_by = request.user
        transfer.approved_date = datetime.now()
        transfer.save()

        return JsonResponse({
            'success': True,
            'message': f'تم اعتماد التحويل {transfer.transfer_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def warehouse_transfer_ship(request, pk):
    """شحن التحويل (خصم من المخزن المرسل)"""
    if request.method == 'POST':
        transfer = get_object_or_404(WarehouseTransfer, pk=pk)

        if not transfer.can_be_shipped:
            return JsonResponse({'success': False, 'message': 'يجب اعتماد التحويل أولاً'})

        with transaction.atomic():
            # التحقق من توفر الكميات في المخزن المرسل
            from .models import Stock

            for item in transfer.items.all():
                try:
                    stock = Stock.objects.get(warehouse=transfer.from_warehouse, item=item.item)
                    if stock.quantity < item.quantity_requested:
                        return JsonResponse({
                            'success': False,
                            'message': f'الكمية المتاحة من {item.item.name} غير كافية. المتاح: {stock.quantity}'
                        })
                except Stock.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'الصنف {item.item.name} غير متوفر في المخزن المرسل'
                    })

            # خصم الكميات من المخزن المرسل
            from .models import StockMovement, StockMovementItem

            # إنشاء حركة مخزون للشحن
            movement = StockMovement.objects.create(
                movement_type='OUT',
                reference_number=f'{transfer.transfer_number}-SHIP',
                date=transfer.date,
                warehouse=transfer.from_warehouse,
                notes=f'شحن تحويل إلى {transfer.to_warehouse.name}: {transfer.transfer_reason}',
                total_amount=transfer.total_estimated_value,
                created_by=request.user
            )

            # تطبيق كل صنف
            for item in transfer.items.all():
                # تحديث الكمية المشحونة
                item.quantity_shipped = item.quantity_requested

                # الحصول على تكلفة الوحدة من المخزون
                stock = Stock.objects.get(warehouse=transfer.from_warehouse, item=item.item)
                item.unit_cost = stock.average_cost
                item.total_cost = item.quantity_shipped * item.unit_cost
                item.save()

                # إنشاء حركة للصنف
                StockMovementItem.objects.create(
                    movement=movement,
                    item=item.item,
                    quantity=-item.quantity_shipped,  # كمية سالبة للشحن
                    unit_cost=item.unit_cost,
                    total_cost=-item.total_cost,
                    batch_number=item.batch_number
                )

                # خصم الكمية من المخزون المرسل
                stock.quantity -= item.quantity_shipped
                stock.last_movement_date = datetime.now()
                stock.save()

            # تحديث حالة التحويل
            transfer.status = 'IN_TRANSIT'
            transfer.shipped_by = request.user
            transfer.shipped_date = datetime.now()
            transfer.save()

        return JsonResponse({
            'success': True,
            'message': f'تم شحن التحويل {transfer.transfer_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def warehouse_transfer_receive(request, pk):
    """استلام التحويل (إضافة للمخزن المستقبل)"""
    if request.method == 'POST':
        transfer = get_object_or_404(WarehouseTransfer, pk=pk)

        if not transfer.can_be_received:
            return JsonResponse({'success': False, 'message': 'التحويل ليس في حالة الشحن'})

        with transaction.atomic():
            # إضافة الكميات للمخزن المستقبل
            from .models import Stock, StockMovement, StockMovementItem

            # إنشاء حركة مخزون للاستلام
            movement = StockMovement.objects.create(
                movement_type='IN',
                reference_number=f'{transfer.transfer_number}-RECEIVE',
                date=datetime.now().date(),
                warehouse=transfer.to_warehouse,
                notes=f'استلام تحويل من {transfer.from_warehouse.name}: {transfer.transfer_reason}',
                total_amount=transfer.total_estimated_value,
                created_by=request.user
            )

            # تطبيق كل صنف
            for item in transfer.items.all():
                # تحديث الكمية المستلمة
                item.quantity_received = item.quantity_shipped
                item.save()

                # إنشاء حركة للصنف
                StockMovementItem.objects.create(
                    movement=movement,
                    item=item.item,
                    quantity=item.quantity_received,  # كمية موجبة للاستلام
                    unit_cost=item.unit_cost,
                    total_cost=item.total_cost,
                    expiry_date=item.expiry_date,
                    batch_number=item.batch_number
                )

                # إضافة الكمية للمخزن المستقبل
                stock, created = Stock.objects.get_or_create(
                    warehouse=transfer.to_warehouse,
                    item=item.item,
                    defaults={
                        'quantity': 0,
                        'average_cost': item.unit_cost
                    }
                )

                # حساب المتوسط المرجح للتكلفة
                if stock.quantity > 0:
                    total_value = (stock.quantity * stock.average_cost) + item.total_cost
                    stock.quantity += item.quantity_received
                    stock.average_cost = total_value / stock.quantity
                else:
                    stock.quantity = item.quantity_received
                    stock.average_cost = item.unit_cost

                stock.last_movement_date = datetime.now()
                stock.save()

            # تحديث حالة التحويل
            transfer.status = 'COMPLETED'
            transfer.received_by = request.user
            transfer.received_date = datetime.now()
            transfer.save()

        return JsonResponse({
            'success': True,
            'message': f'تم استلام التحويل {transfer.transfer_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def warehouse_transfer_cancel(request, pk):
    """إلغاء التحويل"""
    if request.method == 'POST':
        transfer = get_object_or_404(WarehouseTransfer, pk=pk)

        if not transfer.can_be_cancelled:
            return JsonResponse({'success': False, 'message': 'لا يمكن إلغاء التحويل في هذه الحالة'})

        transfer.status = 'CANCELLED'
        transfer.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إلغاء التحويل {transfer.transfer_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def warehouse_transfer_delete(request, pk):
    """حذف التحويل"""
    if request.method == 'DELETE':
        transfer = get_object_or_404(WarehouseTransfer, pk=pk)

        if transfer.status not in ['DRAFT', 'CANCELLED']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف تحويل معتمد أو مكتمل'})

        transfer_number = transfer.transfer_number
        transfer.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف التحويل {transfer_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# ==================== Item Transformation Views ====================

@login_required
def item_transformation_list(request):
    """قائمة تحويلات الأصناف"""
    form = ItemTransformationFilterForm(request.GET)
    transformations = ItemTransformation.objects.all().select_related('warehouse', 'created_by')

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        warehouse = form.cleaned_data.get('warehouse')
        transformation_type = form.cleaned_data.get('transformation_type')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if search:
            transformations = transformations.filter(
                Q(transformation_number__icontains=search) |
                Q(transformation_reason__icontains=search)
            )

        if warehouse:
            transformations = transformations.filter(warehouse=warehouse)

        if transformation_type:
            transformations = transformations.filter(transformation_type=transformation_type)

        if status:
            transformations = transformations.filter(status=status)

        if date_from:
            transformations = transformations.filter(date__gte=date_from)

        if date_to:
            transformations = transformations.filter(date__lte=date_to)

    transformations = transformations.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(transformations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_transformations = transformations.count()
    draft_transformations = transformations.filter(status='DRAFT').count()
    approved_transformations = transformations.filter(status='APPROVED').count()
    completed_transformations = transformations.filter(status='COMPLETED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_transformations': total_transformations,
        'draft_transformations': draft_transformations,
        'approved_transformations': approved_transformations,
        'completed_transformations': completed_transformations,
        'title': 'تحويلات من صنف إلى صنف'
    }
    return render(request, 'inventory/item_transformation_list.html', context)


@login_required
def item_transformation_create(request):
    """إضافة تحويل جديد من صنف إلى صنف"""
    if request.method == 'POST':
        form = ItemTransformationForm(request.POST)
        input_formset = ItemTransformationInputFormSet(request.POST, prefix='inputs')
        output_formset = ItemTransformationOutputFormSet(request.POST, prefix='outputs')

        if form.is_valid() and input_formset.is_valid() and output_formset.is_valid():
            with transaction.atomic():
                transformation = form.save(commit=False)
                transformation.created_by = request.user
                transformation.save()

                # حفظ المدخلات
                input_formset.instance = transformation
                inputs = input_formset.save()

                # حفظ المخرجات
                output_formset.instance = transformation
                outputs = output_formset.save()

                # حساب الإجماليات
                total_input_value = sum(item.total_cost for item in inputs)
                total_output_value = sum(item.total_cost for item in outputs)

                transformation.total_input_value = total_input_value
                transformation.total_output_value = total_output_value
                transformation.save()

                messages.success(request, f'تم إنشاء التحويل {transformation.transformation_number} بنجاح')
                return redirect('inventory:item_transformation_detail', pk=transformation.pk)
    else:
        form = ItemTransformationForm()
        input_formset = ItemTransformationInputFormSet(prefix='inputs')
        output_formset = ItemTransformationOutputFormSet(prefix='outputs')

    context = {
        'form': form,
        'input_formset': input_formset,
        'output_formset': output_formset,
        'title': 'إضافة تحويل جديد من صنف إلى صنف',
        'action': 'إضافة'
    }
    return render(request, 'inventory/item_transformation_form.html', context)


@login_required
def item_transformation_detail(request, pk):
    """تفاصيل التحويل"""
    transformation = get_object_or_404(ItemTransformation, pk=pk)
    inputs = transformation.inputs.all().select_related('item')
    outputs = transformation.outputs.all().select_related('item')

    context = {
        'transformation': transformation,
        'inputs': inputs,
        'outputs': outputs,
        'title': f'تحويل رقم: {transformation.transformation_number}'
    }
    return render(request, 'inventory/item_transformation_detail.html', context)


@login_required
def item_transformation_edit(request, pk):
    """تعديل التحويل"""
    transformation = get_object_or_404(ItemTransformation, pk=pk)

    # التحقق من إمكانية التعديل
    if not transformation.can_be_edited:
        messages.error(request, 'لا يمكن تعديل التحويل بعد اعتماده')
        return redirect('inventory:item_transformation_detail', pk=pk)

    if request.method == 'POST':
        form = ItemTransformationForm(request.POST, instance=transformation)
        input_formset = ItemTransformationInputFormSet(request.POST, instance=transformation, prefix='inputs')
        output_formset = ItemTransformationOutputFormSet(request.POST, instance=transformation, prefix='outputs')

        if form.is_valid() and input_formset.is_valid() and output_formset.is_valid():
            with transaction.atomic():
                transformation = form.save(commit=False)
                transformation.updated_by = request.user
                transformation.save()

                # حفظ المدخلات والمخرجات
                inputs = input_formset.save()
                outputs = output_formset.save()

                # حساب الإجماليات
                total_input_value = sum(item.total_cost for item in inputs)
                total_output_value = sum(item.total_cost for item in outputs)

                transformation.total_input_value = total_input_value
                transformation.total_output_value = total_output_value
                transformation.save()

                messages.success(request, f'تم تحديث التحويل {transformation.transformation_number} بنجاح')
                return redirect('inventory:item_transformation_detail', pk=transformation.pk)
    else:
        form = ItemTransformationForm(instance=transformation)
        input_formset = ItemTransformationInputFormSet(instance=transformation, prefix='inputs')
        output_formset = ItemTransformationOutputFormSet(instance=transformation, prefix='outputs')

    context = {
        'form': form,
        'input_formset': input_formset,
        'output_formset': output_formset,
        'transformation': transformation,
        'title': f'تعديل التحويل: {transformation.transformation_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/item_transformation_form.html', context)


@login_required
def item_transformation_approve(request, pk):
    """اعتماد التحويل"""
    if request.method == 'POST':
        transformation = get_object_or_404(ItemTransformation, pk=pk)

        if not transformation.can_be_approved:
            return JsonResponse({'success': False, 'message': 'التحويل معتمد مسبقاً أو ملغي'})

        transformation.status = 'APPROVED'
        transformation.approved_by = request.user
        transformation.approved_date = datetime.now()
        transformation.save()

        return JsonResponse({
            'success': True,
            'message': f'تم اعتماد التحويل {transformation.transformation_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def item_transformation_complete(request, pk):
    """إكمال التحويل (تطبيق على المخزون)"""
    if request.method == 'POST':
        transformation = get_object_or_404(ItemTransformation, pk=pk)

        if not transformation.can_be_completed:
            return JsonResponse({'success': False, 'message': 'يجب اعتماد التحويل أولاً'})

        with transaction.atomic():
            # التحقق من توفر الكميات المطلوبة للمدخلات
            from .models import Stock

            for input_item in transformation.inputs.all():
                try:
                    stock = Stock.objects.get(warehouse=transformation.warehouse, item=input_item.item)
                    if stock.quantity < input_item.quantity:
                        return JsonResponse({
                            'success': False,
                            'message': f'الكمية المتاحة من {input_item.item.name} غير كافية. المتاح: {stock.quantity}'
                        })
                except Stock.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'الصنف {input_item.item.name} غير متوفر في المخزون'
                    })

            # تطبيق التحويل على المخزون
            from .models import StockMovement, StockMovementItem

            # إنشاء حركة مخزون للتحويل
            movement = StockMovement.objects.create(
                movement_type='TRANSFORMATION',
                reference_number=transformation.transformation_number,
                date=transformation.date,
                warehouse=transformation.warehouse,
                notes=f'تحويل أصناف: {transformation.transformation_reason}',
                total_amount=transformation.net_value_change,
                created_by=request.user
            )

            # معالجة المدخلات (خصم من المخزون)
            for input_item in transformation.inputs.all():
                # تحديث تكلفة الوحدة من المخزون
                stock = Stock.objects.get(warehouse=transformation.warehouse, item=input_item.item)
                input_item.unit_cost = stock.average_cost
                input_item.total_cost = input_item.quantity * input_item.unit_cost
                input_item.save()

                # إنشاء حركة للصنف المستهلك
                StockMovementItem.objects.create(
                    movement=movement,
                    item=input_item.item,
                    quantity=-input_item.quantity,  # كمية سالبة للاستهلاك
                    unit_cost=input_item.unit_cost,
                    total_cost=-input_item.total_cost,
                    expiry_date=input_item.expiry_date,
                    batch_number=input_item.batch_number
                )

                # خصم الكمية من المخزون
                stock.quantity -= input_item.quantity
                stock.last_movement_date = datetime.now()
                stock.save()

            # معالجة المخرجات (إضافة للمخزون)
            for output_item in transformation.outputs.all():
                # حساب تكلفة الوحدة للمخرجات
                if transformation.total_input_value > 0:
                    # توزيع التكلفة بناءً على النسبة
                    cost_ratio = output_item.total_cost / transformation.total_output_value if transformation.total_output_value > 0 else 1
                    allocated_input_cost = transformation.total_input_value * cost_ratio
                    allocated_transformation_cost = transformation.transformation_cost * cost_ratio
                    output_item.unit_cost = (allocated_input_cost + allocated_transformation_cost) / output_item.quantity
                    output_item.total_cost = output_item.quantity * output_item.unit_cost
                    output_item.save()

                # إنشاء حركة للصنف المنتج
                StockMovementItem.objects.create(
                    movement=movement,
                    item=output_item.item,
                    quantity=output_item.quantity,  # كمية موجبة للإنتاج
                    unit_cost=output_item.unit_cost,
                    total_cost=output_item.total_cost,
                    expiry_date=output_item.expiry_date,
                    batch_number=output_item.batch_number
                )

                # إضافة الكمية للمخزون
                stock, created = Stock.objects.get_or_create(
                    warehouse=transformation.warehouse,
                    item=output_item.item,
                    defaults={
                        'quantity': 0,
                        'average_cost': output_item.unit_cost
                    }
                )

                # حساب المتوسط المرجح للتكلفة
                if stock.quantity > 0:
                    total_value = (stock.quantity * stock.average_cost) + output_item.total_cost
                    stock.quantity += output_item.quantity
                    stock.average_cost = total_value / stock.quantity
                else:
                    stock.quantity = output_item.quantity
                    stock.average_cost = output_item.unit_cost

                stock.last_movement_date = datetime.now()
                stock.save()

            # تحديث الإجماليات والحالة
            transformation.total_input_value = sum(item.total_cost for item in transformation.inputs.all())
            transformation.total_output_value = sum(item.total_cost for item in transformation.outputs.all())
            transformation.status = 'COMPLETED'
            transformation.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إكمال التحويل {transformation.transformation_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def item_transformation_cancel(request, pk):
    """إلغاء التحويل"""
    if request.method == 'POST':
        transformation = get_object_or_404(ItemTransformation, pk=pk)

        if not transformation.can_be_cancelled:
            return JsonResponse({'success': False, 'message': 'لا يمكن إلغاء التحويل في هذه الحالة'})

        transformation.status = 'CANCELLED'
        transformation.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إلغاء التحويل {transformation.transformation_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def item_transformation_delete(request, pk):
    """حذف التحويل"""
    if request.method == 'DELETE':
        transformation = get_object_or_404(ItemTransformation, pk=pk)

        if transformation.status not in ['DRAFT', 'CANCELLED']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف تحويل معتمد أو مكتمل'})

        transformation_number = transformation.transformation_number
        transformation.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف التحويل {transformation_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# ==================== Manufacturing Order Views ====================

@login_required
def manufacturing_order_list(request):
    """قائمة أوامر الإنتاج"""
    form = ManufacturingOrderFilterForm(request.GET)
    orders = ManufacturingOrder.objects.all().select_related('warehouse', 'product_item', 'created_by')

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        warehouse = form.cleaned_data.get('warehouse')
        product_item = form.cleaned_data.get('product_item')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        overdue_only = form.cleaned_data.get('overdue_only')

        if search:
            orders = orders.filter(
                Q(order_number__icontains=search) |
                Q(product_item__name__icontains=search)
            )

        if warehouse:
            orders = orders.filter(warehouse=warehouse)

        if product_item:
            orders = orders.filter(product_item=product_item)

        if status:
            orders = orders.filter(status=status)

        if priority:
            orders = orders.filter(priority=priority)

        if date_from:
            orders = orders.filter(date__gte=date_from)

        if date_to:
            orders = orders.filter(date__lte=date_to)

        if overdue_only:
            from datetime import date
            orders = orders.filter(
                expected_completion_date__lt=date.today(),
                status__in=['APPROVED', 'IN_PRODUCTION']
            )

    orders = orders.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_orders = orders.count()
    draft_orders = orders.filter(status='DRAFT').count()
    approved_orders = orders.filter(status='APPROVED').count()
    in_production_orders = orders.filter(status='IN_PRODUCTION').count()
    completed_orders = orders.filter(status='COMPLETED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_orders': total_orders,
        'draft_orders': draft_orders,
        'approved_orders': approved_orders,
        'in_production_orders': in_production_orders,
        'completed_orders': completed_orders,
        'title': 'أوامر الإنتاج التام التصنيع'
    }
    return render(request, 'inventory/manufacturing_order_list.html', context)


@login_required
def manufacturing_order_create(request):
    """إضافة أمر إنتاج جديد"""
    if request.method == 'POST':
        form = ManufacturingOrderForm(request.POST)
        material_formset = ManufacturingOrderMaterialFormSet(request.POST, prefix='materials')

        if form.is_valid() and material_formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.created_by = request.user
                order.save()

                # حفظ المواد الخام
                material_formset.instance = order
                materials = material_formset.save()

                # حساب الإجماليات
                total_material_cost = sum(material.total_cost for material in materials)
                total_production_cost = order.quantity_to_produce * order.production_cost_per_unit

                order.total_material_cost = total_material_cost
                order.total_production_cost = total_production_cost
                order.total_cost = total_material_cost + total_production_cost
                order.save()

                messages.success(request, f'تم إنشاء أمر الإنتاج {order.order_number} بنجاح')
                return redirect('inventory:manufacturing_order_detail', pk=order.pk)
    else:
        form = ManufacturingOrderForm()
        material_formset = ManufacturingOrderMaterialFormSet(prefix='materials')

    context = {
        'form': form,
        'material_formset': material_formset,
        'title': 'إضافة أمر إنتاج جديد',
        'action': 'إضافة'
    }
    return render(request, 'inventory/manufacturing_order_form.html', context)


@login_required
def manufacturing_order_detail(request, pk):
    """تفاصيل أمر الإنتاج"""
    order = get_object_or_404(ManufacturingOrder, pk=pk)
    materials = order.materials.all().select_related('material')

    context = {
        'order': order,
        'materials': materials,
        'title': f'أمر إنتاج رقم: {order.order_number}'
    }
    return render(request, 'inventory/manufacturing_order_detail.html', context)


@login_required
def start_production(request, pk):
    """بدء عملية الإنتاج"""
    order = get_object_or_404(ManufacturingOrder, pk=pk)

    if request.method == 'POST':
        try:
            order.start_production()
            messages.success(request, f'تم بدء الإنتاج لأمر {order.order_number} بنجاح')
            return redirect('inventory:manufacturing_order_detail', pk=order.pk)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    return redirect('inventory:manufacturing_order_detail', pk=order.pk)


@login_required
def complete_production(request, pk):
    """إكمال عملية الإنتاج"""
    order = get_object_or_404(ManufacturingOrder, pk=pk)

    if request.method == 'POST':
        try:
            quantity_produced = request.POST.get('quantity_produced')
            if quantity_produced:
                quantity_produced = float(quantity_produced)
                order.complete_production(quantity_produced)
            else:
                order.complete_production()

            messages.success(request, f'تم إكمال الإنتاج لأمر {order.order_number} بنجاح')
            return redirect('inventory:manufacturing_order_detail', pk=order.pk)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    return redirect('inventory:manufacturing_order_detail', pk=order.pk)


@login_required
def production_materials_check(request, pk):
    """فحص توفر المواد الخام للإنتاج"""
    order = get_object_or_404(ManufacturingOrder, pk=pk)

    materials_status = []
    for material in order.materials.all():
        try:
            stock = Stock.objects.get(warehouse=order.warehouse, item=material.material)
            available = stock.available_quantity
            required = material.quantity_required
            status = {
                'material': material,
                'available_quantity': available,
                'required_quantity': required,
                'is_sufficient': available >= required,
                'shortage': max(0, required - available)
            }
        except Stock.DoesNotExist:
            status = {
                'material': material,
                'available_quantity': 0,
                'required_quantity': material.quantity_required,
                'is_sufficient': False,
                'shortage': material.quantity_required
            }
        materials_status.append(status)

    context = {
        'title': f'فحص المواد الخام - {order.order_number}',
        'order': order,
        'materials_status': materials_status,
        'can_start_production': all(status['is_sufficient'] for status in materials_status)
    }

    return render(request, 'inventory/production_materials_check.html', context)


@login_required
def opening_inventory_create(request):
    """إنشاء جرد افتتاحي جديد"""
    if request.method == 'POST':
        form = PhysicalInventoryForm(request.POST)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.inventory_type = 'OPENING'
            inventory.created_by = request.user
            inventory.save()

            messages.success(request, f'تم إنشاء الجرد الافتتاحي {inventory.inventory_number} بنجاح')
            return redirect('inventory:opening_inventory_detail', pk=inventory.pk)
    else:
        form = PhysicalInventoryForm()
        # تعيين نوع الجرد كافتتاحي
        form.fields['inventory_type'].initial = 'OPENING'
        form.fields['inventory_type'].widget = forms.HiddenInput()

    context = {
        'title': 'إنشاء جرد افتتاحي جديد',
        'form': form,
        'breadcrumb': [
            {'name': 'المخزون', 'url': reverse('dashboard:home')},
            {'name': 'الجرد الافتتاحي', 'url': reverse('inventory:opening_inventory_list')},
            {'name': 'إنشاء جديد', 'url': '#'}
        ]
    }

    return render(request, 'inventory/opening_inventory_form.html', context)


@login_required
def opening_inventory_list(request):
    """قائمة الجرد الافتتاحي"""
    inventories = PhysicalInventory.objects.filter(
        inventory_type='OPENING'
    ).select_related('warehouse', 'created_by').order_by('-date', '-id')

    # فلترة
    warehouse_id = request.GET.get('warehouse')
    if warehouse_id:
        inventories = inventories.filter(warehouse_id=warehouse_id)

    status = request.GET.get('status')
    if status:
        inventories = inventories.filter(status=status)

    financial_year = request.GET.get('financial_year')
    if financial_year:
        inventories = inventories.filter(financial_year=financial_year)

    # Pagination
    paginator = Paginator(inventories, 20)
    page = request.GET.get('page')
    inventories = paginator.get_page(page)

    context = {
        'title': 'الجرد الافتتاحي',
        'inventories': inventories,
        'warehouses': Warehouse.objects.filter(is_active=True),
        'breadcrumb': [
            {'name': 'المخزون', 'url': reverse('dashboard:home')},
            {'name': 'الجرد الافتتاحي', 'url': '#'}
        ]
    }

    return render(request, 'inventory/opening_inventory_list.html', context)


@login_required
def opening_inventory_detail(request, pk):
    """تفاصيل الجرد الافتتاحي"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk, inventory_type='OPENING')

    context = {
        'title': f'الجرد الافتتاحي - {inventory.inventory_number}',
        'inventory': inventory,
        'breadcrumb': [
            {'name': 'المخزون', 'url': reverse('dashboard:home')},
            {'name': 'الجرد الافتتاحي', 'url': reverse('inventory:opening_inventory_list')},
            {'name': inventory.inventory_number, 'url': '#'}
        ]
    }

    return render(request, 'inventory/opening_inventory_detail.html', context)


@login_required
def opening_inventory_edit(request, pk):
    """تعديل الجرد الافتتاحي"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk, inventory_type='OPENING')

    if not inventory.can_be_edited:
        messages.error(request, 'لا يمكن تعديل هذا الجرد في حالته الحالية')
        return redirect('inventory:opening_inventory_detail', pk=inventory.pk)

    if request.method == 'POST':
        form = PhysicalInventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.updated_by = request.user
            inventory.save()

            messages.success(request, 'تم تحديث الجرد الافتتاحي بنجاح')
            return redirect('inventory:opening_inventory_detail', pk=inventory.pk)
    else:
        form = PhysicalInventoryForm(instance=inventory)
        form.fields['inventory_type'].widget = forms.HiddenInput()

    context = {
        'title': f'تعديل الجرد الافتتاحي - {inventory.inventory_number}',
        'form': form,
        'inventory': inventory,
        'breadcrumb': [
            {'name': 'المخزون', 'url': reverse('dashboard:home')},
            {'name': 'الجرد الافتتاحي', 'url': reverse('inventory:opening_inventory_list')},
            {'name': inventory.inventory_number, 'url': reverse('inventory:opening_inventory_detail', kwargs={'pk': inventory.pk})},
            {'name': 'تعديل', 'url': '#'}
        ]
    }

    return render(request, 'inventory/opening_inventory_form.html', context)


@login_required
def opening_inventory_add_items(request, pk):
    """إضافة أصناف للجرد الافتتاحي"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk, inventory_type='OPENING')

    if not inventory.can_be_edited:
        messages.error(request, 'لا يمكن تعديل هذا الجرد في حالته الحالية')
        return redirect('inventory:opening_inventory_detail', pk=inventory.pk)

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity')
        unit_cost = request.POST.get('unit_cost')
        expiry_date = request.POST.get('expiry_date')
        batch_number = request.POST.get('batch_number')
        location = request.POST.get('location')
        notes = request.POST.get('notes')

        try:
            item = Item.objects.get(pk=item_id)

            # التحقق من عدم وجود الصنف مسبقاً
            if inventory.items.filter(item=item, batch_number=batch_number or '').exists():
                messages.error(request, f'الصنف {item.name} موجود بالفعل في الجرد')
                return redirect('inventory:opening_inventory_add_items', pk=inventory.pk)

            # إنشاء صنف الجرد
            inventory_item = PhysicalInventoryItem.objects.create(
                inventory=inventory,
                item=item,
                system_quantity=0,  # للجرد الافتتاحي لا توجد كمية في النظام
                counted_quantity=Decimal(quantity),
                unit_cost=Decimal(unit_cost),
                expiry_date=expiry_date if expiry_date else None,
                batch_number=batch_number or '',
                location=location or '',
                notes=notes or '',
                counted_by=request.user,
                counted_date=timezone.now(),
                is_counted=True
            )

            # حساب الإجماليات
            inventory.calculate_opening_totals()

            messages.success(request, f'تم إضافة الصنف {item.name} بنجاح')
            return redirect('inventory:opening_inventory_add_items', pk=inventory.pk)

        except Item.DoesNotExist:
            messages.error(request, 'الصنف المحدد غير موجود')
        except (ValueError, TypeError) as e:
            messages.error(request, f'خطأ في البيانات: {str(e)}')

    # جلب الأصناف المتاحة
    available_items = Item.objects.filter(is_active=True).order_by('name')

    context = {
        'title': f'إضافة أصناف - {inventory.inventory_number}',
        'inventory': inventory,
        'available_items': available_items,
        'breadcrumb': [
            {'name': 'المخزون', 'url': reverse('dashboard:home')},
            {'name': 'الجرد الافتتاحي', 'url': reverse('inventory:opening_inventory_list')},
            {'name': inventory.inventory_number, 'url': reverse('inventory:opening_inventory_detail', kwargs={'pk': inventory.pk})},
            {'name': 'إضافة أصناف', 'url': '#'}
        ]
    }

    return render(request, 'inventory/opening_inventory_add_items.html', context)


@login_required
def opening_inventory_apply(request, pk):
    """تطبيق الجرد الافتتاحي على المخزون"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk, inventory_type='OPENING')

    if request.method == 'POST':
        try:
            # إكمال الجرد أولاً إذا لم يكن مكتملاً
            if inventory.status == 'DRAFT':
                inventory.status = 'COMPLETED'
                inventory.completed_by = request.user
                inventory.completed_date = timezone.now()
                inventory.save()

            # تطبيق الجرد على المخزون
            inventory.apply_opening_inventory(request.user)

            messages.success(request, f'تم تطبيق الجرد الافتتاحي {inventory.inventory_number} على المخزون بنجاح')
            return redirect('inventory:opening_inventory_detail', pk=inventory.pk)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    return redirect('inventory:opening_inventory_detail', pk=inventory.pk)


@login_required
def manufacturing_order_edit(request, pk):
    """تعديل أمر الإنتاج"""
    order = get_object_or_404(ManufacturingOrder, pk=pk)

    # التحقق من إمكانية التعديل
    if not order.can_be_edited:
        messages.error(request, 'لا يمكن تعديل أمر الإنتاج بعد اعتماده')
        return redirect('inventory:manufacturing_order_detail', pk=pk)

    if request.method == 'POST':
        form = ManufacturingOrderForm(request.POST, instance=order)
        material_formset = ManufacturingOrderMaterialFormSet(request.POST, instance=order, prefix='materials')

        if form.is_valid() and material_formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.updated_by = request.user
                order.save()

                # حفظ المواد الخام
                materials = material_formset.save()

                # حساب الإجماليات
                total_material_cost = sum(material.total_cost for material in materials)
                total_production_cost = order.quantity_to_produce * order.production_cost_per_unit

                order.total_material_cost = total_material_cost
                order.total_production_cost = total_production_cost
                order.total_cost = total_material_cost + total_production_cost
                order.save()

                messages.success(request, f'تم تحديث أمر الإنتاج {order.order_number} بنجاح')
                return redirect('inventory:manufacturing_order_detail', pk=order.pk)
    else:
        form = ManufacturingOrderForm(instance=order)
        material_formset = ManufacturingOrderMaterialFormSet(instance=order, prefix='materials')

    context = {
        'form': form,
        'material_formset': material_formset,
        'order': order,
        'title': f'تعديل أمر الإنتاج: {order.order_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/manufacturing_order_form.html', context)


@login_required
def manufacturing_order_approve(request, pk):
    """اعتماد أمر الإنتاج"""
    if request.method == 'POST':
        order = get_object_or_404(ManufacturingOrder, pk=pk)

        if not order.can_be_approved:
            return JsonResponse({'success': False, 'message': 'أمر الإنتاج معتمد مسبقاً أو ملغي'})

        order.status = 'APPROVED'
        order.approved_by = request.user
        order.approved_date = datetime.now()
        order.save()

        return JsonResponse({
            'success': True,
            'message': f'تم اعتماد أمر الإنتاج {order.order_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def manufacturing_order_start(request, pk):
    """بدء الإنتاج"""
    if request.method == 'POST':
        order = get_object_or_404(ManufacturingOrder, pk=pk)

        if not order.can_be_started:
            return JsonResponse({'success': False, 'message': 'يجب اعتماد أمر الإنتاج أولاً'})

        with transaction.atomic():
            # التحقق من توفر المواد الخام
            from .models import Stock

            for material in order.materials.all():
                try:
                    stock = Stock.objects.get(warehouse=order.warehouse, item=material.material)
                    if stock.quantity < material.quantity_required:
                        return JsonResponse({
                            'success': False,
                            'message': f'الكمية المتاحة من {material.material.name} غير كافية. المتاح: {stock.quantity}'
                        })
                except Stock.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'المادة الخام {material.material.name} غير متوفرة في المخزون'
                    })

            # خصم المواد الخام من المخزون
            from .models import StockMovement, StockMovementItem

            # إنشاء حركة مخزون لبدء الإنتاج
            movement = StockMovement.objects.create(
                movement_type='PRODUCTION_START',
                reference_number=order.order_number,
                date=order.date,
                warehouse=order.warehouse,
                notes=f'بدء إنتاج: {order.product_item.name}',
                total_amount=-order.total_material_cost,
                created_by=request.user
            )

            # خصم المواد الخام
            for material in order.materials.all():
                # تحديث تكلفة المادة من المخزون
                stock = Stock.objects.get(warehouse=order.warehouse, item=material.material)
                material.unit_cost = stock.average_cost
                material.total_cost = material.quantity_required * material.unit_cost
                material.quantity_consumed = material.quantity_required
                material.save()

                # إنشاء حركة للمادة الخام
                StockMovementItem.objects.create(
                    movement=movement,
                    item=material.material,
                    quantity=-material.quantity_required,  # كمية سالبة للاستهلاك
                    unit_cost=material.unit_cost,
                    total_cost=-material.total_cost,
                    expiry_date=material.expiry_date,
                    batch_number=material.batch_number
                )

                # خصم الكمية من المخزون
                stock.quantity -= material.quantity_required
                stock.last_movement_date = datetime.now()
                stock.save()

            # تحديث حالة الأمر
            order.status = 'IN_PRODUCTION'
            order.started_by = request.user
            order.started_date = datetime.now()

            # إعادة حساب التكاليف
            order.total_material_cost = sum(material.total_cost for material in order.materials.all())
            order.total_cost = order.total_material_cost + order.total_production_cost
            order.save()

        return JsonResponse({
            'success': True,
            'message': f'تم بدء إنتاج الأمر {order.order_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def manufacturing_order_complete(request, pk):
    """إكمال الإنتاج (إضافة المنتج النهائي للمخزون)"""
    if request.method == 'POST':
        order = get_object_or_404(ManufacturingOrder, pk=pk)

        if not order.can_be_completed:
            return JsonResponse({'success': False, 'message': 'يجب بدء الإنتاج أولاً'})

        # الحصول على الكمية المنتجة من الطلب
        quantity_produced = request.POST.get('quantity_produced')
        if not quantity_produced:
            return JsonResponse({'success': False, 'message': 'يجب تحديد الكمية المنتجة'})

        try:
            quantity_produced = float(quantity_produced)
            if quantity_produced <= 0:
                return JsonResponse({'success': False, 'message': 'الكمية المنتجة يجب أن تكون أكبر من صفر'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'الكمية المنتجة غير صحيحة'})

        with transaction.atomic():
            # إضافة المنتج النهائي للمخزون
            from .models import Stock, StockMovement, StockMovementItem

            # حساب تكلفة الوحدة للمنتج النهائي
            unit_cost = order.total_cost / order.quantity_to_produce if order.quantity_to_produce > 0 else 0
            total_value = quantity_produced * unit_cost

            # إنشاء حركة مخزون لإكمال الإنتاج
            movement = StockMovement.objects.create(
                movement_type='PRODUCTION_COMPLETE',
                reference_number=f'{order.order_number}-COMPLETE',
                date=datetime.now().date(),
                warehouse=order.warehouse,
                notes=f'إكمال إنتاج: {order.product_item.name}',
                total_amount=total_value,
                created_by=request.user
            )

            # إنشاء حركة للمنتج النهائي
            StockMovementItem.objects.create(
                movement=movement,
                item=order.product_item,
                quantity=quantity_produced,  # كمية موجبة للإنتاج
                unit_cost=unit_cost,
                total_cost=total_value
            )

            # إضافة المنتج النهائي للمخزون
            stock, created = Stock.objects.get_or_create(
                warehouse=order.warehouse,
                item=order.product_item,
                defaults={
                    'quantity': 0,
                    'average_cost': unit_cost
                }
            )

            # حساب المتوسط المرجح للتكلفة
            if stock.quantity > 0:
                total_stock_value = (stock.quantity * stock.average_cost) + total_value
                stock.quantity += quantity_produced
                stock.average_cost = total_stock_value / stock.quantity
            else:
                stock.quantity = quantity_produced
                stock.average_cost = unit_cost

            stock.last_movement_date = datetime.now()
            stock.save()

            # تحديث أمر الإنتاج
            order.quantity_produced = quantity_produced
            order.status = 'COMPLETED'
            order.completed_by = request.user
            order.completed_date = datetime.now()
            order.actual_completion_date = datetime.now().date()
            order.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إكمال إنتاج الأمر {order.order_number} بنجاح. تم إنتاج {quantity_produced} وحدة'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def manufacturing_order_cancel(request, pk):
    """إلغاء أمر الإنتاج"""
    if request.method == 'POST':
        order = get_object_or_404(ManufacturingOrder, pk=pk)

        if not order.can_be_cancelled:
            return JsonResponse({'success': False, 'message': 'لا يمكن إلغاء أمر الإنتاج في هذه الحالة'})

        order.status = 'CANCELLED'
        order.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إلغاء أمر الإنتاج {order.order_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def manufacturing_order_delete(request, pk):
    """حذف أمر الإنتاج"""
    if request.method == 'DELETE':
        order = get_object_or_404(ManufacturingOrder, pk=pk)

        if order.status not in ['DRAFT', 'CANCELLED']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف أمر إنتاج معتمد أو مكتمل'})

        order_number = order.order_number
        order.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف أمر الإنتاج {order_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


# ==================== Physical Inventory Views ====================

@login_required
def physical_inventory_list(request):
    """قائمة الجرد الفعلي"""
    form = PhysicalInventoryFilterForm(request.GET)
    inventories = PhysicalInventory.objects.all().select_related('warehouse', 'created_by')

    # تطبيق الفلاتر
    if form.is_valid():
        search = form.cleaned_data.get('search')
        warehouse = form.cleaned_data.get('warehouse')
        inventory_type = form.cleaned_data.get('inventory_type')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        discrepancies_only = form.cleaned_data.get('discrepancies_only')

        if search:
            inventories = inventories.filter(
                Q(inventory_number__icontains=search) |
                Q(reason__icontains=search)
            )

        if warehouse:
            inventories = inventories.filter(warehouse=warehouse)

        if inventory_type:
            inventories = inventories.filter(inventory_type=inventory_type)

        if status:
            inventories = inventories.filter(status=status)

        if date_from:
            inventories = inventories.filter(date__gte=date_from)

        if date_to:
            inventories = inventories.filter(date__lte=date_to)

        if discrepancies_only:
            inventories = inventories.filter(total_discrepancies__gt=0)

    inventories = inventories.order_by('-date', '-id')

    # تقسيم الصفحات
    paginator = Paginator(inventories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات
    total_inventories = inventories.count()
    draft_inventories = inventories.filter(status='DRAFT').count()
    in_progress_inventories = inventories.filter(status='IN_PROGRESS').count()
    completed_inventories = inventories.filter(status='COMPLETED').count()
    approved_inventories = inventories.filter(status='APPROVED').count()

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_inventories': total_inventories,
        'draft_inventories': draft_inventories,
        'in_progress_inventories': in_progress_inventories,
        'completed_inventories': completed_inventories,
        'approved_inventories': approved_inventories,
        'title': 'الجرد الفعلي للمخزون'
    }
    return render(request, 'inventory/physical_inventory_list.html', context)


@login_required
def physical_inventory_create(request):
    """إنشاء جرد فعلي جديد"""
    if request.method == 'POST':
        form = PhysicalInventoryForm(request.POST)

        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.created_by = request.user
            inventory.save()

            messages.success(request, f'تم إنشاء الجرد {inventory.inventory_number} بنجاح')
            return redirect('inventory:physical_inventory_detail', pk=inventory.pk)
    else:
        form = PhysicalInventoryForm()

    context = {
        'form': form,
        'title': 'إنشاء جرد فعلي جديد',
        'action': 'إنشاء'
    }
    return render(request, 'inventory/physical_inventory_form.html', context)


@login_required
def physical_inventory_detail(request, pk):
    """تفاصيل الجرد الفعلي"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk)
    items = inventory.items.all().select_related('item')

    context = {
        'inventory': inventory,
        'items': items,
        'title': f'جرد رقم: {inventory.inventory_number}'
    }
    return render(request, 'inventory/physical_inventory_detail.html', context)


@login_required
def physical_inventory_edit(request, pk):
    """تعديل الجرد الفعلي"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk)

    # التحقق من إمكانية التعديل
    if not inventory.can_be_edited:
        messages.error(request, 'لا يمكن تعديل الجرد بعد بدء التنفيذ')
        return redirect('inventory:physical_inventory_detail', pk=pk)

    if request.method == 'POST':
        form = PhysicalInventoryForm(request.POST, instance=inventory)

        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.updated_by = request.user
            inventory.save()

            messages.success(request, f'تم تحديث الجرد {inventory.inventory_number} بنجاح')
            return redirect('inventory:physical_inventory_detail', pk=inventory.pk)
    else:
        form = PhysicalInventoryForm(instance=inventory)

    context = {
        'form': form,
        'inventory': inventory,
        'title': f'تعديل الجرد: {inventory.inventory_number}',
        'action': 'تحديث'
    }
    return render(request, 'inventory/physical_inventory_form.html', context)


@login_required
def physical_inventory_start(request, pk):
    """بدء الجرد الفعلي"""
    if request.method == 'POST':
        inventory = get_object_or_404(PhysicalInventory, pk=pk)

        if not inventory.can_be_started:
            return JsonResponse({'success': False, 'message': 'الجرد بدأ مسبقاً أو ملغي'})

        with transaction.atomic():
            # إنشاء أصناف الجرد من المخزون الحالي
            from .models import Stock

            stocks = Stock.objects.filter(warehouse=inventory.warehouse, quantity__gt=0)

            for stock in stocks:
                PhysicalInventoryItem.objects.create(
                    inventory=inventory,
                    item=stock.item,
                    system_quantity=stock.quantity,
                    unit_cost=stock.average_cost
                )

            # تحديث حالة الجرد
            inventory.status = 'IN_PROGRESS'
            inventory.started_by = request.user
            inventory.started_date = datetime.now()
            inventory.save()

        return JsonResponse({
            'success': True,
            'message': f'تم بدء الجرد {inventory.inventory_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def physical_inventory_count(request, pk):
    """صفحة جرد الأصناف"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk)

    if inventory.status != 'IN_PROGRESS':
        messages.error(request, 'يجب أن يكون الجرد قيد التنفيذ لإجراء العد')
        return redirect('inventory:physical_inventory_detail', pk=pk)

    items = inventory.items.all().select_related('item').order_by('item__name')

    # فلترة الأصناف
    search = request.GET.get('search', '')
    counted_filter = request.GET.get('counted', '')

    if search:
        items = items.filter(item__name__icontains=search)

    if counted_filter == 'yes':
        items = items.filter(is_counted=True)
    elif counted_filter == 'no':
        items = items.filter(is_counted=False)

    # تقسيم الصفحات
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'inventory': inventory,
        'page_obj': page_obj,
        'search': search,
        'counted_filter': counted_filter,
        'title': f'جرد الأصناف - {inventory.inventory_number}'
    }
    return render(request, 'inventory/physical_inventory_count.html', context)


@login_required
def physical_inventory_count_item(request, pk, item_pk):
    """جرد صنف واحد"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk)
    inventory_item = get_object_or_404(PhysicalInventoryItem, inventory=inventory, pk=item_pk)

    if inventory.status != 'IN_PROGRESS':
        messages.error(request, 'يجب أن يكون الجرد قيد التنفيذ لإجراء العد')
        return redirect('inventory:physical_inventory_detail', pk=pk)

    if request.method == 'POST':
        form = CountItemForm(request.POST)

        if form.is_valid():
            inventory_item.counted_quantity = form.cleaned_data['counted_quantity']
            inventory_item.expiry_date = form.cleaned_data['expiry_date']
            inventory_item.batch_number = form.cleaned_data['batch_number']
            inventory_item.location = form.cleaned_data['location']
            inventory_item.discrepancy_reason = form.cleaned_data['discrepancy_reason']
            inventory_item.notes = form.cleaned_data['notes']
            inventory_item.counted_by = request.user
            inventory_item.counted_date = datetime.now()
            inventory_item.is_counted = True
            inventory_item.save()

            messages.success(request, f'تم جرد الصنف {inventory_item.item.name} بنجاح')
            return redirect('inventory:physical_inventory_count', pk=pk)
    else:
        form = CountItemForm(initial={
            'counted_quantity': inventory_item.system_quantity,
            'expiry_date': inventory_item.expiry_date,
            'batch_number': inventory_item.batch_number,
            'location': inventory_item.location,
        })

    context = {
        'inventory': inventory,
        'inventory_item': inventory_item,
        'form': form,
        'title': f'جرد الصنف: {inventory_item.item.name}'
    }
    return render(request, 'inventory/physical_inventory_count_item.html', context)


@login_required
def physical_inventory_complete(request, pk):
    """إكمال الجرد"""
    if request.method == 'POST':
        inventory = get_object_or_404(PhysicalInventory, pk=pk)

        if not inventory.can_be_completed:
            return JsonResponse({'success': False, 'message': 'يجب أن يكون الجرد قيد التنفيذ'})

        with transaction.atomic():
            # حساب الإحصائيات
            items = inventory.items.all()
            total_items = items.count()
            counted_items = items.filter(is_counted=True).count()

            if counted_items == 0:
                return JsonResponse({'success': False, 'message': 'يجب جرد صنف واحد على الأقل'})

            # حساب الفروقات
            discrepancies = 0
            total_value_difference = 0

            for item in items.filter(is_counted=True):
                if item.has_discrepancy:
                    discrepancies += 1
                total_value_difference += item.difference_value

            # تحديث الجرد
            inventory.status = 'COMPLETED'
            inventory.completed_by = request.user
            inventory.completed_date = datetime.now()
            inventory.total_items_counted = counted_items
            inventory.total_discrepancies = discrepancies
            inventory.total_value_difference = total_value_difference
            inventory.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إكمال الجرد {inventory.inventory_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def physical_inventory_approve(request, pk):
    """اعتماد الجرد وتطبيق الفروقات على المخزون"""
    if request.method == 'POST':
        inventory = get_object_or_404(PhysicalInventory, pk=pk)

        if not inventory.can_be_approved:
            return JsonResponse({'success': False, 'message': 'يجب إكمال الجرد أولاً'})

        with transaction.atomic():
            # تطبيق الفروقات على المخزون
            from .models import Stock, StockMovement, StockMovementItem

            # إنشاء حركة مخزون للجرد
            movement = StockMovement.objects.create(
                movement_type='INVENTORY_ADJUSTMENT',
                reference_number=inventory.inventory_number,
                date=inventory.date,
                warehouse=inventory.warehouse,
                notes=f'تسوية جرد فعلي: {inventory.reason}',
                total_amount=inventory.total_value_difference,
                created_by=request.user
            )

            # تطبيق الفروقات
            for item in inventory.items.filter(is_counted=True, difference_quantity__ne=0):
                # إنشاء حركة للصنف
                StockMovementItem.objects.create(
                    movement=movement,
                    item=item.item,
                    quantity=item.difference_quantity,
                    unit_cost=item.unit_cost,
                    total_cost=item.difference_value,
                    expiry_date=item.expiry_date,
                    batch_number=item.batch_number
                )

                # تحديث المخزون
                try:
                    stock = Stock.objects.get(warehouse=inventory.warehouse, item=item.item)
                    stock.quantity = item.counted_quantity
                    stock.last_movement_date = datetime.now()
                    stock.save()
                except Stock.DoesNotExist:
                    # إنشاء مخزون جديد إذا لم يكن موجود
                    if item.counted_quantity > 0:
                        Stock.objects.create(
                            warehouse=inventory.warehouse,
                            item=item.item,
                            quantity=item.counted_quantity,
                            average_cost=item.unit_cost,
                            last_movement_date=datetime.now()
                        )

            # تحديث حالة الجرد
            inventory.status = 'APPROVED'
            inventory.approved_by = request.user
            inventory.approved_date = datetime.now()
            inventory.save()

        return JsonResponse({
            'success': True,
            'message': f'تم اعتماد الجرد {inventory.inventory_number} وتطبيق الفروقات بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def physical_inventory_cancel(request, pk):
    """إلغاء الجرد"""
    if request.method == 'POST':
        inventory = get_object_or_404(PhysicalInventory, pk=pk)

        if not inventory.can_be_cancelled:
            return JsonResponse({'success': False, 'message': 'لا يمكن إلغاء الجرد في هذه الحالة'})

        inventory.status = 'CANCELLED'
        inventory.save()

        return JsonResponse({
            'success': True,
            'message': f'تم إلغاء الجرد {inventory.inventory_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def physical_inventory_delete(request, pk):
    """حذف الجرد"""
    if request.method == 'DELETE':
        inventory = get_object_or_404(PhysicalInventory, pk=pk)

        if inventory.status not in ['DRAFT', 'CANCELLED']:
            return JsonResponse({'success': False, 'message': 'لا يمكن حذف جرد معتمد أو مكتمل'})

        inventory_number = inventory.inventory_number
        inventory.delete()

        return JsonResponse({
            'success': True,
            'message': f'تم حذف الجرد {inventory_number} بنجاح'
        })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def items_search(request):
    """البحث عن الأصناف للـ autocomplete"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'items': []})

    from definitions.models import Item

    items = Item.objects.filter(
        Q(code__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query),
        is_active=True
    ).select_related('unit')[:20]

    items_data = []
    for item in items:
        items_data.append({
            'id': item.id,
            'code': item.code,
            'name': item.name,
            'description': item.description or '',
            'unit': item.unit.name if item.unit else '',
            'cost_price': float(item.cost_price) if item.cost_price else 0,
            'sale_price': float(item.sale_price) if item.sale_price else 0,
        })

    return JsonResponse({'items': items_data})


@login_required
def item_detail(request, pk):
    """تفاصيل الصنف للـ autocomplete"""
    from definitions.models import Item

    try:
        item = Item.objects.select_related('unit').get(pk=pk, is_active=True)
        item_data = {
            'id': item.id,
            'code': item.code,
            'name': item.name,
            'description': item.description or '',
            'unit': item.unit.name if item.unit else '',
            'cost_price': float(item.cost_price) if item.cost_price else 0,
            'sale_price': float(item.sale_price) if item.sale_price else 0,
        }
        return JsonResponse({'item': item_data})
    except Item.DoesNotExist:
        return JsonResponse({'error': 'الصنف غير موجود'}, status=404)


@login_required
def physical_inventory_report(request, pk):
    """تقرير الجرد الفعلي"""
    inventory = get_object_or_404(PhysicalInventory, pk=pk)
    items = inventory.items.all().select_related('item').order_by('item__name')

    # فلترة الأصناف
    filter_type = request.GET.get('filter', 'all')

    if filter_type == 'discrepancies':
        items = items.filter(difference_quantity__ne=0)
    elif filter_type == 'surplus':
        items = items.filter(difference_quantity__gt=0)
    elif filter_type == 'shortage':
        items = items.filter(difference_quantity__lt=0)
    elif filter_type == 'counted':
        items = items.filter(is_counted=True)
    elif filter_type == 'not_counted':
        items = items.filter(is_counted=False)

    context = {
        'inventory': inventory,
        'items': items,
        'filter_type': filter_type,
        'title': f'تقرير الجرد: {inventory.inventory_number}'
    }
    return render(request, 'inventory/physical_inventory_report.html', context)


@login_required
def get_warehouse_items(request, warehouse_id):
    """جلب الأصناف الموجودة في مخزن معين"""
    try:
        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

        # جلب الأصناف التي لها رصيد في المخزن
        from .models import Stock
        stocks = Stock.objects.filter(
            warehouse=warehouse,
            quantity__gt=0
        ).select_related('item', 'item__category', 'item__unit').order_by('item__name')

        items_data = []
        for stock in stocks:
            items_data.append({
                'id': stock.item.id,
                'code': stock.item.code,
                'name': stock.item.name,
                'category': stock.item.category.name if stock.item.category else '',
                'unit': stock.item.unit.name if stock.item.unit else '',
                'current_quantity': float(stock.quantity),
                'average_cost': float(stock.average_cost),
                'total_value': float(stock.quantity * stock.average_cost),
                'last_movement_date': stock.last_movement_date.strftime('%Y-%m-%d') if stock.last_movement_date else '',
                'min_stock_level': float(stock.item.min_stock) if stock.item.min_stock else 0,
                'max_stock_level': float(stock.item.max_stock) if stock.item.max_stock else 0,
                'reorder_point': float(stock.item.min_stock) if stock.item.min_stock else 0,
            })

        return JsonResponse({
            'success': True,
            'warehouse_name': warehouse.name,
            'items_count': len(items_data),
            'items': items_data,
            'total_value': sum(item['total_value'] for item in items_data)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
