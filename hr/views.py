from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Department, Position, SalarySystem, Employee
from .forms import DepartmentForm, PositionForm, SalarySystemForm, EmployeeForm


@login_required
def dashboard(request):
    """لوحة تحكم شؤون العاملين"""
    # إحصائيات عامة
    total_employees = Employee.objects.filter(is_active=True).count()
    active_employees = Employee.objects.filter(status='ACTIVE', is_active=True).count()
    total_departments = Department.objects.filter(is_active=True).count()
    total_positions = Position.objects.filter(is_active=True).count()
    total_salary_systems = SalarySystem.objects.filter(is_active=True).count()

    # الموظفين الجدد (آخر 30 يوم)
    from datetime import date, timedelta
    thirty_days_ago = date.today() - timedelta(days=30)
    new_employees = Employee.objects.filter(
        hire_date__gte=thirty_days_ago,
        is_active=True
    ).count()

    # توزيع الموظفين حسب الأقسام
    departments_stats = Department.objects.filter(is_active=True).annotate(
        employee_count=Count('employees', filter=Q(employees__is_active=True))
    ).order_by('-employee_count')[:5]

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_departments': total_departments,
        'total_positions': total_positions,
        'total_salary_systems': total_salary_systems,
        'new_employees': new_employees,
        'departments_stats': departments_stats,
    }
    return render(request, 'hr/dashboard.html', context)


# أنظمة صرف المرتبات
@login_required
def salary_system_list(request):
    """قائمة أنظمة صرف المرتبات"""
    search_query = request.GET.get('search', '')
    system_type_filter = request.GET.get('system_type', '')

    salary_systems = SalarySystem.objects.filter(is_active=True)

    if search_query:
        salary_systems = salary_systems.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )

    if system_type_filter:
        salary_systems = salary_systems.filter(system_type=system_type_filter)

    salary_systems = salary_systems.order_by('name')

    # Pagination
    paginator = Paginator(salary_systems, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'system_type_filter': system_type_filter,
        'system_types': SalarySystem.SYSTEM_TYPES,
    }
    return render(request, 'hr/salary_system_list.html', context)


@login_required
def salary_system_create(request):
    """إضافة نظام صرف مرتب جديد"""
    if request.method == 'POST':
        form = SalarySystemForm(request.POST)
        if form.is_valid():
            salary_system = form.save(commit=False)
            salary_system.created_by = request.user
            salary_system.save()
            messages.success(request, 'تم إضافة نظام صرف المرتب بنجاح')
            return redirect('hr:salary_system_list')
    else:
        form = SalarySystemForm()

    context = {
        'form': form,
        'title': 'إضافة نظام صرف مرتب جديد',
        'action': 'إضافة'
    }
    return render(request, 'hr/salary_system_form.html', context)


@login_required
def salary_system_detail(request, pk):
    """تفاصيل نظام صرف المرتب"""
    salary_system = get_object_or_404(SalarySystem, pk=pk)
    employees = salary_system.employees.filter(is_active=True)

    context = {
        'salary_system': salary_system,
        'employees': employees,
    }
    return render(request, 'hr/salary_system_detail.html', context)


@login_required
def salary_system_edit(request, pk):
    """تعديل نظام صرف المرتب"""
    salary_system = get_object_or_404(SalarySystem, pk=pk)

    if request.method == 'POST':
        form = SalarySystemForm(request.POST, instance=salary_system)
        if form.is_valid():
            salary_system = form.save(commit=False)
            salary_system.updated_by = request.user
            salary_system.save()
            messages.success(request, 'تم تحديث نظام صرف المرتب بنجاح')
            return redirect('hr:salary_system_detail', pk=salary_system.pk)
    else:
        form = SalarySystemForm(instance=salary_system)

    context = {
        'form': form,
        'salary_system': salary_system,
        'title': f'تعديل نظام صرف المرتب: {salary_system.name}',
        'action': 'تحديث'
    }
    return render(request, 'hr/salary_system_form.html', context)


@login_required
@require_http_methods(["POST"])
def salary_system_delete(request, pk):
    """حذف نظام صرف المرتب"""
    salary_system = get_object_or_404(SalarySystem, pk=pk)

    # التحقق من عدم وجود موظفين مرتبطين
    if salary_system.employees.exists():
        return JsonResponse({
            'success': False,
            'message': 'لا يمكن حذف نظام صرف المرتب لوجود موظفين مرتبطين به'
        })

    salary_system.is_active = False
    salary_system.updated_by = request.user
    salary_system.save()

    return JsonResponse({
        'success': True,
        'message': 'تم حذف نظام صرف المرتب بنجاح'
    })


# الأقسام
@login_required
def department_list(request):
    """قائمة الأقسام"""
    search_query = request.GET.get('search', '')

    departments = Department.objects.filter(is_active=True)

    if search_query:
        departments = departments.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(name_english__icontains=search_query)
        )

    departments = departments.order_by('name')

    # Pagination
    paginator = Paginator(departments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'hr/department_list.html', context)


@login_required
def department_create(request):
    """إضافة قسم جديد"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.created_by = request.user
            department.save()
            messages.success(request, 'تم إضافة القسم بنجاح')
            return redirect('hr:department_list')
    else:
        form = DepartmentForm()

    context = {
        'form': form,
        'title': 'إضافة قسم جديد',
        'action': 'إضافة'
    }
    return render(request, 'hr/department_form.html', context)


@login_required
def department_detail(request, pk):
    """تفاصيل القسم"""
    department = get_object_or_404(Department, pk=pk)
    employees = department.employees.filter(is_active=True)
    positions = department.positions.filter(is_active=True)
    sub_departments = department.sub_departments.filter(is_active=True)

    context = {
        'department': department,
        'employees': employees,
        'positions': positions,
        'sub_departments': sub_departments,
    }
    return render(request, 'hr/department_detail.html', context)


@login_required
def department_edit(request, pk):
    """تعديل القسم"""
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save(commit=False)
            department.updated_by = request.user
            department.save()
            messages.success(request, 'تم تحديث القسم بنجاح')
            return redirect('hr:department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)

    context = {
        'form': form,
        'department': department,
        'title': f'تعديل القسم: {department.name}',
        'action': 'تحديث'
    }
    return render(request, 'hr/department_form.html', context)


@login_required
@require_http_methods(["POST"])
def department_delete(request, pk):
    """حذف القسم"""
    department = get_object_or_404(Department, pk=pk)

    # التحقق من عدم وجود موظفين أو مناصب مرتبطة
    if department.employees.exists() or department.positions.exists():
        return JsonResponse({
            'success': False,
            'message': 'لا يمكن حذف القسم لوجود موظفين أو مناصب مرتبطة به'
        })

    department.is_active = False
    department.updated_by = request.user
    department.save()

    return JsonResponse({
        'success': True,
        'message': 'تم حذف القسم بنجاح'
    })


# المناصب
@login_required
def position_list(request):
    """قائمة المناصب"""
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')

    positions = Position.objects.filter(is_active=True).select_related('department')

    if search_query:
        positions = positions.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(name_english__icontains=search_query)
        )

    if department_filter:
        positions = positions.filter(department_id=department_filter)

    positions = positions.order_by('name')

    # Pagination
    paginator = Paginator(positions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # للفلترة
    departments = Department.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
        'departments': departments,
    }
    return render(request, 'hr/position_list.html', context)


@login_required
def position_create(request):
    """إضافة منصب جديد"""
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.created_by = request.user
            position.save()
            messages.success(request, 'تم إضافة المنصب بنجاح')
            return redirect('hr:position_list')
    else:
        form = PositionForm()

    context = {
        'form': form,
        'title': 'إضافة منصب جديد',
        'action': 'إضافة'
    }
    return render(request, 'hr/position_form.html', context)


@login_required
def position_detail(request, pk):
    """تفاصيل المنصب"""
    position = get_object_or_404(Position, pk=pk)
    employees = position.employees.filter(is_active=True)

    context = {
        'position': position,
        'employees': employees,
    }
    return render(request, 'hr/position_detail.html', context)


@login_required
def position_edit(request, pk):
    """تعديل المنصب"""
    position = get_object_or_404(Position, pk=pk)

    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save(commit=False)
            position.updated_by = request.user
            position.save()
            messages.success(request, 'تم تحديث المنصب بنجاح')
            return redirect('hr:position_detail', pk=position.pk)
    else:
        form = PositionForm(instance=position)

    context = {
        'form': form,
        'position': position,
        'title': f'تعديل المنصب: {position.name}',
        'action': 'تحديث'
    }
    return render(request, 'hr/position_form.html', context)


@login_required
@require_http_methods(["POST"])
def position_delete(request, pk):
    """حذف المنصب"""
    position = get_object_or_404(Position, pk=pk)

    # التحقق من عدم وجود موظفين مرتبطين
    if position.employees.exists():
        return JsonResponse({
            'success': False,
            'message': 'لا يمكن حذف المنصب لوجود موظفين مرتبطين به'
        })

    position.is_active = False
    position.updated_by = request.user
    position.save()

    return JsonResponse({
        'success': True,
        'message': 'تم حذف المنصب بنجاح'
    })


# الموظفين
@login_required
def employee_list(request):
    """قائمة الموظفين"""
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')

    employees = Employee.objects.filter(is_active=True).select_related(
        'person', 'department', 'position', 'salary_system'
    )

    if search_query:
        employees = employees.filter(
            Q(employee_number__icontains=search_query) |
            Q(person__name__icontains=search_query) |
            Q(person__name_english__icontains=search_query) |
            Q(person__phone__icontains=search_query) |
            Q(person__mobile__icontains=search_query)
        )

    if department_filter:
        employees = employees.filter(department_id=department_filter)

    if status_filter:
        employees = employees.filter(status=status_filter)

    employees = employees.order_by('employee_number')

    # Pagination
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # للفلترة
    departments = Department.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
        'departments': departments,
        'status_choices': Employee.STATUS_CHOICES,
    }
    return render(request, 'hr/employee_list.html', context)


@login_required
def employee_create(request):
    """إضافة موظف جديد"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.created_by = request.user
            employee.save()
            messages.success(request, 'تم إضافة الموظف بنجاح')
            return redirect('hr:employee_list')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
        'title': 'إضافة موظف جديد',
        'action': 'إضافة'
    }
    return render(request, 'hr/employee_form.html', context)


@login_required
def employee_detail(request, pk):
    """تفاصيل الموظف"""
    employee = get_object_or_404(Employee, pk=pk)

    context = {
        'employee': employee,
    }
    return render(request, 'hr/employee_detail.html', context)


@login_required
def employee_edit(request, pk):
    """تعديل الموظف"""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.updated_by = request.user
            employee.save()
            messages.success(request, 'تم تحديث بيانات الموظف بنجاح')
            return redirect('hr:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'title': f'تعديل الموظف: {employee.full_name}',
        'action': 'تحديث'
    }
    return render(request, 'hr/employee_form.html', context)


@login_required
@require_http_methods(["POST"])
def employee_delete(request, pk):
    """حذف الموظف"""
    employee = get_object_or_404(Employee, pk=pk)

    employee.is_active = False
    employee.updated_by = request.user
    employee.save()

    return JsonResponse({
        'success': True,
        'message': 'تم حذف الموظف بنجاح'
    })
