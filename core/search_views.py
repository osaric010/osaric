from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.urls import reverse
import json

# Import models from different apps
from definitions.models import Item, Person, Warehouse, Bank, Treasury
from inventory.models import StockIncrease, StockDecrease, PhysicalInventory

# Try to import optional models
try:
    from sales.models import SalesInvoice
except ImportError:
    SalesInvoice = None

try:
    from purchases.models import PurchaseInvoice
except ImportError:
    PurchaseInvoice = None

try:
    from assets.models import Asset
except ImportError:
    Asset = None

try:
    from treasury.models import Receipt, Payment
except ImportError:
    Receipt = None
    Payment = None


@login_required
@require_http_methods(["GET"])
def global_search(request):
    """البحث الشامل في النظام"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({
            'success': False,
            'message': 'يجب أن يكون البحث أكثر من حرفين',
            'results': []
        })
    
    results = []

    # البحث في أقسام وصفحات التطبيق
    app_sections = search_app_sections(query)
    results.extend(app_sections)

    try:
        # البحث في الأصناف
        items = Item.objects.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) |
            Q(barcode__icontains=query)
        ).select_related('category', 'unit')[:5]
        
        for item in items:
            results.append({
                'type': 'item',
                'title': item.name,
                'description': f'كود: {item.code} - فئة: {item.category.name if item.category else "غير محدد"}',
                'url': f'/definitions/items/{item.id}/',
                'icon': 'fas fa-box',
                'id': item.id
            })
        
        # البحث في الأشخاص
        persons = Person.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(code__icontains=query)
        )[:5]
        
        for person in persons:
            person_type = "عميل" if person.is_customer else "مورد" if person.is_supplier else "شخص"
            results.append({
                'type': 'person',
                'title': person.name,
                'description': f'{person_type} - هاتف: {person.phone or "غير محدد"}',
                'url': f'/definitions/persons/{person.id}/',
                'icon': 'fas fa-user',
                'id': person.id
            })
        
        # البحث في المخازن
        warehouses = Warehouse.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:3]
        
        for warehouse in warehouses:
            results.append({
                'type': 'warehouse',
                'title': warehouse.name,
                'description': f'كود: {warehouse.code} - الموقع: {warehouse.location or "غير محدد"}',
                'url': f'/definitions/warehouses/{warehouse.id}/',
                'icon': 'fas fa-warehouse',
                'id': warehouse.id
            })
        
        # البحث في البنوك
        banks = Bank.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:3]
        
        for bank in banks:
            results.append({
                'type': 'bank',
                'title': bank.name,
                'description': f'كود: {bank.code}',
                'url': f'/definitions/banks/{bank.id}/',
                'icon': 'fas fa-university',
                'id': bank.id
            })
        
        # البحث في الخزائن
        treasuries = Treasury.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:3]
        
        for treasury in treasuries:
            results.append({
                'type': 'treasury',
                'title': treasury.name,
                'description': f'كود: {treasury.code}',
                'url': f'/definitions/treasuries/{treasury.id}/',
                'icon': 'fas fa-cash-register',
                'id': treasury.id
            })
        
        # البحث في فواتير المبيعات
        if SalesInvoice:
            try:
                sales_invoices = SalesInvoice.objects.filter(
                    Q(invoice_number__icontains=query) |
                    Q(customer__name__icontains=query)
                ).select_related('customer')[:3]

                for invoice in sales_invoices:
                    results.append({
                        'type': 'invoice',
                        'title': f'فاتورة مبيعات: {invoice.invoice_number}',
                        'description': f'العميل: {invoice.customer.name if invoice.customer else "غير محدد"} - التاريخ: {invoice.date}',
                        'url': f'/sales/invoices/{invoice.id}/',
                        'icon': 'fas fa-file-invoice',
                        'id': invoice.id
                    })
            except:
                pass
        
        # البحث في فواتير المشتريات
        if PurchaseInvoice:
            try:
                purchase_invoices = PurchaseInvoice.objects.filter(
                    Q(invoice_number__icontains=query) |
                    Q(supplier__name__icontains=query)
                ).select_related('supplier')[:3]

                for invoice in purchase_invoices:
                    results.append({
                        'type': 'invoice',
                        'title': f'فاتورة مشتريات: {invoice.invoice_number}',
                        'description': f'المورد: {invoice.supplier.name if invoice.supplier else "غير محدد"} - التاريخ: {invoice.date}',
                        'url': f'/purchases/invoices/{invoice.id}/',
                        'icon': 'fas fa-file-invoice',
                        'id': invoice.id
                    })
            except:
                pass
        
        # البحث في أذون المخزون
        try:
            stock_increases = StockIncrease.objects.filter(
                Q(increase_number__icontains=query) |
                Q(reason__icontains=query)
            ).select_related('warehouse')[:2]
            
            for increase in stock_increases:
                results.append({
                    'type': 'document',
                    'title': f'إذن زيادة: {increase.increase_number}',
                    'description': f'المخزن: {increase.warehouse.name} - السبب: {increase.reason}',
                    'url': f'/inventory/stock-increases/{increase.id}/',
                    'icon': 'fas fa-plus-circle',
                    'id': increase.id
                })
        except:
            pass
        
        # البحث في الأصول الثابتة
        if Asset:
            try:
                assets = Asset.objects.filter(
                    Q(name__icontains=query) |
                    Q(code__icontains=query)
                ).select_related('asset_group')[:3]

                for asset in assets:
                    results.append({
                        'type': 'asset',
                        'title': asset.name,
                        'description': f'كود: {asset.code} - المجموعة: {asset.asset_group.name if asset.asset_group else "غير محدد"}',
                        'url': f'/assets/assets/{asset.id}/',
                        'icon': 'fas fa-building',
                        'id': asset.id
                    })
            except:
                pass
        
        # البحث في الجرد الافتتاحي
        try:
            opening_inventories = PhysicalInventory.objects.filter(
                Q(inventory_number__icontains=query) &
                Q(inventory_type='OPENING')
            ).select_related('warehouse')[:2]
            
            for inventory in opening_inventories:
                results.append({
                    'type': 'inventory',
                    'title': f'جرد افتتاحي: {inventory.inventory_number}',
                    'description': f'المخزن: {inventory.warehouse.name} - السنة المالية: {inventory.financial_year}',
                    'url': f'/inventory/opening-inventory/{inventory.id}/',
                    'icon': 'fas fa-clipboard-list',
                    'id': inventory.id
                })
        except:
            pass
        
        return JsonResponse({
            'success': True,
            'query': query,
            'results': results,
            'total_count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'حدث خطأ أثناء البحث: {str(e)}',
            'results': []
        })


@login_required
@require_http_methods(["GET"])
def search_suggestions(request):
    """اقتراحات البحث السريع"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({
            'success': False,
            'suggestions': []
        })
    
    suggestions = []
    
    try:
        # اقتراحات من أسماء الأصناف
        items = Item.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:5]
        suggestions.extend([{'text': name, 'type': 'item'} for name in items])
        
        # اقتراحات من أسماء الأشخاص
        persons = Person.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:5]
        suggestions.extend([{'text': name, 'type': 'person'} for name in persons])
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions[:10]  # أقصى 10 اقتراحات
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e),
            'suggestions': []
        })


def search_app_sections(query):
    """البحث في أقسام وصفحات التطبيق"""
    query_lower = query.lower()

    # معالجة الكلمات المرادفة والمشابهة
    synonyms = {
        'مخزن': ['مستودع', 'مخازن', 'مستودعات', 'warehouse', 'stock'],
        'عميل': ['زبون', 'عملاء', 'زبائن', 'customer', 'client'],
        'مورد': ['موردين', 'supplier', 'vendor'],
        'فاتورة': ['فواتير', 'invoice', 'bill'],
        'صنف': ['منتج', 'اصناف', 'منتجات', 'item', 'product'],
        'بنك': ['بنوك', 'مصرف', 'bank'],
        'خزينة': ['خزائن', 'نقدية', 'treasury', 'cash'],
        'تقرير': ['تقارير', 'report', 'reports'],
        'حساب': ['حسابات', 'account', 'accounts'],
        'جرد': ['عد', 'inventory', 'count'],
        'مبيعات': ['بيع', 'sales', 'selling'],
        'مشتريات': ['شراء', 'purchases', 'buying'],
        'انتاج': ['تصنيع', 'production', 'manufacturing'],
        'اصول': ['اصل', 'assets', 'asset'],
        'فرع': ['فروع', 'branch', 'branches']
    }

    # توسيع البحث ليشمل المرادفات
    search_terms = [query_lower]
    for main_word, synonym_list in synonyms.items():
        if query_lower in main_word or main_word in query_lower:
            search_terms.extend(synonym_list)
        for synonym in synonym_list:
            if query_lower in synonym or synonym in query_lower:
                search_terms.append(main_word)
                search_terms.extend(synonym_list)
                break

    # قاموس أقسام التطبيق مع URLs والأوصاف
    app_sections = {
        # التعريفات
        'تعريفات': {
            'url': '/definitions/',
            'icon': 'fas fa-cogs',
            'description': 'إدارة التعريفات الأساسية للنظام',
            'keywords': ['تعريفات', 'اعدادات', 'settings', 'definitions']
        },
        'الأصناف': {
            'url': '/definitions/items/',
            'icon': 'fas fa-box',
            'description': 'إدارة أصناف المخزون والمنتجات',
            'keywords': ['اصناف', 'منتجات', 'مخزون', 'items', 'products']
        },
        'الأشخاص': {
            'url': '/definitions/persons/',
            'icon': 'fas fa-users',
            'description': 'إدارة العملاء والموردين',
            'keywords': ['اشخاص', 'عملاء', 'موردين', 'persons', 'customers', 'suppliers']
        },
        'المخازن': {
            'url': '/definitions/warehouses/',
            'icon': 'fas fa-warehouse',
            'description': 'إدارة المخازن ومواقع التخزين',
            'keywords': ['مخازن', 'مستودعات', 'warehouses', 'storage']
        },
        'البنوك': {
            'url': '/definitions/banks/',
            'icon': 'fas fa-university',
            'description': 'إدارة البنوك والحسابات المصرفية',
            'keywords': ['بنوك', 'حسابات', 'banks', 'accounts']
        },
        'الخزائن': {
            'url': '/definitions/treasuries/',
            'icon': 'fas fa-cash-register',
            'description': 'إدارة الخزائن والنقدية',
            'keywords': ['خزائن', 'نقدية', 'treasuries', 'cash']
        },

        # المخزون
        'المخزون': {
            'url': '/inventory/',
            'icon': 'fas fa-boxes',
            'description': 'إدارة المخزون والحركات',
            'keywords': ['مخزون', 'حركات', 'inventory', 'stock']
        },
        'أذون الزيادة': {
            'url': '/inventory/stock-increases/',
            'icon': 'fas fa-plus-circle',
            'description': 'أذون زيادة المخزون',
            'keywords': ['زيادة', 'اذون', 'increase', 'receipts']
        },
        'أذون النقص': {
            'url': '/inventory/stock-decreases/',
            'icon': 'fas fa-minus-circle',
            'description': 'أذون نقص المخزون',
            'keywords': ['نقص', 'اذون', 'decrease', 'issues']
        },
        'الجرد الفعلي': {
            'url': '/inventory/physical-inventory/',
            'icon': 'fas fa-clipboard-check',
            'description': 'الجرد الفعلي وتسجيل الفروق',
            'keywords': ['جرد', 'فعلي', 'physical', 'inventory', 'count']
        },
        'الجرد الافتتاحي': {
            'url': '/inventory/opening-inventory/',
            'icon': 'fas fa-clipboard-list',
            'description': 'الجرد الافتتاحي لأول المدة',
            'keywords': ['جرد', 'افتتاحي', 'opening', 'initial']
        },
        'التحويلات بين المخازن': {
            'url': '/inventory/transfers/',
            'icon': 'fas fa-exchange-alt',
            'description': 'تحويل البضائع بين المخازن',
            'keywords': ['تحويلات', 'نقل', 'transfers', 'move']
        },
        'الإنتاج': {
            'url': '/inventory/manufacturing/',
            'icon': 'fas fa-industry',
            'description': 'إدارة أوامر الإنتاج والتصنيع',
            'keywords': ['انتاج', 'تصنيع', 'manufacturing', 'production']
        },

        # المبيعات
        'المبيعات': {
            'url': '/sales/',
            'icon': 'fas fa-shopping-cart',
            'description': 'إدارة فواتير وعمليات المبيعات',
            'keywords': ['مبيعات', 'فواتير', 'sales', 'invoices']
        },
        'فواتير المبيعات': {
            'url': '/sales/invoices/',
            'icon': 'fas fa-file-invoice',
            'description': 'فواتير المبيعات للعملاء',
            'keywords': ['فواتير', 'مبيعات', 'sales', 'invoices']
        },
        'مردودات المبيعات': {
            'url': '/sales/returns/',
            'icon': 'fas fa-undo',
            'description': 'مردودات وإرجاعات المبيعات',
            'keywords': ['مردودات', 'ارجاعات', 'returns', 'refunds']
        },
        'عروض الأسعار': {
            'url': '/sales/quotations/',
            'icon': 'fas fa-file-contract',
            'description': 'عروض الأسعار للعملاء',
            'keywords': ['عروض', 'اسعار', 'quotations', 'quotes']
        },

        # المشتريات
        'المشتريات': {
            'url': '/purchases/',
            'icon': 'fas fa-shopping-bag',
            'description': 'إدارة فواتير وعمليات المشتريات',
            'keywords': ['مشتريات', 'فواتير', 'purchases', 'buying']
        },
        'فواتير المشتريات': {
            'url': '/purchases/invoices/',
            'icon': 'fas fa-file-invoice-dollar',
            'description': 'فواتير المشتريات من الموردين',
            'keywords': ['فواتير', 'مشتريات', 'purchases', 'invoices']
        },
        'مردودات المشتريات': {
            'url': '/purchases/returns/',
            'icon': 'fas fa-reply',
            'description': 'مردودات وإرجاعات المشتريات',
            'keywords': ['مردودات', 'ارجاعات', 'returns', 'refunds']
        },
        'طلبات الشراء': {
            'url': '/purchases/orders/',
            'icon': 'fas fa-clipboard-list',
            'description': 'طلبات الشراء من الموردين',
            'keywords': ['طلبات', 'شراء', 'orders', 'purchase']
        },

        # الخزينة
        'الخزينة': {
            'url': '/treasury/',
            'icon': 'fas fa-money-bill-wave',
            'description': 'إدارة المقبوضات والمدفوعات',
            'keywords': ['خزينة', 'مقبوضات', 'مدفوعات', 'treasury', 'payments']
        },
        'المقبوضات': {
            'url': '/treasury/receipts/',
            'icon': 'fas fa-hand-holding-usd',
            'description': 'سندات القبض والمقبوضات',
            'keywords': ['مقبوضات', 'سندات', 'receipts', 'income']
        },
        'المدفوعات': {
            'url': '/treasury/payments/',
            'icon': 'fas fa-credit-card',
            'description': 'سندات الصرف والمدفوعات',
            'keywords': ['مدفوعات', 'سندات', 'payments', 'expenses']
        },

        # البنوك
        'البنوك والحسابات': {
            'url': '/banks/',
            'icon': 'fas fa-university',
            'description': 'إدارة الحسابات المصرفية',
            'keywords': ['بنوك', 'حسابات', 'مصرفية', 'banks', 'accounts']
        },
        'الإيداعات': {
            'url': '/banks/deposits/',
            'icon': 'fas fa-piggy-bank',
            'description': 'إيداعات البنك',
            'keywords': ['ايداعات', 'بنك', 'deposits', 'bank']
        },
        'السحوبات': {
            'url': '/banks/withdrawals/',
            'icon': 'fas fa-money-check-alt',
            'description': 'سحوبات البنك',
            'keywords': ['سحوبات', 'بنك', 'withdrawals', 'bank']
        },

        # الأصول الثابتة
        'الأصول الثابتة': {
            'url': '/assets/',
            'icon': 'fas fa-building',
            'description': 'إدارة الأصول الثابتة والاستهلاك',
            'keywords': ['اصول', 'ثابتة', 'استهلاك', 'assets', 'depreciation']
        },

        # الحسابات العامة
        'الحسابات العامة': {
            'url': '/accounting/',
            'icon': 'fas fa-calculator',
            'description': 'القيود والحسابات العامة',
            'keywords': ['حسابات', 'قيود', 'accounting', 'journal']
        },
        'القيود اليومية': {
            'url': '/accounting/journal-entries/',
            'icon': 'fas fa-book',
            'description': 'القيود اليومية والمحاسبية',
            'keywords': ['قيود', 'يومية', 'journal', 'entries']
        },
        'الحسابات الختامية': {
            'url': '/accounting/final-accounts/',
            'icon': 'fas fa-chart-line',
            'description': 'الحسابات الختامية والميزانية',
            'keywords': ['ختامية', 'ميزانية', 'final', 'balance']
        },

        # التقارير
        'التقارير': {
            'url': '/reports/',
            'icon': 'fas fa-chart-bar',
            'description': 'التقارير والإحصائيات',
            'keywords': ['تقارير', 'احصائيات', 'reports', 'statistics']
        },
        'تقارير المبيعات': {
            'url': '/reports/sales/',
            'icon': 'fas fa-chart-pie',
            'description': 'تقارير المبيعات والأرباح',
            'keywords': ['تقارير', 'مبيعات', 'ارباح', 'sales', 'reports']
        },
        'تقارير المخزون': {
            'url': '/reports/inventory/',
            'icon': 'fas fa-boxes',
            'description': 'تقارير المخزون والحركات',
            'keywords': ['تقارير', 'مخزون', 'حركات', 'inventory', 'reports']
        },
        'تقارير المالية': {
            'url': '/reports/financial/',
            'icon': 'fas fa-money-bill',
            'description': 'التقارير المالية والمحاسبية',
            'keywords': ['تقارير', 'مالية', 'محاسبية', 'financial', 'reports']
        },

        # الفروع والمقار
        'الفروع والمقار': {
            'url': '/branches/',
            'icon': 'fas fa-sitemap',
            'description': 'إدارة الفروع والمقار',
            'keywords': ['فروع', 'مقار', 'branches', 'headquarters']
        },

        # الخدمات
        'الخدمات': {
            'url': '/services/',
            'icon': 'fas fa-tools',
            'description': 'خدمات النظام والصيانة',
            'keywords': ['خدمات', 'صيانة', 'services', 'maintenance']
        },
        'النسخ الاحتياطي': {
            'url': '/services/backup/',
            'icon': 'fas fa-download',
            'description': 'النسخ الاحتياطي للبيانات',
            'keywords': ['نسخ', 'احتياطي', 'backup', 'data']
        },
        'إعدادات النظام': {
            'url': '/services/settings/',
            'icon': 'fas fa-cog',
            'description': 'إعدادات وخيارات النظام',
            'keywords': ['اعدادات', 'خيارات', 'settings', 'options']
        },

        # النوافذ
        'النوافذ': {
            'url': '/windows/',
            'icon': 'fas fa-window-maximize',
            'description': 'إدارة النوافذ والواجهات',
            'keywords': ['نوافذ', 'واجهات', 'windows', 'interface']
        }
    }

    matching_sections = []

    for section_name, section_data in app_sections.items():
        section_matched = False
        match_type = 'description'

        # البحث في اسم القسم باستخدام جميع المصطلحات
        for term in search_terms:
            if term in section_name.lower():
                matching_sections.append({
                    'type': 'section',
                    'title': section_name,
                    'description': section_data['description'],
                    'url': section_data['url'],
                    'icon': section_data['icon'],
                    'match_type': 'name'
                })
                section_matched = True
                break

        if section_matched:
            continue

        # البحث في الكلمات المفتاحية
        for term in search_terms:
            for keyword in section_data['keywords']:
                if term in keyword.lower():
                    matching_sections.append({
                        'type': 'section',
                        'title': section_name,
                        'description': section_data['description'],
                        'url': section_data['url'],
                        'icon': section_data['icon'],
                        'match_type': 'keyword'
                    })
                    section_matched = True
                    break
            if section_matched:
                break

        if section_matched:
            continue

        # البحث في الوصف
        for term in search_terms:
            if term in section_data['description'].lower():
                matching_sections.append({
                    'type': 'section',
                    'title': section_name,
                    'description': section_data['description'],
                    'url': section_data['url'],
                    'icon': section_data['icon'],
                    'match_type': 'description'
                })
                break

    # ترتيب النتائج حسب نوع المطابقة
    matching_sections.sort(key=lambda x: {
        'name': 0,
        'keyword': 1,
        'description': 2
    }.get(x['match_type'], 3))

    return matching_sections[:8]  # أقصى 8 نتائج
