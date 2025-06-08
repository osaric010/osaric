"""
Views لجرد بضاعة أول المدة في الحسابات العامة
Opening Inventory Views for Accounting
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db import transaction
from django.utils import timezone
from django.urls import reverse

from .models import OpeningInventory, OpeningInventoryItem
from .forms import OpeningInventoryForm, OpeningInventoryItemFormSet
from definitions.models import Warehouse, Item, Currency
from core.currency_utils import format_currency


@login_required
def opening_inventory_list(request):
    """قائمة جرد أول المدة"""
    
    # الفلترة
    queryset = OpeningInventory.objects.all()
    
    # البحث
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(inventory_number__icontains=search) |
            Q(warehouse__name__icontains=search) |
            Q(fiscal_year__icontains=search) |
            Q(period_name__icontains=search)
        )
    
    # فلترة المخزن
    warehouse_id = request.GET.get('warehouse')
    if warehouse_id:
        queryset = queryset.filter(warehouse_id=warehouse_id)
    
    # فلترة السنة المالية
    fiscal_year = request.GET.get('fiscal_year')
    if fiscal_year:
        queryset = queryset.filter(fiscal_year=fiscal_year)
    
    # فلترة الحالة
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    
    # فلترة التاريخ
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    
    # ترتيب النتائج
    queryset = queryset.order_by('-date', '-id')
    
    # التصفح
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # إحصائيات
    stats = {
        'total_count': OpeningInventory.objects.count(),
        'draft_count': OpeningInventory.objects.filter(status='DRAFT').count(),
        'approved_count': OpeningInventory.objects.filter(status='APPROVED').count(),
        'posted_count': OpeningInventory.objects.filter(status='POSTED').count(),
    }
    
    context = {
        'title': 'جرد بضاعة أول المدة',
        'page_obj': page_obj,
        'warehouses': Warehouse.objects.filter(is_active=True),
        'stats': stats,
        'search': search,
        'selected_warehouse': warehouse_id,
        'selected_fiscal_year': fiscal_year,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'accounting/opening_inventory_list.html', context)


@login_required
def opening_inventory_create(request):
    """إنشاء جرد أول المدة جديد"""
    
    if request.method == 'POST':
        form = OpeningInventoryForm(request.POST)
        formset = OpeningInventoryItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # حفظ جرد أول المدة
                    opening_inventory = form.save(commit=False)
                    opening_inventory.created_by = request.user
                    opening_inventory.save()
                    
                    # حفظ الأصناف
                    formset.instance = opening_inventory
                    items = formset.save(commit=False)
                    
                    for item in items:
                        item.recorded_by = request.user
                        item.save()
                    
                    # حذف الأصناف المحذوفة
                    for item in formset.deleted_objects:
                        item.delete()
                    
                    # تحديث الإحصائيات
                    opening_inventory.save()
                    
                    messages.success(request, f'تم إنشاء جرد أول المدة {opening_inventory.inventory_number} بنجاح')
                    return redirect('accounting:opening_inventory_detail', pk=opening_inventory.pk)
                    
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء الحفظ: {str(e)}')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه')
    else:
        form = OpeningInventoryForm()
        formset = OpeningInventoryItemFormSet()
    
    context = {
        'title': 'إنشاء جرد أول المدة',
        'form': form,
        'formset': formset,
        'warehouses': Warehouse.objects.filter(is_active=True),
        'items': Item.objects.filter(is_active=True).order_by('name'),
        'currencies': Currency.objects.filter(is_active=True),
    }
    
    return render(request, 'accounting/opening_inventory_form.html', context)


@login_required
def opening_inventory_detail(request, pk):
    """تفاصيل جرد أول المدة"""
    
    opening_inventory = get_object_or_404(OpeningInventory, pk=pk)
    items = opening_inventory.items.all().order_by('item__name')
    
    # إحصائيات
    stats = {
        'total_items': items.count(),
        'total_quantity': items.aggregate(total=Sum('opening_quantity'))['total'] or 0,
        'total_value': items.aggregate(total=Sum('total_value'))['total'] or 0,
    }
    
    context = {
        'title': f'جرد أول المدة - {opening_inventory.inventory_number}',
        'opening_inventory': opening_inventory,
        'items': items,
        'stats': stats,
    }
    
    return render(request, 'accounting/opening_inventory_detail.html', context)


@login_required
def opening_inventory_edit(request, pk):
    """تعديل جرد أول المدة"""
    
    opening_inventory = get_object_or_404(OpeningInventory, pk=pk)
    
    # التحقق من إمكانية التعديل
    if not opening_inventory.can_be_edited:
        messages.error(request, 'لا يمكن تعديل هذا الجرد في الحالة الحالية')
        return redirect('accounting:opening_inventory_detail', pk=pk)
    
    if request.method == 'POST':
        form = OpeningInventoryForm(request.POST, instance=opening_inventory)
        formset = OpeningInventoryItemFormSet(request.POST, instance=opening_inventory)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # حفظ جرد أول المدة
                    opening_inventory = form.save(commit=False)
                    opening_inventory.updated_by = request.user
                    opening_inventory.save()
                    
                    # حفظ الأصناف
                    items = formset.save(commit=False)
                    
                    for item in items:
                        if not item.recorded_by:
                            item.recorded_by = request.user
                        item.save()
                    
                    # حذف الأصناف المحذوفة
                    for item in formset.deleted_objects:
                        item.delete()
                    
                    # تحديث الإحصائيات
                    opening_inventory.save()
                    
                    messages.success(request, f'تم تحديث جرد أول المدة {opening_inventory.inventory_number} بنجاح')
                    return redirect('accounting:opening_inventory_detail', pk=opening_inventory.pk)
                    
            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء الحفظ: {str(e)}')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه')
    else:
        form = OpeningInventoryForm(instance=opening_inventory)
        formset = OpeningInventoryItemFormSet(instance=opening_inventory)
    
    context = {
        'title': f'تعديل جرد أول المدة - {opening_inventory.inventory_number}',
        'form': form,
        'formset': formset,
        'opening_inventory': opening_inventory,
        'warehouses': Warehouse.objects.filter(is_active=True),
        'items': Item.objects.filter(is_active=True).order_by('name'),
        'currencies': Currency.objects.filter(is_active=True),
    }
    
    return render(request, 'accounting/opening_inventory_form.html', context)


@login_required
def opening_inventory_approve(request, pk):
    """اعتماد جرد أول المدة"""
    
    opening_inventory = get_object_or_404(OpeningInventory, pk=pk)
    
    if not opening_inventory.can_be_approved:
        messages.error(request, 'لا يمكن اعتماد هذا الجرد في الحالة الحالية')
        return redirect('accounting:opening_inventory_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                opening_inventory.status = 'APPROVED'
                opening_inventory.approved_by = request.user
                opening_inventory.approved_date = timezone.now()
                opening_inventory.save()
                
                messages.success(request, f'تم اعتماد جرد أول المدة {opening_inventory.inventory_number} بنجاح')
                
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الاعتماد: {str(e)}')
    
    return redirect('accounting:opening_inventory_detail', pk=pk)


@login_required
def opening_inventory_post(request, pk):
    """ترحيل جرد أول المدة"""
    
    opening_inventory = get_object_or_404(OpeningInventory, pk=pk)
    
    if not opening_inventory.can_be_posted:
        messages.error(request, 'لا يمكن ترحيل هذا الجرد في الحالة الحالية')
        return redirect('accounting:opening_inventory_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # إنشاء قيد افتتاحي للمخزون
                from .models import OpeningBalance
                
                # حساب إجمالي قيمة المخزون
                total_inventory_value = opening_inventory.total_value
                
                # إنشاء قيد افتتاحي للمخزون
                opening_balance = OpeningBalance.objects.create(
                    balance_number=f'OB-INV-{opening_inventory.inventory_number}',
                    balance_date=opening_inventory.date,
                    balance_type='INVENTORY',
                    debit_amount=total_inventory_value,
                    credit_amount=0,
                    description=f'جرد بضاعة أول المدة - {opening_inventory.warehouse.name} - {opening_inventory.fiscal_year}',
                    notes=f'تم الترحيل من جرد أول المدة رقم {opening_inventory.inventory_number}',
                    created_by=request.user
                )
                
                # تحديث حالة الجرد
                opening_inventory.status = 'POSTED'
                opening_inventory.posted_by = request.user
                opening_inventory.posted_date = timezone.now()
                opening_inventory.save()
                
                messages.success(request, f'تم ترحيل جرد أول المدة {opening_inventory.inventory_number} بنجاح')
                
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الترحيل: {str(e)}')
    
    return redirect('accounting:opening_inventory_detail', pk=pk)


@login_required
def opening_inventory_delete(request, pk):
    """حذف جرد أول المدة"""
    
    opening_inventory = get_object_or_404(OpeningInventory, pk=pk)
    
    if not opening_inventory.can_be_cancelled:
        messages.error(request, 'لا يمكن حذف هذا الجرد في الحالة الحالية')
        return redirect('accounting:opening_inventory_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            inventory_number = opening_inventory.inventory_number
            opening_inventory.delete()
            messages.success(request, f'تم حذف جرد أول المدة {inventory_number} بنجاح')
            return redirect('accounting:opening_inventory_list')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء الحذف: {str(e)}')
    
    return redirect('accounting:opening_inventory_detail', pk=pk)


@login_required
def get_item_cost(request):
    """الحصول على تكلفة الصنف عبر AJAX"""
    
    item_id = request.GET.get('item_id')
    if item_id:
        try:
            item = Item.objects.get(pk=item_id, is_active=True)
            return JsonResponse({
                'success': True,
                'cost_price': float(item.cost_price or 0),
                'unit_name': item.unit.name if item.unit else '',
            })
        except Item.DoesNotExist:
            pass
    
    return JsonResponse({'success': False})


@login_required
def opening_inventory_report(request, pk):
    """تقرير جرد أول المدة"""
    
    opening_inventory = get_object_or_404(OpeningInventory, pk=pk)
    items = opening_inventory.items.all().order_by('item__name')
    
    context = {
        'opening_inventory': opening_inventory,
        'items': items,
        'total_value': sum(item.total_value for item in items),
        'total_quantity': sum(item.opening_quantity for item in items),
    }
    
    return render(request, 'accounting/opening_inventory_report.html', context)
