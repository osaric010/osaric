#!/usr/bin/env python
"""
إنشاء بيانات تجريبية لتطبيق شؤون العاملين
"""

import os
import sys
import django
from decimal import Decimal

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osaric_accounts.settings')
django.setup()

from django.contrib.auth.models import User
from definitions.models import Currency, Person
from hr.models import Department, Position, SalarySystem, Employee


def create_sample_data():
    """إنشاء بيانات تجريبية"""
    
    print("إنشاء بيانات تجريبية لشؤون العاملين...")
    
    # الحصول على العملة الافتراضية
    currency, created = Currency.objects.get_or_create(
        code='EGP',
        defaults={
            'name': 'الجنيه المصري',
            'symbol': 'ج.م',
            'exchange_rate': Decimal('1.0000'),
            'is_base_currency': True,
        }
    )
    
    # إنشاء الأقسام
    departments_data = [
        {'code': 'HR', 'name': 'الموارد البشرية', 'name_english': 'Human Resources'},
        {'code': 'IT', 'name': 'تقنية المعلومات', 'name_english': 'Information Technology'},
        {'code': 'FIN', 'name': 'المالية والمحاسبة', 'name_english': 'Finance & Accounting'},
        {'code': 'SALES', 'name': 'المبيعات', 'name_english': 'Sales'},
        {'code': 'ADMIN', 'name': 'الإدارة العامة', 'name_english': 'Administration'},
    ]
    
    departments = {}
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
        departments[dept_data['code']] = dept
        if created:
            print(f"تم إنشاء القسم: {dept.name}")
    
    # إنشاء المناصب
    positions_data = [
        {'code': 'MGR', 'name': 'مدير', 'department': 'ADMIN'},
        {'code': 'ASST_MGR', 'name': 'مساعد مدير', 'department': 'ADMIN'},
        {'code': 'HR_SPEC', 'name': 'أخصائي موارد بشرية', 'department': 'HR'},
        {'code': 'IT_SPEC', 'name': 'أخصائي تقنية معلومات', 'department': 'IT'},
        {'code': 'ACCOUNTANT', 'name': 'محاسب', 'department': 'FIN'},
        {'code': 'SALES_REP', 'name': 'مندوب مبيعات', 'department': 'SALES'},
        {'code': 'CLERK', 'name': 'موظف إداري', 'department': 'ADMIN'},
    ]
    
    positions = {}
    for pos_data in positions_data:
        dept_code = pos_data.pop('department')
        pos_data['department'] = departments[dept_code]
        pos, created = Position.objects.get_or_create(
            code=pos_data['code'],
            defaults=pos_data
        )
        positions[pos_data['code']] = pos
        if created:
            print(f"تم إنشاء المنصب: {pos.name}")
    
    # إنشاء أنظمة صرف المرتبات
    salary_systems_data = [
        {
            'code': 'MONTHLY_BASIC',
            'name': 'نظام المرتب الشهري الأساسي',
            'description': 'نظام مرتب شهري أساسي للموظفين الإداريين',
            'system_type': 'MONTHLY',
            'currency': currency,
            'basic_salary': Decimal('5000.00'),
            'include_overtime': True,
            'overtime_rate': Decimal('1.5'),
            'social_insurance_rate': Decimal('14.0'),
            'tax_exemption': Decimal('9000.00'),
        },
        {
            'code': 'MONTHLY_SENIOR',
            'name': 'نظام المرتب الشهري للمناصب العليا',
            'description': 'نظام مرتب شهري للمدراء والمناصب العليا',
            'system_type': 'MONTHLY',
            'currency': currency,
            'basic_salary': Decimal('12000.00'),
            'include_overtime': False,
            'overtime_rate': Decimal('1.0'),
            'social_insurance_rate': Decimal('14.0'),
            'tax_exemption': Decimal('9000.00'),
        },
        {
            'code': 'HOURLY_TEMP',
            'name': 'نظام الأجر بالساعة',
            'description': 'نظام أجر بالساعة للموظفين المؤقتين',
            'system_type': 'HOURLY',
            'currency': currency,
            'basic_salary': Decimal('25.00'),
            'include_overtime': True,
            'overtime_rate': Decimal('1.5'),
            'social_insurance_rate': Decimal('14.0'),
            'tax_exemption': Decimal('0.00'),
        },
    ]
    
    salary_systems = {}
    for sys_data in salary_systems_data:
        sys, created = SalarySystem.objects.get_or_create(
            code=sys_data['code'],
            defaults=sys_data
        )
        salary_systems[sys_data['code']] = sys
        if created:
            print(f"تم إنشاء نظام صرف المرتب: {sys.name}")
    
    # إنشاء أشخاص موظفين
    employees_data = [
        {
            'person_data': {
                'code': 'EMP001',
                'name': 'أحمد محمد علي',
                'name_english': 'Ahmed Mohamed Ali',
                'person_type': 'EMPLOYEE',
                'entity_type': 'INDIVIDUAL',
                'phone': '0123456789',
                'mobile': '01012345678',
                'email': 'ahmed.ali@company.com',
                'address': 'القاهرة، مصر',
                'city': 'القاهرة',
                'country': 'مصر',
            },
            'employee_data': {
                'employee_number': 'EMP001',
                'department': departments['IT'],
                'position': positions['IT_SPEC'],
                'salary_system': salary_systems['MONTHLY_BASIC'],
                'hire_date': '2023-01-15',
                'current_salary': Decimal('6000.00'),
                'status': 'ACTIVE',
            }
        },
        {
            'person_data': {
                'code': 'EMP002',
                'name': 'فاطمة أحمد محمود',
                'name_english': 'Fatma Ahmed Mahmoud',
                'person_type': 'EMPLOYEE',
                'entity_type': 'INDIVIDUAL',
                'phone': '0123456790',
                'mobile': '01012345679',
                'email': 'fatma.mahmoud@company.com',
                'address': 'الجيزة، مصر',
                'city': 'الجيزة',
                'country': 'مصر',
            },
            'employee_data': {
                'employee_number': 'EMP002',
                'department': departments['HR'],
                'position': positions['HR_SPEC'],
                'salary_system': salary_systems['MONTHLY_BASIC'],
                'hire_date': '2023-02-01',
                'current_salary': Decimal('5500.00'),
                'status': 'ACTIVE',
            }
        },
        {
            'person_data': {
                'code': 'EMP003',
                'name': 'محمد سعد إبراهيم',
                'name_english': 'Mohamed Saad Ibrahim',
                'person_type': 'EMPLOYEE',
                'entity_type': 'INDIVIDUAL',
                'phone': '0123456791',
                'mobile': '01012345680',
                'email': 'mohamed.ibrahim@company.com',
                'address': 'الإسكندرية، مصر',
                'city': 'الإسكندرية',
                'country': 'مصر',
            },
            'employee_data': {
                'employee_number': 'EMP003',
                'department': departments['ADMIN'],
                'position': positions['MGR'],
                'salary_system': salary_systems['MONTHLY_SENIOR'],
                'hire_date': '2022-06-01',
                'current_salary': Decimal('15000.00'),
                'status': 'ACTIVE',
            }
        },
    ]
    
    # إنشاء الموظفين
    for emp_data in employees_data:
        # إنشاء الشخص
        person, created = Person.objects.get_or_create(
            code=emp_data['person_data']['code'],
            defaults=emp_data['person_data']
        )
        if created:
            print(f"تم إنشاء الشخص: {person.name}")
        
        # إنشاء الموظف
        emp_data['employee_data']['person'] = person
        employee, created = Employee.objects.get_or_create(
            employee_number=emp_data['employee_data']['employee_number'],
            defaults=emp_data['employee_data']
        )
        if created:
            print(f"تم إنشاء الموظف: {employee.full_name}")
    
    print("\nتم إنشاء البيانات التجريبية بنجاح!")
    print(f"الأقسام: {Department.objects.count()}")
    print(f"المناصب: {Position.objects.count()}")
    print(f"أنظمة صرف المرتبات: {SalarySystem.objects.count()}")
    print(f"الموظفين: {Employee.objects.count()}")


if __name__ == '__main__':
    create_sample_data()
