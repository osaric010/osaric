from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import TaskbarSettings


class Command(BaseCommand):
    help = 'تطبيق إعدادات شريط المهام على جميع المستخدمين'

    def add_arguments(self, parser):
        parser.add_argument(
            '--position',
            type=str,
            default='HORIZONTAL',
            help='موضع شريط المهام (NONE, AUTO_HIDE, VERTICAL, HORIZONTAL)'
        )
        parser.add_argument(
            '--theme',
            type=str,
            default='default',
            help='مظهر شريط المهام (default, dark, light, blue)'
        )
        parser.add_argument(
            '--size',
            type=str,
            default='medium',
            help='حجم شريط المهام (small, medium, large)'
        )
        parser.add_argument(
            '--show-icons',
            action='store_true',
            default=True,
            help='إظهار الأيقونات'
        )
        parser.add_argument(
            '--show-text',
            action='store_true',
            default=True,
            help='إظهار النص'
        )
        parser.add_argument(
            '--auto-hide',
            action='store_true',
            default=False,
            help='إخفاء تلقائي'
        )

    def handle(self, *args, **options):
        self.stdout.write('تطبيق إعدادات شريط المهام...')

        # الترتيب الافتراضي للقوائم
        default_menu_order = [
            'dashboard',
            'definitions',
            'sales',
            'purchases',
            'inventory',
            'accounting',
            'branches',
            'services',
            'reports'
        ]

        # العناصر المثبتة افتراضياً
        default_pinned_items = ['dashboard', 'sales', 'purchases']

        users_updated = 0
        users_created = 0

        for user in User.objects.filter(is_active=True):
            settings, created = TaskbarSettings.objects.get_or_create(
                user=user,
                defaults={
                    'position': options['position'],
                    'auto_hide': options['auto_hide'],
                    'show_icons': options['show_icons'],
                    'show_text': options['show_text'],
                    'theme': options['theme'],
                    'size': options['size'],
                    'menu_order': default_menu_order,
                    'pinned_items': default_pinned_items,
                }
            )

            if created:
                users_created += 1
                self.stdout.write(f'تم إنشاء إعدادات جديدة للمستخدم: {user.username}')
            else:
                # تحديث الإعدادات الموجودة
                settings.position = options['position']
                settings.auto_hide = options['auto_hide']
                settings.show_icons = options['show_icons']
                settings.show_text = options['show_text']
                settings.theme = options['theme']
                settings.size = options['size']
                
                # تحديث ترتيب القوائم إذا كان فارغاً
                if not settings.menu_order:
                    settings.menu_order = default_menu_order
                
                # تحديث العناصر المثبتة إذا كانت فارغة
                if not settings.pinned_items:
                    settings.pinned_items = default_pinned_items
                
                settings.save()
                users_updated += 1
                self.stdout.write(f'تم تحديث إعدادات المستخدم: {user.username}')

        self.stdout.write(
            self.style.SUCCESS(
                f'تم الانتهاء! تم إنشاء إعدادات لـ {users_created} مستخدم وتحديث {users_updated} مستخدم'
            )
        )

        # عرض ملخص الإعدادات المطبقة
        self.stdout.write('\nالإعدادات المطبقة:')
        self.stdout.write(f'- الموضع: {options["position"]}')
        self.stdout.write(f'- المظهر: {options["theme"]}')
        self.stdout.write(f'- الحجم: {options["size"]}')
        self.stdout.write(f'- إظهار الأيقونات: {"نعم" if options["show_icons"] else "لا"}')
        self.stdout.write(f'- إظهار النص: {"نعم" if options["show_text"] else "لا"}')
        self.stdout.write(f'- إخفاء تلقائي: {"نعم" if options["auto_hide"] else "لا"}')
        self.stdout.write(f'- ترتيب القوائم: {", ".join(default_menu_order)}')
        self.stdout.write(f'- العناصر المثبتة: {", ".join(default_pinned_items)}')
