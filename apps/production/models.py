from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User
from django.utils import timezone


class WorkerProfile(BaseModel):
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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile', verbose_name="کاربر")
    stage = models.CharField(max_length=50, choices=STATION_CHOICES, verbose_name="مرحله کاری")
    skills = models.JSONField(default=list, blank=True, verbose_name="مهارت‌ها (لیست رشته‌ها)")
    skill_priority = models.JSONField(default=dict, blank=True, verbose_name="اولویت/میزان مهارت کارگر")
    is_available = models.BooleanField(default=True, verbose_name="فعال برای زمان‌بندی")
    work_start = models.TimeField(default=timezone.now, verbose_name="شروع کار")
    work_end = models.TimeField(default=timezone.now, verbose_name="پایان کار")
    break_start = models.TimeField(default=timezone.now, verbose_name="شروع استراحت")
    break_end = models.TimeField(default=timezone.now, verbose_name="پایان استراحت")
    excluded_products = models.ManyToManyField('catalog.Product', blank=True, verbose_name="محصولات ممنوعه")

    def __str__(self):
        return f"{self.user.username} - {self.get_stage_display()}"

    class Meta:
        verbose_name = "پروفایل کارگر"
        verbose_name_plural = "پروفایل کارگران"


class PaintingProcess(BaseModel):
    name = models.CharField(max_length=100, verbose_name="نام روند")
    code = models.CharField(max_length=20, unique=True, verbose_name="کد روند")
    color_codes = models.JSONField(default=list, verbose_name="لیست کدهای رنگی مرتبط")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "روند نقاشی"
        verbose_name_plural = "روندهای نقاشی"


class PaintingStage(BaseModel):
    process = models.ForeignKey(PaintingProcess, on_delete=models.CASCADE, related_name='stages')
    order = models.PositiveSmallIntegerField(verbose_name="ترتیب مرحله")
    name = models.CharField(max_length=100, verbose_name="نام مرحله")
    duration_minutes = models.PositiveIntegerField(verbose_name="زمان انجام (دقیقه)")
    drying_time_minutes = models.PositiveIntegerField(default=0, verbose_name="زمان خشک‌شدن (دقیقه)")
    required_skill = models.CharField(max_length=50, default='painter', verbose_name="مهارت مورد نیاز")

    SKILL_CHOICES = [
        ('painter', 'نقاش'),
        ('sealer', 'رزین‌کار'),
        ('primer', 'پرایمر'),
        ('polisher', 'پولیش'),
        ('sprayer', 'سم‌پاش'),
    ]

    class Meta:
        ordering = ['process', 'order']
        unique_together = ('process', 'order')
        verbose_name = "مرحله نقاشی"
        verbose_name_plural = "مراحل نقاشی"

    def __str__(self):
        return f"{self.process.name} - مرحله {self.order}: {self.name}"


class PaintingAssignmentRule(BaseModel):
    RULE_TYPE_CHOICES = [
        ('priority', 'فقط اولویت‌دهی'),
        ('exclusive', 'محدودکننده'),
        ('exclusion', 'منع‌کننده'),
    ]
    worker = models.ForeignKey(
        WorkerProfile,
        on_delete=models.CASCADE,
        verbose_name="کارگر",
        related_name='assignment_rules'
    )
    painting_stage = models.ForeignKey(
        PaintingStage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="مرحله نقاشی (اختیاری)"
    )
    color_codes = models.JSONField(
        null=True,
        blank=True,
        verbose_name="کدهای رنگ",
        help_text="لیست کدهای رنگی که این قانون برای آن‌ها اعمال می‌شود (خالی = همه رنگ‌ها)"
    )
    process = models.ForeignKey(
        PaintingProcess,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="روند نقاشی (اختیاری)"
    )
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPE_CHOICES,
        default='priority',
        verbose_name="نوع قانون"
    )
    priority = models.IntegerField(
        default=100,
        verbose_name="اولویت",
        help_text="عدد بالاتر = اولویت بیشتر در زمان‌بندی (فقط برای نوع اولویت‌دهی)"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "قانون تخصیص کارگر"
        verbose_name_plural = "قوانین تخصیص کارگر"
        ordering = ['-priority', 'worker']

    def __str__(self):
        parts = []
        if self.painting_stage:
            parts.append(str(self.painting_stage))
        if self.color_codes:
            parts.append(f"رنگ‌های {', '.join(self.color_codes)}")
        type_label = dict(self.RULE_TYPE_CHOICES).get(self.rule_type, self.rule_type)
        return f"{self.worker} [{type_label}] ← {' + '.join(parts)}"


class Holiday(BaseModel):
    date = models.DateField(unique=True, verbose_name="تاریخ تعطیلی")
    description = models.CharField(max_length=200, blank=True, verbose_name="مناسبت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تعطیلی"
        verbose_name_plural = "تعطیلات"
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.description}" if self.description else str(self.date)


def create_paint_tasks(tasks_list, order, quantity, process, base_step, order_item, color_part=''):
    """ایجاد تسک‌های نقاشی برای یک قطعه/آیتم و افزودن به task_list."""
    stages = process.stages.all().order_by('order')
    for idx, stage in enumerate(stages, start=1):
        tasks_list.append(
            ProductionTask(
                order=order,
                part=None,
                station_name='paint',
                step_order=base_step + idx,
                quantity=quantity,
                status='pending' if idx == 1 else 'waiting',
                painting_stage=stage,
                order_item=order_item,
                color_part=color_part,
            )
        )
