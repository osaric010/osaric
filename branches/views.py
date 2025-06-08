from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from .models import Branch, BranchOpeningBalance, GoodsTransfer, CashMovement, BankMovement, CollectionRevenue
from datetime import datetime, timedelta


@login_required
def branches_home(request):
    """لوحة تحكم الفروع"""
    # إحصائيات سريعة
    total_branches = Branch.objects.filter(is_active=True).count()
    active_branches = Branch.objects.filter(is_active=True).count()

    # إحصائيات الحركات الحديثة
    recent_cash_movements = CashMovement.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_bank_movements = BankMovement.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_goods_transfers = GoodsTransfer.objects.filter(is_active=True).order_by('-created_at')[:5]

    context = {
        'title': 'لوحة تحكم المركز الرئيسي والفروع',
        'total_branches': total_branches,
        'active_branches': active_branches,
        'recent_cash_movements': recent_cash_movements,
        'recent_bank_movements': recent_bank_movements,
        'recent_goods_transfers': recent_goods_transfers,
    }
    return render(request, 'branches/home.html', context)


@login_required
def branch_list(request):
    """قائمة الفروع"""
    search = request.GET.get('search', '')
    branches = Branch.objects.all()

    if search:
        branches = branches.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(manager_name__icontains=search)
        )

    branches = branches.order_by('name')

    # Pagination
    paginator = Paginator(branches, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'تعريف الفروع',
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'branches/branch_list.html', context)


@login_required
def branch_add(request):
    """إضافة فرع جديد"""
    if request.method == 'POST':
        # معالجة البيانات المرسلة
        name = request.POST.get('name')
        code = request.POST.get('code')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        manager_name = request.POST.get('manager_name')

        # التحقق من عدم تكرار الكود
        if Branch.objects.filter(code=code).exists():
            messages.error(request, 'كود الفرع موجود مسبقاً')
            return render(request, 'branches/branch_form.html', {
                'title': 'إضافة فرع جديد',
                'form_data': request.POST
            })

        # إنشاء الفرع
        branch = Branch.objects.create(
            name=name,
            code=code,
            address=address,
            phone=phone,
            email=email,
            manager_name=manager_name,
            created_by=request.user
        )

        messages.success(request, 'تم إضافة الفرع بنجاح')
        return redirect('branches:branch_list')

    context = {
        'title': 'إضافة فرع جديد',
    }
    return render(request, 'branches/branch_form.html', context)


@login_required
def branch_edit(request, pk):
    """تعديل فرع"""
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == 'POST':
        # معالجة البيانات المرسلة
        name = request.POST.get('name')
        code = request.POST.get('code')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        manager_name = request.POST.get('manager_name')
        is_active = request.POST.get('is_active') == 'on'

        # التحقق من عدم تكرار الكود
        if Branch.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, 'كود الفرع موجود مسبقاً')
            return render(request, 'branches/branch_form.html', {
                'title': 'تعديل الفرع',
                'branch': branch,
                'form_data': request.POST
            })

        # تحديث الفرع
        branch.name = name
        branch.code = code
        branch.address = address
        branch.phone = phone
        branch.email = email
        branch.manager_name = manager_name
        branch.is_active = is_active
        branch.save()

        messages.success(request, 'تم تحديث الفرع بنجاح')
        return redirect('branches:branch_list')

    context = {
        'title': 'تعديل الفرع',
        'branch': branch,
    }
    return render(request, 'branches/branch_form.html', context)


@login_required
def branch_delete(request, pk):
    """حذف فرع"""
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == 'POST':
        branch.delete()
        messages.success(request, 'تم حذف الفرع بنجاح')
        return redirect('branches:branch_list')

    context = {
        'title': 'حذف الفرع',
        'branch': branch,
    }
    return render(request, 'branches/branch_confirm_delete.html', context)


# القيد الافتتاحي
@login_required
def opening_balance(request):
    """القيد الافتتاحي رصيد أول المدة للفروع"""
    context = {
        'title': 'القيد الافتتاحي رصيد أول المدة للفروع',
    }
    return render(request, 'branches/opening_balance.html', context)


@login_required
def opening_balance_add(request):
    """إضافة قيد افتتاحي"""
    context = {
        'title': 'إضافة قيد افتتاحي',
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'branches/opening_balance_form.html', context)


@login_required
def opening_balance_edit(request, pk):
    """تعديل قيد افتتاحي"""
    context = {
        'title': 'تعديل قيد افتتاحي',
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'branches/opening_balance_form.html', context)


# بضاعة مرحلة للفروع
@login_required
def goods_transfer(request):
    """بضاعة مرحلة للفروع"""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    branch_filter = request.GET.get('branch_id', '')

    transfers = GoodsTransfer.objects.filter(is_active=True)

    if search:
        transfers = transfers.filter(
            Q(transfer_number__icontains=search) |
            Q(branch__name__icontains=search) |
            Q(notes__icontains=search)
        )

    if status_filter:
        transfers = transfers.filter(status=status_filter)

    if branch_filter:
        transfers = transfers.filter(branch_id=branch_filter)

    transfers = transfers.order_by('-transfer_date')

    # Pagination
    paginator = Paginator(transfers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_transfers = transfers.count()
    total_amount = transfers.aggregate(total=Sum('total_amount'))['total'] or 0
    pending_count = transfers.filter(status='PENDING').count()
    received_count = transfers.filter(status='RECEIVED').count()

    context = {
        'title': 'بضاعة مرحلة للفروع',
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'branch_filter': branch_filter,
        'branches': Branch.objects.filter(is_active=True),
        'total_transfers': total_transfers,
        'total_amount': total_amount,
        'pending_count': pending_count,
        'received_count': received_count,
    }
    return render(request, 'branches/goods_transfer.html', context)


@login_required
def goods_transfer_add(request):
    """إضافة تحويل بضاعة"""
    if request.method == 'POST':
        # الحصول على البيانات
        transfer_number = request.POST.get('transfer_number')
        branch_id = request.POST.get('branch')
        transfer_date = request.POST.get('transfer_date')
        total_amount = request.POST.get('total_amount')
        status = request.POST.get('status', 'PENDING')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم التحويل
        if GoodsTransfer.objects.filter(transfer_number=transfer_number).exists():
            messages.error(request, 'رقم التحويل موجود مسبقاً')
            return render(request, 'branches/goods_transfer_form.html', {
                'title': 'إضافة تحويل بضاعة',
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء التحويل
            transfer = GoodsTransfer.objects.create(
                transfer_number=transfer_number,
                branch_id=branch_id,
                transfer_date=transfer_date,
                total_amount=total_amount,
                status=status,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة تحويل البضاعة رقم {transfer_number} بنجاح')
            return redirect('branches:goods_transfer')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ التحويل: {str(e)}')

    context = {
        'title': 'إضافة تحويل بضاعة',
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'branches/goods_transfer_form.html', context)


@login_required
def goods_transfer_edit(request, pk):
    """تعديل تحويل بضاعة"""
    transfer = get_object_or_404(GoodsTransfer, pk=pk)

    if request.method == 'POST':
        # الحصول على البيانات
        transfer_number = request.POST.get('transfer_number')
        branch_id = request.POST.get('branch')
        transfer_date = request.POST.get('transfer_date')
        total_amount = request.POST.get('total_amount')
        status = request.POST.get('status')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم التحويل
        if GoodsTransfer.objects.filter(transfer_number=transfer_number).exclude(pk=pk).exists():
            messages.error(request, 'رقم التحويل موجود مسبقاً')
            return render(request, 'branches/goods_transfer_form.html', {
                'title': 'تعديل تحويل بضاعة',
                'transfer': transfer,
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # تحديث التحويل
            transfer.transfer_number = transfer_number
            transfer.branch_id = branch_id
            transfer.transfer_date = transfer_date
            transfer.total_amount = total_amount
            transfer.status = status
            transfer.notes = notes
            transfer.save()

            messages.success(request, f'تم تحديث تحويل البضاعة رقم {transfer_number} بنجاح')
            return redirect('branches:goods_transfer')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء تحديث التحويل: {str(e)}')

    context = {
        'title': 'تعديل تحويل بضاعة',
        'transfer': transfer,
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'branches/goods_transfer_form.html', context)


@login_required
def goods_transfer_delete(request, pk):
    """حذف تحويل بضاعة"""
    transfer = get_object_or_404(GoodsTransfer, pk=pk)

    if request.method == 'POST':
        transfer_number = transfer.transfer_number
        transfer.delete()
        messages.success(request, f'تم حذف تحويل البضاعة رقم {transfer_number} بنجاح')
        return redirect('branches:goods_transfer')

    context = {
        'title': 'حذف تحويل البضاعة',
        'transfer': transfer,
    }
    return render(request, 'branches/goods_transfer_confirm_delete.html', context)


# النقدية - الخزائن
@login_required
def cash_received(request):
    """نقدية واردة للخزينة من خزائن الفروع"""
    search = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    movements = CashMovement.objects.filter(
        is_active=True,
        movement_type='RECEIVED_FROM_BRANCH'
    )

    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(branch__name__icontains=search) |
            Q(description__icontains=search)
        )

    if branch_filter:
        movements = movements.filter(branch_id=branch_filter)

    if date_from:
        movements = movements.filter(movement_date__gte=date_from)

    if date_to:
        movements = movements.filter(movement_date__lte=date_to)

    movements = movements.order_by('-movement_date')

    # Pagination
    paginator = Paginator(movements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_movements = movements.count()
    total_amount = movements.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'نقدية واردة للخزينة من خزائن الفروع',
        'page_obj': page_obj,
        'search': search,
        'branch_filter': branch_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': Branch.objects.filter(is_active=True),
        'total_movements': total_movements,
        'total_amount': total_amount,
    }
    return render(request, 'branches/cash_received.html', context)


@login_required
def cash_received_add(request):
    """إضافة نقدية واردة"""
    if request.method == 'POST':
        # الحصول على البيانات
        movement_number = request.POST.get('movement_number')
        branch_id = request.POST.get('branch')
        movement_date = request.POST.get('movement_date')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم الحركة
        if CashMovement.objects.filter(movement_number=movement_number).exists():
            messages.error(request, 'رقم الحركة موجود مسبقاً')
            return render(request, 'branches/cash_movement_form.html', {
                'title': 'إضافة نقدية واردة',
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء الحركة النقدية
            movement = CashMovement.objects.create(
                movement_number=movement_number,
                branch_id=branch_id,
                movement_type='RECEIVED_FROM_BRANCH',
                movement_date=movement_date,
                amount=amount,
                description=description,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة النقدية الواردة رقم {movement_number} بنجاح')
            return redirect('branches:cash_received')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الحركة: {str(e)}')

    context = {
        'title': 'إضافة نقدية واردة',
        'branches': Branch.objects.filter(is_active=True),
        'movement_type': 'RECEIVED_FROM_BRANCH',
    }
    return render(request, 'branches/cash_movement_form.html', context)


@login_required
def cash_sent(request):
    """نقدية صادرة من الخزينة إلى خزائن الفروع"""
    search = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    movements = CashMovement.objects.filter(
        is_active=True,
        movement_type='SENT_TO_BRANCH'
    )

    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(branch__name__icontains=search) |
            Q(description__icontains=search)
        )

    if branch_filter:
        movements = movements.filter(branch_id=branch_filter)

    if date_from:
        movements = movements.filter(movement_date__gte=date_from)

    if date_to:
        movements = movements.filter(movement_date__lte=date_to)

    movements = movements.order_by('-movement_date')

    # Pagination
    paginator = Paginator(movements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_movements = movements.count()
    total_amount = movements.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'نقدية صادرة من الخزينة إلى خزائن الفروع',
        'page_obj': page_obj,
        'search': search,
        'branch_filter': branch_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': Branch.objects.filter(is_active=True),
        'total_movements': total_movements,
        'total_amount': total_amount,
    }
    return render(request, 'branches/cash_sent.html', context)


@login_required
def cash_sent_add(request):
    """إضافة نقدية صادرة"""
    if request.method == 'POST':
        # الحصول على البيانات
        movement_number = request.POST.get('movement_number')
        branch_id = request.POST.get('branch')
        movement_date = request.POST.get('movement_date')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم الحركة
        if CashMovement.objects.filter(movement_number=movement_number).exists():
            messages.error(request, 'رقم الحركة موجود مسبقاً')
            return render(request, 'branches/cash_movement_form.html', {
                'title': 'إضافة نقدية صادرة',
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء الحركة النقدية
            movement = CashMovement.objects.create(
                movement_number=movement_number,
                branch_id=branch_id,
                movement_type='SENT_TO_BRANCH',
                movement_date=movement_date,
                amount=amount,
                description=description,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة النقدية الصادرة رقم {movement_number} بنجاح')
            return redirect('branches:cash_sent')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الحركة: {str(e)}')

    context = {
        'title': 'إضافة نقدية صادرة',
        'branches': Branch.objects.filter(is_active=True),
        'movement_type': 'SENT_TO_BRANCH',
    }
    return render(request, 'branches/cash_movement_form.html', context)


# البنوك - خزائن الفروع
@login_required
def bank_deposits_from_branches(request):
    """إيداعات بنكية واردة من خزائن الفروع"""
    search = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    movements = BankMovement.objects.filter(
        is_active=True,
        movement_type='DEPOSIT_FROM_BRANCH_TREASURY'
    )

    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(branch__name__icontains=search) |
            Q(bank_name__icontains=search) |
            Q(description__icontains=search)
        )

    if branch_filter:
        movements = movements.filter(branch_id=branch_filter)

    if date_from:
        movements = movements.filter(movement_date__gte=date_from)

    if date_to:
        movements = movements.filter(movement_date__lte=date_to)

    movements = movements.order_by('-movement_date')

    # Pagination
    paginator = Paginator(movements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_movements = movements.count()
    total_amount = movements.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'إيداعات بنكية واردة من خزائن الفروع',
        'page_obj': page_obj,
        'search': search,
        'branch_filter': branch_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': Branch.objects.filter(is_active=True),
        'total_movements': total_movements,
        'total_amount': total_amount,
    }
    return render(request, 'branches/bank_deposits_from_branches.html', context)


@login_required
def bank_deposits_from_branches_add(request):
    """إضافة إيداع بنكي من خزينة فرع"""
    if request.method == 'POST':
        # الحصول على البيانات
        movement_number = request.POST.get('movement_number')
        branch_id = request.POST.get('branch')
        movement_date = request.POST.get('movement_date')
        amount = request.POST.get('amount')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        description = request.POST.get('description')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم الحركة
        if BankMovement.objects.filter(movement_number=movement_number).exists():
            messages.error(request, 'رقم الحركة موجود مسبقاً')
            return render(request, 'branches/bank_movement_form.html', {
                'title': 'إضافة إيداع بنكي من خزينة فرع',
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء الحركة البنكية
            movement = BankMovement.objects.create(
                movement_number=movement_number,
                branch_id=branch_id,
                movement_type='DEPOSIT_FROM_BRANCH_TREASURY',
                movement_date=movement_date,
                amount=amount,
                bank_name=bank_name,
                account_number=account_number,
                description=description,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة الإيداع البنكي رقم {movement_number} بنجاح')
            return redirect('branches:bank_deposits_from_branches')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الحركة: {str(e)}')

    context = {
        'title': 'إضافة إيداع بنكي من خزينة فرع',
        'branches': Branch.objects.filter(is_active=True),
        'movement_type': 'DEPOSIT_FROM_BRANCH_TREASURY',
    }
    return render(request, 'branches/bank_movement_form.html', context)


@login_required
def bank_withdrawals_to_branches(request):
    """مسحوبات بنكية تم إيداعها في خزائن الفروع"""
    search = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    movements = BankMovement.objects.filter(
        is_active=True,
        movement_type='WITHDRAWAL_TO_BRANCH_TREASURY'
    )

    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(branch__name__icontains=search) |
            Q(bank_name__icontains=search) |
            Q(description__icontains=search)
        )

    if branch_filter:
        movements = movements.filter(branch_id=branch_filter)

    if date_from:
        movements = movements.filter(movement_date__gte=date_from)

    if date_to:
        movements = movements.filter(movement_date__lte=date_to)

    movements = movements.order_by('-movement_date')

    # Pagination
    paginator = Paginator(movements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_movements = movements.count()
    total_amount = movements.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'مسحوبات بنكية تم إيداعها في خزائن الفروع',
        'page_obj': page_obj,
        'search': search,
        'branch_filter': branch_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': Branch.objects.filter(is_active=True),
        'total_movements': total_movements,
        'total_amount': total_amount,
    }
    return render(request, 'branches/bank_withdrawals_to_branches.html', context)


@login_required
def bank_withdrawals_to_branches_add(request):
    """إضافة مسحوب بنكي لخزينة فرع"""
    if request.method == 'POST':
        # الحصول على البيانات
        movement_number = request.POST.get('movement_number')
        branch_id = request.POST.get('branch')
        movement_date = request.POST.get('movement_date')
        amount = request.POST.get('amount')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        description = request.POST.get('description')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم الحركة
        if BankMovement.objects.filter(movement_number=movement_number).exists():
            messages.error(request, 'رقم الحركة موجود مسبقاً')
            return render(request, 'branches/bank_movement_form.html', {
                'title': 'إضافة مسحوب بنكي لخزينة فرع',
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء الحركة البنكية
            movement = BankMovement.objects.create(
                movement_number=movement_number,
                branch_id=branch_id,
                movement_type='WITHDRAWAL_TO_BRANCH_TREASURY',
                movement_date=movement_date,
                amount=amount,
                bank_name=bank_name,
                account_number=account_number,
                description=description,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة المسحوب البنكي رقم {movement_number} بنجاح')
            return redirect('branches:bank_withdrawals_to_branches')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الحركة: {str(e)}')

    context = {
        'title': 'إضافة مسحوب بنكي لخزينة فرع',
        'branches': Branch.objects.filter(is_active=True),
        'movement_type': 'WITHDRAWAL_TO_BRANCH_TREASURY',
    }
    return render(request, 'branches/bank_movement_form.html', context)


# البنوك - بنوك الفروع
@login_required
def bank_deposits_from_branch_banks(request):
    """إيداعات بنكية واردة من بنوك الفروع"""
    search = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    movements = BankMovement.objects.filter(
        is_active=True,
        movement_type='DEPOSIT_FROM_BRANCH_BANK'
    )

    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(branch__name__icontains=search) |
            Q(bank_name__icontains=search) |
            Q(description__icontains=search)
        )

    if branch_filter:
        movements = movements.filter(branch_id=branch_filter)

    if date_from:
        movements = movements.filter(movement_date__gte=date_from)

    if date_to:
        movements = movements.filter(movement_date__lte=date_to)

    movements = movements.order_by('-movement_date')

    # Pagination
    paginator = Paginator(movements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_movements = movements.count()
    total_amount = movements.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'إيداعات بنكية واردة من بنوك الفروع',
        'page_obj': page_obj,
        'search': search,
        'branch_filter': branch_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': Branch.objects.filter(is_active=True),
        'total_movements': total_movements,
        'total_amount': total_amount,
    }
    return render(request, 'branches/bank_deposits_from_branch_banks.html', context)


@login_required
def bank_deposits_from_branch_banks_add(request):
    """إضافة إيداع بنكي من بنك فرع"""
    if request.method == 'POST':
        # الحصول على البيانات
        movement_number = request.POST.get('movement_number')
        branch_id = request.POST.get('branch')
        movement_date = request.POST.get('movement_date')
        amount = request.POST.get('amount')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        description = request.POST.get('description')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم الحركة
        if BankMovement.objects.filter(movement_number=movement_number).exists():
            messages.error(request, 'رقم الحركة موجود مسبقاً')
            return render(request, 'branches/bank_movement_form.html', {
                'title': 'إضافة إيداع بنكي من بنك فرع',
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء الحركة البنكية
            movement = BankMovement.objects.create(
                movement_number=movement_number,
                branch_id=branch_id,
                movement_type='DEPOSIT_FROM_BRANCH_BANK',
                movement_date=movement_date,
                amount=amount,
                bank_name=bank_name,
                account_number=account_number,
                description=description,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة الإيداع البنكي رقم {movement_number} بنجاح')
            return redirect('branches:bank_deposits_from_branch_banks')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الحركة: {str(e)}')

    context = {
        'title': 'إضافة إيداع بنكي من بنك فرع',
        'branches': Branch.objects.filter(is_active=True),
        'movement_type': 'DEPOSIT_FROM_BRANCH_BANK',
    }
    return render(request, 'branches/bank_movement_form.html', context)


@login_required
def bank_withdrawals_to_branch_banks(request):
    """مسحوبات بنكية تم إيداعها في بنوك الفروع"""
    search = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    movements = BankMovement.objects.filter(
        is_active=True,
        movement_type='WITHDRAWAL_TO_BRANCH_BANK'
    )

    if search:
        movements = movements.filter(
            Q(movement_number__icontains=search) |
            Q(branch__name__icontains=search) |
            Q(bank_name__icontains=search) |
            Q(description__icontains=search)
        )

    if branch_filter:
        movements = movements.filter(branch_id=branch_filter)

    if date_from:
        movements = movements.filter(movement_date__gte=date_from)

    if date_to:
        movements = movements.filter(movement_date__lte=date_to)

    movements = movements.order_by('-movement_date')

    # Pagination
    paginator = Paginator(movements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_movements = movements.count()
    total_amount = movements.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'مسحوبات بنكية تم إيداعها في بنوك الفروع',
        'page_obj': page_obj,
        'search': search,
        'branch_filter': branch_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': Branch.objects.filter(is_active=True),
        'total_movements': total_movements,
        'total_amount': total_amount,
    }
    return render(request, 'branches/bank_withdrawals_to_branch_banks.html', context)


@login_required
def bank_withdrawals_to_branch_banks_add(request):
    """إضافة مسحوب بنكي لبنك فرع"""
    if request.method == 'POST':
        # الحصول على البيانات
        movement_number = request.POST.get('movement_number')
        branch_id = request.POST.get('branch')
        movement_date = request.POST.get('movement_date')
        amount = request.POST.get('amount')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        description = request.POST.get('description')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم الحركة
        if BankMovement.objects.filter(movement_number=movement_number).exists():
            messages.error(request, 'رقم الحركة موجود مسبقاً')
            return render(request, 'branches/bank_movement_form.html', {
                'title': 'إضافة مسحوب بنكي لبنك فرع',
                'branches': Branch.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء الحركة البنكية
            movement = BankMovement.objects.create(
                movement_number=movement_number,
                branch_id=branch_id,
                movement_type='WITHDRAWAL_TO_BRANCH_BANK',
                movement_date=movement_date,
                amount=amount,
                bank_name=bank_name,
                account_number=account_number,
                description=description,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة المسحوب البنكي رقم {movement_number} بنجاح')
            return redirect('branches:bank_withdrawals_to_branch_banks')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الحركة: {str(e)}')

    context = {
        'title': 'إضافة مسحوب بنكي لبنك فرع',
        'branches': Branch.objects.filter(is_active=True),
        'movement_type': 'WITHDRAWAL_TO_BRANCH_BANK',
    }
    return render(request, 'branches/bank_movement_form.html', context)


# الإيرادات التحصيلية
@login_required
def collection_revenues(request):
    """إيرادات تحصيلية تخص الفروع"""
    context = {
        'title': 'إيرادات تحصيلية تخص الفروع',
    }
    return render(request, 'branches/collection_revenues.html', context)


@login_required
def collection_revenues_add(request):
    """إضافة إيراد تحصيلي"""
    context = {
        'title': 'إضافة إيراد تحصيلي',
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'branches/collection_revenue_form.html', context)


@login_required
def collection_revenues_edit(request, pk):
    """تعديل إيراد تحصيلي"""
    context = {
        'title': 'تعديل إيراد تحصيلي',
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'branches/collection_revenue_form.html', context)


@login_required
def cash_treasury_demo(request):
    """صفحة توضيحية للنقدية - الخزائن"""
    context = {
        'title': 'النقدية - الخزائن - عرض توضيحي',
    }
    return render(request, 'branches/cash_treasury_demo.html', context)


# المصروفات المحملة على الفروع
@login_required
def branch_expenses(request):
    """عرض المصروفات المحملة على الفروع"""
    search = request.GET.get('search', '')
    branch_filter = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # هنا يمكن إضافة نموذج للمصروفات المحملة
    # expenses = BranchExpense.objects.filter(is_active=True)

    context = {
        'title': 'المصروفات المحملة على الفروع',
        'search': search,
        'branch_filter': branch_filter,
        'date_from': date_from,
        'date_to': date_to,
        'branches': Branch.objects.filter(is_active=True),
        # 'page_obj': page_obj,
        # 'total_expenses': total_expenses,
        # 'total_amount': total_amount,
    }
    return render(request, 'branches/branch_expenses.html', context)


@login_required
def branch_expenses_add(request):
    """إضافة مصروف محمل على فرع"""
    if request.method == 'POST':
        # معالجة البيانات المرسلة
        messages.success(request, 'تم إضافة المصروف المحمل بنجاح')
        return redirect('branches:branch_expenses')

    context = {
        'title': 'إضافة مصروف محمل على فرع',
        'branches': Branch.objects.filter(is_active=True),
    }
    return render(request, 'branches/branch_expense_form.html', context)


@login_required
def branch_expenses_edit(request, pk):
    """تعديل مصروف محمل على فرع"""
    # expense = get_object_or_404(BranchExpense, pk=pk)

    if request.method == 'POST':
        # معالجة البيانات المرسلة
        messages.success(request, 'تم تحديث المصروف المحمل بنجاح')
        return redirect('branches:branch_expenses')

    context = {
        'title': 'تعديل مصروف محمل على فرع',
        'branches': Branch.objects.filter(is_active=True),
        # 'expense': expense,
    }
    return render(request, 'branches/branch_expense_form.html', context)


@login_required
def branch_expenses_delete(request, pk):
    """حذف مصروف محمل على فرع"""
    # expense = get_object_or_404(BranchExpense, pk=pk)

    if request.method == 'POST':
        # expense.delete()
        messages.success(request, 'تم حذف المصروف المحمل بنجاح')
        return redirect('branches:branch_expenses')

    context = {
        'title': 'حذف مصروف محمل على فرع',
        # 'expense': expense,
    }
    return render(request, 'branches/branch_expense_confirm_delete.html', context)


# التقارير المتخصصة
@login_required
def branch_account_statement(request):
    """تقرير كشف حساب فرع"""
    branch_id = request.GET.get('branch_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    selected_branch = None
    if branch_id:
        selected_branch = get_object_or_404(Branch, pk=branch_id)

    # جمع البيانات من مختلف الجداول
    cash_movements = []
    bank_movements = []
    goods_transfers = []
    collection_revenues = []

    if selected_branch:
        # الحركات النقدية
        cash_movements = CashMovement.objects.filter(
            branch=selected_branch,
            is_active=True
        )

        # الحركات البنكية
        bank_movements = BankMovement.objects.filter(
            branch=selected_branch,
            is_active=True
        )

        # تحويلات البضائع
        goods_transfers = GoodsTransfer.objects.filter(
            branch=selected_branch,
            is_active=True
        )

        # الإيرادات التحصيلية
        collection_revenues = CollectionRevenue.objects.filter(
            branch=selected_branch,
            is_active=True
        )

        # تطبيق فلاتر التاريخ
        if date_from:
            cash_movements = cash_movements.filter(movement_date__gte=date_from)
            bank_movements = bank_movements.filter(movement_date__gte=date_from)
            goods_transfers = goods_transfers.filter(transfer_date__gte=date_from)
            collection_revenues = collection_revenues.filter(revenue_date__gte=date_from)

        if date_to:
            cash_movements = cash_movements.filter(movement_date__lte=date_to)
            bank_movements = bank_movements.filter(movement_date__lte=date_to)
            goods_transfers = goods_transfers.filter(transfer_date__lte=date_to)
            collection_revenues = collection_revenues.filter(revenue_date__lte=date_to)

    context = {
        'title': 'تقرير كشف حساب فرع',
        'branches': Branch.objects.filter(is_active=True),
        'selected_branch': selected_branch,
        'branch_id': branch_id,
        'date_from': date_from,
        'date_to': date_to,
        'cash_movements': cash_movements,
        'bank_movements': bank_movements,
        'goods_transfers': goods_transfers,
        'collection_revenues': collection_revenues,
    }
    return render(request, 'branches/reports/branch_account_statement.html', context)


@login_required
def branches_balances_report(request):
    """تقرير أرصدة الفروع"""
    date_filter = request.GET.get('date', '')

    branches = Branch.objects.filter(is_active=True)
    branches_data = []

    for branch in branches:
        # حساب الأرصدة لكل فرع
        cash_received = CashMovement.objects.filter(
            branch=branch,
            movement_type='RECEIVED_FROM_BRANCH',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        cash_sent = CashMovement.objects.filter(
            branch=branch,
            movement_type='SENT_TO_BRANCH',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        bank_deposits = BankMovement.objects.filter(
            branch=branch,
            movement_type='DEPOSIT_FROM_BRANCH',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        bank_withdrawals = BankMovement.objects.filter(
            branch=branch,
            movement_type='WITHDRAWAL_TO_BRANCH',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        goods_value = GoodsTransfer.objects.filter(
            branch=branch,
            is_active=True
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        collection_revenues_total = CollectionRevenue.objects.filter(
            branch=branch,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

        # حساب الرصيد الإجمالي
        total_balance = (cash_received - cash_sent +
                        bank_deposits - bank_withdrawals +
                        goods_value + collection_revenues_total)

        branches_data.append({
            'branch': branch,
            'cash_received': cash_received,
            'cash_sent': cash_sent,
            'cash_balance': cash_received - cash_sent,
            'bank_deposits': bank_deposits,
            'bank_withdrawals': bank_withdrawals,
            'bank_balance': bank_deposits - bank_withdrawals,
            'goods_value': goods_value,
            'collection_revenues': collection_revenues_total,
            'total_balance': total_balance,
        })

    context = {
        'title': 'تقرير أرصدة الفروع',
        'date_filter': date_filter,
        'branches_data': branches_data,
    }
    return render(request, 'branches/reports/branches_balances_report.html', context)


@login_required
def branch_notifications_report(request):
    """تقرير إشعارات العمليات التي تخص الفروع"""
    branch_filter = request.GET.get('branch_id', '')
    operation_type = request.GET.get('operation_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    notifications = []

    # جمع الإشعارات من مختلف العمليات
    if not operation_type or operation_type == 'cash':
        cash_movements = CashMovement.objects.filter(is_active=True)
        if branch_filter:
            cash_movements = cash_movements.filter(branch_id=branch_filter)
        if date_from:
            cash_movements = cash_movements.filter(movement_date__gte=date_from)
        if date_to:
            cash_movements = cash_movements.filter(movement_date__lte=date_to)

        for movement in cash_movements:
            notifications.append({
                'type': 'نقدية',
                'operation': 'واردة' if movement.movement_type == 'RECEIVED_FROM_BRANCH' else 'صادرة',
                'branch': movement.branch.name,
                'amount': movement.amount,
                'date': movement.movement_date,
                'number': movement.movement_number,
                'description': movement.description,
            })

    if not operation_type or operation_type == 'bank':
        bank_movements = BankMovement.objects.filter(is_active=True)
        if branch_filter:
            bank_movements = bank_movements.filter(branch_id=branch_filter)
        if date_from:
            bank_movements = bank_movements.filter(movement_date__gte=date_from)
        if date_to:
            bank_movements = bank_movements.filter(movement_date__lte=date_to)

        for movement in bank_movements:
            notifications.append({
                'type': 'بنكية',
                'operation': 'إيداع' if 'DEPOSIT' in movement.movement_type else 'سحب',
                'branch': movement.branch.name,
                'amount': movement.amount,
                'date': movement.movement_date,
                'number': movement.movement_number,
                'description': movement.description,
            })

    if not operation_type or operation_type == 'goods':
        goods_transfers = GoodsTransfer.objects.filter(is_active=True)
        if branch_filter:
            goods_transfers = goods_transfers.filter(branch_id=branch_filter)
        if date_from:
            goods_transfers = goods_transfers.filter(transfer_date__gte=date_from)
        if date_to:
            goods_transfers = goods_transfers.filter(transfer_date__lte=date_to)

        for transfer in goods_transfers:
            notifications.append({
                'type': 'بضائع',
                'operation': 'تحويل',
                'branch': transfer.branch.name,
                'amount': transfer.total_amount,
                'date': transfer.transfer_date,
                'number': transfer.transfer_number,
                'description': transfer.notes,
            })

    # ترتيب الإشعارات حسب التاريخ
    notifications.sort(key=lambda x: x['date'], reverse=True)

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'تقرير إشعارات العمليات التي تخص الفروع',
        'branches': Branch.objects.filter(is_active=True),
        'branch_filter': branch_filter,
        'operation_type': operation_type,
        'date_from': date_from,
        'date_to': date_to,
        'page_obj': page_obj,
        'total_notifications': len(notifications),
    }
    return render(request, 'branches/reports/branch_notifications_report.html', context)
