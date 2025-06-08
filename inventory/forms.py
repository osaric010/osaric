from django import forms
from django.forms import inlineformset_factory
from .models import (StockIncrease, StockIncreaseItem, StockDecrease, StockDecreaseItem,
                    GoodsReceivedOnLoan, GoodsReceivedOnLoanItem,
                    GoodsIssuedOnLoan, GoodsIssuedOnLoanItem,
                    WarehouseTransfer, WarehouseTransferItem,
                    ItemTransformation, ItemTransformationInput, ItemTransformationOutput,
                    ManufacturingOrder, ManufacturingOrderMaterial,
                    PhysicalInventory, PhysicalInventoryItem)
from definitions.models import Warehouse, Item


class StockIncreaseForm(forms.ModelForm):
    """نموذج إذن إضافة الزيادات"""
    
    class Meta:
        model = StockIncrease
        fields = ['increase_number', 'date', 'warehouse', 'reason', 'notes']
        widgets = {
            'increase_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل سبب الزيادة'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date
            self.fields['date'].initial = date.today()
            
        # إنشاء رقم إذن تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['increase_number'].initial = f'INC-{timestamp}'


class StockIncreaseItemForm(forms.ModelForm):
    """نموذج أصناف إذن الزيادات"""
    
    class Meta:
        model = StockIncreaseItem
        fields = ['item', 'quantity', 'unit_cost', 'expiry_date', 'batch_number', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formset للأصناف
StockIncreaseItemFormSet = inlineformset_factory(
    StockIncrease,
    StockIncreaseItem,
    form=StockIncreaseItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class StockIncreaseFilterForm(forms.Form):
    """نموذج فلترة أذون الزيادات"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم الإذن أو المخزن أو السبب'
        })
    )
    
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + StockIncrease._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class StockDecreaseForm(forms.ModelForm):
    """نموذج إذن صرف النواقص"""

    class Meta:
        model = StockDecrease
        fields = ['decrease_number', 'date', 'warehouse', 'reason', 'notes']
        widgets = {
            'decrease_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل سبب النقص'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date
            self.fields['date'].initial = date.today()

        # إنشاء رقم إذن تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['decrease_number'].initial = f'DEC-{timestamp}'


class StockDecreaseItemForm(forms.ModelForm):
    """نموذج أصناف إذن النواقص"""

    class Meta:
        model = StockDecreaseItem
        fields = ['item', 'quantity', 'unit_cost', 'batch_number', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formset للأصناف
StockDecreaseItemFormSet = inlineformset_factory(
    StockDecrease,
    StockDecreaseItem,
    form=StockDecreaseItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class StockDecreaseFilterForm(forms.Form):
    """نموذج فلترة أذون النواقص"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم الإذن أو المخزن أو السبب'
        })
    )

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + StockDecrease._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class GoodsReceivedOnLoanForm(forms.ModelForm):
    """نموذج بضاعة مضافة سلفة من الغير"""

    class Meta:
        model = GoodsReceivedOnLoan
        fields = ['loan_number', 'date', 'warehouse', 'lender_name', 'lender_phone',
                  'lender_address', 'loan_reason', 'expected_return_date', 'notes']
        widgets = {
            'loan_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lender_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الشخص أو الجهة المُقرضة'
            }),
            'lender_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف (اختياري)'
            }),
            'lender_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'العنوان (اختياري)'
            }),
            'loan_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سبب استلام السلفة'
            }),
            'expected_return_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date, timedelta
            self.fields['date'].initial = date.today()
            # تحديد تاريخ الإرجاع المتوقع (شهر من اليوم)
            self.fields['expected_return_date'].initial = date.today() + timedelta(days=30)

        # إنشاء رقم سلفة تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['loan_number'].initial = f'LOAN-IN-{timestamp}'


class GoodsReceivedOnLoanItemForm(forms.ModelForm):
    """نموذج أصناف البضاعة المضافة سلفة"""

    class Meta:
        model = GoodsReceivedOnLoanItem
        fields = ['item', 'quantity_received', 'estimated_unit_value', 'condition_received',
                  'expiry_date', 'batch_number', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity_received': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'estimated_unit_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'condition_received': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حالة البضاعة (جيدة، متوسطة، إلخ)'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formset للأصناف
GoodsReceivedOnLoanItemFormSet = inlineformset_factory(
    GoodsReceivedOnLoan,
    GoodsReceivedOnLoanItem,
    form=GoodsReceivedOnLoanItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class GoodsReceivedOnLoanFilterForm(forms.Form):
    """نموذج فلترة البضائع المضافة سلفة"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم السلفة أو اسم المُقرض'
        })
    )

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + GoodsReceivedOnLoan._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="السلف المتأخرة فقط"
    )


class GoodsIssuedOnLoanForm(forms.ModelForm):
    """نموذج بضاعة منصرفة سلفة لدى الغير"""

    class Meta:
        model = GoodsIssuedOnLoan
        fields = ['loan_number', 'date', 'warehouse', 'borrower_name', 'borrower_phone',
                  'borrower_address', 'loan_reason', 'expected_return_date', 'notes']
        widgets = {
            'loan_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'borrower_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الشخص أو الجهة المُستعيرة'
            }),
            'borrower_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف (اختياري)'
            }),
            'borrower_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'العنوان (اختياري)'
            }),
            'loan_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سبب صرف السلفة'
            }),
            'expected_return_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date, timedelta
            self.fields['date'].initial = date.today()
            # تحديد تاريخ الإرجاع المتوقع (شهر من اليوم)
            self.fields['expected_return_date'].initial = date.today() + timedelta(days=30)

        # إنشاء رقم سلفة تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['loan_number'].initial = f'LOAN-OUT-{timestamp}'


class GoodsIssuedOnLoanItemForm(forms.ModelForm):
    """نموذج أصناف البضاعة المنصرفة سلفة"""

    class Meta:
        model = GoodsIssuedOnLoanItem
        fields = ['item', 'quantity_issued', 'estimated_unit_value', 'condition_issued',
                  'expiry_date', 'batch_number', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity_issued': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'estimated_unit_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'condition_issued': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حالة البضاعة (جيدة، متوسطة، إلخ)'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formset للأصناف
GoodsIssuedOnLoanItemFormSet = inlineformset_factory(
    GoodsIssuedOnLoan,
    GoodsIssuedOnLoanItem,
    form=GoodsIssuedOnLoanItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class GoodsIssuedOnLoanFilterForm(forms.Form):
    """نموذج فلترة البضائع المنصرفة سلفة"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم السلفة أو اسم المُستعير'
        })
    )

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + GoodsIssuedOnLoan._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="السلف المتأخرة فقط"
    )


class WarehouseTransferForm(forms.ModelForm):
    """نموذج تحويل بين المخازن"""

    class Meta:
        model = WarehouseTransfer
        fields = ['transfer_number', 'date', 'from_warehouse', 'to_warehouse',
                  'transfer_reason', 'notes']
        widgets = {
            'transfer_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'from_warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'to_warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transfer_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سبب التحويل'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date
            self.fields['date'].initial = date.today()

        # إنشاء رقم تحويل تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['transfer_number'].initial = f'TRF-{timestamp}'

    def clean(self):
        cleaned_data = super().clean()
        from_warehouse = cleaned_data.get('from_warehouse')
        to_warehouse = cleaned_data.get('to_warehouse')

        if from_warehouse and to_warehouse and from_warehouse == to_warehouse:
            raise forms.ValidationError('لا يمكن التحويل من وإلى نفس المخزن')

        return cleaned_data


class WarehouseTransferItemForm(forms.ModelForm):
    """نموذج أصناف تحويل المخازن"""

    class Meta:
        model = WarehouseTransferItem
        fields = ['item', 'quantity_requested', 'unit_cost', 'expiry_date',
                  'batch_number', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity_requested': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formset للأصناف
WarehouseTransferItemFormSet = inlineformset_factory(
    WarehouseTransfer,
    WarehouseTransferItem,
    form=WarehouseTransferItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class WarehouseTransferFilterForm(forms.Form):
    """نموذج فلترة تحويلات المخازن"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم التحويل أو السبب'
        })
    )

    from_warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن المرسلة",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    to_warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن المستقبلة",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + WarehouseTransfer._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class ItemTransformationForm(forms.ModelForm):
    """نموذج التحويل من صنف إلى صنف"""

    class Meta:
        model = ItemTransformation
        fields = ['transformation_number', 'date', 'warehouse', 'transformation_type',
                  'transformation_reason', 'transformation_cost', 'notes']
        widgets = {
            'transformation_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transformation_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transformation_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سبب التحويل'
            }),
            'transformation_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date
            self.fields['date'].initial = date.today()

        # إنشاء رقم تحويل تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['transformation_number'].initial = f'ITF-{timestamp}'


class ItemTransformationInputForm(forms.ModelForm):
    """نموذج مدخلات التحويل"""

    class Meta:
        model = ItemTransformationInput
        fields = ['item', 'quantity', 'unit_cost', 'expiry_date', 'batch_number', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


class ItemTransformationOutputForm(forms.ModelForm):
    """نموذج مخرجات التحويل"""

    class Meta:
        model = ItemTransformationOutput
        fields = ['item', 'quantity', 'unit_cost', 'expiry_date', 'batch_number', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formsets للمدخلات والمخرجات
ItemTransformationInputFormSet = inlineformset_factory(
    ItemTransformation,
    ItemTransformationInput,
    form=ItemTransformationInputForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)

ItemTransformationOutputFormSet = inlineformset_factory(
    ItemTransformation,
    ItemTransformationOutput,
    form=ItemTransformationOutputForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class ItemTransformationFilterForm(forms.Form):
    """نموذج فلترة تحويلات الأصناف"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم التحويل أو السبب'
        })
    )

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    transformation_type = forms.ChoiceField(
        choices=[('', 'جميع الأنواع')] + ItemTransformation._meta.get_field('transformation_type').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + ItemTransformation._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class ManufacturingOrderForm(forms.ModelForm):
    """نموذج أمر إنتاج تام تصنيع"""

    class Meta:
        model = ManufacturingOrder
        fields = ['order_number', 'date', 'warehouse', 'product_item', 'quantity_to_produce',
                  'finished_goods_warehouse', 'operating_expenses', 'labor_cost', 'overhead_cost',
                  'priority', 'expected_completion_date', 'notes']
        widgets = {
            'order_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'product_item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity_to_produce': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'finished_goods_warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'operating_expenses': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 ج.م'
            }),
            'labor_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 ج.م'
            }),
            'overhead_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 ج.م'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date, timedelta
            self.fields['date'].initial = date.today()
            # تحديد تاريخ الإنجاز المتوقع (أسبوع من اليوم)
            self.fields['expected_completion_date'].initial = date.today() + timedelta(days=7)

        # إنشاء رقم أمر إنتاج تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['order_number'].initial = f'MFG-{timestamp}'


class ManufacturingOrderMaterialForm(forms.ModelForm):
    """نموذج مواد خام أمر الإنتاج"""

    class Meta:
        model = ManufacturingOrderMaterial
        fields = ['material', 'quantity_required', 'unit_cost', 'expiry_date',
                  'batch_number', 'notes']
        widgets = {
            'material': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.001',
                'placeholder': '0.000'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formset للمواد الخام
ManufacturingOrderMaterialFormSet = inlineformset_factory(
    ManufacturingOrder,
    ManufacturingOrderMaterial,
    form=ManufacturingOrderMaterialForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)


class ManufacturingOrderFilterForm(forms.Form):
    """نموذج فلترة أوامر الإنتاج"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم الأمر أو المنتج'
        })
    )

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    product_item = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        required=False,
        empty_label="جميع المنتجات",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + ManufacturingOrder._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    priority = forms.ChoiceField(
        choices=[('', 'جميع الأولويات')] + ManufacturingOrder._meta.get_field('priority').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="الأوامر المتأخرة فقط"
    )


class PhysicalInventoryForm(forms.ModelForm):
    """نموذج الجرد الفعلي"""

    class Meta:
        model = PhysicalInventory
        fields = ['inventory_number', 'date', 'warehouse', 'inventory_type', 'reason', 'notes', 'financial_year']
        widgets = {
            'inventory_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'inventory_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سبب إجراء الجرد'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
            'financial_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2024',
                'maxlength': '10'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحديد التاريخ الافتراضي
        if not self.instance.pk:
            from datetime import date
            self.fields['date'].initial = date.today()

        # إنشاء رقم جرد تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['inventory_number'].initial = f'INV-{timestamp}'

            # تعيين السنة المالية الافتراضية للجرد الافتتاحي
            current_year = datetime.now().year
            self.fields['financial_year'].initial = str(current_year)

        # إظهار/إخفاء حقل السنة المالية حسب نوع الجرد
        if self.instance.pk and self.instance.inventory_type != 'OPENING':
            self.fields['financial_year'].widget = forms.HiddenInput()
            self.fields['financial_year'].required = False


class PhysicalInventoryItemForm(forms.ModelForm):
    """نموذج أصناف الجرد الفعلي"""

    class Meta:
        model = PhysicalInventoryItem
        fields = ['item', 'counted_quantity', 'expiry_date', 'batch_number',
                  'location', 'discrepancy_reason', 'notes']
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'counted_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'placeholder': '0.000'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'batch_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الدفعة (اختياري)'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموقع في المخزن (اختياري)'
            }),
            'discrepancy_reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سبب الفرق (في حالة وجود فرق)'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }


# إنشاء Formset لأصناف الجرد
PhysicalInventoryItemFormSet = inlineformset_factory(
    PhysicalInventory,
    PhysicalInventoryItem,
    form=PhysicalInventoryItemForm,
    extra=0,
    min_num=0,
    can_delete=True
)


class PhysicalInventoryFilterForm(forms.Form):
    """نموذج فلترة الجرد الفعلي"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'البحث في رقم الجرد أو السبب'
        })
    )

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    inventory_type = forms.ChoiceField(
        choices=[('', 'جميع الأنواع')] + PhysicalInventory._meta.get_field('inventory_type').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + PhysicalInventory._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    discrepancies_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="الجرد مع فروقات فقط"
    )


class CountItemForm(forms.Form):
    """نموذج جرد صنف واحد"""

    counted_quantity = forms.DecimalField(
        max_digits=15,
        decimal_places=3,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.001',
            'min': '0',
            'placeholder': '0.000'
        }),
        label="الكمية المجردة"
    )

    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="تاريخ الانتهاء"
    )

    batch_number = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'رقم الدفعة (اختياري)'
        }),
        label="رقم الدفعة"
    )

    location = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الموقع في المخزن (اختياري)'
        }),
        label="الموقع"
    )

    discrepancy_reason = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'سبب الفرق (في حالة وجود فرق)'
        }),
        label="سبب الفرق"
    )

    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ملاحظات (اختياري)'
        }),
        label="ملاحظات"
    )


# تم نقل نماذج جرد أول المدة إلى تطبيق الحسابات العامة (accounting)
