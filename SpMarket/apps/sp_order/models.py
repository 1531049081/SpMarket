from django.db import models

from db.base_model import BaseModel


class Payment(BaseModel):
    """
        支付方式
    """
    pay_name = models.CharField(verbose_name='支付方式',
                                max_length=20
                                )

    class Meta:
        verbose_name = "支付方式"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.pay_name


class Transport(BaseModel):
    """
        配送方式
    """
    name = models.CharField(verbose_name='配送方式',
                            max_length=20
                            )
    money = models.DecimalField(verbose_name='金额',
                                max_digits=9,
                                decimal_places=2,
                                default=0
                                )

    class Meta:
        verbose_name = "配送方式"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class OrderInfo(BaseModel):
    order_status_choices = (
        (0, '待付款'),
        (1, '退发货'),
        (2, '待收货'),
        (3, '待评价'),
        (4, '已完成'),
        (5, '取消订单'),
    )
    """订单信息表"""
    order_sn = models.CharField(verbose_name="订单编号", max_length=150)
    order_money = models.DecimalField(verbose_name="订单总金额", max_digits=9, decimal_places=2, default=0)
    order_goods_money = models.DecimalField(verbose_name="商品总金额", max_digits=9, decimal_places=2, default=0)
    user = models.ForeignKey(to="sp_user.Users", verbose_name="所属用户")
    receiver = models.CharField(verbose_name="收货人姓名", max_length=100)
    receiver_phone = models.CharField(verbose_name="收货人电话", max_length=11)
    address = models.CharField(verbose_name="收货人地址", max_length=200)
    order_status = models.SmallIntegerField(verbose_name="订单状态", choices=order_status_choices, default=0)
    transport = models.ForeignKey(to="Transport", verbose_name="运输方式")
    transport_price = models.DecimalField(verbose_name="运费", max_digits=9, decimal_places=2, default=0)
    payment = models.ForeignKey(to="Payment", verbose_name="支付方式", null=True, blank=True)
    pay_money = models.DecimalField(verbose_name="实际支付金额", max_digits=9, decimal_places=2, default=0)
    description = models.CharField(verbose_name="备注说明", max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "订单基本信息表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_sn


class OrderGoods(BaseModel):
    """订单商品表"""
    order = models.ForeignKey(to="OrderInfo", verbose_name="所属订单")
    goods_sku = models.ForeignKey(to='sp_goods.GoodsSKU', verbose_name="商品SKU")
    price = models.DecimalField(verbose_name="商品单价", max_digits=9, decimal_places=2, default=0)
    count = models.IntegerField(verbose_name="订单商品数量", default=0)

    class Meta:
        verbose_name = "订单商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}".format(self.order.order_sn, self.goods_sku.sku_name)
