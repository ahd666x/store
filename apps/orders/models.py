from django.db import models
from apps.common.models import BaseModel
from apps.common.fields import PersianDateField, PersianDateTimeField
from apps.accounts.models import User
from apps.catalog.models import Product
import jdatetime
import qrcode
import os
from django.conf import settings


def generate_qr_code(data, folder_name, filename_prefix):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    media_root = settings.MEDIA_ROOT
    folder = os.path.join(media_root, folder_name)
    os.makedirs(folder, exist_ok=True)
    
    filename = f"{filename_prefix}.png"
    filepath = os.path.join(folder, filename)
    img.save(filepath)
    
    return os.path.join(folder_name, filename)


class Customer(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        verbose_name="نماینده"
    )
    name = models.CharField(max_length=100, verbose_name="نام مشتری")
    phone = models.CharField(max_length=20, blank=True, verbose_name="تلفن")
    address = models.TextField(blank=True, verbose_name="آدرس")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"


class Order(BaseModel):
    ORDER_STATUS = (
        ('draft', 'پیش‌نویس'),
        ('planned', 'برنامه‌ریزی شده'),
        ('producing', 'در حال تولید'),
        ('completed', 'تکمیل شده'),
        ('paid', 'پرداخت شده'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    )

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name="نماینده")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="مشتری")
    number = models.CharField(max_length=10, blank=True, verbose_name="شماره سفارش")
    created_at = PersianDateField(default=jdatetime.date.today, verbose_name="تاریخ سفارش")
    due_date = PersianDateField(null=True, blank=True, verbose_name="تاریخ تحویل")
    priority = models.PositiveSmallIntegerField(
        default=3,
        choices=[(1, 'بسیار بالا'), (2, 'بالا'), (3, 'متوسط'), (4, 'پایین')],
        verbose_name="اولویت"
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='draft',
        verbose_name="وضعیت سفارش"
    )
    total_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="مبلغ کل")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="تخفیف")
    final_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="مبلغ نهایی")
    discount = models.ForeignKey('discounts.Discount', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تخفیف")
    shipping_address = models.TextField(verbose_name="آدرس ارسال")
    tracking_code = models.CharField(max_length=100, blank=True, verbose_name="کد رهگیری")
    paid_at = PersianDateTimeField(null=True, blank=True, verbose_name="تاریخ پرداخت")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش {self.id} - {self.customer}"

    @property
    def total_price(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def packaging_summary(self):
        total_units = 0
        packed_units = 0
        shipped_units = 0
        for item in self.items.all():
            item_total = item.packaging_units.count()
            total_units += item_total
            packed_units += item.packaging_units.filter(is_packed=True).count()
            shipped_units += item.packaging_units.filter(is_shipped=True).count()
        return {
            'total': total_units,
            'packed': packed_units,
            'shipped': shipped_units,
        }

    def calculate_total(self):
        self.total_amount = sum(item.total_price for item in self.items.all())
        self.final_amount = self.total_amount - self.discount_amount
        self.save()


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="سفارش")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="محصول")
    notes = models.CharField(max_length=200, blank=True, verbose_name="توضیحات")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    size = models.CharField(max_length=100, blank=True, verbose_name="اندازه")
    qr_code = models.ImageField(upload_to='qr/', blank=True, null=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت واحد")

    class Meta:
        verbose_name = "لیست سفارش"
        verbose_name_plural = "لیست سفارش‌ها"

    def __str__(self):
        return f"{self.product.name} (سفارش {self.order.id})"

    @property
    def color_summary(self):
        colors = self.ordercolor.all()
        parts = []
        for c in colors:
            if c.code and c.code != 'nan':
                parts.append(f"{c.part}:{c.code}")
        return "-".join(parts) if parts else "بدون رنگ"

    @property
    def packaging_progress(self):
        total = self.packaging_units.count()
        packed = self.packaging_units.filter(is_packed=True).count()
        return packed, total

    @property
    def shipping_progress(self):
        total = self.packaging_units.count()
        shipped = self.packaging_units.filter(is_shipped=True).count()
        return shipped, total

    @property
    def is_fully_packed(self):
        packed, total = self.packaging_progress
        return total > 0 and packed == total

    @property
    def is_fully_shipped(self):
        shipped, total = self.shipping_progress
        return total > 0 and shipped == total

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def calculate_price(self):
        if not self.product:
            return 0

        order_size_str = self.size or self.product.default_size
        default_size_str = self.product.default_size

        if not order_size_str or not default_size_str:
            return int(self.product.base_price or 0)

        import re
        order_numbers = re.findall(r'\d+', order_size_str)
        default_numbers = re.findall(r'\d+', default_size_str)

        if not order_numbers or not default_numbers:
            return int(self.product.base_price or 0)

        order_length = int(order_numbers[0])
        default_length = int(default_numbers[0])

        if default_length == 0:
            return int(self.product.base_price or 0)

        base_price_int = int(self.product.base_price or 0)
        increment_percent_float = float(self.product.price_increment_per_cm or 0)

        diff_percent = ((order_length - default_length) * increment_percent_float) / 100
        price_increase = base_price_int * diff_percent
        final_price = base_price_int + price_increase

        if final_price < 0:
            return 0
        return int(round(final_price))

    def save(self, *args, **kwargs):
        if self.product:
            try:
                self.unit_price = self.calculate_price()
            except Exception:
                if self.product and self.product.base_price is not None:
                    self.unit_price = int(self.product.base_price)
                else:
                    self.unit_price = 0

        is_new = not self.pk
        super().save(*args, **kwargs)

        if is_new and not self.qr_code and self.product:
            qr_data = f"Order:{self.order_id}|Product:{self.product.name}|Qty:{self.quantity}|Size:{self.size or '-'}"
            filename_prefix = f"order_{self.order_id}_item_{self.id}"
            relative_path = generate_qr_code(qr_data, 'qr', filename_prefix)
            self.qr_code = relative_path
            super().save(update_fields=['qr_code'])


class OrderColor(models.Model):
    PART_CHOICES = [
        ('بدنه', 'بدنه'),
        ('درب', 'درب'),
        ('دستگیره', 'دستگیره'),
        ('پایه', 'پایه'),
        ('صفحه', 'صفحه'),
        ('رینگ', 'رینگ'),
    ]
    CODE_CHOICES = [(str(i), str(i)) for i in range(1, 11)]
    CODE_CHOICES.append(('جناغی', 'جناغی'))
    CODE_CHOICES.append(('بتنی', 'بتنی'))

    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='ordercolor', verbose_name="آیتم سفارش")
    part = models.CharField(max_length=20, choices=PART_CHOICES, verbose_name="قطعه")
    code = models.CharField(max_length=20, choices=CODE_CHOICES, verbose_name="کد رنگ")

    def __str__(self):
        return f"{self.part}:{self.code}"

    class Meta:
        verbose_name = "رنگ سفارش"
        verbose_name_plural = "رنگ‌های سفارش"
        unique_together = ['orderitem', 'part']


class PackagingUnit(BaseModel):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='packaging_units', verbose_name="آیتم سفارش")
    unit_number = models.PositiveIntegerField(verbose_name="شماره واحد")
    qr_code = models.ImageField(upload_to='packaging_qr/', blank=True, null=True)
    is_packed = models.BooleanField(default=False, verbose_name="بسته‌بندی شده")
    is_shipped = models.BooleanField(default=False, verbose_name="ارسال شده")
    packed_at = PersianDateTimeField(null=True, blank=True, verbose_name="زمان بسته‌بندی")
    shipped_at = PersianDateTimeField(null=True, blank=True, verbose_name="زمان ارسال")
    packed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='packed_units', verbose_name="بسته‌بندی‌کننده")
    shipped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipped_units', verbose_name="ارسال‌کننده")

    class Meta:
        verbose_name = "واحد بسته‌بندی"
        verbose_name_plural = "واحدهای بسته‌بندی"
        unique_together = ['order_item', 'unit_number']
        ordering = ['order_item', 'unit_number']

    def __str__(self):
        return f"واحد {self.unit_number} - {self.order_item}"

    def save(self, *args, **kwargs):
        if not self.qr_code and self.order_item_id:
            qr_data = f"Unit:{self.unit_number}|OrderItem:{self.order_item_id}|Order:{self.order_item.order_id}|Product:{self.order_item.product.name}"
            filename_prefix = f"unit_{self.order_item_id}_{self.unit_number}"
            relative_path = generate_qr_code(qr_data, 'packaging_qr', filename_prefix)
            self.qr_code = relative_path
        super().save(*args, **kwargs)


class ProductionTask(BaseModel):
    STATION_CHOICES = [
        ('cut', 'برش'),
        ('cnc', 'CNC'),
        ('dr', 'سوراخکاری'),
        ('pvc', 'نوارکاری'),
        ('prs', 'پرس'),
        ('mon', 'مونتاژ اول'),
        ('vacum', 'وکیوم'),
        ('paint', 'نقاشی'),
        ('assembly2', 'مونتاژ نهایی'),
        ('packaging', 'بسته‌بندی'),
        ('shipping', 'ارسال شده'),
    ]

    TASK_STATUS = (
        ('waiting', 'در انتظار مرحله قبل'),
        ('pending', 'آماده انجام'),
        ('done', 'تکمیل شده'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tasks', verbose_name="سفارش")
    part = models.ForeignKey('catalog.Part', on_delete=models.PROTECT, null=True, blank=True, verbose_name="قطعه")
    station_name = models.CharField(max_length=50, choices=STATION_CHOICES, verbose_name="ایستگاه کاری")
    step_order = models.PositiveIntegerField(verbose_name="اولویت مرحله")
    quantity = models.PositiveIntegerField(verbose_name="عدد قطعه")
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='waiting', verbose_name="وضعیت")
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="انجام‌دهنده")
    completed_at = PersianDateTimeField(null=True, blank=True, verbose_name="زمان تکمیل")
    order_item = models.ForeignKey(
        OrderItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='paint_tasks',
        verbose_name="آیتم سفارش مرتبط"
    )
    color_part = models.CharField(max_length=50, blank=True, verbose_name="بخش رنگی")
    painting_stage = models.ForeignKey(
        'production.PaintingStage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="مرحله نقاشی"
    )
    scheduled_start = models.DateTimeField(null=True, blank=True, verbose_name="زمان شروع برنامه‌ریزی شده")
    scheduled_end = models.DateTimeField(null=True, blank=True, verbose_name="زمان پایان برنامه‌ریزی شده")
    assigned_worker = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        verbose_name="کارگر تخصیص‌یافته"
    )

    class Meta:
        verbose_name = "وظیفه تولید"
        verbose_name_plural = "وظایف تولید"
        ordering = ['order', 'step_order']
        indexes = [
            models.Index(fields=['station_name', 'scheduled_start']),
            models.Index(fields=['assigned_worker', 'scheduled_start']),
            models.Index(fields=['order_item', 'station_name', 'status']),
        ]

    def __str__(self):
        target = self.part or self.order_item or "—"
        return f"{self.get_station_name_display()} | {target} (سفارش {self.order.id})"

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = ProductionTask.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        if self.status == 'done' and old_status != 'done':
            if not self.completed_at:
                from django.utils import timezone
                self.completed_at = timezone.now()

        super().save(*args, **kwargs)

        if self.status == 'done' and old_status != 'done':
            self._activate_next_task()

    def _activate_next_task(self):
        if self.order_item_id:
            next_step = ProductionTask.objects.filter(
                order=self.order,
                order_item=self.order_item,
                color_part=self.color_part,
                step_order=self.step_order + 1,
            ).first()
        else:
            next_step = ProductionTask.objects.filter(
                order=self.order,
                part=self.part,
                step_order=self.step_order + 1,
            ).first()

        if next_step and next_step.status == 'waiting':
            next_step.status = 'pending'
            next_step.save()

        self._update_order_status()

    def _update_order_status(self):
        order = self.order
        if order.status in {'paid', 'shipped', 'delivered', 'cancelled'}:
            return

        all_tasks = order.tasks.all()
        total = all_tasks.count()
        done = all_tasks.filter(status='done').count()

        if total == 0:
            return
        if done == total:
            new_status = 'completed'
        elif done > 0:
            new_status = 'producing'
        else:
            new_status = 'planned'

        if order.status != new_status:
            order.status = new_status
            order.save(update_fields=['status'])


class ProductionLog(BaseModel):
    STATION_CHOICES = [
        ('cut', 'برش'),
        ('cnc', 'CNC'),
        ('dr', 'سوراخکاری'),
        ('pvc', 'نوارکاری'),
        ('prs', 'پرس'),
        ('mon', 'مونتاژ اول'),
        ('vacum', 'وکیوم'),
        ('paint', 'نقاشی'),
        ('assembly2', 'مونتاژ نهایی'),
        ('packaging', 'بسته‌بندی'),
        ('shipping', 'ارسال شده'),
    ]

    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='logs', verbose_name="آیتم سفارش")
    stage = models.CharField(max_length=50, choices=STATION_CHOICES, verbose_name="مرحله")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name="کاربر")
    notes = models.CharField(max_length=200, blank=True, verbose_name="یادداشت")
    created_at = PersianDateField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "گزارش تولید"
        verbose_name_plural = "گزارش‌های تولید"
        ordering = ['-created_at']


class ShipmentLog(BaseModel):
    packaging_unit = models.ForeignKey(
        PackagingUnit,
        on_delete=models.CASCADE,
        related_name='shipment_logs',
        verbose_name="بسته‌بندی"
    )
    plate_number = models.CharField(max_length=50, verbose_name="پلاک")
    shipped_at = PersianDateTimeField(auto_now_add=True, verbose_name="زمان ارسال")
    shipped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="ارسال‌کننده")

    class Meta:
        verbose_name = "بارگیری"
        verbose_name_plural = "بارگیری"
        ordering = ['-shipped_at']
