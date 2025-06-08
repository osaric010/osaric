"""
نماذج الحسابات العامة - Accounting Forms
"""

from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import (
    Account, BalanceTransfer, AccountMerge, JournalEntry, JournalEntryLine,
    OpeningBalance, ProfitCenter, ProfitDistribution, ProfitDistributionLine,
    AccountingPeriod, OpeningInventory, OpeningInventoryItem
)
from definitions.models import Person, Item, Warehouse, Currency
from decimal import Decimal


class OpeningInventoryForm(forms.ModelForm):
    """نموذج جرد بضاعة أول المدة"""
    
    class Meta:
        model = OpeningInventory
        fields = [
            'inventory_number', 'date', 'warehouse', 'fiscal_year', 'period_name',
            'currency', 'exchange_rate', 'notes'
        ]
        widgets = {
            'inventory_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم جرد أول المدة'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fiscal_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2024'
            }),
            'period_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الفترة المالية الأولى'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'exchange_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0.0001'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعيين العملة الافتراضية
        if not self.instance.pk:
            try:
                default_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
                if default_currency:
                    self.initial['currency'] = default_currency
                    self.initial['exchange_rate'] = default_currency.exchange_rate
            except:
                pass
        
        # تعيين السنة المالية الحالية
        if not self.instance.pk and not self.initial.get('fiscal_year'):
            from datetime import date
            self.initial['fiscal_year'] = str(date.today().year)
        
        # إنشاء رقم جرد تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['inventory_number'].initial = f'OPN-{timestamp}'

    def clean_inventory_number(self):
        """التحقق من رقم الجرد"""
        inventory_number = self.cleaned_data.get('inventory_number')
        if inventory_number:
            # التحقق من عدم تكرار الرقم
            existing = OpeningInventory.objects.filter(
                inventory_number=inventory_number
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError('رقم جرد أول المدة موجود بالفعل')
        
        return inventory_number

    def clean(self):
        """التحقق من صحة البيانات"""
        cleaned_data = super().clean()
        warehouse = cleaned_data.get('warehouse')
        fiscal_year = cleaned_data.get('fiscal_year')
        
        # التحقق من عدم وجود جرد أول مدة آخر لنفس المخزن والسنة المالية
        if warehouse and fiscal_year:
            existing = OpeningInventory.objects.filter(
                warehouse=warehouse,
                fiscal_year=fiscal_year,
                status__in=['APPROVED', 'POSTED']
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise ValidationError(
                    f'يوجد بالفعل جرد أول مدة معتمد للمخزن {warehouse.name} '
                    f'للسنة المالية {fiscal_year}'
                )
        
        return cleaned_data


class OpeningInventoryItemForm(forms.ModelForm):
    """نموذج صنف جرد أول المدة"""
    
    class Meta:
        model = OpeningInventoryItem
        fields = [
            'item', 'opening_quantity', 'unit_cost', 'expiry_date', 'batch_number',
            'serial_number', 'location', 'condition', 'quality_grade', 'notes'
        ]
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select item-select',
                'data-placeholder': 'اختر الصنف'
            }),
            'opening_quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'step': '0.001',
                'min': '0',
                'placeholder': '0.000'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control cost-input',
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
                'placeholder': 'رقم الدفعة'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرقم التسلسلي'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموقع في المخزن'
            }),
            'condition': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quality_grade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ملاحظات'
            }),
        }

    def __init__(self, *args, **kwargs):
        warehouse = kwargs.pop('warehouse', None)
        super().__init__(*args, **kwargs)

        # تعيين تكلفة الوحدة من الصنف عند اختياره
        if self.instance and self.instance.pk and hasattr(self.instance, 'item') and self.instance.item and not self.instance.unit_cost:
            self.initial['unit_cost'] = self.instance.item.cost_price or Decimal('0.00')

    def clean_opening_quantity(self):
        """التحقق من كمية أول المدة"""
        quantity = self.cleaned_data.get('opening_quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError('كمية أول المدة يجب أن تكون موجبة')
        return quantity

    def clean_unit_cost(self):
        """التحقق من تكلفة الوحدة"""
        cost = self.cleaned_data.get('unit_cost')
        if cost is not None and cost < 0:
            raise ValidationError('تكلفة الوحدة يجب أن تكون موجبة')
        return cost

    def clean_expiry_date(self):
        """التحقق من تاريخ الانتهاء"""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date:
            from datetime import date
            if expiry_date <= date.today():
                raise ValidationError('تاريخ الانتهاء يجب أن يكون في المستقبل')
        return expiry_date


# إنشاء Formset لأصناف جرد أول المدة
OpeningInventoryItemFormSet = inlineformset_factory(
    OpeningInventory,
    OpeningInventoryItem,
    form=OpeningInventoryItemForm,
    extra=1,
    min_num=0,
    can_delete=True,
    fields=[
        'item', 'opening_quantity', 'unit_cost', 'expiry_date', 'batch_number',
        'serial_number', 'location', 'condition', 'quality_grade', 'notes'
    ]
)


class OpeningInventorySearchForm(forms.Form):
    """نموذج البحث في جرد أول المدة"""
    
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(is_active=True),
        required=False,
        empty_label="جميع المخازن",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="المخزن"
    )
    
    fiscal_year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'السنة المالية'
        }),
        label="السنة المالية"
    )
    
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + OpeningInventory._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="الحالة"
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="من تاريخ"
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="إلى تاريخ"
    )


class OpeningInventoryApprovalForm(forms.ModelForm):
    """نموذج اعتماد جرد أول المدة"""
    
    approval_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'ملاحظات الاعتماد'
        }),
        label="ملاحظات الاعتماد"
    )
    
    class Meta:
        model = OpeningInventory
        fields = ['approval_notes']

    def save(self, commit=True, user=None):
        """حفظ الاعتماد"""
        instance = super().save(commit=False)
        
        if user:
            instance.approved_by = user
            from django.utils import timezone
            instance.approved_date = timezone.now()
            instance.status = 'APPROVED'
        
        if commit:
            instance.save()
        
        return instance


class BulkOpeningInventoryForm(forms.Form):
    """نموذج إدخال جماعي لجرد أول المدة"""
    
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="المخزن"
    )
    
    items_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'أدخل بيانات الأصناف بالتنسيق التالي:\nكود الصنف,الكمية,التكلفة,رقم الدفعة\nمثال:\nITEM001,100,25.50,BATCH001\nITEM002,50,15.75,BATCH002'
        }),
        label="بيانات الأصناف"
    )

    def clean_items_data(self):
        """التحقق من بيانات الأصناف"""
        items_data = self.cleaned_data.get('items_data')
        if not items_data:
            raise ValidationError('يجب إدخال بيانات الأصناف')
        
        lines = items_data.strip().split('\n')
        parsed_items = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',')
            if len(parts) < 3:
                raise ValidationError(
                    f'السطر {line_num}: يجب أن يحتوي على الأقل على كود الصنف والكمية والتكلفة'
                )
            
            try:
                item_code = parts[0].strip()
                quantity = Decimal(parts[1].strip())
                cost = Decimal(parts[2].strip())
                batch = parts[3].strip() if len(parts) > 3 else ''
                
                # التحقق من وجود الصنف
                try:
                    item = Item.objects.get(code=item_code, is_active=True)
                except Item.DoesNotExist:
                    raise ValidationError(f'السطر {line_num}: الصنف {item_code} غير موجود')
                
                # التحقق من الكمية والتكلفة
                if quantity < 0:
                    raise ValidationError(f'السطر {line_num}: الكمية يجب أن تكون موجبة')
                if cost < 0:
                    raise ValidationError(f'السطر {line_num}: التكلفة يجب أن تكون موجبة')
                
                parsed_items.append({
                    'item': item,
                    'quantity': quantity,
                    'cost': cost,
                    'batch': batch
                })
                
            except (ValueError, IndexError) as e:
                raise ValidationError(f'السطر {line_num}: خطأ في تنسيق البيانات')
        
        if not parsed_items:
            raise ValidationError('لم يتم العثور على أصناف صحيحة')
        
        return parsed_items
