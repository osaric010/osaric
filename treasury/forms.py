from django import forms
from django.forms import inlineformset_factory
from .models import (TreasuryTransaction, Receipt, Payment, Expense, Revenue, 
                     ExpenseType, RevenueType, PaymentNote, ReceiptNote,
                     CustodyReceiptOut, CustodyReceiptIn, TreasuryTransfer)
from definitions.models import Treasury
from sales.models import Customer
from purchases.models import Supplier


class TreasuryTransactionForm(forms.ModelForm):
    """نموذج معاملات الخزينة"""
    
    class Meta:
        model = TreasuryTransaction
        fields = ['transaction_number', 'date', 'treasury', 'transaction_type', 'amount',
                  'description', 'customer', 'supplier', 'to_treasury', 'reference_number', 'notes']
        widgets = {
            'transaction_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'وصف المعاملة'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'to_treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم المرجع (اختياري)'
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
            
        # إنشاء رقم معاملة تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['transaction_number'].initial = f'TR-{timestamp}'


class ReceiptForm(forms.ModelForm):
    """نموذج التحصيل النقدي"""

    class Meta:
        model = Receipt
        fields = ['receipt_number', 'date', 'treasury', 'customer', 'amount', 'payment_method',
                  'check_number', 'check_date', 'check_bank', 'description', 'notes']
        widgets = {
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'check_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الشيك'
            }),
            'check_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'check_bank': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'البنك المسحوب عليه'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'بيان الإيصال'
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
            
        # إنشاء رقم إيصال تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['receipt_number'].initial = f'RC-{timestamp}'


class PaymentForm(forms.ModelForm):
    """نموذج إيصالات الدفع"""
    
    class Meta:
        model = Payment
        fields = ['payment_number', 'date', 'treasury', 'supplier', 'amount', 'payment_method',
                  'check_number', 'check_date', 'description', 'notes']
        widgets = {
            'payment_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'check_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الشيك'
            }),
            'check_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'بيان الإيصال'
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
            
        # إنشاء رقم إيصال تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['payment_number'].initial = f'PY-{timestamp}'


class ExpenseTypeForm(forms.ModelForm):
    """نموذج أنواع المصروفات"""
    
    class Meta:
        model = ExpenseType
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'كود نوع المصروف'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم نوع المصروف'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف نوع المصروف (اختياري)'
            }),
        }


class ExpenseForm(forms.ModelForm):
    """نموذج المصروفات"""
    
    class Meta:
        model = Expense
        fields = ['expense_number', 'date', 'treasury', 'expense_type', 'amount',
                  'description', 'beneficiary', 'notes']
        widgets = {
            'expense_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expense_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'بيان المصروف'
            }),
            'beneficiary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'المستفيد من المصروف'
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
            
        # إنشاء رقم مصروف تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['expense_number'].initial = f'EX-{timestamp}'


class RevenueTypeForm(forms.ModelForm):
    """نموذج أنواع الإيرادات"""
    
    class Meta:
        model = RevenueType
        fields = ['code', 'name', 'description']
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
                'placeholder': 'وصف نوع الإيراد (اختياري)'
            }),
        }


class RevenueForm(forms.ModelForm):
    """نموذج الإيرادات"""
    
    class Meta:
        model = Revenue
        fields = ['revenue_number', 'date', 'treasury', 'revenue_type', 'amount',
                  'description', 'source', 'notes']
        widgets = {
            'revenue_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'revenue_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'بيان الإيراد'
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مصدر الإيراد'
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
            
        # إنشاء رقم إيراد تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['revenue_number'].initial = f'RV-{timestamp}'


class PaymentNoteForm(forms.ModelForm):
    """نموذج أوراق الدفع"""

    class Meta:
        model = PaymentNote
        fields = ['note_number', 'date', 'due_date', 'treasury', 'supplier', 'amount',
                  'description', 'notes']
        widgets = {
            'note_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'بيان ورقة الدفع'
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
            # تحديد تاريخ الاستحقاق (30 يوم من اليوم)
            self.fields['due_date'].initial = date.today() + timedelta(days=30)

        # إنشاء رقم ورقة دفع تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['note_number'].initial = f'PN-{timestamp}'


class ReceiptNoteForm(forms.ModelForm):
    """نموذج أوراق القبض"""

    class Meta:
        model = ReceiptNote
        fields = ['note_number', 'date', 'due_date', 'treasury', 'customer', 'amount',
                  'description', 'notes']
        widgets = {
            'note_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'بيان ورقة القبض'
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
            # تحديد تاريخ الاستحقاق (30 يوم من اليوم)
            self.fields['due_date'].initial = date.today() + timedelta(days=30)

        # إنشاء رقم ورقة قبض تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['note_number'].initial = f'RN-{timestamp}'


class CustodyReceiptOutForm(forms.ModelForm):
    """نموذج إيصالات الأمانة الصادرة"""

    class Meta:
        model = CustodyReceiptOut
        fields = ['receipt_number', 'date', 'treasury', 'custodian', 'custodian_id', 'amount',
                  'purpose', 'expected_return_date', 'notes']
        widgets = {
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'custodian': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم أمين العهدة'
            }),
            'custodian_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهوية (اختياري)'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'purpose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الغرض من الأمانة'
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
            from datetime import date
            self.fields['date'].initial = date.today()

        # إنشاء رقم إيصال تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['receipt_number'].initial = f'CO-{timestamp}'


class CustodyReceiptInForm(forms.ModelForm):
    """نموذج إيصالات الأمانة الواردة"""

    class Meta:
        model = CustodyReceiptIn
        fields = ['receipt_number', 'date', 'treasury', 'depositor', 'depositor_id', 'amount',
                  'purpose', 'expected_return_date', 'notes']
        widgets = {
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'depositor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المودع'
            }),
            'depositor_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهوية (اختياري)'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'purpose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الغرض من الإيداع'
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
            from datetime import date
            self.fields['date'].initial = date.today()

        # إنشاء رقم إيصال تلقائي
        if not self.instance.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.fields['receipt_number'].initial = f'CI-{timestamp}'


class TreasuryTransferForm(forms.ModelForm):
    """نموذج تحويل بين الخزائن"""

    class Meta:
        model = TreasuryTransfer
        fields = ['transfer_number', 'date', 'from_treasury', 'to_treasury', 'amount',
                  'description', 'notes']
        widgets = {
            'transfer_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'سيتم إنشاؤه تلقائياً'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'from_treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'to_treasury': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'بيان التحويل'
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
            self.fields['transfer_number'].initial = f'TT-{timestamp}'

    def clean(self):
        cleaned_data = super().clean()
        from_treasury = cleaned_data.get('from_treasury')
        to_treasury = cleaned_data.get('to_treasury')

        if from_treasury and to_treasury and from_treasury == to_treasury:
            raise forms.ValidationError('لا يمكن التحويل من خزينة إلى نفس الخزينة')

        return cleaned_data
