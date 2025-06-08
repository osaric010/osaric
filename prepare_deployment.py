#!/usr/bin/env python3
"""
سكريبت تحضير النشر السريع
Quick deployment preparation script
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """تشغيل أمر مع عرض الوصف"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - تم بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - فشل: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_git_status():
    """التحقق من حالة Git"""
    print("🔍 التحقق من حالة Git...")
    
    # التحقق من وجود Git
    if not run_command("git --version", "التحقق من Git"):
        print("❌ Git غير مثبت. يرجى تثبيت Git أولاً.")
        return False
    
    # التحقق من وجود مستودع Git
    if not os.path.exists('.git'):
        print("📁 إنشاء مستودع Git جديد...")
        if not run_command("git init", "إنشاء مستودع Git"):
            return False
    
    return True

def prepare_files():
    """تحضير الملفات للنشر"""
    print("📋 تحضير ملفات النشر...")
    
    # التحقق من وجود الملفات المطلوبة
    required_files = [
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'railway.json',
        'manage.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ ملفات مفقودة: {', '.join(missing_files)}")
        return False
    
    print("✅ جميع الملفات المطلوبة موجودة")
    return True

def create_github_repo():
    """إنشاء مستودع GitHub"""
    print("\n🐙 إعداد GitHub...")
    
    repo_name = input("أدخل اسم المستودع (أو اتركه فارغاً لـ 'osaric-accounts'): ").strip()
    if not repo_name:
        repo_name = "osaric-accounts"
    
    print(f"📝 سيتم إنشاء مستودع باسم: {repo_name}")
    
    # إضافة جميع الملفات
    if not run_command("git add .", "إضافة الملفات"):
        return False
    
    # إنشاء commit
    commit_message = "Initial commit - Osaric Accounts System ready for deployment"
    if not run_command(f'git commit -m "{commit_message}"', "إنشاء commit"):
        return False
    
    # تعيين branch رئيسي
    if not run_command("git branch -M main", "تعيين branch main"):
        return False
    
    print(f"\n📋 خطوات إنشاء المستودع على GitHub:")
    print(f"1. اذهب إلى: https://github.com/new")
    print(f"2. اسم المستودع: {repo_name}")
    print(f"3. اجعله Public")
    print(f"4. لا تضيف README أو .gitignore أو LICENSE")
    print(f"5. انقر 'Create repository'")
    print(f"6. انسخ رابط المستودع (https://github.com/username/{repo_name}.git)")
    
    github_url = input("\nالصق رابط المستودع هنا: ").strip()
    
    if github_url:
        # إضافة remote origin
        if not run_command(f"git remote add origin {github_url}", "إضافة remote origin"):
            return False
        
        # رفع الكود
        if not run_command("git push -u origin main", "رفع الكود إلى GitHub"):
            return False
        
        print(f"✅ تم رفع الكود إلى: {github_url}")
        return github_url
    
    return False

def show_deployment_options(github_url=None):
    """عرض خيارات النشر"""
    print("\n" + "="*60)
    print("🚀 خيارات النشر المتاحة")
    print("="*60)
    
    print("\n1️⃣ Railway (الأسرع والأسهل - مجاني):")
    print("   🔗 https://railway.app/new")
    print("   📋 اختر 'Deploy from GitHub repo'")
    if github_url:
        print(f"   📁 المستودع: {github_url}")
    print("   ⚡ نشر تلقائي + قاعدة بيانات مجانية")
    
    print("\n2️⃣ Render (موثوق - مجاني):")
    print("   🔗 https://render.com")
    print("   📋 إنشاء 'Web Service' جديد")
    print("   🔧 Build Command: pip install -r requirements.txt")
    print("   🚀 Start Command: gunicorn osaric_accounts.wsgi:application")
    
    print("\n3️⃣ Heroku (كلاسيكي - مجاني محدود):")
    print("   🔗 https://heroku.com")
    print("   📋 إنشاء تطبيق جديد")
    print("   🔗 ربط مع GitHub")
    print("   🗄️ إضافة Heroku Postgres")
    
    print("\n4️⃣ Vercel (للواجهات الأمامية):")
    print("   🔗 https://vercel.com")
    print("   📋 استيراد من GitHub")
    print("   ⚙️ إعداد كـ Django app")

def main():
    """الدالة الرئيسية"""
    print("🎯 مرحباً بك في سكريبت تحضير النشر السريع")
    print("🏢 نظام حسابات أوساريك")
    print("-" * 50)
    
    # التحقق من Git
    if not check_git_status():
        return
    
    # تحضير الملفات
    if not prepare_files():
        return
    
    # سؤال المستخدم عن GitHub
    create_github = input("\nهل تريد رفع الكود إلى GitHub؟ (y/n): ").lower().strip()
    
    github_url = None
    if create_github in ['y', 'yes', 'نعم']:
        github_url = create_github_repo()
    
    # عرض خيارات النشر
    show_deployment_options(github_url)
    
    print("\n" + "="*60)
    print("🎉 تم تحضير المشروع للنشر بنجاح!")
    print("="*60)
    
    print("\n📋 الخطوات التالية:")
    print("1. اختر منصة النشر من الخيارات أعلاه")
    print("2. اتبع التعليمات لكل منصة")
    print("3. ستحصل على رابط موثق مجاني")
    print("4. بيانات الدخول: admin / admin123")
    
    print("\n🔗 روابط مفيدة:")
    print("📚 دليل النشر: RAILWAY_DEPLOYMENT.md")
    print("📖 الوثائق: README.md")
    print("🆘 الدعم: support@osaric.com")
    
    print("\n🚀 حظاً موفقاً!")

if __name__ == "__main__":
    main()
