from django import forms
from django.utils import timezone
from .models import (
    Customer, SalesInvoice, SalesInvoiceItem, SalesReturn, SalesReturnItem,
    PriceList, PriceListItem, Quotation, QuotationItem, DiscountPolicy
)


class CustomerForm(forms.ModelForm):
    """نموذج العملاء"""

    class Meta:
        model = Customer
        fields = [
            'code', 'name', 'contact_person', 'phone', 'email', 'address',
            'tax_number', 'credit_limit', 'payment_terms', 'discount_percentage'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'كود العميل'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العميل'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الشخص المسؤول'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'العنوان'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الرقم الضريبي'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'payment_terms': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class SalesInvoiceForm(forms.ModelForm):
    """نموذج فاتورة المبيعات"""

    class Meta:
        model = SalesInvoice
        fields = [
            'invoice_number', 'date', 'customer', 'warehouse', 'currency',
            'exchange_rate', 'due_date', 'notes', 'salesperson'
        ]
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الفاتورة'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات'}),
            'salesperson': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()


class SalesInvoiceItemForm(forms.ModelForm):
    """نموذج صنف فاتورة المبيعات"""

    class Meta:
        model = SalesInvoiceItem
        fields = ['item', 'quantity', 'unit_price', 'discount_percentage', 'tax_percentage']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class SalesReturnForm(forms.ModelForm):
    """نموذج مرتجع المبيعات"""

    class Meta:
        model = SalesReturn
        fields = [
            'return_number', 'date', 'original_invoice', 'customer',
            'warehouse', 'reason', 'notes'
        ]
        widgets = {
            'return_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم المرتجع'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'original_invoice': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'سبب الإرجاع'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()


class SalesReturnItemForm(forms.ModelForm):
    """نموذج صنف مرتجع المبيعات"""

    class Meta:
        model = SalesReturnItem
        fields = ['item', 'quantity', 'unit_price']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class PriceListForm(forms.ModelForm):
    """نموذج قائمة الأسعار"""

    class Meta:
        model = PriceList
        fields = [
            'code', 'name', 'description', 'start_date', 'end_date',
            'is_default', 'currency', 'price_type'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'كود قائمة الأسعار'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم قائمة الأسعار'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'الوصف'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'price_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and start_date and end_date <= start_date:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')

        return cleaned_data


class PriceListItemForm(forms.ModelForm):
    """نموذج عنصر قائمة الأسعار"""

    class Meta:
        model = PriceListItem
        fields = ['item', 'unit_price', 'min_quantity', 'max_discount_percentage']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'max_discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class QuotationForm(forms.ModelForm):
    """نموذج عرض السعر"""

    class Meta:
        model = Quotation
        fields = [
            'quotation_number', 'date', 'customer', 'currency', 'exchange_rate',
            'valid_until', 'terms_and_conditions', 'notes', 'salesperson'
        ]
        widgets = {
            'quotation_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم عرض السعر'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'exchange_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'الشروط والأحكام'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات'}),
            'salesperson': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
            # تعيين تاريخ انتهاء الصلاحية بعد 30 يوم
            self.fields['valid_until'].initial = timezone.now().date() + timezone.timedelta(days=30)


class QuotationItemForm(forms.ModelForm):
    """نموذج صنف عرض السعر"""

    class Meta:
        model = QuotationItem
        fields = [
            'item', 'quantity', 'unit_price', 'discount_percentage',
            'tax_percentage', 'description', 'delivery_time'
        ]
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'وصف إضافي'}),
            'delivery_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مدة التسليم'}),
        }


class DiscountPolicyForm(forms.ModelForm):
    """نموذج سياسة الخصم"""

    class Meta:
        model = DiscountPolicy
        fields = [
            'name', 'description', 'discount_type', 'discount_percentage',
            'discount_amount', 'min_quantity', 'min_amount', 'start_date',
            'end_date', 'applicable_customers', 'applicable_items'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم السياسة'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'الوصف'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'min_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'applicable_customers': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'applicable_items': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and start_date and end_date <= start_date:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')

        return cleaned_data


class PriceDisplayForm(forms.Form):
    """نموذج عرض الأسعار"""
    item = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="الصنف"
    )
    price_list = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="قائمة الأسعار",
        required=False
    )
    customer = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="العميل",
        required=False
    )
    quantity = forms.DecimalField(
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
        label="الكمية"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from definitions.models import Item
        self.fields['item'].queryset = Item.objects.all()
        self.fields['price_list'].queryset = PriceList.objects.all()
        self.fields['customer'].queryset = Customer.objects.all()


class QuotationPeriodReportForm(forms.Form):
    """نموذج تقرير عروض الأسعار خلال فترة"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="من تاريخ"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="إلى تاريخ"
    )
    customer = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="العميل",
        required=False
    )
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + Quotation._meta.get_field('status').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="الحالة",
        required=False
    )
    salesperson = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="مندوب المبيعات",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import User
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['salesperson'].queryset = User.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد أو يساوي تاريخ البداية')

        return cleaned_data
