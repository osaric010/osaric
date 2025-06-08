from django import forms
from .models import Department, Position, SalarySystem, Employee
from definitions.models import Person


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['code', 'name', 'name_english', 'description', 'parent_department', 'manager']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'كود القسم'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم القسم'}),
            'name_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم بالإنجليزية'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف القسم'}),
            'parent_department': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['code', 'name', 'name_english', 'description', 'department']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'كود المنصب'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المنصب'}),
            'name_english': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم بالإنجليزية'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف المنصب'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }


class SalarySystemForm(forms.ModelForm):
    class Meta:
        model = SalarySystem
        fields = [
            'code', 'name', 'description', 'system_type', 'currency',
            'basic_salary', 'include_overtime', 'overtime_rate',
            'social_insurance_rate', 'tax_exemption'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'كود النظام'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم النظام'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف النظام'}),
            'system_type': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'include_overtime': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'overtime_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'social_insurance_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'tax_exemption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'person', 'employee_number', 'department', 'position', 'salary_system',
            'hire_date', 'contract_start_date', 'contract_end_date',
            'status', 'current_salary'
        ]
        widgets = {
            'person': forms.Select(attrs={'class': 'form-select'}),
            'employee_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الموظف'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'salary_system': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'current_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تصفية الأشخاص لإظهار الموظفين فقط أو الذين لم يتم تعيينهم بعد
        self.fields['person'].queryset = Person.objects.filter(
            person_type__in=['EMPLOYEE', 'OTHER']
        ).exclude(
            employee_profile__isnull=False
        )
