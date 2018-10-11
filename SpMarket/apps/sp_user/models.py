from django.core import validators
from django.db import models

# Create your models here.
from db.base_model import BaseModel


class Users(BaseModel):
    # 更新时间,修改时间,是否删除从BaseModel继承
    """
    用户模型
    """
    # 性别选项
    sex_choices = (
        (1, '男'),
        (2, "女"),
        (3, "保密"),
    )
    nickname = models.CharField(verbose_name='昵称',
                                max_length=20,
                                null=True,
                                blank=True,
                                )
    phone = models.CharField(verbose_name='手机号码',
                             max_length=11,
                             validators=[
                                 validators.RegexValidator(r'^1[3-9]\d{9}$',"手机号码格式错误")
                             ],
                             )
    password = models.CharField(verbose_name='密码',
                                max_length=64,
                                # validators=[
                                #     validators.MinLengthValidator(6),
                                #     validators.MaxLengthValidator(16),
                                # ]
                                )
    gender = models.SmallIntegerField(verbose_name='性别',
                                      default=3,
                                      choices=sex_choices,
                                      )
    head = models.ImageField(verbose_name='用户头像',
                             upload_to='head/%Y/%m',
                             default='user/201809/25/1.jpg',
                             )
    birthday = models.DateField(verbose_name='出生日期',
                                null=True,
                                blank=True,
                                )
    school_name = models.CharField(verbose_name='学校名称',
                                   max_length=50,
                                   null=True,
                                   blank=True,
                                   )
    address = models.CharField(verbose_name='学校详细地址',
                               max_length=100,
                               null=True,
                               blank=True,
                               )
    hometown = models.CharField(verbose_name='老家',
                                max_length=100,
                                null=True, blank=True,
                                )

    class Meta:
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.phone


class TestImageModel(models.Model):
    head = models.ImageField(upload_to="user/%Y%m/%d",
                             verbose_name="用户头像")




class UserAddress(BaseModel):
    """用户收货地址管理"""
    user = models.ForeignKey(to="Users", verbose_name="创建人")
    username = models.CharField(verbose_name="收货人", max_length=100)
    phone = models.CharField(verbose_name="收货人电话",
                             max_length=11,
                             validators=[
                                 validators.RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误!")
                             ],
                             )
    hcity = models.CharField(verbose_name="省", max_length=100)
    hproper = models.CharField(verbose_name="市", max_length=100, blank=True, default='')
    harea = models.CharField(verbose_name="区", max_length=100, blank=True, default='')
    brief = models.CharField(verbose_name="详细地址", max_length=255)
    isDefault = models.BooleanField(verbose_name="是否设置为默认", default=False, blank=True)

    class Meta:
        verbose_name = "收货地址管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
