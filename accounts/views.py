from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms


class ProfileEditForm(forms.ModelForm):
    """نموذج تعديل الملف الشخصي"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'الاسم الأول',
            'last_name': 'اسم العائلة',
            'email': 'البريد الإلكتروني',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل الاسم الأول'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم العائلة'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'أدخل البريد الإلكتروني'}),
        }


@login_required
def profile(request):
    """صفحة الملف الشخصي"""
    return render(request, 'accounts/profile.html')


@login_required
def edit_profile(request):
    """تعديل الملف الشخصي"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """تغيير كلمة المرور"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # للحفاظ على تسجيل الدخول
            messages.success(request, 'تم تغيير كلمة المرور بنجاح!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
