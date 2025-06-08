from django.contrib import admin
from .models import (TreasuryTransaction, Receipt, Payment, Expense, Revenue,
                     ExpenseType, RevenueType, PaymentNote, ReceiptNote,
                     CustodyReceiptOut, CustodyReceiptIn, TreasuryTransfer)


@admin.register(TreasuryTransaction)
class TreasuryTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'date', 'treasury', 'transaction_type', 'amount', 'description']
    list_filter = ['transaction_type', 'treasury', 'date']
    search_fields = ['transaction_number', 'description']
    ordering = ['-date', '-id']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'date', 'treasury', 'customer', 'amount', 'payment_method']
    list_filter = ['payment_method', 'treasury', 'date']
    search_fields = ['receipt_number', 'customer__name', 'description']
    ordering = ['-date', '-id']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'date', 'treasury', 'supplier', 'amount', 'payment_method']
    list_filter = ['payment_method', 'treasury', 'date']
    search_fields = ['payment_number', 'supplier__name', 'description']
    ordering = ['-date', '-id']


@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expense_number', 'date', 'treasury', 'expense_type', 'amount', 'beneficiary']
    list_filter = ['expense_type', 'treasury', 'date']
    search_fields = ['expense_number', 'description', 'beneficiary']
    ordering = ['-date', '-id']


@admin.register(RevenueType)
class RevenueTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['revenue_number', 'date', 'treasury', 'revenue_type', 'amount', 'source']
    list_filter = ['revenue_type', 'treasury', 'date']
    search_fields = ['revenue_number', 'description', 'source']
    ordering = ['-date', '-id']


@admin.register(PaymentNote)
class PaymentNoteAdmin(admin.ModelAdmin):
    list_display = ['note_number', 'date', 'due_date', 'treasury', 'supplier', 'amount', 'status']
    list_filter = ['status', 'treasury', 'date']
    search_fields = ['note_number', 'supplier__name', 'description']
    ordering = ['-date', '-id']


@admin.register(ReceiptNote)
class ReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['note_number', 'date', 'due_date', 'treasury', 'customer', 'amount', 'status']
    list_filter = ['status', 'treasury', 'date']
    search_fields = ['note_number', 'customer__name', 'description']
    ordering = ['-date', '-id']


@admin.register(CustodyReceiptOut)
class CustodyReceiptOutAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'date', 'treasury', 'custodian', 'amount', 'status']
    list_filter = ['status', 'treasury', 'date']
    search_fields = ['receipt_number', 'custodian', 'purpose']
    ordering = ['-date', '-id']


@admin.register(CustodyReceiptIn)
class CustodyReceiptInAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'date', 'treasury', 'depositor', 'amount', 'status']
    list_filter = ['status', 'treasury', 'date']
    search_fields = ['receipt_number', 'depositor', 'purpose']
    ordering = ['-date', '-id']


@admin.register(TreasuryTransfer)
class TreasuryTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_number', 'date', 'from_treasury', 'to_treasury', 'amount', 'status']
    list_filter = ['status', 'from_treasury', 'to_treasury', 'date']
    search_fields = ['transfer_number', 'description']
    ordering = ['-date', '-id']
