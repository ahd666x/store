from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.catalog.models import ProductSection, ColorMaterialMap


class Command(BaseCommand):
    help = 'Check for colors used in product sections that do not have a ColorMaterialMap.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exit-nonzero',
            action='store_true',
            help='Exit with status 1 if unmapped colors are found.',
        )

    def handle(self, *args, **options):
        import sys, io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        self.stdout = sys.stdout

        used_color_ids = ProductSection.objects.values_list('color', flat=True).distinct()
        unmapped = []
        for color_id in used_color_ids:
            section = ProductSection.objects.select_related('product', 'color').filter(color_id=color_id).first()
            if not section:
                continue
            if not ColorMaterialMap.objects.filter(color_id=color_id).exists():
                products = ProductSection.objects.filter(color_id=color_id).values_list('product__name', flat=True).distinct()
                unmapped.append({
                    'color': section.color,
                    'products': list(products),
                })

        if unmapped:
            self.stdout.write(self.style.WARNING('رنگ‌های بدون نگاشت متریال:'))
            for item in unmapped:
                self.stdout.write(f"- {item['color'].name}")
                for product_name in item['products']:
                    self.stdout.write(f"    • {product_name}")
            if options['exit_nonzero']:
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS('همه رنگ‌ها نگاشت متریال دارند.'))
