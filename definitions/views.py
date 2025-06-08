from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import (
    Currency, Warehouse, ItemCategory, Unit, Item, Bank, Treasury,
    WarehouseZone, WarehouseLocation, ItemLocation, AssetGroup, Person,
    ExpenseCategory, ExpenseItem, RevenueCategory, RevenueItem,
    ProductionStage, FinishedProduct, ProfitCenter, Printer, CompanySettings
)
from .forms import (
    CurrencyForm, WarehouseForm, ItemCategoryForm, UnitForm,
    ItemForm, BankForm, TreasuryForm, WarehouseZoneForm,
    WarehouseLocationForm, ItemLocationForm, AssetGroupForm, PersonForm,
    ExpenseCategoryForm, ExpenseItemForm, RevenueCategoryForm, RevenueItemForm,
    ProductionStageForm, FinishedProductForm, ProfitCenterForm, PrinterForm
)
from core.currency_utils import get_default_currency, format_currency


@login_required
def definitions_home(request):
    """الصفحة الرئيسية للتعريفات"""
    context = {
        'currencies_count': Currency.objects.filter(is_active=True).count(),
        'warehouses_count': Warehouse.objects.filter(is_active=True).count(),
        'categories_count': ItemCategory.objects.filter(is_active=True).count(),
        'units_count': Unit.objects.filter(is_active=True).count(),
        'items_count': Item.objects.filter(is_active=True).count(),
        'banks_count': Bank.objects.filter(is_active=True).count(),
        'treasuries_count': Treasury.objects.filter(is_active=True).count(),
        'zones_count': WarehouseZone.objects.filter(is_active=True).count(),
        'locations_count': WarehouseLocation.objects.filter(is_active=True).count(),
        'item_locations_count': ItemLocation.objects.filter(is_active=True).count(),
        'asset_groups_count': AssetGroup.objects.filter(is_active=True).count(),
        'persons_count': Person.objects.filter(is_active=True).count(),
        'customers_count': Person.objects.filter(is_active=True, is_active_customer=True).count(),
        'suppliers_count': Person.objects.filter(is_active=True, is_active_supplier=True).count(),
        'expense_categories_count': ExpenseCategory.objects.filter(is_active=True).count(),
        'expense_items_count': ExpenseItem.objects.filter(is_active=True).count(),
        'revenue_categories_count': RevenueCategory.objects.filter(is_active=True).count(),
        'revenue_items_count': RevenueItem.objects.filter(is_active=True).count(),
        'production_stages_count': ProductionStage.objects.filter(is_active=True).count(),
        'finished_products_count': FinishedProduct.objects.filter(is_active=True).count(),
        'profit_centers_count': ProfitCenter.objects.filter(is_active=True).count(),
        'printers_count': Printer.objects.filter(is_active=True).count(),
    }
    return render(request, 'definitions/home.html', context)


# Currency Views
@login_required
def currency_list(request):
    """قائمة العملات"""
    search_query = request.GET.get('search', '')
    currencies = Currency.objects.filter(is_active=True)

    if search_query:
        currencies = currencies.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    currencies = currencies.order_by('name')
    paginator = Paginator(currencies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'العملات'
    }
    return render(request, 'definitions/currency_list.html', context)


@login_required
def currency_create(request):
    """إضافة عملة جديدة"""
    if request.method == 'POST':
        form = CurrencyForm(request.POST)
        if form.is_valid():
            currency = form.save(commit=False)
            currency.created_by = request.user
            currency.save()
            messages.success(request, 'تم إضافة العملة بنجاح')
            return redirect('definitions:currency_list')
    else:
        form = CurrencyForm()

    context = {
        'form': form,
        'title': 'إضافة عملة جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/currency_form.html', context)


@login_required
def currency_edit(request, pk):
    """تعديل عملة"""
    currency = get_object_or_404(Currency, pk=pk)

    if request.method == 'POST':
        form = CurrencyForm(request.POST, instance=currency)
        if form.is_valid():
            currency = form.save(commit=False)
            currency.updated_by = request.user
            currency.save()
            messages.success(request, 'تم تحديث العملة بنجاح')
            return redirect('definitions:currency_list')
    else:
        form = CurrencyForm(instance=currency)

    context = {
        'form': form,
        'currency': currency,
        'title': f'تعديل العملة: {currency.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/currency_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def currency_delete(request, pk):
    """حذف عملة"""
    currency = get_object_or_404(Currency, pk=pk)
    currency.is_active = False
    currency.updated_by = request.user
    currency.save()
    return JsonResponse({'success': True, 'message': 'تم حذف العملة بنجاح'})


# Warehouse Views
@login_required
def warehouse_list(request):
    """قائمة المخازن"""
    search_query = request.GET.get('search', '')
    warehouses = Warehouse.objects.filter(is_active=True)

    if search_query:
        warehouses = warehouses.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    warehouses = warehouses.order_by('name')
    paginator = Paginator(warehouses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'المخازن'
    }
    return render(request, 'definitions/warehouse_list.html', context)


@login_required
def warehouse_create(request):
    """إضافة مخزن جديد"""
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.created_by = request.user
            warehouse.save()
            messages.success(request, 'تم إضافة المخزن بنجاح')
            return redirect('definitions:warehouse_list')
    else:
        form = WarehouseForm()

    context = {
        'form': form,
        'title': 'إضافة مخزن جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/warehouse_form.html', context)


@login_required
def warehouse_edit(request, pk):
    """تعديل مخزن"""
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.updated_by = request.user
            warehouse.save()
            messages.success(request, 'تم تحديث المخزن بنجاح')
            return redirect('definitions:warehouse_list')
    else:
        form = WarehouseForm(instance=warehouse)

    context = {
        'form': form,
        'warehouse': warehouse,
        'title': f'تعديل المخزن: {warehouse.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/warehouse_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def warehouse_delete(request, pk):
    """حذف مخزن"""
    warehouse = get_object_or_404(Warehouse, pk=pk)
    warehouse.is_active = False
    warehouse.updated_by = request.user
    warehouse.save()
    return JsonResponse({'success': True, 'message': 'تم حذف المخزن بنجاح'})


# Category Views
@login_required
def category_list(request):
    """قائمة فئات الأصناف"""
    search_query = request.GET.get('search', '')
    categories = ItemCategory.objects.filter(is_active=True)

    if search_query:
        categories = categories.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    categories = categories.order_by('name')
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'فئات الأصناف'
    }
    return render(request, 'definitions/category_list.html', context)


@login_required
def category_create(request):
    """إضافة فئة جديدة"""
    if request.method == 'POST':
        form = ItemCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, 'تم إضافة الفئة بنجاح')
            return redirect('definitions:category_list')
    else:
        form = ItemCategoryForm()

    context = {
        'form': form,
        'title': 'إضافة فئة جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/category_form.html', context)


@login_required
def category_edit(request, pk):
    """تعديل فئة"""
    category = get_object_or_404(ItemCategory, pk=pk)

    if request.method == 'POST':
        form = ItemCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.updated_by = request.user
            category.save()
            messages.success(request, 'تم تحديث الفئة بنجاح')
            return redirect('definitions:category_list')
    else:
        form = ItemCategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'title': f'تعديل الفئة: {category.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/category_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def category_delete(request, pk):
    """حذف فئة"""
    category = get_object_or_404(ItemCategory, pk=pk)
    category.is_active = False
    category.updated_by = request.user
    category.save()
    return JsonResponse({'success': True, 'message': 'تم حذف الفئة بنجاح'})


# Unit Views
@login_required
def unit_list(request):
    """قائمة وحدات القياس"""
    search_query = request.GET.get('search', '')
    units = Unit.objects.filter(is_active=True)

    if search_query:
        units = units.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(symbol__icontains=search_query)
        )

    units = units.order_by('name')
    paginator = Paginator(units, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'وحدات القياس'
    }
    return render(request, 'definitions/unit_list.html', context)


@login_required
def unit_create(request):
    """إضافة وحدة قياس جديدة"""
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.created_by = request.user
            unit.save()
            messages.success(request, 'تم إضافة وحدة القياس بنجاح')
            return redirect('definitions:unit_list')
    else:
        form = UnitForm()

    context = {
        'form': form,
        'title': 'إضافة وحدة قياس جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/unit_form.html', context)


@login_required
def unit_edit(request, pk):
    """تعديل وحدة قياس"""
    unit = get_object_or_404(Unit, pk=pk)

    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.updated_by = request.user
            unit.save()
            messages.success(request, 'تم تحديث وحدة القياس بنجاح')
            return redirect('definitions:unit_list')
    else:
        form = UnitForm(instance=unit)

    context = {
        'form': form,
        'unit': unit,
        'title': f'تعديل وحدة القياس: {unit.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/unit_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def unit_delete(request, pk):
    """حذف وحدة قياس"""
    unit = get_object_or_404(Unit, pk=pk)
    unit.is_active = False
    unit.updated_by = request.user
    unit.save()
    return JsonResponse({'success': True, 'message': 'تم حذف وحدة القياس بنجاح'})


# Item Views
@login_required
def item_list(request):
    """قائمة الأصناف"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    items = Item.objects.filter(is_active=True).select_related('category', 'unit')

    if search_query:
        items = items.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )

    if category_filter:
        items = items.filter(category_id=category_filter)

    items = items.order_by('name')
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = ItemCategory.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
        'title': 'الأصناف'
    }
    return render(request, 'definitions/item_list.html', context)


@login_required
def item_create(request):
    """إضافة صنف جديد"""
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            messages.success(request, 'تم إضافة الصنف بنجاح')
            return redirect('definitions:item_list')
    else:
        form = ItemForm()

    context = {
        'form': form,
        'title': 'إضافة صنف جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/item_form.html', context)


@login_required
def item_detail(request, pk):
    """تفاصيل الصنف"""
    item = get_object_or_404(Item, pk=pk)
    context = {
        'item': item,
        'title': f'تفاصيل الصنف: {item.name}'
    }
    return render(request, 'definitions/item_detail.html', context)


@login_required
def item_edit(request, pk):
    """تعديل صنف"""
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.updated_by = request.user
            item.save()
            messages.success(request, 'تم تحديث الصنف بنجاح')
            return redirect('definitions:item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)

    context = {
        'form': form,
        'item': item,
        'title': f'تعديل الصنف: {item.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/item_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def item_delete(request, pk):
    """حذف صنف"""
    item = get_object_or_404(Item, pk=pk)
    item.is_active = False
    item.updated_by = request.user
    item.save()
    return JsonResponse({'success': True, 'message': 'تم حذف الصنف بنجاح'})


# Bank Views
@login_required
def bank_list(request):
    """قائمة البنوك"""
    search_query = request.GET.get('search', '')
    banks = Bank.objects.filter(is_active=True).select_related('currency')

    if search_query:
        banks = banks.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(account_number__icontains=search_query)
        )

    banks = banks.order_by('name')
    paginator = Paginator(banks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'البنوك'
    }
    return render(request, 'definitions/bank_list.html', context)


@login_required
def bank_create(request):
    """إضافة بنك جديد"""
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.created_by = request.user
            bank.save()
            messages.success(request, 'تم إضافة البنك بنجاح')
            return redirect('definitions:bank_list')
    else:
        form = BankForm()

    context = {
        'form': form,
        'title': 'إضافة بنك جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/bank_form.html', context)


@login_required
def bank_edit(request, pk):
    """تعديل بنك"""
    bank = get_object_or_404(Bank, pk=pk)

    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.updated_by = request.user
            bank.save()
            messages.success(request, 'تم تحديث البنك بنجاح')
            return redirect('definitions:bank_list')
    else:
        form = BankForm(instance=bank)

    context = {
        'form': form,
        'bank': bank,
        'title': f'تعديل البنك: {bank.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/bank_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def bank_delete(request, pk):
    """حذف بنك"""
    bank = get_object_or_404(Bank, pk=pk)
    bank.is_active = False
    bank.updated_by = request.user
    bank.save()
    return JsonResponse({'success': True, 'message': 'تم حذف البنك بنجاح'})


# Treasury Views
@login_required
def treasury_list(request):
    """قائمة الخزائن"""
    search_query = request.GET.get('search', '')
    treasuries = Treasury.objects.filter(is_active=True).select_related('currency', 'responsible_person')

    if search_query:
        treasuries = treasuries.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    treasuries = treasuries.order_by('name')
    paginator = Paginator(treasuries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'الخزائن'
    }
    return render(request, 'definitions/treasury_list.html', context)


@login_required
def treasury_create(request):
    """إضافة خزينة جديدة"""
    if request.method == 'POST':
        form = TreasuryForm(request.POST)
        if form.is_valid():
            treasury = form.save(commit=False)
            treasury.created_by = request.user
            treasury.save()
            messages.success(request, 'تم إضافة الخزينة بنجاح')
            return redirect('definitions:treasury_list')
    else:
        form = TreasuryForm()

    context = {
        'form': form,
        'title': 'إضافة خزينة جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/treasury_form.html', context)


@login_required
def treasury_edit(request, pk):
    """تعديل خزينة"""
    treasury = get_object_or_404(Treasury, pk=pk)

    if request.method == 'POST':
        form = TreasuryForm(request.POST, instance=treasury)
        if form.is_valid():
            treasury = form.save(commit=False)
            treasury.updated_by = request.user
            treasury.save()
            messages.success(request, 'تم تحديث الخزينة بنجاح')
            return redirect('definitions:treasury_list')
    else:
        form = TreasuryForm(instance=treasury)

    context = {
        'form': form,
        'treasury': treasury,
        'title': f'تعديل الخزينة: {treasury.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/treasury_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def treasury_delete(request, pk):
    """حذف خزينة"""
    treasury = get_object_or_404(Treasury, pk=pk)
    treasury.is_active = False
    treasury.updated_by = request.user
    treasury.save()
    return JsonResponse({'success': True, 'message': 'تم حذف الخزينة بنجاح'})


# Warehouse Zone Views
@login_required
def zone_list(request):
    """قائمة مناطق المخازن"""
    search_query = request.GET.get('search', '')
    warehouse_filter = request.GET.get('warehouse', '')
    zones = WarehouseZone.objects.filter(is_active=True).select_related('warehouse')

    if search_query:
        zones = zones.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(warehouse__name__icontains=search_query)
        )

    if warehouse_filter:
        zones = zones.filter(warehouse_id=warehouse_filter)

    zones = zones.order_by('warehouse__name', 'name')
    paginator = Paginator(zones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    warehouses = Warehouse.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'warehouse_filter': warehouse_filter,
        'warehouses': warehouses,
        'title': 'مناطق المخازن'
    }
    return render(request, 'definitions/zone_list.html', context)


@login_required
def zone_create(request):
    """إضافة منطقة مخزن جديدة"""
    if request.method == 'POST':
        form = WarehouseZoneForm(request.POST)
        if form.is_valid():
            zone = form.save(commit=False)
            zone.created_by = request.user
            zone.save()
            messages.success(request, 'تم إضافة منطقة المخزن بنجاح')
            return redirect('definitions:zone_list')
    else:
        form = WarehouseZoneForm()

    context = {
        'form': form,
        'title': 'إضافة منطقة مخزن جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/zone_form.html', context)


@login_required
def zone_edit(request, pk):
    """تعديل منطقة مخزن"""
    zone = get_object_or_404(WarehouseZone, pk=pk)

    if request.method == 'POST':
        form = WarehouseZoneForm(request.POST, instance=zone)
        if form.is_valid():
            zone = form.save(commit=False)
            zone.updated_by = request.user
            zone.save()
            messages.success(request, 'تم تحديث منطقة المخزن بنجاح')
            return redirect('definitions:zone_list')
    else:
        form = WarehouseZoneForm(instance=zone)

    context = {
        'form': form,
        'zone': zone,
        'title': f'تعديل منطقة المخزن: {zone.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/zone_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def zone_delete(request, pk):
    """حذف منطقة مخزن"""
    zone = get_object_or_404(WarehouseZone, pk=pk)
    zone.is_active = False
    zone.updated_by = request.user
    zone.save()
    return JsonResponse({'success': True, 'message': 'تم حذف منطقة المخزن بنجاح'})


# Warehouse Location Views
@login_required
def location_list(request):
    """قائمة مواقع المخازن"""
    search_query = request.GET.get('search', '')
    warehouse_filter = request.GET.get('warehouse', '')
    zone_filter = request.GET.get('zone', '')
    locations = WarehouseLocation.objects.filter(is_active=True).select_related('warehouse', 'zone')

    if search_query:
        locations = locations.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(aisle__icontains=search_query) |
            Q(rack__icontains=search_query)
        )

    if warehouse_filter:
        locations = locations.filter(warehouse_id=warehouse_filter)

    if zone_filter:
        locations = locations.filter(zone_id=zone_filter)

    locations = locations.order_by('warehouse__name', 'aisle', 'rack', 'shelf')
    paginator = Paginator(locations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    warehouses = Warehouse.objects.filter(is_active=True).order_by('name')
    zones = WarehouseZone.objects.filter(is_active=True).order_by('warehouse__name', 'name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'warehouse_filter': warehouse_filter,
        'zone_filter': zone_filter,
        'warehouses': warehouses,
        'zones': zones,
        'title': 'مواقع المخازن'
    }
    return render(request, 'definitions/location_list.html', context)


@login_required
def location_create(request):
    """إضافة موقع مخزن جديد"""
    if request.method == 'POST':
        form = WarehouseLocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.created_by = request.user
            location.save()
            messages.success(request, 'تم إضافة موقع المخزن بنجاح')
            return redirect('definitions:location_list')
    else:
        form = WarehouseLocationForm()

    context = {
        'form': form,
        'title': 'إضافة موقع مخزن جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/location_form.html', context)


@login_required
def location_edit(request, pk):
    """تعديل موقع مخزن"""
    location = get_object_or_404(WarehouseLocation, pk=pk)

    if request.method == 'POST':
        form = WarehouseLocationForm(request.POST, instance=location)
        if form.is_valid():
            location = form.save(commit=False)
            location.updated_by = request.user
            location.save()
            messages.success(request, 'تم تحديث موقع المخزن بنجاح')
            return redirect('definitions:location_list')
    else:
        form = WarehouseLocationForm(instance=location)

    context = {
        'form': form,
        'location': location,
        'title': f'تعديل موقع المخزن: {location.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/location_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def location_delete(request, pk):
    """حذف موقع مخزن"""
    location = get_object_or_404(WarehouseLocation, pk=pk)
    location.is_active = False
    location.updated_by = request.user
    location.save()
    return JsonResponse({'success': True, 'message': 'تم حذف موقع المخزن بنجاح'})


# Item Location Views
@login_required
def item_location_list(request):
    """قائمة مواقع الأصناف"""
    search_query = request.GET.get('search', '')
    warehouse_filter = request.GET.get('warehouse', '')
    item_filter = request.GET.get('item', '')
    item_locations = ItemLocation.objects.filter(is_active=True).select_related(
        'item', 'warehouse', 'location'
    )

    if search_query:
        item_locations = item_locations.filter(
            Q(item__name__icontains=search_query) |
            Q(item__code__icontains=search_query) |
            Q(location__name__icontains=search_query)
        )

    if warehouse_filter:
        item_locations = item_locations.filter(warehouse_id=warehouse_filter)

    if item_filter:
        item_locations = item_locations.filter(item_id=item_filter)

    item_locations = item_locations.order_by('item__name', 'warehouse__name', 'priority')
    paginator = Paginator(item_locations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    warehouses = Warehouse.objects.filter(is_active=True).order_by('name')
    items = Item.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'warehouse_filter': warehouse_filter,
        'item_filter': item_filter,
        'warehouses': warehouses,
        'items': items,
        'title': 'مواقع الأصناف'
    }
    return render(request, 'definitions/item_location_list.html', context)


@login_required
def item_location_create(request):
    """إضافة موقع صنف جديد"""
    if request.method == 'POST':
        form = ItemLocationForm(request.POST)
        if form.is_valid():
            item_location = form.save(commit=False)
            item_location.created_by = request.user
            item_location.save()
            messages.success(request, 'تم إضافة موقع الصنف بنجاح')
            return redirect('definitions:item_location_list')
    else:
        form = ItemLocationForm()

    context = {
        'form': form,
        'title': 'إضافة موقع صنف جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/item_location_form.html', context)


@login_required
def item_location_edit(request, pk):
    """تعديل موقع صنف"""
    item_location = get_object_or_404(ItemLocation, pk=pk)

    if request.method == 'POST':
        form = ItemLocationForm(request.POST, instance=item_location)
        if form.is_valid():
            item_location = form.save(commit=False)
            item_location.updated_by = request.user
            item_location.save()
            messages.success(request, 'تم تحديث موقع الصنف بنجاح')
            return redirect('definitions:item_location_list')
    else:
        form = ItemLocationForm(instance=item_location)

    context = {
        'form': form,
        'item_location': item_location,
        'title': f'تعديل موقع الصنف: {item_location.item.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/item_location_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def item_location_delete(request, pk):
    """حذف موقع صنف"""
    item_location = get_object_or_404(ItemLocation, pk=pk)
    item_location.is_active = False
    item_location.updated_by = request.user
    item_location.save()
    return JsonResponse({'success': True, 'message': 'تم حذف موقع الصنف بنجاح'})


# Asset Group Views
@login_required
def asset_group_list(request):
    """قائمة مجموعات الأصول"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    parent_filter = request.GET.get('parent', '')

    asset_groups = AssetGroup.objects.filter(is_active=True).select_related('parent')

    if search_query:
        asset_groups = asset_groups.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        asset_groups = asset_groups.filter(asset_category=category_filter)

    if parent_filter:
        asset_groups = asset_groups.filter(parent_id=parent_filter)

    asset_groups = asset_groups.order_by('name')
    paginator = Paginator(asset_groups, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # للفلترة
    categories = AssetGroup.ASSET_CATEGORY_CHOICES if hasattr(AssetGroup, 'ASSET_CATEGORY_CHOICES') else []
    parent_groups = AssetGroup.objects.filter(is_active=True, parent__isnull=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'parent_filter': parent_filter,
        'categories': categories,
        'parent_groups': parent_groups,
        'title': 'مجموعات الأصول'
    }
    return render(request, 'definitions/asset_group_list.html', context)


@login_required
def asset_group_create(request):
    """إضافة مجموعة أصول جديدة"""
    if request.method == 'POST':
        form = AssetGroupForm(request.POST)
        if form.is_valid():
            asset_group = form.save(commit=False)
            asset_group.created_by = request.user
            asset_group.save()
            messages.success(request, 'تم إضافة مجموعة الأصول بنجاح')
            return redirect('definitions:asset_group_list')
    else:
        form = AssetGroupForm()

    context = {
        'form': form,
        'title': 'إضافة مجموعة أصول جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/asset_group_form.html', context)


@login_required
def asset_group_edit(request, pk):
    """تعديل مجموعة أصول"""
    asset_group = get_object_or_404(AssetGroup, pk=pk)

    if request.method == 'POST':
        form = AssetGroupForm(request.POST, instance=asset_group)
        if form.is_valid():
            asset_group = form.save(commit=False)
            asset_group.updated_by = request.user
            asset_group.save()
            messages.success(request, 'تم تحديث مجموعة الأصول بنجاح')
            return redirect('definitions:asset_group_list')
    else:
        form = AssetGroupForm(instance=asset_group)

    context = {
        'form': form,
        'asset_group': asset_group,
        'title': f'تعديل مجموعة الأصول: {asset_group.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/asset_group_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def asset_group_delete(request, pk):
    """حذف مجموعة أصول"""
    asset_group = get_object_or_404(AssetGroup, pk=pk)

    # التحقق من وجود مجموعات فرعية
    if asset_group.get_children().exists():
        return JsonResponse({
            'success': False,
            'message': 'لا يمكن حذف مجموعة تحتوي على مجموعات فرعية'
        })

    asset_group.is_active = False
    asset_group.updated_by = request.user
    asset_group.save()
    return JsonResponse({'success': True, 'message': 'تم حذف مجموعة الأصول بنجاح'})


# Person Views
@login_required
def person_list(request):
    """قائمة الأشخاص والجهات"""
    search_query = request.GET.get('search', '')
    person_type_filter = request.GET.get('person_type', '')
    entity_type_filter = request.GET.get('entity_type', '')

    persons = Person.objects.filter(is_active=True)

    if search_query:
        persons = persons.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(name_english__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if person_type_filter:
        persons = persons.filter(person_type=person_type_filter)

    if entity_type_filter:
        persons = persons.filter(entity_type=entity_type_filter)

    persons = persons.order_by('name')
    paginator = Paginator(persons, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'person_type_filter': person_type_filter,
        'entity_type_filter': entity_type_filter,
        'title': 'الأشخاص والجهات'
    }
    return render(request, 'definitions/person_list.html', context)


@login_required
def person_create(request):
    """إضافة شخص/جهة جديدة"""
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.created_by = request.user
            person.save()
            messages.success(request, 'تم إضافة الشخص/الجهة بنجاح')
            return redirect('definitions:person_list')
    else:
        form = PersonForm()

    context = {
        'form': form,
        'title': 'إضافة شخص/جهة جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/person_form.html', context)


@login_required
def person_edit(request, pk):
    """تعديل شخص/جهة"""
    person = get_object_or_404(Person, pk=pk)

    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            person = form.save(commit=False)
            person.updated_by = request.user
            person.save()
            messages.success(request, 'تم تحديث الشخص/الجهة بنجاح')
            return redirect('definitions:person_list')
    else:
        form = PersonForm(instance=person)

    context = {
        'form': form,
        'person': person,
        'title': f'تعديل الشخص/الجهة: {person.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/person_form.html', context)


@login_required
def person_detail(request, pk):
    """تفاصيل شخص/جهة"""
    person = get_object_or_404(Person, pk=pk)

    context = {
        'person': person,
        'title': f'تفاصيل الشخص/الجهة: {person.name}'
    }
    return render(request, 'definitions/person_detail.html', context)


@login_required
@require_http_methods(["DELETE"])
def person_delete(request, pk):
    """حذف شخص/جهة"""
    person = get_object_or_404(Person, pk=pk)
    person.is_active = False
    person.updated_by = request.user
    person.save()
    return JsonResponse({'success': True, 'message': 'تم حذف الشخص/الجهة بنجاح'})


# Expense Category Views
@login_required
def expense_category_list(request):
    """قائمة فئات المصروفات"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    expense_categories = ExpenseCategory.objects.filter(is_active=True)

    if search_query:
        expense_categories = expense_categories.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        expense_categories = expense_categories.filter(category=category_filter)

    expense_categories = expense_categories.order_by('name')
    paginator = Paginator(expense_categories, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'title': 'فئات المصروفات'
    }
    return render(request, 'definitions/expense_category_list.html', context)


@login_required
def expense_category_create(request):
    """إضافة فئة مصروف جديدة"""
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            expense_category = form.save(commit=False)
            expense_category.created_by = request.user
            expense_category.save()
            messages.success(request, 'تم إضافة فئة المصروف بنجاح')
            return redirect('definitions:expense_category_list')
    else:
        form = ExpenseCategoryForm()

    context = {
        'form': form,
        'title': 'إضافة فئة مصروف جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/expense_category_form.html', context)


@login_required
def expense_category_edit(request, pk):
    """تعديل فئة مصروف"""
    expense_category = get_object_or_404(ExpenseCategory, pk=pk)

    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=expense_category)
        if form.is_valid():
            expense_category = form.save(commit=False)
            expense_category.updated_by = request.user
            expense_category.save()
            messages.success(request, 'تم تحديث فئة المصروف بنجاح')
            return redirect('definitions:expense_category_list')
    else:
        form = ExpenseCategoryForm(instance=expense_category)

    context = {
        'form': form,
        'expense_category': expense_category,
        'title': f'تعديل فئة المصروف: {expense_category.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/expense_category_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def expense_category_delete(request, pk):
    """حذف فئة مصروف"""
    expense_category = get_object_or_404(ExpenseCategory, pk=pk)
    expense_category.is_active = False
    expense_category.updated_by = request.user
    expense_category.save()
    return JsonResponse({'success': True, 'message': 'تم حذف فئة المصروف بنجاح'})


# Expense Item Views
@login_required
def expense_item_list(request):
    """قائمة بنود المصروفات"""
    search_query = request.GET.get('search', '')
    expense_category_filter = request.GET.get('expense_category', '')

    expense_items = ExpenseItem.objects.filter(is_active=True).select_related('expense_category')

    if search_query:
        expense_items = expense_items.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(expense_category__name__icontains=search_query)
        )

    if expense_category_filter:
        expense_items = expense_items.filter(expense_category_id=expense_category_filter)

    expense_items = expense_items.order_by('expense_category__name', 'name')
    paginator = Paginator(expense_items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    expense_categories = ExpenseCategory.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'expense_category_filter': expense_category_filter,
        'expense_categories': expense_categories,
        'title': 'بنود المصروفات'
    }
    return render(request, 'definitions/expense_item_list.html', context)


@login_required
def expense_item_create(request):
    """إضافة بند مصروف جديد"""
    if request.method == 'POST':
        form = ExpenseItemForm(request.POST)
        if form.is_valid():
            expense_item = form.save(commit=False)
            expense_item.created_by = request.user
            expense_item.save()
            messages.success(request, 'تم إضافة بند المصروف بنجاح')
            return redirect('definitions:expense_item_list')
    else:
        form = ExpenseItemForm()

    context = {
        'form': form,
        'title': 'إضافة بند مصروف جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/expense_item_form.html', context)


@login_required
def expense_item_edit(request, pk):
    """تعديل بند مصروف"""
    expense_item = get_object_or_404(ExpenseItem, pk=pk)

    if request.method == 'POST':
        form = ExpenseItemForm(request.POST, instance=expense_item)
        if form.is_valid():
            expense_item = form.save(commit=False)
            expense_item.updated_by = request.user
            expense_item.save()
            messages.success(request, 'تم تحديث بند المصروف بنجاح')
            return redirect('definitions:expense_item_list')
    else:
        form = ExpenseItemForm(instance=expense_item)

    context = {
        'form': form,
        'expense_item': expense_item,
        'title': f'تعديل بند المصروف: {expense_item.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/expense_item_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def expense_item_delete(request, pk):
    """حذف بند مصروف"""
    expense_item = get_object_or_404(ExpenseItem, pk=pk)
    expense_item.is_active = False
    expense_item.updated_by = request.user
    expense_item.save()
    return JsonResponse({'success': True, 'message': 'تم حذف بند المصروف بنجاح'})


# Revenue Category Views
@login_required
def revenue_category_list(request):
    """قائمة فئات الإيرادات"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    revenue_categories = RevenueCategory.objects.filter(is_active=True)

    if search_query:
        revenue_categories = revenue_categories.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        revenue_categories = revenue_categories.filter(category=category_filter)

    revenue_categories = revenue_categories.order_by('name')
    paginator = Paginator(revenue_categories, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'title': 'فئات الإيرادات'
    }
    return render(request, 'definitions/revenue_category_list.html', context)


@login_required
def revenue_category_create(request):
    """إضافة فئة إيراد جديدة"""
    if request.method == 'POST':
        form = RevenueCategoryForm(request.POST)
        if form.is_valid():
            revenue_category = form.save(commit=False)
            revenue_category.created_by = request.user
            revenue_category.save()
            messages.success(request, 'تم إضافة فئة الإيراد بنجاح')
            return redirect('definitions:revenue_category_list')
    else:
        form = RevenueCategoryForm()

    context = {
        'form': form,
        'title': 'إضافة فئة إيراد جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/revenue_category_form.html', context)


@login_required
def revenue_category_edit(request, pk):
    """تعديل فئة إيراد"""
    revenue_category = get_object_or_404(RevenueCategory, pk=pk)

    if request.method == 'POST':
        form = RevenueCategoryForm(request.POST, instance=revenue_category)
        if form.is_valid():
            revenue_category = form.save(commit=False)
            revenue_category.updated_by = request.user
            revenue_category.save()
            messages.success(request, 'تم تحديث فئة الإيراد بنجاح')
            return redirect('definitions:revenue_category_list')
    else:
        form = RevenueCategoryForm(instance=revenue_category)

    context = {
        'form': form,
        'revenue_category': revenue_category,
        'title': f'تعديل فئة الإيراد: {revenue_category.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/revenue_category_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def revenue_category_delete(request, pk):
    """حذف فئة إيراد"""
    revenue_category = get_object_or_404(RevenueCategory, pk=pk)
    revenue_category.is_active = False
    revenue_category.updated_by = request.user
    revenue_category.save()
    return JsonResponse({'success': True, 'message': 'تم حذف فئة الإيراد بنجاح'})


# Revenue Item Views
@login_required
def revenue_item_list(request):
    """قائمة بنود الإيرادات"""
    search_query = request.GET.get('search', '')
    revenue_category_filter = request.GET.get('revenue_category', '')

    revenue_items = RevenueItem.objects.filter(is_active=True).select_related('revenue_category')

    if search_query:
        revenue_items = revenue_items.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(revenue_category__name__icontains=search_query)
        )

    if revenue_category_filter:
        revenue_items = revenue_items.filter(revenue_category_id=revenue_category_filter)

    revenue_items = revenue_items.order_by('revenue_category__name', 'name')
    paginator = Paginator(revenue_items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    revenue_categories = RevenueCategory.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'revenue_category_filter': revenue_category_filter,
        'revenue_categories': revenue_categories,
        'title': 'بنود الإيرادات'
    }
    return render(request, 'definitions/revenue_item_list.html', context)


@login_required
def revenue_item_create(request):
    """إضافة بند إيراد جديد"""
    if request.method == 'POST':
        form = RevenueItemForm(request.POST)
        if form.is_valid():
            revenue_item = form.save(commit=False)
            revenue_item.created_by = request.user
            revenue_item.save()
            messages.success(request, 'تم إضافة بند الإيراد بنجاح')
            return redirect('definitions:revenue_item_list')
    else:
        form = RevenueItemForm()

    context = {
        'form': form,
        'title': 'إضافة بند إيراد جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/revenue_item_form.html', context)


@login_required
def revenue_item_edit(request, pk):
    """تعديل بند إيراد"""
    revenue_item = get_object_or_404(RevenueItem, pk=pk)

    if request.method == 'POST':
        form = RevenueItemForm(request.POST, instance=revenue_item)
        if form.is_valid():
            revenue_item = form.save(commit=False)
            revenue_item.updated_by = request.user
            revenue_item.save()
            messages.success(request, 'تم تحديث بند الإيراد بنجاح')
            return redirect('definitions:revenue_item_list')
    else:
        form = RevenueItemForm(instance=revenue_item)

    context = {
        'form': form,
        'revenue_item': revenue_item,
        'title': f'تعديل بند الإيراد: {revenue_item.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/revenue_item_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def revenue_item_delete(request, pk):
    """حذف بند إيراد"""
    revenue_item = get_object_or_404(RevenueItem, pk=pk)
    revenue_item.is_active = False
    revenue_item.updated_by = request.user
    revenue_item.save()
    return JsonResponse({'success': True, 'message': 'تم حذف بند الإيراد بنجاح'})


# Production Stage Views
@login_required
def production_stage_list(request):
    """قائمة مراحل الإنتاج"""
    search_query = request.GET.get('search', '')
    stage_type_filter = request.GET.get('stage_type', '')
    stages = ProductionStage.objects.filter(is_active=True).select_related('responsible_user')

    if search_query:
        stages = stages.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if stage_type_filter:
        stages = stages.filter(stage_type=stage_type_filter)

    stages = stages.order_by('sequence_number', 'name')
    paginator = Paginator(stages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات أنواع المراحل
    stage_types = ProductionStage._meta.get_field('stage_type').choices

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'stage_type_filter': stage_type_filter,
        'stage_types': stage_types,
        'title': 'مراحل الإنتاج'
    }
    return render(request, 'definitions/production_stage_list.html', context)


@login_required
def production_stage_create(request):
    """إضافة مرحلة إنتاج جديدة"""
    if request.method == 'POST':
        form = ProductionStageForm(request.POST)
        if form.is_valid():
            stage = form.save(commit=False)
            stage.created_by = request.user
            stage.save()
            messages.success(request, 'تم إضافة مرحلة الإنتاج بنجاح')
            return redirect('definitions:production_stage_list')
    else:
        form = ProductionStageForm()

    context = {
        'form': form,
        'title': 'إضافة مرحلة إنتاج جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/production_stage_form.html', context)


@login_required
def production_stage_detail(request, pk):
    """تفاصيل مرحلة الإنتاج"""
    stage = get_object_or_404(ProductionStage, pk=pk)
    context = {
        'stage': stage,
        'title': f'تفاصيل مرحلة الإنتاج: {stage.name}'
    }
    return render(request, 'definitions/production_stage_detail.html', context)


@login_required
def production_stage_edit(request, pk):
    """تعديل مرحلة إنتاج"""
    stage = get_object_or_404(ProductionStage, pk=pk)

    if request.method == 'POST':
        form = ProductionStageForm(request.POST, instance=stage)
        if form.is_valid():
            stage = form.save(commit=False)
            stage.updated_by = request.user
            stage.save()
            messages.success(request, 'تم تحديث مرحلة الإنتاج بنجاح')
            return redirect('definitions:production_stage_detail', pk=stage.pk)
    else:
        form = ProductionStageForm(instance=stage)

    context = {
        'form': form,
        'stage': stage,
        'title': f'تعديل مرحلة الإنتاج: {stage.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/production_stage_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def production_stage_delete(request, pk):
    """حذف مرحلة إنتاج"""
    stage = get_object_or_404(ProductionStage, pk=pk)
    stage.is_active = False
    stage.updated_by = request.user
    stage.save()
    return JsonResponse({'success': True, 'message': 'تم حذف مرحلة الإنتاج بنجاح'})


# Finished Product Views
@login_required
def finished_product_list(request):
    """قائمة المنتجات التامة"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    products = FinishedProduct.objects.filter(is_active=True).select_related('category', 'unit')

    if search_query:
        products = products.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(name_english__icontains=search_query) |
            Q(barcode__icontains=search_query) |
            Q(sku__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    products = products.order_by('name')
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = ItemCategory.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
        'title': 'المنتجات التامة'
    }
    return render(request, 'definitions/finished_product_list.html', context)


@login_required
def finished_product_create(request):
    """إضافة منتج تام جديد"""
    if request.method == 'POST':
        form = FinishedProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'تم إضافة المنتج التام بنجاح')
            return redirect('definitions:finished_product_list')
    else:
        form = FinishedProductForm()

    context = {
        'form': form,
        'title': 'إضافة منتج تام جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/finished_product_form.html', context)


@login_required
def finished_product_detail(request, pk):
    """تفاصيل المنتج التام"""
    product = get_object_or_404(FinishedProduct, pk=pk)

    context = {
        'product': product,
        'title': f'تفاصيل المنتج التام: {product.name}'
    }
    return render(request, 'definitions/finished_product_detail.html', context)


@login_required
def finished_product_edit(request, pk):
    """تعديل منتج تام"""
    product = get_object_or_404(FinishedProduct, pk=pk)

    if request.method == 'POST':
        form = FinishedProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_by = request.user
            product.save()
            messages.success(request, 'تم تحديث المنتج التام بنجاح')
            return redirect('definitions:finished_product_detail', pk=product.pk)
    else:
        form = FinishedProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'title': f'تعديل المنتج التام: {product.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/finished_product_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def finished_product_delete(request, pk):
    """حذف منتج تام"""
    product = get_object_or_404(FinishedProduct, pk=pk)
    product.is_active = False
    product.updated_by = request.user
    product.save()
    return JsonResponse({'success': True, 'message': 'تم حذف المنتج التام بنجاح'})


# Profit Center Views
@login_required
def profit_center_list(request):
    """قائمة مراكز الربحية"""
    search_query = request.GET.get('search', '')
    level_filter = request.GET.get('level', '')
    parent_filter = request.GET.get('parent', '')

    centers = ProfitCenter.objects.filter(is_active=True).select_related('parent', 'manager')

    if search_query:
        centers = centers.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(name_english__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if level_filter:
        centers = centers.filter(level=level_filter)

    if parent_filter:
        centers = centers.filter(parent_id=parent_filter)

    centers = centers.order_by('level', 'code', 'name')
    paginator = Paginator(centers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    levels = centers.values_list('level', flat=True).distinct().order_by('level')
    parents = ProfitCenter.objects.filter(is_active=True, level__lt=3).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'level_filter': level_filter,
        'parent_filter': parent_filter,
        'levels': levels,
        'parents': parents,
        'title': 'مراكز الربحية'
    }
    return render(request, 'definitions/profit_center_list.html', context)


@login_required
def profit_center_create(request):
    """إضافة مركز ربحية جديد"""
    if request.method == 'POST':
        form = ProfitCenterForm(request.POST)
        if form.is_valid():
            center = form.save(commit=False)
            center.created_by = request.user
            center.save()
            messages.success(request, 'تم إضافة مركز الربحية بنجاح')
            return redirect('definitions:profit_center_list')
    else:
        form = ProfitCenterForm()

    context = {
        'form': form,
        'title': 'إضافة مركز ربحية جديد',
        'action': 'إضافة'
    }
    return render(request, 'definitions/profit_center_form.html', context)


@login_required
def profit_center_detail(request, pk):
    """تفاصيل مركز الربحية"""
    center = get_object_or_404(ProfitCenter, pk=pk)
    children = center.children.filter(is_active=True).order_by('code')

    context = {
        'center': center,
        'children': children,
        'title': f'تفاصيل مركز الربحية: {center.name}'
    }
    return render(request, 'definitions/profit_center_detail.html', context)


@login_required
def profit_center_edit(request, pk):
    """تعديل مركز ربحية"""
    center = get_object_or_404(ProfitCenter, pk=pk)

    if request.method == 'POST':
        form = ProfitCenterForm(request.POST, instance=center)
        if form.is_valid():
            center = form.save(commit=False)
            center.updated_by = request.user
            center.save()
            messages.success(request, 'تم تحديث مركز الربحية بنجاح')
            return redirect('definitions:profit_center_detail', pk=center.pk)
    else:
        form = ProfitCenterForm(instance=center)

    context = {
        'form': form,
        'center': center,
        'title': f'تعديل مركز الربحية: {center.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/profit_center_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def profit_center_delete(request, pk):
    """حذف مركز ربحية"""
    center = get_object_or_404(ProfitCenter, pk=pk)
    center.is_active = False
    center.updated_by = request.user
    center.save()
    return JsonResponse({'success': True, 'message': 'تم حذف مركز الربحية بنجاح'})


# Printer Views
@login_required
def printer_list(request):
    """قائمة الطابعات"""
    search_query = request.GET.get('search', '')
    printer_type_filter = request.GET.get('printer_type', '')
    connection_type_filter = request.GET.get('connection_type', '')
    usage_type_filter = request.GET.get('usage_type', '')

    printers = Printer.objects.filter(is_active=True).select_related('responsible_user')

    if search_query:
        printers = printers.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if printer_type_filter:
        printers = printers.filter(printer_type=printer_type_filter)

    if connection_type_filter:
        printers = printers.filter(connection_type=connection_type_filter)

    if usage_type_filter:
        printers = printers.filter(usage_type=usage_type_filter)

    printers = printers.order_by('name')
    paginator = Paginator(printers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # خيارات الفلترة
    printer_types = Printer.PRINTER_TYPE_CHOICES if hasattr(Printer, 'PRINTER_TYPE_CHOICES') else [
        ('THERMAL', 'حرارية'),
        ('INKJET', 'نفث الحبر'),
        ('LASER', 'ليزر'),
        ('DOT_MATRIX', 'نقطية'),
        ('LABEL', 'ملصقات'),
        ('RECEIPT', 'فواتير'),
        ('BARCODE', 'باركود'),
        ('PHOTO', 'صور'),
        ('OTHER', 'أخرى'),
    ]

    connection_types = [
        ('USB', 'USB'),
        ('NETWORK', 'شبكة'),
        ('BLUETOOTH', 'بلوتوث'),
        ('WIFI', 'واي فاي'),
        ('SERIAL', 'تسلسلي'),
        ('PARALLEL', 'متوازي'),
    ]

    usage_types = [
        ('INVOICES', 'الفواتير'),
        ('REPORTS', 'التقارير'),
        ('LABELS', 'الملصقات'),
        ('RECEIPTS', 'الإيصالات'),
        ('BARCODES', 'الباركود'),
        ('DOCUMENTS', 'المستندات'),
        ('GENERAL', 'عام'),
    ]

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'printer_type_filter': printer_type_filter,
        'connection_type_filter': connection_type_filter,
        'usage_type_filter': usage_type_filter,
        'printer_types': printer_types,
        'connection_types': connection_types,
        'usage_types': usage_types,
        'title': 'الطابعات'
    }
    return render(request, 'definitions/printer_list.html', context)


@login_required
def printer_create(request):
    """إضافة طابعة جديدة"""
    if request.method == 'POST':
        form = PrinterForm(request.POST)
        if form.is_valid():
            printer = form.save(commit=False)
            printer.created_by = request.user
            printer.save()
            messages.success(request, 'تم إضافة الطابعة بنجاح')
            return redirect('definitions:printer_list')
    else:
        form = PrinterForm()

    context = {
        'form': form,
        'title': 'إضافة طابعة جديدة',
        'action': 'إضافة'
    }
    return render(request, 'definitions/printer_form.html', context)


@login_required
def printer_detail(request, pk):
    """تفاصيل الطابعة"""
    printer = get_object_or_404(Printer, pk=pk)

    context = {
        'printer': printer,
        'title': f'تفاصيل الطابعة: {printer.name}'
    }
    return render(request, 'definitions/printer_detail.html', context)


@login_required
def printer_edit(request, pk):
    """تعديل طابعة"""
    printer = get_object_or_404(Printer, pk=pk)

    if request.method == 'POST':
        form = PrinterForm(request.POST, instance=printer)
        if form.is_valid():
            printer = form.save(commit=False)
            printer.updated_by = request.user
            printer.save()
            messages.success(request, 'تم تحديث الطابعة بنجاح')
            return redirect('definitions:printer_detail', pk=printer.pk)
    else:
        form = PrinterForm(instance=printer)

    context = {
        'form': form,
        'printer': printer,
        'title': f'تعديل الطابعة: {printer.name}',
        'action': 'تحديث'
    }
    return render(request, 'definitions/printer_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def printer_delete(request, pk):
    """حذف طابعة"""
    printer = get_object_or_404(Printer, pk=pk)
    printer.is_active = False
    printer.updated_by = request.user
    printer.save()
    return JsonResponse({'success': True, 'message': 'تم حذف الطابعة بنجاح'})


# Company Settings Views
@login_required
def company_settings(request):
    """إعدادات الشركة"""
    settings = CompanySettings.get_settings()

    if request.method == 'POST':
        # معالجة رفع الشعار
        if 'logo' in request.FILES:
            logo_file = request.FILES['logo']

            # التحقق من نوع الملف
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if logo_file.content_type not in allowed_types:
                messages.error(request, 'نوع الملف غير مدعوم. يرجى اختيار صورة بصيغة JPG أو PNG')
                return redirect('definitions:company_settings')

            # التحقق من حجم الملف (5MB كحد أقصى)
            if logo_file.size > 5 * 1024 * 1024:
                messages.error(request, 'حجم الملف كبير جداً. الحد الأقصى 5 ميجابايت')
                return redirect('definitions:company_settings')

            settings.logo = logo_file

        # معالجة باقي البيانات
        settings.company_name = request.POST.get('company_name', settings.company_name)
        settings.company_name_english = request.POST.get('company_name_english', settings.company_name_english)
        settings.phone = request.POST.get('phone', settings.phone)
        settings.mobile = request.POST.get('mobile', settings.mobile)
        settings.email = request.POST.get('email', settings.email)
        settings.website = request.POST.get('website', settings.website)
        settings.address = request.POST.get('address', settings.address)
        settings.city = request.POST.get('city', settings.city)
        settings.state = request.POST.get('state', settings.state)
        settings.country = request.POST.get('country', settings.country)
        settings.postal_code = request.POST.get('postal_code', settings.postal_code)
        settings.tax_number = request.POST.get('tax_number', settings.tax_number)
        settings.commercial_register = request.POST.get('commercial_register', settings.commercial_register)
        settings.app_name = request.POST.get('app_name', settings.app_name)
        settings.app_version = request.POST.get('app_version', settings.app_version)

        try:
            settings.save()
            messages.success(request, 'تم حفظ إعدادات الشركة بنجاح')
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء حفظ الإعدادات: {str(e)}')

        return redirect('definitions:company_settings')

    context = {
        'title': 'إعدادات الشركة',
        'settings': settings,
    }
    return render(request, 'definitions/company_settings.html', context)


@login_required
@require_http_methods(["POST"])
def upload_logo(request):
    """رفع شعار الشركة عبر AJAX"""
    if 'logo' not in request.FILES:
        return JsonResponse({'error': 'لم يتم اختيار ملف'}, status=400)

    logo_file = request.FILES['logo']

    # التحقق من نوع الملف
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if logo_file.content_type not in allowed_types:
        return JsonResponse({'error': 'نوع الملف غير مدعوم. يرجى اختيار صورة بصيغة JPG أو PNG'}, status=400)

    # التحقق من حجم الملف (5MB كحد أقصى)
    if logo_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'حجم الملف كبير جداً. الحد الأقصى 5 ميجابايت'}, status=400)

    try:
        settings = CompanySettings.get_settings()
        settings.logo = logo_file
        settings.save()

        return JsonResponse({
            'success': True,
            'logo_url': settings.logo_url,
            'message': 'تم رفع الشعار بنجاح'
        })
    except Exception as e:
        return JsonResponse({'error': f'حدث خطأ أثناء رفع الشعار: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def remove_logo(request):
    """حذف شعار الشركة"""
    try:
        settings = CompanySettings.get_settings()
        if settings.logo:
            settings.logo.delete()
            settings.save()
            return JsonResponse({
                'success': True,
                'message': 'تم حذف الشعار بنجاح'
            })
        else:
            return JsonResponse({'error': 'لا يوجد شعار لحذفه'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'حدث خطأ أثناء حذف الشعار: {str(e)}'}, status=500)


@login_required
def get_company_info(request):
    """الحصول على معلومات الشركة للاستخدام في JavaScript"""
    settings = CompanySettings.get_settings()

    return JsonResponse({
        'company_name': settings.company_name,
        'company_name_english': settings.company_name_english,
        'logo_url': settings.logo_url,
        'app_name': settings.app_name,
        'app_version': settings.app_version,
        'phone': settings.phone,
        'email': settings.email,
        'address': settings.full_address,
    })



