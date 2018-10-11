from django.contrib import admin

# Register your models here.
from sp_order.models import Transport

# 注册运输方式到后台
admin.site.register(Transport)