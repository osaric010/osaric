from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Currency, Warehouse, ItemCategory, Unit, Item, Bank, Treasury,
    WarehouseZone, WarehouseLocation, ItemLocation, AssetGroup, Person,
    ExpenseCategory, ExpenseItem, RevenueCategory, RevenueItem,
    ProductionStage, FinishedProduct, ProfitCenter, Printer, CompanySettings
)


class CompanySettingsForm(forms.ModelForm):
    """نموذج إعدادات الشركة"""

    class Meta:
        model = CompanySettings
        fields = [
            'company_name', 'company_name_english', 'logo',
            'phone', 'mobile', 'email', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'tax_number', 'commercial_register', 'default_currency',
            'app_name', 'app_version', 'items_per_page', 'date_format',
            'session_timeout_minutes', 'password_min_length',
            'auto_backup_enabled', 'backup_frequency_days',
            'email_notifications_enabled', 'sms_notifications_enabled',
            'default_report_format', 'print_logo_on_reports', 'print_company_info',
            'notes'
        ]

        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الشركة'
            }),
            'company_name_english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name in English'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الجوال'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموقع الإلكتروني'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المدينة'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المحافظة'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الدولة'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرمز البريدي'
            }),
            'tax_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرقم الضريبي'
            }),
            'commercial_register': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'السجل التجاري'
            }),
            'default_currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'app_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم التطبيق'
            }),
            'app_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'إصدار التطبيق'
            }),
            'items_per_page': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 100
            }),
            'date_format': forms.Select(attrs={
                'class': 'form-select'
            }),
            'session_timeout_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 480
            }),
            'password_min_length': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 4,
                'max': 20
            }),
            'auto_backup_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'backup_frequency_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 365
            }),
            'email_notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sms_notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'default_report_format': forms.Select(attrs={
                'class': 'form-select'
            }),
            'print_logo_on_reports': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'print_company_info': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'ملاحظات إضافية'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تحديد العملات المتاحة
        self.fields['default_currency'].queryset = Currency.objects.filter(is_active=True)
        self.fields['default_currency'].empty_label = "اختر العملة الافتراضية"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            from django.core.validators import validate_email
            try:
                validate_email(email)
            except:
                raise forms.ValidationError('البريد الإلكتروني غير صحيح')
        return email

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            # التحقق من نوع الملف
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if hasattr(logo, 'content_type') and logo.content_type not in allowed_types:
                raise forms.ValidationError('نوع الملف غير مدعوم. يرجى اختيار صورة بصيغة JPG أو PNG')

            # التحقق من حجم الملف (5MB كحد أقصى)
            if hasattr(logo, 'size') and logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('حجم الملف كبير جداً. الحد الأقصى 5 ميجابايت')

        return logo


class CurrencyForm(forms.ModelForm):
    """نموذج العملة"""
    
    class Meta:
        model = Currency
        fields = ['code', 'name', 'symbol', 'exchange_rate', 'is_base_currency']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثل: USD, EUR',
                'maxlength': 3
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم العملة'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رمز العملة مثل: $, €'
            }),
            'exchange_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0.0001'
            }),
            'is_base_currency': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'code': 'رمز العملة',
            'name': 'اسم العملة',
            'symbol': 'رمز العملة',
            'exchange_rate': 'سعر الصرف',
            'is_base_currency': 'العملة الأساسية'
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper()
            # Check if code already exists (excluding current instance)
            existing = Currency.objects.filter(code=code, is_active=True)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('رمز العملة موجود بالفعل')
        return code

    def clean(self):
        cleaned_data = super().clean()
        is_base_currency = cleaned_data.get('is_base_currency')
        
        if is_base_currency:
            # Check if there's already a base currency (excluding current instance)
            existing_base = Currency.objects.filter(is_base_currency=True, is_active=True)
            if self.instance.pk:
                existing_base = existing_base.exclude(pk=self.instance.pk)
            if existing_base.exists():
                raise ValidationError('يمكن أن تكون هناك عملة أساسية واحدة فقط')
        
        return cleaned_data


class WarehouseForm(forms.ModelForm):
    """نموذج المخزن"""
    
    class Meta:
        model = Warehouse
        fields = ['code', 'name', 'location', 'manager', 'capacity']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود المخزن'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المخزن'
            }),
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'عنوان المخزن'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
        labels = {
            'code': 'كود المخزن',
            'name': 'اسم المخزن',
            'location': 'الموقع',
            'manager': 'مدير المخزن',
            'capacity': 'السعة'
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper()
            # Check if code already exists (excluding current instance)
            existing = Warehouse.objects.filter(code=code, is_active=True)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('كود المخزن موجود بالفعل')
        return code


class ItemCategoryForm(forms.ModelForm):
    """نموذج فئة الصنف"""
    
    class Meta:
        model = ItemCategory
        fields = ['code', 'name', 'parent', 'description']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الفئة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الفئة'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الفئة'
            })
        }
        labels = {
            'code': 'كود الفئة',
            'name': 'اسم الفئة',
            'parent': 'الفئة الأب',
            'description': 'الوصف'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude self from parent choices to prevent circular reference
        if self.instance.pk:
            self.fields['parent'].queryset = ItemCategory.objects.filter(
                is_active=True
            ).exclude(pk=self.instance.pk)
        else:
            self.fields['parent'].queryset = ItemCategory.objects.filter(is_active=True)


class UnitForm(forms.ModelForm):
    """نموذج وحدة القياس"""
    
    class Meta:
        model = Unit
        fields = ['code', 'name', 'symbol']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الوحدة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الوحدة'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رمز الوحدة'
            })
        }
        labels = {
            'code': 'كود الوحدة',
            'name': 'اسم الوحدة',
            'symbol': 'رمز الوحدة'
        }


class ItemForm(forms.ModelForm):
    """نموذج الصنف"""
    
    class Meta:
        model = Item
        fields = [
            'code', 'name', 'category', 'unit', 'barcode', 'description',
            'cost_price', 'selling_price', 'min_stock', 'max_stock',
            'weight', 'dimensions', 'image'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الصنف'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الصنف'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الباركود'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الصنف'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'min_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الطول × العرض × الارتفاع'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'code': 'كود الصنف',
            'name': 'اسم الصنف',
            'category': 'الفئة',
            'unit': 'وحدة القياس',
            'barcode': 'الباركود',
            'description': 'الوصف',
            'cost_price': 'سعر التكلفة',
            'selling_price': 'سعر البيع',
            'min_stock': 'الحد الأدنى للمخزون',
            'max_stock': 'الحد الأقصى للمخزون',
            'weight': 'الوزن',
            'dimensions': 'الأبعاد',
            'image': 'صورة الصنف'
        }


class BankForm(forms.ModelForm):
    """نموذج البنك"""
    
    class Meta:
        model = Bank
        fields = [
            'code', 'name', 'branch', 'account_number', 'account_name',
            'currency', 'balance', 'contact_info'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود البنك'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم البنك'
            }),
            'branch': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الفرع'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الحساب'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الحساب'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'contact_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'معلومات الاتصال'
            })
        }
        labels = {
            'code': 'كود البنك',
            'name': 'اسم البنك',
            'branch': 'الفرع',
            'account_number': 'رقم الحساب',
            'account_name': 'اسم الحساب',
            'currency': 'العملة',
            'balance': 'الرصيد',
            'contact_info': 'معلومات الاتصال'
        }


class TreasuryForm(forms.ModelForm):
    """نموذج الخزينة"""
    
    class Meta:
        model = Treasury
        fields = [
            'code', 'name', 'currency', 'balance', 'responsible_person', 'location'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الخزينة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الخزينة'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'responsible_person': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موقع الخزينة'
            })
        }
        labels = {
            'code': 'كود الخزينة',
            'name': 'اسم الخزينة',
            'currency': 'العملة',
            'balance': 'الرصيد',
            'responsible_person': 'المسؤول',
            'location': 'الموقع'
        }


class WarehouseZoneForm(forms.ModelForm):
    """نموذج منطقة المخزن"""

    class Meta:
        model = WarehouseZone
        fields = [
            'code', 'name', 'warehouse', 'description',
            'temperature_controlled', 'humidity_controlled', 'security_level'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود المنطقة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المنطقة'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المنطقة'
            }),
            'temperature_controlled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'humidity_controlled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'security_level': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'code': 'كود المنطقة',
            'name': 'اسم المنطقة',
            'warehouse': 'المخزن',
            'description': 'الوصف',
            'temperature_controlled': 'مكيف الهواء',
            'humidity_controlled': 'مراقب الرطوبة',
            'security_level': 'مستوى الأمان'
        }


class WarehouseLocationForm(forms.ModelForm):
    """نموذج موقع المخزن"""

    class Meta:
        model = WarehouseLocation
        fields = [
            'code', 'name', 'warehouse', 'zone', 'aisle', 'rack', 'shelf', 'bin',
            'capacity', 'capacity_unit', 'max_weight', 'is_available',
            'is_pickable', 'is_receivable', 'notes'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الموقع'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الموقع'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'zone': forms.Select(attrs={
                'class': 'form-select'
            }),
            'aisle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الممر'
            }),
            'rack': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الرف'
            }),
            'shelf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الطبقة'
            }),
            'bin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الصندوق'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'capacity_unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'max_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_pickable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_receivable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات'
            })
        }
        labels = {
            'code': 'كود الموقع',
            'name': 'اسم الموقع',
            'warehouse': 'المخزن',
            'zone': 'المنطقة',
            'aisle': 'الممر',
            'rack': 'الرف',
            'shelf': 'الطبقة',
            'bin': 'الصندوق',
            'capacity': 'السعة',
            'capacity_unit': 'وحدة السعة',
            'max_weight': 'الحد الأقصى للوزن (كجم)',
            'is_available': 'متاح',
            'is_pickable': 'قابل للانتقاء',
            'is_receivable': 'قابل للاستقبال',
            'notes': 'ملاحظات'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # فلترة المناطق حسب المخزن المختار
        if 'warehouse' in self.data:
            try:
                warehouse_id = int(self.data.get('warehouse'))
                self.fields['zone'].queryset = WarehouseZone.objects.filter(
                    warehouse_id=warehouse_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['zone'].queryset = WarehouseZone.objects.filter(
                warehouse=self.instance.warehouse, is_active=True
            )


class ItemLocationForm(forms.ModelForm):
    """نموذج موقع الصنف"""

    class Meta:
        model = ItemLocation
        fields = [
            'item', 'warehouse', 'location', 'min_quantity', 'max_quantity',
            'reorder_point', 'priority', 'location_type', 'is_default'
        ]
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select'
            }),
            'min_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'reorder_point': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'location_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'item': 'الصنف',
            'warehouse': 'المخزن',
            'location': 'الموقع',
            'min_quantity': 'الحد الأدنى',
            'max_quantity': 'الحد الأقصى',
            'reorder_point': 'نقطة إعادة الطلب',
            'priority': 'الأولوية',
            'location_type': 'نوع الموقع',
            'is_default': 'الموقع الافتراضي'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # فلترة المواقع حسب المخزن المختار
        if 'warehouse' in self.data:
            try:
                warehouse_id = int(self.data.get('warehouse'))
                self.fields['location'].queryset = WarehouseLocation.objects.filter(
                    warehouse_id=warehouse_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['location'].queryset = WarehouseLocation.objects.filter(
                warehouse=self.instance.warehouse, is_active=True
            )


class AssetGroupForm(forms.ModelForm):
    """نموذج مجموعة الأصول"""

    class Meta:
        model = AssetGroup
        fields = [
            'code', 'name', 'parent', 'description', 'depreciation_method',
            'default_useful_life', 'default_salvage_value_rate', 'asset_account',
            'depreciation_account', 'accumulated_depreciation_account',
            'requires_insurance', 'requires_maintenance', 'is_depreciable',
            'asset_category', 'min_cost_threshold', 'max_cost_threshold'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود المجموعة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المجموعة'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المجموعة'
            }),
            'depreciation_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'default_useful_life': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '100'
            }),
            'default_salvage_value_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'asset_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم حساب الأصل'
            }),
            'depreciation_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم حساب الاستهلاك'
            }),
            'accumulated_depreciation_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم حساب مجمع الاستهلاك'
            }),
            'requires_insurance': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_maintenance': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_depreciable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'asset_category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'min_cost_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_cost_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
        labels = {
            'code': 'كود المجموعة',
            'name': 'اسم المجموعة',
            'parent': 'المجموعة الأب',
            'description': 'الوصف',
            'depreciation_method': 'طريقة الاستهلاك',
            'default_useful_life': 'العمر الافتراضي (سنوات)',
            'default_salvage_value_rate': 'نسبة القيمة المتبقية (%)',
            'asset_account': 'حساب الأصل',
            'depreciation_account': 'حساب الاستهلاك',
            'accumulated_depreciation_account': 'حساب مجمع الاستهلاك',
            'requires_insurance': 'يتطلب تأمين',
            'requires_maintenance': 'يتطلب صيانة',
            'is_depreciable': 'قابل للاستهلاك',
            'asset_category': 'فئة الأصل',
            'min_cost_threshold': 'الحد الأدنى للتكلفة',
            'max_cost_threshold': 'الحد الأقصى للتكلفة'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # فلترة المجموعات الأب لتجنب الدورات
        if self.instance.pk:
            # استبعاد المجموعة نفسها وجميع المجموعات الفرعية
            excluded_ids = [self.instance.pk]
            excluded_ids.extend([desc.pk for desc in self.instance.get_all_descendants()])
            self.fields['parent'].queryset = AssetGroup.objects.filter(
                is_active=True
            ).exclude(pk__in=excluded_ids)
        else:
            self.fields['parent'].queryset = AssetGroup.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        min_cost = cleaned_data.get('min_cost_threshold')
        max_cost = cleaned_data.get('max_cost_threshold')

        if min_cost and max_cost and max_cost <= min_cost:
            raise forms.ValidationError(
                'الحد الأقصى للتكلفة يجب أن يكون أكبر من الحد الأدنى'
            )

        return cleaned_data


class PersonForm(forms.ModelForm):
    """نموذج الأشخاص والجهات"""

    class Meta:
        model = Person
        fields = [
            'code', 'name', 'name_english', 'person_type', 'entity_type',
            'national_id', 'tax_number', 'commercial_register',
            'phone', 'mobile', 'email', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'credit_limit', 'payment_terms', 'currency',
            'account_receivable', 'account_payable',
            'contact_person', 'contact_title', 'notes',
            'is_active_customer', 'is_active_supplier', 'allow_credit',
            'registration_date'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الشخص/الجهة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم'
            }),
            'name_english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم بالإنجليزية'
            }),
            'person_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'entity_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهوية/السجل التجاري'
            }),
            'tax_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرقم الضريبي'
            }),
            'commercial_register': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'السجل التجاري'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الهاتف'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الجوال'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموقع الإلكتروني'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المدينة'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المحافظة/المنطقة'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الدولة'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرمز البريدي'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'payment_terms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'account_receivable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم حساب المدينين'
            }),
            'account_payable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم حساب الدائنين'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الشخص المسؤول'
            }),
            'contact_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المنصب'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات'
            }),
            'is_active_customer': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active_supplier': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_credit': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'registration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
        labels = {
            'code': 'كود الشخص/الجهة',
            'name': 'الاسم',
            'name_english': 'الاسم بالإنجليزية',
            'person_type': 'نوع الشخص/الجهة',
            'entity_type': 'نوع الكيان',
            'national_id': 'رقم الهوية/السجل التجاري',
            'tax_number': 'الرقم الضريبي',
            'commercial_register': 'السجل التجاري',
            'phone': 'الهاتف',
            'mobile': 'الجوال',
            'email': 'البريد الإلكتروني',
            'website': 'الموقع الإلكتروني',
            'address': 'العنوان',
            'city': 'المدينة',
            'state': 'المحافظة/المنطقة',
            'country': 'الدولة',
            'postal_code': 'الرمز البريدي',
            'credit_limit': 'حد الائتمان',
            'payment_terms': 'مدة السداد (أيام)',
            'currency': 'العملة الافتراضية',
            'account_receivable': 'حساب المدينين',
            'account_payable': 'حساب الدائنين',
            'contact_person': 'الشخص المسؤول',
            'contact_title': 'المنصب',
            'notes': 'ملاحظات',
            'is_active_customer': 'عميل نشط',
            'is_active_supplier': 'مورد نشط',
            'allow_credit': 'السماح بالائتمان',
            'registration_date': 'تاريخ التسجيل'
        }

    def clean(self):
        cleaned_data = super().clean()
        person_type = cleaned_data.get('person_type')
        is_active_customer = cleaned_data.get('is_active_customer')
        is_active_supplier = cleaned_data.get('is_active_supplier')

        # التحقق من تطابق نوع الشخص مع الحالة النشطة
        if person_type == 'CUSTOMER' and not is_active_customer:
            raise forms.ValidationError('يجب تفعيل "عميل نشط" عند اختيار نوع "عميل"')

        if person_type == 'SUPPLIER' and not is_active_supplier:
            raise forms.ValidationError('يجب تفعيل "مورد نشط" عند اختيار نوع "مورد"')

        if person_type == 'BOTH':
            if not is_active_customer:
                raise forms.ValidationError('يجب تفعيل "عميل نشط" عند اختيار نوع "عميل ومورد"')
            if not is_active_supplier:
                raise forms.ValidationError('يجب تفعيل "مورد نشط" عند اختيار نوع "عميل ومورد"')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تعيين العملة الافتراضية
        try:
            from .models import Currency
            default_currency = Currency.objects.filter(is_base_currency=True).first()
            if default_currency and not self.instance.pk:
                self.initial['currency'] = default_currency
        except:
            pass

        # تعيين القيم الافتراضية حسب نوع الشخص
        if not self.instance.pk:  # فقط للسجلات الجديدة
            person_type = self.initial.get('person_type', 'CUSTOMER')

            if person_type == 'CUSTOMER':
                self.initial['is_active_customer'] = True
                self.initial['is_active_supplier'] = False
            elif person_type == 'SUPPLIER':
                self.initial['is_active_customer'] = False
                self.initial['is_active_supplier'] = True
            elif person_type == 'BOTH':
                self.initial['is_active_customer'] = True
                self.initial['is_active_supplier'] = True
            else:
                self.initial['is_active_customer'] = False
                self.initial['is_active_supplier'] = False


class ExpenseCategoryForm(forms.ModelForm):
    """نموذج فئات المصروفات"""

    class Meta:
        model = ExpenseCategory
        fields = [
            'code', 'name', 'description', 'category',
            'default_account', 'requires_approval', 'max_amount'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود فئة المصروف'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم فئة المصروف'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف فئة المصروف'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'default_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الحساب الافتراضي'
            }),
            'requires_approval': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'max_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
        labels = {
            'code': 'كود فئة المصروف',
            'name': 'اسم فئة المصروف',
            'description': 'الوصف',
            'category': 'تصنيف المصروف',
            'default_account': 'الحساب الافتراضي',
            'requires_approval': 'يتطلب موافقة',
            'max_amount': 'الحد الأقصى للمبلغ'
        }


class ExpenseItemForm(forms.ModelForm):
    """نموذج بنود المصروفات"""

    class Meta:
        model = ExpenseItem
        fields = [
            'code', 'name', 'expense_category', 'description', 'account_number',
            'is_recurring', 'recurring_period', 'min_amount', 'max_amount',
            'requires_document', 'requires_approval'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود المصروف'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المصروف'
            }),
            'expense_category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المصروف'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الحساب'
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'recurring_period': forms.Select(attrs={
                'class': 'form-select'
            }),
            'min_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'requires_document': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_approval': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'code': 'كود بند المصروف',
            'name': 'اسم بند المصروف',
            'expense_category': 'فئة المصروف',
            'description': 'الوصف',
            'account_number': 'رقم الحساب',
            'is_recurring': 'مصروف دوري',
            'recurring_period': 'فترة التكرار',
            'min_amount': 'الحد الأدنى للمبلغ',
            'max_amount': 'الحد الأقصى للمبلغ',
            'requires_document': 'يتطلب مستند',
            'requires_approval': 'يتطلب موافقة'
        }

    def clean(self):
        cleaned_data = super().clean()
        is_recurring = cleaned_data.get('is_recurring')
        recurring_period = cleaned_data.get('recurring_period')

        if is_recurring and not recurring_period:
            raise forms.ValidationError('يجب تحديد فترة التكرار للمصروف الدوري')

        return cleaned_data


class RevenueCategoryForm(forms.ModelForm):
    """نموذج فئات الإيرادات"""

    class Meta:
        model = RevenueCategory
        fields = [
            'code', 'name', 'description', 'category',
            'default_account', 'is_taxable', 'tax_rate'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود نوع الإيراد'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم نوع الإيراد'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف نوع الإيراد'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'default_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الحساب الافتراضي'
            }),
            'is_taxable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            })
        }
        labels = {
            'code': 'كود نوع الإيراد',
            'name': 'اسم نوع الإيراد',
            'description': 'الوصف',
            'category': 'تصنيف الإيراد',
            'default_account': 'الحساب الافتراضي',
            'is_taxable': 'خاضع للضريبة',
            'tax_rate': 'معدل الضريبة (%)'
        }


class RevenueItemForm(forms.ModelForm):
    """نموذج بنود الإيرادات"""

    class Meta:
        model = RevenueItem
        fields = [
            'code', 'name', 'revenue_category', 'description', 'account_number',
            'is_recurring', 'recurring_period', 'is_taxable', 'tax_rate',
            'min_amount', 'max_amount', 'requires_contract', 'commission_rate'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الإيراد'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الإيراد'
            }),
            'revenue_category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الإيراد'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الحساب'
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'recurring_period': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_taxable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'min_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'requires_contract': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'commission_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            })
        }
        labels = {
            'code': 'كود الإيراد',
            'name': 'اسم الإيراد',
            'revenue_type': 'نوع الإيراد',
            'description': 'الوصف',
            'account_number': 'رقم الحساب',
            'is_recurring': 'إيراد دوري',
            'recurring_period': 'فترة التكرار',
            'is_taxable': 'خاضع للضريبة',
            'tax_rate': 'معدل الضريبة (%)',
            'min_amount': 'الحد الأدنى للمبلغ',
            'max_amount': 'الحد الأقصى للمبلغ',
            'requires_contract': 'يتطلب عقد',
            'commission_rate': 'معدل العمولة (%)'
        }

    def clean(self):
        cleaned_data = super().clean()
        is_recurring = cleaned_data.get('is_recurring')
        recurring_period = cleaned_data.get('recurring_period')

        if is_recurring and not recurring_period:
            raise forms.ValidationError('يجب تحديد فترة التكرار للإيراد الدوري')

        return cleaned_data


class ProductionStageForm(forms.ModelForm):
    """نموذج مراحل الإنتاج"""

    class Meta:
        model = ProductionStage
        fields = [
            'code', 'name', 'description', 'sequence_number', 'stage_type',
            'location', 'required_equipment', 'estimated_duration_hours',
            'setup_time_hours', 'labor_cost_per_hour', 'overhead_cost_per_hour',
            'responsible_user', 'cost_center', 'requires_approval',
            'requires_quality_check', 'is_critical', 'can_run_parallel',
            'quality_standards', 'acceptance_criteria'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود المرحلة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المرحلة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المرحلة'
            }),
            'sequence_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'stage_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موقع المرحلة'
            }),
            'required_equipment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'المعدات المطلوبة'
            }),
            'estimated_duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'setup_time_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'labor_cost_per_hour': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'overhead_cost_per_hour': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'responsible_user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cost_center': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مركز التكلفة'
            }),
            'requires_approval': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_quality_check': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_critical': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'can_run_parallel': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'quality_standards': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'معايير الجودة'
            }),
            'acceptance_criteria': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'معايير القبول'
            })
        }
        labels = {
            'code': 'كود المرحلة',
            'name': 'اسم المرحلة',
            'description': 'الوصف',
            'sequence_number': 'رقم التسلسل',
            'stage_type': 'نوع المرحلة',
            'location': 'الموقع',
            'required_equipment': 'المعدات المطلوبة',
            'estimated_duration_hours': 'المدة المقدرة (ساعات)',
            'setup_time_hours': 'وقت الإعداد (ساعات)',
            'labor_cost_per_hour': 'تكلفة العمالة/ساعة',
            'overhead_cost_per_hour': 'التكاليف الإضافية/ساعة',
            'responsible_user': 'المسؤول',
            'cost_center': 'مركز التكلفة',
            'requires_approval': 'تتطلب موافقة',
            'requires_quality_check': 'تتطلب فحص جودة',
            'is_critical': 'مرحلة حرجة',
            'can_run_parallel': 'يمكن تشغيلها بالتوازي',
            'quality_standards': 'معايير الجودة',
            'acceptance_criteria': 'معايير القبول'
        }


class FinishedProductForm(forms.ModelForm):
    """نموذج المنتجات التامة"""

    class Meta:
        model = FinishedProduct
        fields = [
            'code', 'name', 'name_english', 'description', 'category', 'unit',
            'brand', 'model', 'version', 'barcode', 'sku', 'specifications',
            'weight', 'dimensions', 'color', 'material', 'standard_cost',
            'material_cost', 'labor_cost', 'overhead_cost', 'selling_price',
            'wholesale_price', 'retail_price', 'min_stock', 'max_stock',
            'reorder_point', 'production_lead_time', 'batch_size',
            'quality_grade', 'shelf_life_days', 'certifications',
            'compliance_standards', 'packaging_type', 'package_weight',
            'package_dimensions', 'units_per_package', 'inventory_account',
            'cogs_account', 'revenue_account', 'is_manufactured',
            'is_sellable', 'is_purchasable', 'track_serial_numbers',
            'track_lot_numbers', 'image', 'technical_drawing', 'notes'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود المنتج'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المنتج'
            }),
            'name_english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم بالإنجليزية'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المنتج'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'العلامة التجارية'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموديل'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الإصدار'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الباركود'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم المنتج'
            }),
            'specifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'المواصفات الفنية'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الأبعاد'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اللون'
            }),
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المادة'
            }),
            'standard_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'material_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'labor_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'overhead_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'wholesale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'retail_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'min_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'max_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'reorder_point': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'production_lead_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'batch_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'quality_grade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'shelf_life_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'الشهادات والمعايير'
            }),
            'compliance_standards': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'معايير الامتثال'
            }),
            'packaging_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نوع التعبئة'
            }),
            'package_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0'
            }),
            'package_dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أبعاد العبوة'
            }),
            'units_per_package': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'inventory_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حساب المخزون'
            }),
            'cogs_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حساب تكلفة البضاعة المباعة'
            }),
            'revenue_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حساب الإيرادات'
            }),
            'is_manufactured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_sellable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_purchasable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'track_serial_numbers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'track_lot_numbers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'technical_drawing': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات'
            })
        }
        labels = {
            'code': 'كود المنتج',
            'name': 'اسم المنتج',
            'name_english': 'الاسم بالإنجليزية',
            'description': 'الوصف',
            'category': 'فئة المنتج',
            'unit': 'وحدة القياس',
            'brand': 'العلامة التجارية',
            'model': 'الموديل',
            'version': 'الإصدار',
            'barcode': 'الباركود',
            'sku': 'رقم المنتج',
            'specifications': 'المواصفات الفنية',
            'weight': 'الوزن (كجم)',
            'dimensions': 'الأبعاد',
            'color': 'اللون',
            'material': 'المادة',
            'standard_cost': 'التكلفة المعيارية',
            'material_cost': 'تكلفة المواد',
            'labor_cost': 'تكلفة العمالة',
            'overhead_cost': 'التكاليف الإضافية',
            'selling_price': 'سعر البيع',
            'wholesale_price': 'سعر الجملة',
            'retail_price': 'سعر التجزئة',
            'min_stock': 'الحد الأدنى للمخزون',
            'max_stock': 'الحد الأقصى للمخزون',
            'reorder_point': 'نقطة إعادة الطلب',
            'production_lead_time': 'مدة الإنتاج (أيام)',
            'batch_size': 'حجم الدفعة',
            'quality_grade': 'درجة الجودة',
            'shelf_life_days': 'مدة الصلاحية (أيام)',
            'certifications': 'الشهادات والمعايير',
            'compliance_standards': 'معايير الامتثال',
            'packaging_type': 'نوع التعبئة',
            'package_weight': 'وزن العبوة (كجم)',
            'package_dimensions': 'أبعاد العبوة',
            'units_per_package': 'الوحدات في العبوة',
            'inventory_account': 'حساب المخزون',
            'cogs_account': 'حساب تكلفة البضاعة المباعة',
            'revenue_account': 'حساب الإيرادات',
            'is_manufactured': 'منتج مصنع',
            'is_sellable': 'قابل للبيع',
            'is_purchasable': 'قابل للشراء',
            'track_serial_numbers': 'تتبع الأرقام التسلسلية',
            'track_lot_numbers': 'تتبع أرقام الدفعات',
            'image': 'صورة المنتج',
            'technical_drawing': 'الرسم الفني',
            'notes': 'ملاحظات'
        }


class ProfitCenterForm(forms.ModelForm):
    """نموذج مراكز الربحية"""

    class Meta:
        model = ProfitCenter
        fields = [
            'code', 'name', 'name_english', 'description', 'parent',
            'manager', 'location', 'phone', 'email', 'target_revenue',
            'target_profit', 'target_profit_margin', 'evaluation_period',
            'revenue_account', 'expense_account', 'asset_account',
            'allocate_overhead', 'overhead_allocation_method', 'overhead_percentage',
            'include_in_reports', 'consolidate_children', 'start_date', 'end_date', 'notes'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود مركز الربحية'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم مركز الربحية'
            }),
            'name_english': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم بالإنجليزية'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف مركز الربحية'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموقع'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
            'target_revenue': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'target_profit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'target_profit_margin': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'evaluation_period': forms.Select(attrs={
                'class': 'form-select'
            }),
            'revenue_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حساب الإيرادات'
            }),
            'expense_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حساب المصروفات'
            }),
            'asset_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'حساب الأصول'
            }),
            'allocate_overhead': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'overhead_allocation_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'overhead_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'include_in_reports': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'consolidate_children': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات'
            })
        }
        labels = {
            'code': 'كود مركز الربحية',
            'name': 'اسم مركز الربحية',
            'name_english': 'الاسم بالإنجليزية',
            'description': 'الوصف',
            'parent': 'مركز الربحية الأب',
            'manager': 'المدير المسؤول',
            'location': 'الموقع',
            'phone': 'الهاتف',
            'email': 'البريد الإلكتروني',
            'target_revenue': 'هدف الإيرادات السنوي',
            'target_profit': 'هدف الربح السنوي',
            'target_profit_margin': 'هدف هامش الربح (%)',
            'evaluation_period': 'فترة التقييم',
            'revenue_account': 'حساب الإيرادات',
            'expense_account': 'حساب المصروفات',
            'asset_account': 'حساب الأصول',
            'allocate_overhead': 'توزيع التكاليف الإضافية',
            'overhead_allocation_method': 'طريقة توزيع التكاليف',
            'overhead_percentage': 'نسبة التكاليف الإضافية (%)',
            'include_in_reports': 'تضمين في التقارير',
            'consolidate_children': 'دمج البيانات من المراكز الفرعية',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'notes': 'ملاحظات'
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and start_date and end_date <= start_date:
            raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')

        return cleaned_data


class PrinterForm(forms.ModelForm):
    """نموذج الطابعات"""

    class Meta:
        model = Printer
        fields = [
            'code', 'name', 'description', 'brand', 'model', 'serial_number',
            'printer_type', 'connection_type', 'ip_address', 'port',
            'paper_size', 'paper_width', 'paper_height', 'dpi', 'print_speed',
            'color_support', 'duplex_support', 'location', 'department',
            'responsible_user', 'usage_type', 'is_default', 'is_shared',
            'auto_cut', 'cash_drawer', 'purchase_date', 'warranty_expiry',
            'last_maintenance', 'next_maintenance', 'notes'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود الطابعة'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الطابعة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الطابعة'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'العلامة التجارية'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الموديل'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الرقم التسلسلي'
            }),
            'printer_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'connection_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '192.168.1.100'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '65535'
            }),
            'paper_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'paper_width': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'paper_height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'dpi': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '72'
            }),
            'print_speed': forms.Select(attrs={
                'class': 'form-select'
            }),
            'color_support': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'duplex_support': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موقع الطابعة'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'القسم'
            }),
            'responsible_user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'usage_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_shared': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'auto_cut': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'cash_drawer': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'warranty_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'last_maintenance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'next_maintenance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات'
            })
        }
        labels = {
            'code': 'كود الطابعة',
            'name': 'اسم الطابعة',
            'description': 'الوصف',
            'brand': 'العلامة التجارية',
            'model': 'الموديل',
            'serial_number': 'الرقم التسلسلي',
            'printer_type': 'نوع الطابعة',
            'connection_type': 'نوع الاتصال',
            'ip_address': 'عنوان IP',
            'port': 'رقم المنفذ',
            'paper_size': 'حجم الورق',
            'paper_width': 'عرض الورق (مم)',
            'paper_height': 'طول الورق (مم)',
            'dpi': 'دقة الطباعة (DPI)',
            'print_speed': 'سرعة الطباعة',
            'color_support': 'دعم الألوان',
            'duplex_support': 'دعم الطباعة على الوجهين',
            'location': 'الموقع',
            'department': 'القسم',
            'responsible_user': 'المسؤول',
            'usage_type': 'نوع الاستخدام',
            'is_default': 'الطابعة الافتراضية',
            'is_shared': 'طابعة مشتركة',
            'auto_cut': 'قطع تلقائي للورق',
            'cash_drawer': 'فتح درج النقد',
            'purchase_date': 'تاريخ الشراء',
            'warranty_expiry': 'انتهاء الضمان',
            'last_maintenance': 'آخر صيانة',
            'next_maintenance': 'الصيانة القادمة',
            'notes': 'ملاحظات'
        }

    def clean(self):
        cleaned_data = super().clean()
        connection_type = cleaned_data.get('connection_type')
        ip_address = cleaned_data.get('ip_address')
        paper_size = cleaned_data.get('paper_size')
        paper_width = cleaned_data.get('paper_width')
        paper_height = cleaned_data.get('paper_height')
        purchase_date = cleaned_data.get('purchase_date')
        warranty_expiry = cleaned_data.get('warranty_expiry')
        last_maintenance = cleaned_data.get('last_maintenance')
        next_maintenance = cleaned_data.get('next_maintenance')

        # التحقق من عنوان IP للطابعات الشبكية
        if connection_type in ['NETWORK', 'WIFI'] and not ip_address:
            raise forms.ValidationError('عنوان IP مطلوب للطابعات الشبكية')

        # التحقق من أبعاد الورق المخصص
        if paper_size == 'CUSTOM':
            if not paper_width or not paper_height:
                raise forms.ValidationError('أبعاد الورق مطلوبة للحجم المخصص')

        # التحقق من التواريخ
        if warranty_expiry and purchase_date and warranty_expiry <= purchase_date:
            raise forms.ValidationError('تاريخ انتهاء الضمان يجب أن يكون بعد تاريخ الشراء')

        if next_maintenance and last_maintenance and next_maintenance <= last_maintenance:
            raise forms.ValidationError('تاريخ الصيانة القادمة يجب أن يكون بعد آخر صيانة')

        return cleaned_data



