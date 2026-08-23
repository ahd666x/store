from django.db import models
from django.utils.text import slugify
from apps.common.models import BaseModel
from apps.common.managers import ActiveManager
from apps.accounts.models import User


class ProductCategory(BaseModel):
    name = models.CharField(max_length=100, verbose_name="نام دسته")
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True, verbose_name="اسلاگ")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while ProductCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)


class Color(BaseModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام رنگ")
    code = models.CharField(max_length=7, blank=True, verbose_name="کد رنگ (هگز)")

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ‌ها"

    def __str__(self):
        return self.name


class Material(BaseModel):
    name = models.CharField(max_length=100, verbose_name="نام ورق")
    thickness = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="ضخامت (میلی‌متر)")

    class Meta:
        verbose_name = "متریال"
        verbose_name_plural = "متریال‌ها"

    def __str__(self):
        return f"{self.name} ({self.thickness}mm)"


class Product(BaseModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products', verbose_name="دسته")
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(max_length=220, unique=True, blank=True, allow_unicode=True, verbose_name="اسلاگ")
    color = models.CharField(max_length=100, blank=True, verbose_name="رنگ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    default_size = models.CharField(max_length=100, blank=True, verbose_name="سایز پیش‌فرض")
    default_colors = models.JSONField(default=dict, blank=True, verbose_name="رنگ‌های پیش‌فرض")
    base_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت پایه")
    price_increment_per_cm = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="افزایش قیمت به ازای هر سانتی‌متر")
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="قیمت")
    length = models.PositiveIntegerField(null=True, blank=True, verbose_name="طول (سانتی‌متر)")
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name="عرض (سانتی‌متر)")
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name="ارتفاع (سانتی‌متر)")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی")
    parts_list_key = models.CharField(max_length=255, blank=True, verbose_name="مسیر فایل")

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.price and self.base_price:
            self.price = self.base_price
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        if hasattr(self, 'avg_rating') and self.avg_rating is not None:
            return round(self.avg_rating, 1)
        reviews = self.reviews.filter(is_active=True)
        if not reviews.exists():
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def review_count(self):
        if hasattr(self, 'rev_count') and self.rev_count is not None:
            return self.rev_count
        return self.reviews.filter(is_active=True).count()


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name='images', verbose_name="رنگ")
    image = models.ImageField(upload_to='products/', verbose_name="تصویر")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="متن جایگزین")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} - {self.id}"


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="محصول")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="امتیاز")
    comment = models.TextField(blank=True, verbose_name="نظر")
    image = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name="تصویر نظر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "نظر محصول"
        verbose_name_plural = "نظرات محصول"
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"


class ProductSection(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sections', verbose_name="محصول")
    name = models.CharField(max_length=100, verbose_name="نام قسمت")
    color = models.ForeignKey(Color, on_delete=models.PROTECT, verbose_name="رنگ")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = "جزء محصول"
        verbose_name_plural = "اجزای محصول"

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class Piece(BaseModel):
    section = models.ForeignKey(ProductSection, on_delete=models.CASCADE, related_name='pieces', verbose_name="جزء محصول")
    length = models.PositiveIntegerField(verbose_name="طول (سانتی‌متر)")
    width = models.PositiveIntegerField(verbose_name="عرض (سانتی‌متر)")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        verbose_name = "قطعه"
        verbose_name_plural = "قطعات"

    def __str__(self):
        return f"{self.section.product.name} - {self.section.name} - {self.length}×{self.width}"


class Part(BaseModel):
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='parts', verbose_name="متریال")
    name = models.CharField(max_length=100, verbose_name="نام قطعه")
    length = models.DecimalField(max_digits=7, decimal_places=1, verbose_name="طول (X)")
    width = models.DecimalField(max_digits=7, decimal_places=1, verbose_name="عرض (Y)")
    grain = models.CharField(max_length=100, blank=True, verbose_name="دسته")
    pname = models.CharField(max_length=100, verbose_name="نام محصول")
    turn = models.BooleanField(default=False, verbose_name="چرخش")

    f26 = models.CharField(max_length=100, blank=True, verbose_name="نوار لبه F26")
    f18 = models.CharField(max_length=100, blank=True, verbose_name="نوار لبه F18")
    f4 = models.CharField(max_length=100, blank=True, verbose_name="نوار لبه F4")
    f5 = models.CharField(max_length=100, blank=True, verbose_name="نوار لبه F5")

    f3 = models.CharField(max_length=100, blank=True, verbose_name="بارکد F3")
    f2 = models.CharField(max_length=100, blank=True, verbose_name="نام قطعه F2")

    routing_code = models.CharField(max_length=255, verbose_name="تحویل به مرحله")

    base_part = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variations',
        verbose_name="قطعه پایه"
    )

    class Meta:
        verbose_name = "قطعه تولید"
        verbose_name_plural = "قطعات تولید"

    def __str__(self):
        return f"{self.f2 or self.name} ({self.length}x{self.width})"


class ProductBOM(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bom')
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد در هر محصول")

    color_part = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="بخش رنگی"
    )

    allow_material_override = models.BooleanField(default=False, verbose_name="امکان تغییر متریال با رنگ")
    color_material_map = models.JSONField(default=dict, blank=True, verbose_name="نگاشت رنگ به متریال")

    size_affected = models.BooleanField(default=False, verbose_name="تحت تأثیر اندازه")
    size_adjustment_rule = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="قانون تغییر اندازه"
    )

    class Meta:
        verbose_name = "فرمول ساخت"
        verbose_name_plural = "فرمول‌های ساخت"
        unique_together = ['product', 'part']

    def __str__(self):
        return f"{self.product.name}: {self.quantity}x {self.part.name}"


class StockAlert(BaseModel):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='stock_alerts', verbose_name="کاربر")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts', verbose_name="محصول")
    is_notified = models.BooleanField(default=False, verbose_name="اعلان شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "اعلان موجودی"
        verbose_name_plural = "اعلان‌های موجودی"
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"اعلان موجودی {self.product.name} برای {self.user.username}"


class ComparisonList(BaseModel):
    session_key = models.CharField(max_length=40, db_index=True, verbose_name="کلید جلسه")
    products = models.ManyToManyField(Product, related_name='comparisons', verbose_name="محصولات مقایسه")

    class Meta:
        verbose_name = "لیست مقایسه"
        verbose_name_plural = "لیست‌های مقایسه"

    def __str__(self):
        return f"مقایسه محصولات - {self.session_key}"
