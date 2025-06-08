from django import forms
from django.contrib.auth.models import User
from .models import (
    Supplier, PurchaseInvoice, PurchaseReturn, PurchaseOrder, EarnedDiscount
)
from definitions.models import Item, Warehouse, Currency


class SupplierForm(forms.ModelForm):
    """نموذج الموردين"""
    
    class Meta:
        model = Supplier
        fields = [
            'code', 'name', 'contact_person', 'phone', 'email', 'address',
            'tax_number', 'credit_limit', 'payment_terms'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'كود المورد'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المورد'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الشخص المسؤول'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'العنوان'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الرقم الضريبي'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'payment_terms': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class PurchaseInvoiceForm(forms.ModelForm):
    """نموذج فواتير المشتريات"""
    
    class Meta:
        model = PurchaseInvoice
        fields = [
            'invoice_number', 'supplier_invoice_number', 'date', 'supplier',
            'warehouse', 'currency', 'exchange_rate', 'due_date', 'notes'
        ]
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الفاتورة'}),
            'supplier_invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم فاتورة المورد'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0.0001'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.all()
        self.fields['warehouse'].queryset = Warehouse.objects.all()
        self.fields['currency'].queryset = Currency.objects.all()


class PurchaseReturnForm(forms.ModelForm):
    """نموذج مرتجعات المشتريات"""
    
    class Meta:
        model = PurchaseReturn
        fields = [
            'return_number', 'date', 'original_invoice', 'supplier',
            'warehouse', 'reason', 'notes'
        ]
        widgets = {
            'return_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم المرتجع'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'original_invoice': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'سبب الإرجاع'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original_invoice'].queryset = PurchaseInvoice.objects.all()
        self.fields['supplier'].queryset = Supplier.objects.all()
        self.fields['warehouse'].queryset = Warehouse.objects.all()


class PurchaseOrderForm(forms.ModelForm):
    """نموذج أوامر الشراء"""
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'order_number', 'date', 'supplier', 'warehouse',
            'expected_delivery_date', 'notes'
        ]
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الأمر'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.all()
        self.fields['warehouse'].queryset = Warehouse.objects.all()


class EarnedDiscountForm(forms.ModelForm):
    """نموذج الخصم المكتسب"""
    
    class Meta:
        model = EarnedDiscount
        fields = [
            'discount_number', 'date', 'supplier', 'discount_type',
            'reference_invoice', 'reference_order', 'discount_percentage',
            'discount_amount', 'base_amount', 'minimum_quantity',
            'minimum_amount', 'payment_days', 'valid_from', 'valid_until',
            'description', 'notes'
        ]
        widgets = {
            'discount_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الخصم'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'reference_invoice': forms.Select(attrs={'class': 'form-select'}),
            'reference_order': forms.Select(attrs={'class': 'form-select'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'base_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'minimum_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'payment_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'الوصف'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.all()
        self.fields['reference_invoice'].queryset = PurchaseInvoice.objects.all()
        self.fields['reference_order'].queryset = PurchaseOrder.objects.all()


class PurchaseReportForm(forms.Form):
    """نموذج تقارير المشتريات"""
    start_date = forms.DateField(
        label="من تاريخ",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label="إلى تاريخ",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="جميع الموردين",
        label="المورد",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + PurchaseInvoice._meta.get_field('status').choices,
        required=False,
        label="الحالة",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class SupplierPerformanceReportForm(forms.Form):
    """نموذج تقرير أداء الموردين"""
    start_date = forms.DateField(
        label="من تاريخ",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label="إلى تاريخ",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="جميع الموردين",
        label="المورد",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class EarnedDiscountReportForm(forms.Form):
    """نموذج تقرير الخصومات المكتسبة"""
    start_date = forms.DateField(
        label="من تاريخ",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        label="إلى تاريخ",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="جميع الموردين",
        label="المورد",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    discount_type = forms.ChoiceField(
        choices=[('', 'جميع الأنواع')] + EarnedDiscount.DISCOUNT_TYPE_CHOICES,
        required=False,
        label="نوع الخصم",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + EarnedDiscount._meta.get_field('status').choices,
        required=False,
        label="الحالة",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
