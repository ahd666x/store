from django.core.management.base import BaseCommand
from apps.catalog.models import ProductSection, ColorMaterialMap, Color


class Command(BaseCommand):
    help = 'Check for colors used in ProductSection that have no ColorMaterialMap mapping'

    def handle(self, *args, **options):
        sections = ProductSection.objects.select_related('color', 'product__category').all()
        unmapped = []

        for section in sections:
            if not ColorMaterialMap.resolve_material(section.color, section.product.category):
                unmapped.append(section)

        if not unmapped:
            self.stdout.write(self.style.SUCCESS('All colors used in ProductSection have a material mapping.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {len(unmapped)} ProductSection(s) with unmapped colors:'))
        for section in unmapped:
            self.stdout.write(
                f'  - Product: {section.product.name} | Section: {section.name} | Color: {section.color.name} | Category: {section.product.category.name}'
            )

        # Also list all ColorMaterialMap entries for reference
        self.stdout.write('\nExisting ColorMaterialMap entries:')
        for cm in ColorMaterialMap.objects.select_related('color', 'material', 'category').all():
            scope = cm.category.name if cm.category else 'All Categories'
            self.stdout.write(f'  - {cm.color.name} -> {cm.material.name} ({scope})')
