from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date, datetime
from .models import (TreasuryTransaction, Receipt, Payment, Expense, Revenue,
                     ExpenseType, RevenueType, PaymentNote, ReceiptNote,
                     CustodyReceiptOut, CustodyReceiptIn, TreasuryTransfer)
from .forms import (TreasuryTransactionForm, ReceiptForm, PaymentForm, ExpenseForm,
                    RevenueForm, ExpenseTypeForm, RevenueTypeForm, PaymentNoteForm,
                    ReceiptNoteForm, CustodyReceiptOutForm, CustodyReceiptInForm,
                    TreasuryTransferForm)
from definitions.models import Treasury


@login_required
def treasury_home(request):
    """الصفحة الرئيسية للخزينة"""
    # إحصائيات سريعة
    today = date.today()

    # إجمالي الأرصدة
    total_balance = Treasury.objects.filter(is_active=True).aggregate(
        total=Sum('balance'))['total'] or 0

    # معاملات اليوم
    today_transactions = TreasuryTransaction.objects.filter(
        date=today, is_active=True).count()

    # إيصالات القبض اليوم
    today_receipts = Receipt.objects.filter(
        date=today, is_active=True).aggregate(
        total=Sum('amount'))['total'] or 0

    # إيصالات الدفع اليوم
    today_payments = Payment.objects.filter(
        date=today, is_active=True).aggregate(
        total=Sum('amount'))['total'] or 0

    # المصروفات اليوم
    today_expenses = Expense.objects.filter(
        date=today, is_active=True).aggregate(
        total=Sum('amount'))['total'] or 0

    # الإيرادات اليوم
    today_revenues = Revenue.objects.filter(
        date=today, is_active=True).aggregate(
        total=Sum('amount'))['total'] or 0

    # أوراق الدفع المعلقة
    pending_payment_notes = PaymentNote.objects.filter(
        status='PENDING', is_active=True).count()

    # أوراق القبض المعلقة
    pending_receipt_notes = ReceiptNote.objects.filter(
        status='PENDING', is_active=True).count()

    # إيصالات الأمانة النشطة
    active_custody_out = CustodyReceiptOut.objects.filter(
        status='ACTIVE', is_active=True).count()

    active_custody_in = CustodyReceiptIn.objects.filter(
        status='ACTIVE', is_active=True).count()

    # آخر المعاملات
    recent_transactions = TreasuryTransaction.objects.filter(
        is_active=True).select_related('treasury')[:10]

    context = {
        'title': 'الخزينة',
        'total_balance': total_balance,
        'today_transactions': today_transactions,
        'today_receipts': today_receipts,
        'today_payments': today_payments,
        'today_expenses': today_expenses,
        'today_revenues': today_revenues,
        'pending_payment_notes': pending_payment_notes,
        'pending_receipt_notes': pending_receipt_notes,
        'active_custody_out': active_custody_out,
        'active_custody_in': active_custody_in,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'treasury/home.html', context)


# ===== التحصيل النقدي =====
@login_required
def receipt_list(request):
    """قائمة التحصيل النقدي"""
    search_query = request.GET.get('search', '')
    receipts = Receipt.objects.filter(is_active=True).select_related(
        'treasury', 'customer')

    if search_query:
        receipts = receipts.filter(
            Q(receipt_number__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    receipts = receipts.order_by('-date', '-id')
    paginator = Paginator(receipts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'التحصيل النقدي',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/receipt_list.html', context)


@login_required
def receipt_create(request):
    """إضافة إيصال قبض جديد"""
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.created_by = request.user
            receipt.save()

            # إنشاء معاملة خزينة
            TreasuryTransaction.objects.create(
                transaction_number=f'TR-RC-{receipt.receipt_number}',
                date=receipt.date,
                treasury=receipt.treasury,
                transaction_type='RECEIPT',
                amount=receipt.amount,
                description=f'قبض من العميل: {receipt.customer.name}',
                customer=receipt.customer,
                created_by=request.user
            )

            messages.success(request, 'تم إضافة إيصال القبض بنجاح')
            return redirect('treasury:receipt_list')
    else:
        form = ReceiptForm()

    context = {
        'title': 'إضافة إيصال قبض',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/receipt_form.html', context)


@login_required
def receipt_edit(request, pk):
    """تعديل إيصال قبض"""
    receipt = get_object_or_404(Receipt, pk=pk)

    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.updated_by = request.user
            receipt.save()

            messages.success(request, 'تم تعديل إيصال القبض بنجاح')
            return redirect('treasury:receipt_list')
    else:
        form = ReceiptForm(instance=receipt)

    context = {
        'title': 'تعديل إيصال قبض',
        'form': form,
        'receipt': receipt,
        'action': 'تعديل'
    }
    return render(request, 'treasury/receipt_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def receipt_delete(request, pk):
    """حذف إيصال قبض"""
    receipt = get_object_or_404(Receipt, pk=pk)
    receipt.is_active = False
    receipt.updated_by = request.user
    receipt.save()

    return JsonResponse({'success': True, 'message': 'تم حذف إيصال القبض بنجاح'})


# ===== إيصالات الدفع =====
@login_required
def payment_list(request):
    """قائمة إيصالات الدفع"""
    search_query = request.GET.get('search', '')
    payments = Payment.objects.filter(is_active=True).select_related(
        'treasury', 'supplier')

    if search_query:
        payments = payments.filter(
            Q(payment_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    payments = payments.order_by('-date', '-id')
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'إيصالات الدفع',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/payment_list.html', context)


@login_required
def payment_create(request):
    """إضافة إيصال دفع جديد"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()

            # إنشاء معاملة خزينة
            TreasuryTransaction.objects.create(
                transaction_number=f'TR-PY-{payment.payment_number}',
                date=payment.date,
                treasury=payment.treasury,
                transaction_type='PAYMENT',
                amount=payment.amount,
                description=f'دفع للمورد: {payment.supplier.name}',
                supplier=payment.supplier,
                created_by=request.user
            )

            messages.success(request, 'تم إضافة إيصال الدفع بنجاح')
            return redirect('treasury:payment_list')
    else:
        form = PaymentForm()

    context = {
        'title': 'إضافة إيصال دفع',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/payment_form.html', context)


@login_required
def payment_edit(request, pk):
    """تعديل إيصال دفع"""
    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.updated_by = request.user
            payment.save()

            messages.success(request, 'تم تعديل إيصال الدفع بنجاح')
            return redirect('treasury:payment_list')
    else:
        form = PaymentForm(instance=payment)

    context = {
        'title': 'تعديل إيصال دفع',
        'form': form,
        'payment': payment,
        'action': 'تعديل'
    }
    return render(request, 'treasury/payment_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def payment_delete(request, pk):
    """حذف إيصال دفع"""
    payment = get_object_or_404(Payment, pk=pk)
    payment.is_active = False
    payment.updated_by = request.user
    payment.save()

    return JsonResponse({'success': True, 'message': 'تم حذف إيصال الدفع بنجاح'})


# ===== المصروفات =====
@login_required
def expense_list(request):
    """قائمة المصروفات"""
    search_query = request.GET.get('search', '')
    expenses = Expense.objects.filter(is_active=True).select_related(
        'treasury', 'expense_type')

    if search_query:
        expenses = expenses.filter(
            Q(expense_number__icontains=search_query) |
            Q(expense_type__name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(beneficiary__icontains=search_query)
        )

    expenses = expenses.order_by('-date', '-id')
    paginator = Paginator(expenses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'المصروفات',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/expense_list.html', context)


@login_required
def expense_create(request):
    """إضافة مصروف جديد"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()

            # إنشاء معاملة خزينة
            TreasuryTransaction.objects.create(
                transaction_number=f'TR-EX-{expense.expense_number}',
                date=expense.date,
                treasury=expense.treasury,
                transaction_type='EXPENSE',
                amount=expense.amount,
                description=f'مصروف: {expense.expense_type.name}',
                created_by=request.user
            )

            messages.success(request, 'تم إضافة المصروف بنجاح')
            return redirect('treasury:expense_list')
    else:
        form = ExpenseForm()

    context = {
        'title': 'إضافة مصروف',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/expense_form.html', context)


@login_required
def expense_edit(request, pk):
    """تعديل مصروف"""
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.updated_by = request.user
            expense.save()

            messages.success(request, 'تم تعديل المصروف بنجاح')
            return redirect('treasury:expense_list')
    else:
        form = ExpenseForm(instance=expense)

    context = {
        'title': 'تعديل مصروف',
        'form': form,
        'expense': expense,
        'action': 'تعديل'
    }
    return render(request, 'treasury/expense_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def expense_delete(request, pk):
    """حذف مصروف"""
    expense = get_object_or_404(Expense, pk=pk)
    expense.is_active = False
    expense.updated_by = request.user
    expense.save()

    return JsonResponse({'success': True, 'message': 'تم حذف المصروف بنجاح'})


# ===== الإيرادات =====
@login_required
def revenue_list(request):
    """قائمة الإيرادات"""
    search_query = request.GET.get('search', '')
    revenues = Revenue.objects.filter(is_active=True).select_related(
        'treasury', 'revenue_type')

    if search_query:
        revenues = revenues.filter(
            Q(revenue_number__icontains=search_query) |
            Q(revenue_type__name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(source__icontains=search_query)
        )

    revenues = revenues.order_by('-date', '-id')
    paginator = Paginator(revenues, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'الإيرادات',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/revenue_list.html', context)


@login_required
def revenue_create(request):
    """إضافة إيراد جديد"""
    if request.method == 'POST':
        form = RevenueForm(request.POST)
        if form.is_valid():
            revenue = form.save(commit=False)
            revenue.created_by = request.user
            revenue.save()

            # إنشاء معاملة خزينة
            TreasuryTransaction.objects.create(
                transaction_number=f'TR-RV-{revenue.revenue_number}',
                date=revenue.date,
                treasury=revenue.treasury,
                transaction_type='REVENUE',
                amount=revenue.amount,
                description=f'إيراد: {revenue.revenue_type.name}',
                created_by=request.user
            )

            messages.success(request, 'تم إضافة الإيراد بنجاح')
            return redirect('treasury:revenue_list')
    else:
        form = RevenueForm()

    context = {
        'title': 'إضافة إيراد',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/revenue_form.html', context)


@login_required
def revenue_edit(request, pk):
    """تعديل إيراد"""
    revenue = get_object_or_404(Revenue, pk=pk)

    if request.method == 'POST':
        form = RevenueForm(request.POST, instance=revenue)
        if form.is_valid():
            revenue = form.save(commit=False)
            revenue.updated_by = request.user
            revenue.save()

            messages.success(request, 'تم تعديل الإيراد بنجاح')
            return redirect('treasury:revenue_list')
    else:
        form = RevenueForm(instance=revenue)

    context = {
        'title': 'تعديل إيراد',
        'form': form,
        'revenue': revenue,
        'action': 'تعديل'
    }
    return render(request, 'treasury/revenue_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def revenue_delete(request, pk):
    """حذف إيراد"""
    revenue = get_object_or_404(Revenue, pk=pk)
    revenue.is_active = False
    revenue.updated_by = request.user
    revenue.save()

    return JsonResponse({'success': True, 'message': 'تم حذف الإيراد بنجاح'})


# ===== أوراق الدفع =====
@login_required
def payment_note_list(request):
    """قائمة أوراق الدفع"""
    search_query = request.GET.get('search', '')
    payment_notes = PaymentNote.objects.filter(is_active=True).select_related(
        'treasury', 'supplier')

    if search_query:
        payment_notes = payment_notes.filter(
            Q(note_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    payment_notes = payment_notes.order_by('-date', '-id')
    paginator = Paginator(payment_notes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'أوراق الدفع',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/payment_note_list.html', context)


@login_required
def payment_note_create(request):
    """إضافة ورقة دفع جديدة"""
    if request.method == 'POST':
        form = PaymentNoteForm(request.POST)
        if form.is_valid():
            payment_note = form.save(commit=False)
            payment_note.created_by = request.user
            payment_note.save()

            messages.success(request, 'تم إضافة ورقة الدفع بنجاح')
            return redirect('treasury:payment_note_list')
    else:
        form = PaymentNoteForm()

    context = {
        'title': 'إضافة ورقة دفع',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/payment_note_form.html', context)


@login_required
def payment_note_edit(request, pk):
    """تعديل ورقة دفع"""
    payment_note = get_object_or_404(PaymentNote, pk=pk)

    if request.method == 'POST':
        form = PaymentNoteForm(request.POST, instance=payment_note)
        if form.is_valid():
            payment_note = form.save(commit=False)
            payment_note.updated_by = request.user
            payment_note.save()

            messages.success(request, 'تم تعديل ورقة الدفع بنجاح')
            return redirect('treasury:payment_note_list')
    else:
        form = PaymentNoteForm(instance=payment_note)

    context = {
        'title': 'تعديل ورقة دفع',
        'form': form,
        'payment_note': payment_note,
        'action': 'تعديل'
    }
    return render(request, 'treasury/payment_note_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def payment_note_delete(request, pk):
    """حذف ورقة دفع"""
    payment_note = get_object_or_404(PaymentNote, pk=pk)
    payment_note.is_active = False
    payment_note.updated_by = request.user
    payment_note.save()

    return JsonResponse({'success': True, 'message': 'تم حذف ورقة الدفع بنجاح'})


@login_required
@require_http_methods(["POST"])
def payment_note_pay(request, pk):
    """دفع ورقة دفع"""
    payment_note = get_object_or_404(PaymentNote, pk=pk)

    if payment_note.status != 'PENDING':
        return JsonResponse({'success': False, 'message': 'ورقة الدفع غير معلقة'})

    payment_note.status = 'PAID'
    payment_note.payment_date = date.today()
    payment_note.updated_by = request.user
    payment_note.save()

    # إنشاء معاملة خزينة
    TreasuryTransaction.objects.create(
        transaction_number=f'TR-PN-{payment_note.note_number}',
        date=payment_note.payment_date,
        treasury=payment_note.treasury,
        transaction_type='PAYMENT',
        amount=payment_note.amount,
        description=f'دفع ورقة دفع: {payment_note.note_number}',
        supplier=payment_note.supplier,
        created_by=request.user
    )

    return JsonResponse({'success': True, 'message': 'تم دفع ورقة الدفع بنجاح'})


# ===== أوراق القبض =====
@login_required
def receipt_note_list(request):
    """قائمة أوراق القبض"""
    search_query = request.GET.get('search', '')
    receipt_notes = ReceiptNote.objects.filter(is_active=True).select_related(
        'treasury', 'customer')

    if search_query:
        receipt_notes = receipt_notes.filter(
            Q(note_number__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    receipt_notes = receipt_notes.order_by('-date', '-id')
    paginator = Paginator(receipt_notes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'أوراق القبض',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/receipt_note_list.html', context)


@login_required
def receipt_note_create(request):
    """إضافة ورقة قبض جديدة"""
    if request.method == 'POST':
        form = ReceiptNoteForm(request.POST)
        if form.is_valid():
            receipt_note = form.save(commit=False)
            receipt_note.created_by = request.user
            receipt_note.save()

            messages.success(request, 'تم إضافة ورقة القبض بنجاح')
            return redirect('treasury:receipt_note_list')
    else:
        form = ReceiptNoteForm()

    context = {
        'title': 'إضافة ورقة قبض',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/receipt_note_form.html', context)


@login_required
def receipt_note_edit(request, pk):
    """تعديل ورقة قبض"""
    receipt_note = get_object_or_404(ReceiptNote, pk=pk)

    if request.method == 'POST':
        form = ReceiptNoteForm(request.POST, instance=receipt_note)
        if form.is_valid():
            receipt_note = form.save(commit=False)
            receipt_note.updated_by = request.user
            receipt_note.save()

            messages.success(request, 'تم تعديل ورقة القبض بنجاح')
            return redirect('treasury:receipt_note_list')
    else:
        form = ReceiptNoteForm(instance=receipt_note)

    context = {
        'title': 'تعديل ورقة قبض',
        'form': form,
        'receipt_note': receipt_note,
        'action': 'تعديل'
    }
    return render(request, 'treasury/receipt_note_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def receipt_note_delete(request, pk):
    """حذف ورقة قبض"""
    receipt_note = get_object_or_404(ReceiptNote, pk=pk)
    receipt_note.is_active = False
    receipt_note.updated_by = request.user
    receipt_note.save()

    return JsonResponse({'success': True, 'message': 'تم حذف ورقة القبض بنجاح'})


@login_required
@require_http_methods(["POST"])
def receipt_note_collect(request, pk):
    """تحصيل ورقة قبض"""
    receipt_note = get_object_or_404(ReceiptNote, pk=pk)

    if receipt_note.status != 'PENDING':
        return JsonResponse({'success': False, 'message': 'ورقة القبض غير معلقة'})

    receipt_note.status = 'COLLECTED'
    receipt_note.collection_date = date.today()
    receipt_note.updated_by = request.user
    receipt_note.save()

    # إنشاء معاملة خزينة
    TreasuryTransaction.objects.create(
        transaction_number=f'TR-RN-{receipt_note.note_number}',
        date=receipt_note.collection_date,
        treasury=receipt_note.treasury,
        transaction_type='RECEIPT',
        amount=receipt_note.amount,
        description=f'تحصيل ورقة قبض: {receipt_note.note_number}',
        customer=receipt_note.customer,
        created_by=request.user
    )

    return JsonResponse({'success': True, 'message': 'تم تحصيل ورقة القبض بنجاح'})


# ===== إيصالات الأمانة الصادرة =====
@login_required
def custody_out_list(request):
    """قائمة إيصالات الأمانة الصادرة"""
    search_query = request.GET.get('search', '')
    custody_outs = CustodyReceiptOut.objects.filter(is_active=True).select_related('treasury')

    if search_query:
        custody_outs = custody_outs.filter(
            Q(receipt_number__icontains=search_query) |
            Q(custodian__icontains=search_query) |
            Q(purpose__icontains=search_query)
        )

    custody_outs = custody_outs.order_by('-date', '-id')
    paginator = Paginator(custody_outs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'إيصالات الأمانة الصادرة',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/custody_out_list.html', context)


@login_required
def custody_out_create(request):
    """إضافة إيصال أمانة صادر جديد"""
    if request.method == 'POST':
        form = CustodyReceiptOutForm(request.POST)
        if form.is_valid():
            custody_out = form.save(commit=False)
            custody_out.created_by = request.user
            custody_out.save()

            messages.success(request, 'تم إضافة إيصال الأمانة الصادر بنجاح')
            return redirect('treasury:custody_out_list')
    else:
        form = CustodyReceiptOutForm()

    context = {
        'title': 'إضافة إيصال أمانة صادر',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/custody_out_form.html', context)


@login_required
def custody_out_edit(request, pk):
    """تعديل إيصال أمانة صادر"""
    custody_out = get_object_or_404(CustodyReceiptOut, pk=pk)

    if request.method == 'POST':
        form = CustodyReceiptOutForm(request.POST, instance=custody_out)
        if form.is_valid():
            custody_out = form.save(commit=False)
            custody_out.updated_by = request.user
            custody_out.save()

            messages.success(request, 'تم تعديل إيصال الأمانة الصادر بنجاح')
            return redirect('treasury:custody_out_list')
    else:
        form = CustodyReceiptOutForm(instance=custody_out)

    context = {
        'title': 'تعديل إيصال أمانة صادر',
        'form': form,
        'custody_out': custody_out,
        'action': 'تعديل'
    }
    return render(request, 'treasury/custody_out_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def custody_out_delete(request, pk):
    """حذف إيصال أمانة صادر"""
    custody_out = get_object_or_404(CustodyReceiptOut, pk=pk)
    custody_out.is_active = False
    custody_out.updated_by = request.user
    custody_out.save()

    return JsonResponse({'success': True, 'message': 'تم حذف إيصال الأمانة الصادر بنجاح'})


@login_required
@require_http_methods(["POST"])
def custody_out_return(request, pk):
    """إرجاع أمانة صادرة"""
    custody_out = get_object_or_404(CustodyReceiptOut, pk=pk)

    if custody_out.status != 'ACTIVE':
        return JsonResponse({'success': False, 'message': 'الأمانة غير نشطة'})

    custody_out.status = 'RETURNED'
    custody_out.return_date = date.today()
    custody_out.updated_by = request.user
    custody_out.save()

    return JsonResponse({'success': True, 'message': 'تم إرجاع الأمانة بنجاح'})


# ===== إيصالات الأمانة الواردة =====
@login_required
def custody_in_list(request):
    """قائمة إيصالات الأمانة الواردة"""
    search_query = request.GET.get('search', '')
    custody_ins = CustodyReceiptIn.objects.filter(is_active=True).select_related('treasury')

    if search_query:
        custody_ins = custody_ins.filter(
            Q(receipt_number__icontains=search_query) |
            Q(depositor__icontains=search_query) |
            Q(purpose__icontains=search_query)
        )

    custody_ins = custody_ins.order_by('-date', '-id')
    paginator = Paginator(custody_ins, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'إيصالات الأمانة الواردة',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/custody_in_list.html', context)


@login_required
def custody_in_create(request):
    """إضافة إيصال أمانة وارد جديد"""
    if request.method == 'POST':
        form = CustodyReceiptInForm(request.POST)
        if form.is_valid():
            custody_in = form.save(commit=False)
            custody_in.created_by = request.user
            custody_in.save()

            messages.success(request, 'تم إضافة إيصال الأمانة الوارد بنجاح')
            return redirect('treasury:custody_in_list')
    else:
        form = CustodyReceiptInForm()

    context = {
        'title': 'إضافة إيصال أمانة وارد',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/custody_in_form.html', context)


@login_required
def custody_in_edit(request, pk):
    """تعديل إيصال أمانة وارد"""
    custody_in = get_object_or_404(CustodyReceiptIn, pk=pk)

    if request.method == 'POST':
        form = CustodyReceiptInForm(request.POST, instance=custody_in)
        if form.is_valid():
            custody_in = form.save(commit=False)
            custody_in.updated_by = request.user
            custody_in.save()

            messages.success(request, 'تم تعديل إيصال الأمانة الوارد بنجاح')
            return redirect('treasury:custody_in_list')
    else:
        form = CustodyReceiptInForm(instance=custody_in)

    context = {
        'title': 'تعديل إيصال أمانة وارد',
        'form': form,
        'custody_in': custody_in,
        'action': 'تعديل'
    }
    return render(request, 'treasury/custody_in_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def custody_in_delete(request, pk):
    """حذف إيصال أمانة وارد"""
    custody_in = get_object_or_404(CustodyReceiptIn, pk=pk)
    custody_in.is_active = False
    custody_in.updated_by = request.user
    custody_in.save()

    return JsonResponse({'success': True, 'message': 'تم حذف إيصال الأمانة الوارد بنجاح'})


@login_required
@require_http_methods(["POST"])
def custody_in_return(request, pk):
    """إرجاع أمانة واردة"""
    custody_in = get_object_or_404(CustodyReceiptIn, pk=pk)

    if custody_in.status != 'ACTIVE':
        return JsonResponse({'success': False, 'message': 'الأمانة غير نشطة'})

    custody_in.status = 'RETURNED'
    custody_in.return_date = date.today()
    custody_in.updated_by = request.user
    custody_in.save()

    return JsonResponse({'success': True, 'message': 'تم إرجاع الأمانة بنجاح'})


# ===== تحويل بين الخزائن =====
@login_required
def transfer_list(request):
    """قائمة تحويلات بين الخزائن"""
    search_query = request.GET.get('search', '')
    transfers = TreasuryTransfer.objects.filter(is_active=True).select_related(
        'from_treasury', 'to_treasury')

    if search_query:
        transfers = transfers.filter(
            Q(transfer_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    transfers = transfers.order_by('-date', '-id')
    paginator = Paginator(transfers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'تحويل بين الخزائن',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/transfer_list.html', context)


@login_required
def transfer_create(request):
    """إضافة تحويل جديد بين الخزائن"""
    if request.method == 'POST':
        form = TreasuryTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.created_by = request.user
            transfer.save()

            messages.success(request, 'تم إضافة التحويل بنجاح')
            return redirect('treasury:transfer_list')
    else:
        form = TreasuryTransferForm()

    context = {
        'title': 'إضافة تحويل بين خزائن',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/transfer_form.html', context)


@login_required
def transfer_edit(request, pk):
    """تعديل تحويل بين خزائن"""
    transfer = get_object_or_404(TreasuryTransfer, pk=pk)

    if request.method == 'POST':
        form = TreasuryTransferForm(request.POST, instance=transfer)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.updated_by = request.user
            transfer.save()

            messages.success(request, 'تم تعديل التحويل بنجاح')
            return redirect('treasury:transfer_list')
    else:
        form = TreasuryTransferForm(instance=transfer)

    context = {
        'title': 'تعديل تحويل بين خزائن',
        'form': form,
        'transfer': transfer,
        'action': 'تعديل'
    }
    return render(request, 'treasury/transfer_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def transfer_delete(request, pk):
    """حذف تحويل بين خزائن"""
    transfer = get_object_or_404(TreasuryTransfer, pk=pk)
    transfer.is_active = False
    transfer.updated_by = request.user
    transfer.save()

    return JsonResponse({'success': True, 'message': 'تم حذف التحويل بنجاح'})


@login_required
@require_http_methods(["POST"])
def transfer_complete(request, pk):
    """إكمال تحويل بين خزائن"""
    transfer = get_object_or_404(TreasuryTransfer, pk=pk)

    if transfer.status != 'PENDING':
        return JsonResponse({'success': False, 'message': 'التحويل غير معلق'})

    transfer.status = 'COMPLETED'
    transfer.completion_date = date.today()
    transfer.updated_by = request.user
    transfer.save()

    # إنشاء معاملات خزينة
    # معاملة خروج من الخزينة المرسلة
    TreasuryTransaction.objects.create(
        transaction_number=f'TR-TO-{transfer.transfer_number}',
        date=transfer.completion_date,
        treasury=transfer.from_treasury,
        transaction_type='TRANSFER_OUT',
        amount=transfer.amount,
        description=f'تحويل إلى: {transfer.to_treasury.name}',
        to_treasury=transfer.to_treasury,
        created_by=request.user
    )

    # معاملة دخول للخزينة المستقبلة
    TreasuryTransaction.objects.create(
        transaction_number=f'TR-TI-{transfer.transfer_number}',
        date=transfer.completion_date,
        treasury=transfer.to_treasury,
        transaction_type='TRANSFER_IN',
        amount=transfer.amount,
        description=f'تحويل من: {transfer.from_treasury.name}',
        created_by=request.user
    )

    return JsonResponse({'success': True, 'message': 'تم إكمال التحويل بنجاح'})


# ===== أنواع المصروفات والإيرادات =====
@login_required
def expense_type_list(request):
    """قائمة أنواع المصروفات"""
    search_query = request.GET.get('search', '')
    expense_types = ExpenseType.objects.filter(is_active=True)

    if search_query:
        expense_types = expense_types.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    expense_types = expense_types.order_by('name')
    paginator = Paginator(expense_types, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'أنواع المصروفات',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/expense_type_list.html', context)


@login_required
def expense_type_create(request):
    """إضافة نوع مصروف جديد"""
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST)
        if form.is_valid():
            expense_type = form.save(commit=False)
            expense_type.created_by = request.user
            expense_type.save()

            messages.success(request, 'تم إضافة نوع المصروف بنجاح')
            return redirect('treasury:expense_type_list')
    else:
        form = ExpenseTypeForm()

    context = {
        'title': 'إضافة نوع مصروف',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/expense_type_form.html', context)


@login_required
def expense_type_edit(request, pk):
    """تعديل نوع مصروف"""
    expense_type = get_object_or_404(ExpenseType, pk=pk)

    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST, instance=expense_type)
        if form.is_valid():
            expense_type = form.save(commit=False)
            expense_type.updated_by = request.user
            expense_type.save()

            messages.success(request, 'تم تعديل نوع المصروف بنجاح')
            return redirect('treasury:expense_type_list')
    else:
        form = ExpenseTypeForm(instance=expense_type)

    context = {
        'title': 'تعديل نوع مصروف',
        'form': form,
        'expense_type': expense_type,
        'action': 'تعديل'
    }
    return render(request, 'treasury/expense_type_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def expense_type_delete(request, pk):
    """حذف نوع مصروف"""
    expense_type = get_object_or_404(ExpenseType, pk=pk)
    expense_type.is_active = False
    expense_type.updated_by = request.user
    expense_type.save()

    return JsonResponse({'success': True, 'message': 'تم حذف نوع المصروف بنجاح'})


@login_required
def revenue_type_list(request):
    """قائمة أنواع الإيرادات"""
    search_query = request.GET.get('search', '')
    revenue_types = RevenueType.objects.filter(is_active=True)

    if search_query:
        revenue_types = revenue_types.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    revenue_types = revenue_types.order_by('name')
    paginator = Paginator(revenue_types, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'أنواع الإيرادات',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'treasury/revenue_type_list.html', context)


@login_required
def revenue_type_create(request):
    """إضافة نوع إيراد جديد"""
    if request.method == 'POST':
        form = RevenueTypeForm(request.POST)
        if form.is_valid():
            revenue_type = form.save(commit=False)
            revenue_type.created_by = request.user
            revenue_type.save()

            messages.success(request, 'تم إضافة نوع الإيراد بنجاح')
            return redirect('treasury:revenue_type_list')
    else:
        form = RevenueTypeForm()

    context = {
        'title': 'إضافة نوع إيراد',
        'form': form,
        'action': 'إضافة'
    }
    return render(request, 'treasury/revenue_type_form.html', context)


@login_required
def revenue_type_edit(request, pk):
    """تعديل نوع إيراد"""
    revenue_type = get_object_or_404(RevenueType, pk=pk)

    if request.method == 'POST':
        form = RevenueTypeForm(request.POST, instance=revenue_type)
        if form.is_valid():
            revenue_type = form.save(commit=False)
            revenue_type.updated_by = request.user
            revenue_type.save()

            messages.success(request, 'تم تعديل نوع الإيراد بنجاح')
            return redirect('treasury:revenue_type_list')
    else:
        form = RevenueTypeForm(instance=revenue_type)

    context = {
        'title': 'تعديل نوع إيراد',
        'form': form,
        'revenue_type': revenue_type,
        'action': 'تعديل'
    }
    return render(request, 'treasury/revenue_type_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def revenue_type_delete(request, pk):
    """حذف نوع إيراد"""
    revenue_type = get_object_or_404(RevenueType, pk=pk)
    revenue_type.is_active = False
    revenue_type.updated_by = request.user
    revenue_type.save()

    return JsonResponse({'success': True, 'message': 'تم حذف نوع الإيراد بنجاح'})


# ===== التقارير =====
@login_required
def treasury_reports(request):
    """صفحة التقارير"""
    context = {
        'title': 'تقارير الخزينة',
    }
    return render(request, 'treasury/reports.html', context)


@login_required
def transaction_report(request):
    """تقرير المعاملات"""
    context = {
        'title': 'تقرير المعاملات',
    }
    return render(request, 'treasury/transaction_report.html', context)


@login_required
def balance_report(request):
    """تقرير الأرصدة"""
    context = {
        'title': 'تقرير الأرصدة',
    }
    return render(request, 'treasury/balance_report.html', context)
