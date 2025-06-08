"""
مهام مجدولة للنظام
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .currency_rates import currency_service

logger = logging.getLogger(__name__)


class CurrencyRateUpdateTask:
    """مهمة تحديث أسعار العملات"""
    
    def __init__(self):
        self.last_update = None
        self.update_interval = 15  # دقيقة
        
    def should_update(self):
        """تحديد ما إذا كان يجب التحديث"""
        if not self.last_update:
            return True
            
        time_diff = timezone.now() - self.last_update
        return time_diff.total_seconds() >= (self.update_interval * 60)
    
    def run(self):
        """تشغيل مهمة التحديث"""
        if not self.should_update():
            logger.info("لا يحتاج تحديث أسعار العملات الآن")
            return False
            
        logger.info("بدء تحديث أسعار العملات...")
        
        try:
            result = currency_service.update_all_rates()
            
            if result['success'] > 0:
                self.last_update = timezone.now()
                logger.info(f"تم تحديث {result['success']} بنك بنجاح")
                return True
            else:
                logger.warning("فشل في تحديث جميع البنوك")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في تحديث أسعار العملات: {str(e)}")
            return False


class TaskScheduler:
    """مجدول المهام"""
    
    def __init__(self):
        self.currency_task = CurrencyRateUpdateTask()
        self.is_running = False
        
    def start(self):
        """بدء المجدول"""
        if self.is_running:
            logger.warning("المجدول يعمل بالفعل")
            return
            
        self.is_running = True
        logger.info("تم بدء مجدول المهام")
        
    def stop(self):
        """إيقاف المجدول"""
        self.is_running = False
        logger.info("تم إيقاف مجدول المهام")
        
    def run_currency_update(self):
        """تشغيل مهمة تحديث العملات"""
        if not self.is_running:
            return False
            
        return self.currency_task.run()


# إنشاء instance عام للمجدول
task_scheduler = TaskScheduler()


def update_currency_rates_task():
    """دالة لتحديث أسعار العملات (للاستخدام مع Celery أو cron)"""
    return task_scheduler.run_currency_update()


def setup_periodic_tasks():
    """إعداد المهام الدورية"""
    try:
        # يمكن استخدام Celery Beat أو Django-crontab
        # هنا مثال بسيط للتشغيل اليدوي
        
        task_scheduler.start()
        logger.info("تم إعداد المهام الدورية")
        
        # تحديث فوري عند البدء
        task_scheduler.run_currency_update()
        
    except Exception as e:
        logger.error(f"خطأ في إعداد المهام الدورية: {str(e)}")


# Auto-start scheduler when module is imported
if getattr(settings, 'AUTO_START_TASKS', True):
    setup_periodic_tasks()
