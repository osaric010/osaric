from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
from services.models import DeletedRecord, EditHistory, SystemBackup
import random


class Command(BaseCommand):
    help = 'إنشاء أنشطة تجريبية للخدمات'

    def handle(self, *args, **options):
        self.stdout.write('إنشاء أنشطة تجريبية...')

        # الحصول على المستخدم الأول
        try:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR('لا يوجد مستخدمين في النظام'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطأ في الحصول على المستخدم: {e}'))
            return

        # إنشاء سجلات محذوفة تجريبية
        content_type = ContentType.objects.get_for_model(User)
        
        deleted_items = [
            {'object_repr': 'فاتورة مبيعات #001', 'reason': 'خطأ في البيانات'},
            {'object_repr': 'عميل: أحمد محمد', 'reason': 'عميل مكرر'},
            {'object_repr': 'صنف: لابتوب ديل', 'reason': 'صنف ملغي'},
            {'object_repr': 'فاتورة مشتريات #045', 'reason': 'فاتورة خاطئة'},
            {'object_repr': 'مورد: شركة التقنية', 'reason': 'مورد غير نشط'},
        ]

        for i, item in enumerate(deleted_items):
            DeletedRecord.objects.get_or_create(
                content_type=content_type,
                object_id=user.id,
                object_repr=item['object_repr'],
                defaults={
                    'deleted_by': user,
                    'deletion_reason': item['reason'],
                    'is_restored': False,
                    'object_data': {'test': 'data'}
                }
            )

        self.stdout.write('تم إنشاء 5 سجلات محذوفة')

        # إنشاء سجلات تعديل تجريبية
        edit_items = [
            {'field_name': 'السعر', 'old_value': '100', 'new_value': '120'},
            {'field_name': 'الكمية', 'old_value': '50', 'new_value': '45'},
            {'field_name': 'اسم العميل', 'old_value': 'أحمد علي', 'new_value': 'أحمد علي محمد'},
            {'field_name': 'رقم الهاتف', 'old_value': '0501234567', 'new_value': '0507654321'},
            {'field_name': 'العنوان', 'old_value': 'الرياض', 'new_value': 'الرياض - حي النخيل'},
            {'field_name': 'حالة الفاتورة', 'old_value': 'مسودة', 'new_value': 'مؤكدة'},
            {'field_name': 'طريقة الدفع', 'old_value': 'نقدي', 'new_value': 'آجل'},
        ]

        for i, item in enumerate(edit_items):
            EditHistory.objects.get_or_create(
                content_type=content_type,
                object_id=user.id,
                field_name=item['field_name'],
                defaults={
                    'edited_by': user,
                    'old_value': item['old_value'],
                    'new_value': item['new_value'],
                    'edit_reason': 'تحديث البيانات'
                }
            )

        self.stdout.write('تم إنشاء 7 سجلات تعديل')

        # إنشاء نسخ احتياطية تجريبية
        backup_items = [
            {
                'backup_name': 'نسخة احتياطية يومية',
                'backup_type': 'FULL',
                'file_size': 1024 * 1024 * 150,  # 150 MB
                'days_ago': 1
            },
            {
                'backup_name': 'نسخة احتياطية أسبوعية',
                'backup_type': 'INCREMENTAL',
                'file_size': 1024 * 1024 * 75,  # 75 MB
                'days_ago': 7
            },
            {
                'backup_name': 'نسخة احتياطية شهرية',
                'backup_type': 'FULL',
                'file_size': 1024 * 1024 * 300,  # 300 MB
                'days_ago': 30
            },
        ]

        for item in backup_items:
            SystemBackup.objects.get_or_create(
                backup_name=item['backup_name'],
                defaults={
                    'backup_type': item['backup_type'],
                    'file_path': f'/backups/{item["backup_name"].replace(" ", "_")}.sql',
                    'file_size': item['file_size'],
                    'created_by': user,
                    'is_valid': True,
                    'description': f'نسخة احتياطية تحتوي على {random.randint(15, 25)} جدول و {random.randint(1000, 5000)} سجل'
                }
            )

        self.stdout.write('تم إنشاء 3 نسخ احتياطية')

        self.stdout.write(
            self.style.SUCCESS('تم إنشاء جميع الأنشطة التجريبية بنجاح!')
        )
