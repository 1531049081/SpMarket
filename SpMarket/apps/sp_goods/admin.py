from django.contrib import admin

# Register your models here.
from sp_goods.models import Category, Unit, GoodsSPU, Gallery, GoodsSKU, Banner, Activity, ActivityZoneGoods, \
    ActivityZone


admin.site.site_header = "电商管理平台"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 商品分类
    pass


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    # 商品单位
    pass


@admin.register(GoodsSPU)
class GoodsSPUAdmin(admin.ModelAdmin):
    # 商品SPU
    pass


# 关联商品的相册
class GoodsSKUAdminInLine(admin.StackedInline):
    model = Gallery
    extra = 3
    fields = ['goods_sku', 'img_url']


# 注册GoodsSKU的模型平台
@admin.register(GoodsSKU)
# 定制显示效果
class GoodsSKUAdmin(admin.ModelAdmin):
    # 商品SPU
    # 关联模型显示
    inlines = [
        GoodsSKUAdminInLine
    ]


# 注册Banner的模型后台
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    pass


# 注册Activity的模型后台
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    pass


# 注册ActivityZone的模型后台
class ActivityZoneAdminInline(admin.StackedInline):
    model = ActivityZoneGoods
    extra = 2


@admin.register(ActivityZone)
class ActivityZoneAdmin(admin.ModelAdmin):
    inlines = [
        ActivityZoneAdminInline
    ]
