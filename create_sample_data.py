#!/usr/bin/env python
"""
إنشاء بيانات تجريبية لنظام حسابات أوساريك
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osaric_accounts.settings')
django.setup()

from django.contrib.auth.models import User
from definitions.models import Currency, Warehouse, ItemCategory, Unit, Item, Bank, Treasury
from sales.models import Customer, SalesInvoice, SalesInvoiceItem
from purchases.models import Supplier, PurchaseInvoice, PurchaseInvoiceItem
from inventory.models import Stock, StockMovement, StockMovementItem
from treasury.models import ExpenseType, RevenueType

def create_sample_data():
    print("إنشاء البيانات التجريبية...")
    
    # إنشاء العملات
    print("إنشاء العملات...")
    egp, created = Currency.objects.get_or_create(
        code='EGP',
        defaults={
            'name': 'الجنيه المصري',
            'symbol': 'ج.م',
            'exchange_rate': Decimal('1.0000'),
            'is_base_currency': True
        }
    )
    
    usd, created = Currency.objects.get_or_create(
        code='USD',
        defaults={
            'name': 'الدولار الأمريكي',
            'symbol': '$',
            'exchange_rate': Decimal('30.9000'),
            'is_base_currency': False
        }
    )
    
    # إنشاء المخازن
    print("إنشاء المخازن...")
    main_warehouse, created = Warehouse.objects.get_or_create(
        code='WH001',
        defaults={
            'name': 'المخزن الرئيسي',
            'location': 'القاهرة - مدينة نصر',
            'capacity': Decimal('10000.00')
        }
    )
    
    branch_warehouse, created = Warehouse.objects.get_or_create(
        code='WH002',
        defaults={
            'name': 'مخزن الفرع',
            'location': 'الجيزة - المهندسين',
            'capacity': Decimal('5000.00')
        }
    )
    
    # إنشاء فئات الأصناف
    print("إنشاء فئات الأصناف...")
    electronics_cat, created = ItemCategory.objects.get_or_create(
        code='ELEC',
        defaults={'name': 'إلكترونيات'}
    )
    
    office_cat, created = ItemCategory.objects.get_or_create(
        code='OFFICE',
        defaults={'name': 'مستلزمات مكتبية'}
    )
    
    # إنشاء وحدات القياس
    print("إنشاء وحدات القياس...")
    piece_unit, created = Unit.objects.get_or_create(
        code='PCS',
        defaults={'name': 'قطعة', 'symbol': 'قطعة'}
    )
    
    kg_unit, created = Unit.objects.get_or_create(
        code='KG',
        defaults={'name': 'كيلوجرام', 'symbol': 'كجم'}
    )
    
    # إنشاء الأصناف
    print("إنشاء الأصناف...")
    laptop, created = Item.objects.get_or_create(
        code='LAP001',
        defaults={
            'name': 'لابتوب ديل انسبايرون 15',
            'category': electronics_cat,
            'unit': piece_unit,
            'cost_price': Decimal('15000.00'),
            'selling_price': Decimal('18000.00'),
            'min_stock': Decimal('5.00'),
            'max_stock': Decimal('50.00')
        }
    )
    
    mouse, created = Item.objects.get_or_create(
        code='MOU001',
        defaults={
            'name': 'ماوس لاسلكي لوجيتك',
            'category': electronics_cat,
            'unit': piece_unit,
            'cost_price': Decimal('250.00'),
            'selling_price': Decimal('350.00'),
            'min_stock': Decimal('10.00'),
            'max_stock': Decimal('100.00')
        }
    )
    
    paper, created = Item.objects.get_or_create(
        code='PAP001',
        defaults={
            'name': 'ورق طباعة A4',
            'category': office_cat,
            'unit': kg_unit,
            'cost_price': Decimal('80.00'),
            'selling_price': Decimal('120.00'),
            'min_stock': Decimal('20.00'),
            'max_stock': Decimal('200.00')
        }
    )
    
    # إنشاء البنوك
    print("إنشاء البنوك...")
    nbe_bank, created = Bank.objects.get_or_create(
        code='NBE001',
        defaults={
            'name': 'البنك الأهلي المصري',
            'branch': 'فرع مدينة نصر',
            'account_number': '123456789',
            'account_name': 'شركة أوساريك للتجارة',
            'currency': egp,
            'balance': Decimal('500000.00')
        }
    )
    
    # إنشاء الخزائن
    print("إنشاء الخزائن...")
    main_treasury, created = Treasury.objects.get_or_create(
        code='TRS001',
        defaults={
            'name': 'الخزينة الرئيسية',
            'currency': egp,
            'balance': Decimal('50000.00'),
            'location': 'المكتب الرئيسي'
        }
    )
    
    # إنشاء العملاء
    print("إنشاء العملاء...")
    customer1, created = Customer.objects.get_or_create(
        code='CUS001',
        defaults={
            'name': 'شركة التقنية المتقدمة',
            'contact_person': 'أحمد محمد',
            'phone': '01234567890',
            'email': 'ahmed@tech-advanced.com',
            'address': 'القاهرة الجديدة',
            'credit_limit': Decimal('100000.00'),
            'payment_terms': 30
        }
    )
    
    customer2, created = Customer.objects.get_or_create(
        code='CUS002',
        defaults={
            'name': 'مؤسسة النور للتجارة',
            'contact_person': 'فاطمة علي',
            'phone': '01098765432',
            'email': 'fatma@alnour.com',
            'address': 'الإسكندرية',
            'credit_limit': Decimal('50000.00'),
            'payment_terms': 15
        }
    )
    
    # إنشاء الموردين
    print("إنشاء الموردين...")
    supplier1, created = Supplier.objects.get_or_create(
        code='SUP001',
        defaults={
            'name': 'شركة الإلكترونيات الحديثة',
            'contact_person': 'محمد أحمد',
            'phone': '01111111111',
            'email': 'mohamed@modern-electronics.com',
            'address': 'القاهرة',
            'credit_limit': Decimal('200000.00'),
            'payment_terms': 45
        }
    )
    
    # إنشاء أرصدة المخزون
    print("إنشاء أرصدة المخزون...")
    Stock.objects.get_or_create(
        warehouse=main_warehouse,
        item=laptop,
        defaults={
            'quantity': Decimal('25.00'),
            'average_cost': Decimal('15000.00')
        }
    )
    
    Stock.objects.get_or_create(
        warehouse=main_warehouse,
        item=mouse,
        defaults={
            'quantity': Decimal('50.00'),
            'average_cost': Decimal('250.00')
        }
    )
    
    Stock.objects.get_or_create(
        warehouse=main_warehouse,
        item=paper,
        defaults={
            'quantity': Decimal('100.00'),
            'average_cost': Decimal('80.00')
        }
    )
    
    # إنشاء أنواع المصروفات والإيرادات
    print("إنشاء أنواع المصروفات والإيرادات...")
    ExpenseType.objects.get_or_create(
        code='RENT',
        defaults={'name': 'إيجار'}
    )
    
    ExpenseType.objects.get_or_create(
        code='UTIL',
        defaults={'name': 'مرافق'}
    )
    
    RevenueType.objects.get_or_create(
        code='SALES',
        defaults={'name': 'إيرادات مبيعات'}
    )
    
    RevenueType.objects.get_or_create(
        code='OTHER',
        defaults={'name': 'إيرادات أخرى'}
    )
    
    # إنشاء بعض فواتير المبيعات التجريبية
    print("إنشاء فواتير مبيعات تجريبية...")
    today = date.today()
    
    for i in range(5):
        invoice_date = today - timedelta(days=i)
        invoice, created = SalesInvoice.objects.get_or_create(
            invoice_number=f'SAL{(today - timedelta(days=i)).strftime("%Y%m%d")}{i+1:03d}',
            defaults={
                'date': invoice_date,
                'customer': customer1 if i % 2 == 0 else customer2,
                'warehouse': main_warehouse,
                'currency': egp,
                'status': 'CONFIRMED',
                'subtotal': Decimal('18000.00'),
                'total_amount': Decimal('18000.00')
            }
        )
        
        if created:
            SalesInvoiceItem.objects.create(
                invoice=invoice,
                item=laptop,
                quantity=Decimal('1.00'),
                unit_price=Decimal('18000.00'),
                total_amount=Decimal('18000.00')
            )
    
    print("تم إنشاء البيانات التجريبية بنجاح!")

if __name__ == '__main__':
    create_sample_data()
