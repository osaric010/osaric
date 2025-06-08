from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db import transaction
from .models import (
    BalanceTransfer, AccountMerge, JournalEntry, JournalEntryLine,
    OpeningBalance, ProfitCenter, ProfitDistribution, ProfitDistributionLine,
    AccountingPeriod, Account
)
from definitions.models import Person
from datetime import datetime, timedelta


# لوحة تحكم الحسابات العامة
@login_required
def accounting_dashboard(request):
    """لوحة تحكم الحسابات العامة"""

    # إحصائيات سريعة
    total_balance_transfers = BalanceTransfer.objects.filter(is_active=True).count()
    total_journal_entries = JournalEntry.objects.filter(is_active=True).count()
    total_opening_balances = OpeningBalance.objects.filter(is_active=True).count()
    total_profit_centers = ProfitCenter.objects.filter(is_active=True).count()

    # آخر العمليات
    recent_balance_transfers = BalanceTransfer.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_journal_entries = JournalEntry.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_opening_balances = OpeningBalance.objects.filter(is_active=True).order_by('-created_at')[:5]

    # الفترة المحاسبية الحالية
    current_period = AccountingPeriod.objects.filter(is_current=True).first()

    # إحصائيات مالية
    total_debit = JournalEntry.objects.filter(is_active=True).aggregate(
        total=Sum('total_debit'))['total'] or 0
    total_credit = JournalEntry.objects.filter(is_active=True).aggregate(
        total=Sum('total_credit'))['total'] or 0

    # القيود غير المتوازنة
    unbalanced_entries = JournalEntry.objects.filter(
        is_active=True, is_balanced=False).count()

    # القيود غير المرحلة
    unposted_entries = JournalEntry.objects.filter(
        is_active=True, is_posted=False).count()

    context = {
        'title': 'لوحة تحكم الحسابات العامة',
        'total_balance_transfers': total_balance_transfers,
        'total_journal_entries': total_journal_entries,
        'total_opening_balances': total_opening_balances,
        'total_profit_centers': total_profit_centers,
        'recent_balance_transfers': recent_balance_transfers,
        'recent_journal_entries': recent_journal_entries,
        'recent_opening_balances': recent_opening_balances,
        'current_period': current_period,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'unbalanced_entries': unbalanced_entries,
        'unposted_entries': unposted_entries,
    }
    return render(request, 'accounting/dashboard.html', context)


# تحويل رصيد بين الأشخاص
@login_required
def balance_transfer(request):
    """عرض تحويلات الأرصدة بين الأشخاص"""
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    transfers = BalanceTransfer.objects.filter(is_active=True)

    if search:
        transfers = transfers.filter(
            Q(transfer_number__icontains=search) |
            Q(from_person__name__icontains=search) |
            Q(to_person__name__icontains=search) |
            Q(description__icontains=search)
        )

    if date_from:
        transfers = transfers.filter(transfer_date__gte=date_from)

    if date_to:
        transfers = transfers.filter(transfer_date__lte=date_to)

    transfers = transfers.order_by('-transfer_date')

    # Pagination
    paginator = Paginator(transfers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_transfers = transfers.count()
    total_amount = transfers.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'تحويل رصيد بين الأشخاص',
        'page_obj': page_obj,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'total_transfers': total_transfers,
        'total_amount': total_amount,
    }
    return render(request, 'accounting/balance_transfer.html', context)


@login_required
def balance_transfer_add(request):
    """إضافة تحويل رصيد جديد"""
    if request.method == 'POST':
        # معالجة البيانات المرسلة
        transfer_number = request.POST.get('transfer_number')
        transfer_date = request.POST.get('transfer_date')
        from_person_id = request.POST.get('from_person')
        to_person_id = request.POST.get('to_person')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        notes = request.POST.get('notes')

        # التحقق من عدم تكرار رقم التحويل
        if BalanceTransfer.objects.filter(transfer_number=transfer_number).exists():
            messages.error(request, 'رقم التحويل موجود مسبقاً')
            return render(request, 'accounting/balance_transfer_form.html', {
                'title': 'إضافة تحويل رصيد',
                'persons': Person.objects.filter(is_active=True),
                'form_data': request.POST
            })

        try:
            # إنشاء التحويل
            transfer = BalanceTransfer.objects.create(
                transfer_number=transfer_number,
                transfer_date=transfer_date,
                from_person_id=from_person_id,
                to_person_id=to_person_id,
                amount=amount,
                description=description,
                notes=notes,
                created_by=request.user
            )

            messages.success(request, f'تم إضافة تحويل الرصيد رقم {transfer_number} بنجاح')
            return redirect('accounting:balance_transfer')

        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ التحويل: {str(e)}')

    context = {
        'title': 'إضافة تحويل رصيد',
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/balance_transfer_form.html', context)


@login_required
def balance_transfer_edit(request, pk):
    """تعديل تحويل رصيد"""
    transfer = get_object_or_404(BalanceTransfer, pk=pk)

    if request.method == 'POST':
        # معالجة البيانات المرسلة
        messages.success(request, 'تم تحديث تحويل الرصيد بنجاح')
        return redirect('accounting:balance_transfer')

    context = {
        'title': 'تعديل تحويل رصيد',
        'transfer': transfer,
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/balance_transfer_form.html', context)


@login_required
def balance_transfer_delete(request, pk):
    """حذف تحويل رصيد"""
    transfer = get_object_or_404(BalanceTransfer, pk=pk)

    if request.method == 'POST':
        transfer.delete()
        messages.success(request, 'تم حذف تحويل الرصيد بنجاح')
        return redirect('accounting:balance_transfer')

    context = {
        'title': 'حذف تحويل رصيد',
        'transfer': transfer,
    }
    return render(request, 'accounting/balance_transfer_confirm_delete.html', context)


# دمج الحسابات الفرعية
@login_required
def merge_accounts(request):
    """عرض دمج الحسابات الفرعية"""
    context = {
        'title': 'دمج الحسابات الفرعية للأشخاص',
    }
    return render(request, 'accounting/merge_accounts.html', context)


@login_required
def merge_accounts_add(request):
    """إضافة دمج حسابات جديد"""
    context = {
        'title': 'دمج الحسابات الفرعية للأشخاص',
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/merge_accounts_form.html', context)


@login_required
def merge_accounts_edit(request, pk):
    """تعديل دمج حسابات"""
    context = {
        'title': 'تعديل دمج الحسابات',
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/merge_accounts_form.html', context)


@login_required
def merge_accounts_delete(request, pk):
    """حذف دمج حسابات"""
    context = {
        'title': 'حذف دمج الحسابات',
    }
    return render(request, 'accounting/merge_accounts_confirm_delete.html', context)


# القيود المحاسبية
@login_required
def journal_entries(request):
    """عرض القيود المحاسبية"""
    context = {
        'title': 'القيود المحاسبية',
    }
    return render(request, 'accounting/journal_entries.html', context)


@login_required
def journal_entry_add(request):
    """إضافة قيد محاسبي"""
    context = {
        'title': 'إضافة قيد محاسبي',
        'accounts': Account.objects.filter(is_active=True),
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/journal_entry_form.html', context)


@login_required
def journal_entry_edit(request, pk):
    """تعديل قيد محاسبي"""
    context = {
        'title': 'تعديل قيد محاسبي',
        'accounts': Account.objects.filter(is_active=True),
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/journal_entry_form.html', context)


@login_required
def journal_entry_delete(request, pk):
    """حذف قيد محاسبي"""
    context = {
        'title': 'حذف قيد محاسبي',
    }
    return render(request, 'accounting/journal_entry_confirm_delete.html', context)


@login_required
def journal_entry_post(request, pk):
    """ترحيل قيد محاسبي"""
    entry = get_object_or_404(JournalEntry, pk=pk)

    if request.method == 'POST':
        entry.is_posted = True
        entry.save()
        messages.success(request, f'تم ترحيل القيد {entry.entry_number} بنجاح')
        return redirect('accounting:journal_entries')

    context = {
        'title': 'ترحيل قيد محاسبي',
        'entry': entry,
    }
    return render(request, 'accounting/journal_entry_post.html', context)


# القيد الافتتاحي
@login_required
def opening_balance(request):
    """عرض القيد الافتتاحي"""
    context = {
        'title': 'القيد الافتتاحي',
    }
    return render(request, 'accounting/opening_balance.html', context)


@login_required
def opening_balance_setup(request):
    """إعداد القيد الافتتاحي"""
    context = {
        'title': 'إعداد القيد الافتتاحي',
        'balance_types': OpeningBalance.BALANCE_TYPES,
        'person_types': OpeningBalance.PERSON_TYPES,
        'accounts': Account.objects.filter(is_active=True),
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/opening_balance_setup.html', context)


@login_required
def opening_balance_add(request):
    """إضافة قيد افتتاحي"""
    context = {
        'title': 'إضافة قيد افتتاحي',
        'balance_types': OpeningBalance.BALANCE_TYPES,
        'person_types': OpeningBalance.PERSON_TYPES,
        'accounts': Account.objects.filter(is_active=True),
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/opening_balance_form.html', context)


@login_required
def opening_balance_edit(request, pk):
    """تعديل قيد افتتاحي"""
    context = {
        'title': 'تعديل قيد افتتاحي',
        'balance_types': OpeningBalance.BALANCE_TYPES,
        'person_types': OpeningBalance.PERSON_TYPES,
        'accounts': Account.objects.filter(is_active=True),
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/opening_balance_form.html', context)


@login_required
def opening_balance_delete(request, pk):
    """حذف قيد افتتاحي"""
    context = {
        'title': 'حذف قيد افتتاحي',
    }
    return render(request, 'accounting/opening_balance_confirm_delete.html', context)


# الحساب الختامي
@login_required
def profit_centers(request):
    """مراكز الربحية"""
    context = {
        'title': 'مراكز الربحية',
    }
    return render(request, 'accounting/profit_centers.html', context)


@login_required
def profit_center_add(request):
    """إضافة مركز ربحية"""
    context = {
        'title': 'إضافة مركز ربحية',
    }
    return render(request, 'accounting/profit_center_form.html', context)


@login_required
def profit_center_edit(request, pk):
    """تعديل مركز ربحية"""
    context = {
        'title': 'تعديل مركز ربحية',
    }
    return render(request, 'accounting/profit_center_form.html', context)


@login_required
def profit_center_delete(request, pk):
    """حذف مركز ربحية"""
    context = {
        'title': 'حذف مركز ربحية',
    }
    return render(request, 'accounting/profit_center_confirm_delete.html', context)


@login_required
def income_statement(request):
    """قائمة الدخل"""
    context = {
        'title': 'قائمة الدخل',
    }
    return render(request, 'accounting/income_statement.html', context)


@login_required
def balance_sheet(request):
    """المركز المالي"""
    context = {
        'title': 'المركز المالي',
    }
    return render(request, 'accounting/balance_sheet.html', context)


@login_required
def profit_distribution(request):
    """توزيع الأرباح"""
    context = {
        'title': 'توزيع الأرباح',
    }
    return render(request, 'accounting/profit_distribution.html', context)


@login_required
def profit_distribution_add(request):
    """إضافة توزيع أرباح"""
    context = {
        'title': 'إضافة توزيع أرباح',
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/profit_distribution_form.html', context)


@login_required
def profit_distribution_edit(request, pk):
    """تعديل توزيع أرباح"""
    context = {
        'title': 'تعديل توزيع أرباح',
        'persons': Person.objects.filter(is_active=True),
    }
    return render(request, 'accounting/profit_distribution_form.html', context)


@login_required
def profit_distribution_delete(request, pk):
    """حذف توزيع أرباح"""
    context = {
        'title': 'حذف توزيع أرباح',
    }
    return render(request, 'accounting/profit_distribution_confirm_delete.html', context)


@login_required
def period_closure(request):
    """إنهاء فترة الحسابات"""
    current_period = AccountingPeriod.objects.filter(is_current=True).first()

    context = {
        'title': 'إنهاء فترة الحسابات الحالية وفتح فترة جديدة',
        'current_period': current_period,
    }
    return render(request, 'accounting/period_closure.html', context)


@login_required
def period_closure_close(request):
    """إغلاق الفترة الحالية"""
    if request.method == 'POST':
        current_period = AccountingPeriod.objects.filter(is_current=True).first()
        if current_period:
            current_period.is_closed = True
            current_period.closed_date = datetime.now()
            current_period.closed_by = request.user
            current_period.save()
            messages.success(request, f'تم إغلاق فترة الحسابات {current_period.period_name} بنجاح')
        else:
            messages.error(request, 'لا توجد فترة حسابات حالية لإغلاقها')

        return redirect('accounting:period_closure')

    return redirect('accounting:period_closure')


@login_required
def period_closure_open_new(request):
    """فتح فترة حسابات جديدة"""
    if request.method == 'POST':
        period_name = request.POST.get('period_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            new_period = AccountingPeriod.objects.create(
                period_name=period_name,
                start_date=start_date,
                end_date=end_date,
                is_current=True,
                created_by=request.user
            )
            messages.success(request, f'تم فتح فترة حسابات جديدة: {period_name}')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء فتح الفترة الجديدة: {str(e)}')

        return redirect('accounting:period_closure')

    context = {
        'title': 'فتح فترة حسابات جديدة',
    }
    return render(request, 'accounting/period_closure_open_new.html', context)


# AJAX Views للبحث عن الأصناف
@login_required
def items_search(request):
    """البحث عن الأصناف للـ autocomplete"""
    try:
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
            try:
                items_data.append({
                    'id': item.id,
                    'code': item.code or '',
                    'name': item.name or '',
                    'description': item.description or '',
                    'unit': item.unit.name if item.unit else '',
                    'cost_price': float(item.cost_price) if item.cost_price else 0,
                    'sale_price': float(item.selling_price) if item.selling_price else 0,
                })
            except Exception as e:
                # تجاهل الأصناف التي بها مشاكل وأكمل
                continue

        return JsonResponse({'items': items_data})

    except Exception as e:
        return JsonResponse({'error': f'خطأ في البحث: {str(e)}'}, status=500)


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
            'sale_price': float(item.selling_price) if item.selling_price else 0,
        }
        return JsonResponse({'item': item_data})
    except Item.DoesNotExist:
        return JsonResponse({'error': 'الصنف غير موجود'}, status=404)
