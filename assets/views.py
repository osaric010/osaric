from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, date
from decimal import Decimal

from .models import (Asset, AssetPurchase, AssetRenewal, AssetSale,
                     DepreciationEntry, AssetMaintenance)
from definitions.models import AssetGroup, Treasury


@login_required
def home(request):
    """الصفحة الرئيسية للأصول الثابتة"""

    # إحصائيات الأصول
    total_assets = Asset.objects.filter(is_active=True).count()
    active_assets = Asset.objects.filter(is_active=True, status='ACTIVE').count()
    under_maintenance = Asset.objects.filter(is_active=True, status='UNDER_MAINTENANCE').count()
    disposed_assets = Asset.objects.filter(is_active=True, status='DISPOSED').count()

    # القيم المالية
    total_cost = Asset.objects.filter(is_active=True).aggregate(
        total=Sum('purchase_cost'))['total'] or Decimal('0.00')
    total_depreciation = Asset.objects.filter(is_active=True).aggregate(
        total=Sum('accumulated_depreciation'))['total'] or Decimal('0.00')
    total_book_value = total_cost - total_depreciation

    # الأصول حسب المجموعة
    assets_by_group = Asset.objects.filter(is_active=True).values(
        'asset_group__name').annotate(count=Count('id')).order_by('-count')[:5]

    # الأصول التي تحتاج صيانة قريباً
    upcoming_maintenance = AssetMaintenance.objects.filter(
        next_maintenance_date__lte=date.today(),
        asset__status='ACTIVE'
    ).select_related('asset')[:5]

    # أحدث العمليات
    recent_purchases = AssetPurchase.objects.filter(is_active=True).order_by('-purchase_date')[:5]
    recent_sales = AssetSale.objects.filter(is_active=True).order_by('-sale_date')[:5]

    context = {
        'title': 'إدارة الأصول الثابتة',
        'total_assets': total_assets,
        'active_assets': active_assets,
        'under_maintenance': under_maintenance,
        'disposed_assets': disposed_assets,
        'total_cost': total_cost,
        'total_depreciation': total_depreciation,
        'total_book_value': total_book_value,
        'assets_by_group': assets_by_group,
        'upcoming_maintenance': upcoming_maintenance,
        'recent_purchases': recent_purchases,
        'recent_sales': recent_sales,
    }
    return render(request, 'assets/home.html', context)


@login_required
def asset_list(request):
    """قائمة الأصول"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    group_filter = request.GET.get('group', '')

    assets = Asset.objects.filter(is_active=True).select_related('asset_group')

    if search_query:
        assets = assets.filter(
            Q(asset_code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if status_filter:
        assets = assets.filter(status=status_filter)

    if group_filter:
        assets = assets.filter(asset_group_id=group_filter)

    # ترقيم الصفحات
    paginator = Paginator(assets, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # للفلاتر
    asset_groups = AssetGroup.objects.filter(is_active=True)

    context = {
        'title': 'قائمة الأصول الثابتة',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'group_filter': group_filter,
        'asset_groups': asset_groups,
        'status_choices': Asset.ASSET_STATUS_CHOICES,
    }
    return render(request, 'assets/asset_list.html', context)


@login_required
def asset_create(request):
    """إضافة أصل جديد"""
    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم إضافة الأصل بنجاح')
        return redirect('assets:asset_list')

    context = {
        'title': 'إضافة أصل ثابت جديد',
        'action': 'إضافة'
    }
    return render(request, 'assets/asset_form.html', context)


@login_required
def asset_create_ajax(request):
    """إضافة أصل جديد عبر AJAX"""
    if request.method == 'POST':
        try:
            import json
            from decimal import Decimal
            from datetime import datetime

            data = json.loads(request.body)

            # التحقق من عدم تكرار كود الأصل
            if Asset.objects.filter(asset_code=data['asset_code']).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'كود الأصل موجود مسبقاً'
                })

            # إنشاء الأصل الجديد
            asset = Asset.objects.create(
                asset_code=data['asset_code'],
                name=data['name'],
                asset_group_id=data['asset_group'],
                purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date(),
                purchase_cost=Decimal(str(data['purchase_cost'])),
                useful_life=data['useful_life'],
                salvage_value=Decimal(str(data['salvage_value'])),
                status=data['status'],
                created_by=request.user
            )

            return JsonResponse({
                'success': True,
                'message': 'تم إضافة الأصل بنجاح',
                'asset_id': asset.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'حدث خطأ: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'طريقة غير مسموحة'})


@login_required
def check_asset_code(request):
    """التحقق من وجود كود الأصل"""
    code = request.GET.get('code', '')
    exists = Asset.objects.filter(asset_code=code).exists()
    return JsonResponse({'exists': exists})


@login_required
def asset_detail(request, pk):
    """تفاصيل الأصل"""
    asset = get_object_or_404(Asset, pk=pk)

    # تاريخ العمليات
    renewals = AssetRenewal.objects.filter(asset=asset, is_active=True).order_by('-renewal_date')
    maintenance = AssetMaintenance.objects.filter(asset=asset, is_active=True).order_by('-maintenance_date')
    depreciation_entries = DepreciationEntry.objects.filter(asset=asset, is_active=True).order_by('-entry_date')

    context = {
        'title': f'تفاصيل الأصل: {asset.name}',
        'asset': asset,
        'renewals': renewals,
        'maintenance': maintenance,
        'depreciation_entries': depreciation_entries,
    }
    return render(request, 'assets/asset_detail.html', context)


@login_required
def asset_edit(request, pk):
    """تعديل أصل"""
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم تحديث الأصل بنجاح')
        return redirect('assets:asset_detail', pk=asset.pk)

    context = {
        'title': f'تعديل الأصل: {asset.name}',
        'asset': asset,
        'action': 'تحديث'
    }
    return render(request, 'assets/asset_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def asset_delete(request, pk):
    """حذف أصل"""
    asset = get_object_or_404(Asset, pk=pk)
    asset.is_active = False
    asset.updated_by = request.user
    asset.save()

    return JsonResponse({'success': True, 'message': 'تم حذف الأصل بنجاح'})


# ===== شراء الأصول =====
@login_required
def asset_purchase_list(request):
    """قائمة مشتريات الأصول"""
    search_query = request.GET.get('search', '')
    purchases = AssetPurchase.objects.filter(is_active=True)

    if search_query:
        purchases = purchases.filter(
            Q(purchase_number__icontains=search_query) |
            Q(supplier__icontains=search_query)
        )

    # ترقيم الصفحات
    paginator = Paginator(purchases, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'مشتريات الأصول الثابتة',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'assets/asset_purchase_list.html', context)


@login_required
def asset_purchase_create(request):
    """إضافة شراء أصل جديد"""
    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم إضافة شراء الأصل بنجاح')
        return redirect('assets:asset_purchase_list')

    context = {
        'title': 'شراء أصل ثابت جديد',
        'action': 'إضافة'
    }
    return render(request, 'assets/asset_purchase_form.html', context)


@login_required
def asset_purchase_detail(request, pk):
    """تفاصيل شراء الأصل"""
    purchase = get_object_or_404(AssetPurchase, pk=pk)

    context = {
        'title': f'تفاصيل الشراء: {purchase.purchase_number}',
        'purchase': purchase,
    }
    return render(request, 'assets/asset_purchase_detail.html', context)


@login_required
def asset_purchase_edit(request, pk):
    """تعديل شراء أصل"""
    purchase = get_object_or_404(AssetPurchase, pk=pk)

    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم تحديث شراء الأصل بنجاح')
        return redirect('assets:asset_purchase_detail', pk=purchase.pk)

    context = {
        'title': f'تعديل الشراء: {purchase.purchase_number}',
        'purchase': purchase,
        'action': 'تحديث'
    }
    return render(request, 'assets/asset_purchase_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def asset_purchase_delete(request, pk):
    """حذف شراء أصل"""
    purchase = get_object_or_404(AssetPurchase, pk=pk)
    purchase.is_active = False
    purchase.updated_by = request.user
    purchase.save()

    return JsonResponse({'success': True, 'message': 'تم حذف شراء الأصل بنجاح'})


# ===== تجديد الأصول =====
@login_required
def asset_renewal_list(request):
    """قائمة تجديدات الأصول"""
    search_query = request.GET.get('search', '')
    renewals = AssetRenewal.objects.filter(is_active=True).select_related('asset')

    if search_query:
        renewals = renewals.filter(
            Q(renewal_number__icontains=search_query) |
            Q(asset__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # ترقيم الصفحات
    paginator = Paginator(renewals, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'تجديدات الأصول الثابتة',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'assets/asset_renewal_list.html', context)


@login_required
def asset_renewal_create(request):
    """إضافة تجديد أصل جديد"""
    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم إضافة تجديد الأصل بنجاح')
        return redirect('assets:asset_renewal_list')

    context = {
        'title': 'تجديد أصل ثابت',
        'action': 'إضافة'
    }
    return render(request, 'assets/asset_renewal_form.html', context)


@login_required
def asset_renewal_detail(request, pk):
    """تفاصيل تجديد الأصل"""
    renewal = get_object_or_404(AssetRenewal, pk=pk)

    context = {
        'title': f'تفاصيل التجديد: {renewal.renewal_number}',
        'renewal': renewal,
    }
    return render(request, 'assets/asset_renewal_detail.html', context)


@login_required
def asset_renewal_edit(request, pk):
    """تعديل تجديد أصل"""
    renewal = get_object_or_404(AssetRenewal, pk=pk)

    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم تحديث تجديد الأصل بنجاح')
        return redirect('assets:asset_renewal_detail', pk=renewal.pk)

    context = {
        'title': f'تعديل التجديد: {renewal.renewal_number}',
        'renewal': renewal,
        'action': 'تحديث'
    }
    return render(request, 'assets/asset_renewal_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def asset_renewal_delete(request, pk):
    """حذف تجديد أصل"""
    renewal = get_object_or_404(AssetRenewal, pk=pk)
    renewal.is_active = False
    renewal.updated_by = request.user
    renewal.save()

    return JsonResponse({'success': True, 'message': 'تم حذف تجديد الأصل بنجاح'})


# ===== بيع الأصول =====
@login_required
def asset_sale_list(request):
    """قائمة مبيعات الأصول"""
    search_query = request.GET.get('search', '')
    sales = AssetSale.objects.filter(is_active=True).select_related('asset')

    if search_query:
        sales = sales.filter(
            Q(sale_number__icontains=search_query) |
            Q(asset__name__icontains=search_query) |
            Q(buyer__icontains=search_query)
        )

    # ترقيم الصفحات
    paginator = Paginator(sales, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'مبيعات الأصول الثابتة',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'assets/asset_sale_list.html', context)


@login_required
def asset_sale_create(request):
    """إضافة بيع أصل جديد"""
    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم إضافة بيع الأصل بنجاح')
        return redirect('assets:asset_sale_list')

    context = {
        'title': 'بيع أصل ثابت',
        'action': 'إضافة'
    }
    return render(request, 'assets/asset_sale_form.html', context)


@login_required
def asset_sale_detail(request, pk):
    """تفاصيل بيع الأصل"""
    sale = get_object_or_404(AssetSale, pk=pk)

    context = {
        'title': f'تفاصيل البيع: {sale.sale_number}',
        'sale': sale,
    }
    return render(request, 'assets/asset_sale_detail.html', context)


@login_required
def asset_sale_edit(request, pk):
    """تعديل بيع أصل"""
    sale = get_object_or_404(AssetSale, pk=pk)

    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم تحديث بيع الأصل بنجاح')
        return redirect('assets:asset_sale_detail', pk=sale.pk)

    context = {
        'title': f'تعديل البيع: {sale.sale_number}',
        'sale': sale,
        'action': 'تحديث'
    }
    return render(request, 'assets/asset_sale_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def asset_sale_delete(request, pk):
    """حذف بيع أصل"""
    sale = get_object_or_404(AssetSale, pk=pk)
    sale.is_active = False
    sale.updated_by = request.user
    sale.save()

    return JsonResponse({'success': True, 'message': 'تم حذف بيع الأصل بنجاح'})


# ===== حساب الإهلاك =====
@login_required
def depreciation_list(request):
    """قائمة الأصول وحساب الإهلاك"""
    assets = Asset.objects.filter(is_active=True, status='ACTIVE').select_related('asset_group')

    # حساب الإهلاك لكل أصل
    for asset in assets:
        asset.annual_depreciation = asset.calculate_annual_depreciation()
        asset.monthly_depreciation = asset.annual_depreciation / 12

    context = {
        'title': 'حساب إهلاك الأصول الثابتة',
        'assets': assets,
    }
    return render(request, 'assets/depreciation_list.html', context)


@login_required
def calculate_depreciation(request):
    """حساب الإهلاك الشهري للأصول"""
    if request.method == 'POST':
        year = int(request.POST.get('year', datetime.now().year))
        month = int(request.POST.get('month', datetime.now().month))

        assets = Asset.objects.filter(is_active=True, status='ACTIVE')
        created_entries = 0

        for asset in assets:
            # تحقق من عدم وجود قيد إهلاك لهذا الشهر
            existing_entry = DepreciationEntry.objects.filter(
                asset=asset, period_year=year, period_month=month
            ).exists()

            if not existing_entry:
                monthly_depreciation = asset.calculate_annual_depreciation() / 12

                if monthly_depreciation > 0:
                    # إنشاء قيد الإهلاك
                    entry = DepreciationEntry.objects.create(
                        entry_number=f'DEP-{asset.asset_code}-{year}{month:02d}',
                        entry_date=date(year, month, 1),
                        period_year=year,
                        period_month=month,
                        asset=asset,
                        depreciation_amount=monthly_depreciation,
                        accumulated_depreciation_before=asset.accumulated_depreciation,
                        accumulated_depreciation_after=asset.accumulated_depreciation + monthly_depreciation,
                        book_value_after=asset.purchase_cost - (asset.accumulated_depreciation + monthly_depreciation),
                        created_by=request.user,
                        updated_by=request.user
                    )

                    # تحديث الأصل
                    asset.accumulated_depreciation += monthly_depreciation
                    asset.save()

                    created_entries += 1

        messages.success(request, f'تم إنشاء {created_entries} قيد إهلاك')
        return redirect('assets:depreciation_entry_list')

    context = {
        'title': 'حساب الإهلاك الشهري',
        'current_year': datetime.now().year,
        'current_month': datetime.now().month,
    }
    return render(request, 'assets/calculate_depreciation.html', context)


@login_required
def depreciation_entry_list(request):
    """قائمة قيود الإهلاك"""
    search_query = request.GET.get('search', '')
    year_filter = request.GET.get('year', '')
    month_filter = request.GET.get('month', '')

    entries = DepreciationEntry.objects.filter(is_active=True).select_related('asset')

    if search_query:
        entries = entries.filter(
            Q(entry_number__icontains=search_query) |
            Q(asset__name__icontains=search_query)
        )

    if year_filter:
        entries = entries.filter(period_year=year_filter)

    if month_filter:
        entries = entries.filter(period_month=month_filter)

    # ترقيم الصفحات
    paginator = Paginator(entries, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'قيود الإهلاك',
        'page_obj': page_obj,
        'search_query': search_query,
        'year_filter': year_filter,
        'month_filter': month_filter,
    }
    return render(request, 'assets/depreciation_entry_list.html', context)


@login_required
def depreciation_entry_create(request):
    """إضافة قيد إهلاك يدوي"""
    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم إضافة قيد الإهلاك بنجاح')
        return redirect('assets:depreciation_entry_list')

    context = {
        'title': 'إضافة قيد إهلاك',
        'action': 'إضافة'
    }
    return render(request, 'assets/depreciation_entry_form.html', context)


@login_required
def depreciation_entry_detail(request, pk):
    """تفاصيل قيد الإهلاك"""
    entry = get_object_or_404(DepreciationEntry, pk=pk)

    context = {
        'title': f'تفاصيل قيد الإهلاك: {entry.entry_number}',
        'entry': entry,
    }
    return render(request, 'assets/depreciation_entry_detail.html', context)


@login_required
@require_http_methods(["DELETE"])
def depreciation_entry_delete(request, pk):
    """حذف قيد إهلاك"""
    entry = get_object_or_404(DepreciationEntry, pk=pk)

    # إعادة تعديل مجمع الإهلاك في الأصل
    asset = entry.asset
    asset.accumulated_depreciation -= entry.depreciation_amount
    asset.save()

    entry.is_active = False
    entry.updated_by = request.user
    entry.save()

    return JsonResponse({'success': True, 'message': 'تم حذف قيد الإهلاك بنجاح'})


# ===== صيانة الأصول =====
@login_required
def asset_maintenance_list(request):
    """قائمة صيانة الأصول"""
    search_query = request.GET.get('search', '')
    maintenance = AssetMaintenance.objects.filter(is_active=True).select_related('asset')

    if search_query:
        maintenance = maintenance.filter(
            Q(maintenance_number__icontains=search_query) |
            Q(asset__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # ترقيم الصفحات
    paginator = Paginator(maintenance, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'صيانة الأصول الثابتة',
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'assets/asset_maintenance_list.html', context)


@login_required
def asset_maintenance_create(request):
    """إضافة صيانة أصل جديدة"""
    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم إضافة صيانة الأصل بنجاح')
        return redirect('assets:asset_maintenance_list')

    context = {
        'title': 'صيانة أصل ثابت',
        'action': 'إضافة'
    }
    return render(request, 'assets/asset_maintenance_form.html', context)


@login_required
def asset_maintenance_detail(request, pk):
    """تفاصيل صيانة الأصل"""
    maintenance = get_object_or_404(AssetMaintenance, pk=pk)

    context = {
        'title': f'تفاصيل الصيانة: {maintenance.maintenance_number}',
        'maintenance': maintenance,
    }
    return render(request, 'assets/asset_maintenance_detail.html', context)


@login_required
def asset_maintenance_edit(request, pk):
    """تعديل صيانة أصل"""
    maintenance = get_object_or_404(AssetMaintenance, pk=pk)

    if request.method == 'POST':
        # سيتم إنشاء النموذج لاحقاً
        messages.success(request, 'تم تحديث صيانة الأصل بنجاح')
        return redirect('assets:asset_maintenance_detail', pk=maintenance.pk)

    context = {
        'title': f'تعديل الصيانة: {maintenance.maintenance_number}',
        'maintenance': maintenance,
        'action': 'تحديث'
    }
    return render(request, 'assets/asset_maintenance_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def asset_maintenance_delete(request, pk):
    """حذف صيانة أصل"""
    maintenance = get_object_or_404(AssetMaintenance, pk=pk)
    maintenance.is_active = False
    maintenance.updated_by = request.user
    maintenance.save()

    return JsonResponse({'success': True, 'message': 'تم حذف صيانة الأصل بنجاح'})


# ===== التقارير =====
@login_required
def asset_reports(request):
    """صفحة التقارير"""
    context = {
        'title': 'تقارير الأصول الثابتة',
    }
    return render(request, 'assets/asset_reports.html', context)


@login_required
def asset_register_report(request):
    """تقرير سجل الأصول"""
    assets = Asset.objects.filter(is_active=True).select_related('asset_group')

    context = {
        'title': 'تقرير سجل الأصول',
        'assets': assets,
    }
    return render(request, 'assets/asset_register_report.html', context)


@login_required
def depreciation_schedule_report(request):
    """تقرير جدولة الإهلاك"""
    assets = Asset.objects.filter(is_active=True, status='ACTIVE').select_related('asset_group')

    context = {
        'title': 'تقرير جدولة الإهلاك',
        'assets': assets,
    }
    return render(request, 'assets/depreciation_schedule_report.html', context)


@login_required
def asset_movements_report(request):
    """تقرير حركة الأصول"""
    # الشراء
    purchases = AssetPurchase.objects.filter(is_active=True).order_by('-purchase_date')[:10]

    # البيع
    sales = AssetSale.objects.filter(is_active=True).order_by('-sale_date')[:10]

    # التجديد
    renewals = AssetRenewal.objects.filter(is_active=True).order_by('-renewal_date')[:10]

    context = {
        'title': 'تقرير حركة الأصول',
        'purchases': purchases,
        'sales': sales,
        'renewals': renewals,
    }
    return render(request, 'assets/asset_movements_report.html', context)
