import os

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from sp_car.helper import get_car_key
from sp_goods.models import GoodsSKU
from sp_user.helper import verify_login_required
from sp_user.models import UserAddress, Users
from django_redis import get_redis_connection
from sp_order.models import Transport, OrderInfo, OrderGoods
from datetime import datetime
import random
from alipay import AliPay
from django.conf import settings
import time


# ensure/
class EnsureOrderView(View):
    """
        确认订单
    """

    @method_decorator(verify_login_required)
    def get(self, request):  # 显示
        # 接收参数
        user_id = request.session.get("ID")
        """
            1. 需要商品的sku_ids (多个)
            2. 请求方式为GET方式
        """
        # 1. 收货地址的显示
        """
            1. 如果用户没有收货地址,点击添加
            2. 如果有收货地址,并且有默认地址,显示默认地址
                如果没有默认地址,显示最新的一个地址
            3. 点击进去选择其他收货地址
        """
        address = UserAddress.objects.filter(user_id=user_id, is_delete=False, isDefault=True).first()
        if not address:
            # 没有默认的地址
            address = UserAddress.objects.filter(user_id=user_id, is_delete=False).order_by("-create_time").first()

        # 2. 确认商品的显示
        # 链接到redis
        cnn = get_redis_connection("default")
        # 准备 car_key
        car_key = get_car_key(user_id)

        # 接收商品的id 如果传入的字段的值是一个列表, getlist 方法
        sku_ids = request.GET.getlist('sku_ids')

        # 准备一个变量装所有的商品
        goodsList = []
        goods_total_price = 0
        # 获取商品的信息及对应购物车中的数量
        for sku_id in sku_ids:
            # 获取商品的信息
            goods_sku = GoodsSKU.objects.get(pk=sku_id)
            # 获取购物车中的数量
            try:
                count = cnn.hget(car_key, sku_id)
                count = int(count)
            except:
                # 如果购物车中没有获取到商品数量,就跳转到购物车首页
                return redirect(reverse("sp_car:首页"))
            # 提交到goods_sku对象上
            goods_sku.count = count
            # 将商品信息存储到goodsList中
            goodsList.append(goods_sku)
            # 计算商品总价
            goods_total_price += goods_sku.price * count

        # 3. 商品总价和运输方式的选择
        # 运输方式的选择
        transports = Transport.objects.filter(is_delete=False).order_by("money")

        # 合计总价格 商品总价格 + 运费
        transport = transports.first()
        total_price = goods_total_price + transport.money

        context = {
            "address": address,
            "goodsList": goodsList,
            "goods_total_price": goods_total_price,
            "total_price": total_price,
            "transports": transports,
        }
        return render(request, 'sp_order/tureorder.html', context)

    # 使用事务
    @transaction.atomic
    def post(self, request):  # 保存订单数据
        """
            1. 必须登录
            2. 接收请求参数(sku_ids 商品id addr_id 收货地址id transport 运输方式 描述 description)
                判断参数合法性
            3. 将数据保存到订单表

                订单基本信息表(先创建)


                订单商品表(多,后创建)

            4. 清空对应商品在购物车(redis)中的数据
        """

        # 1. 验证是否登录
        user_id = request.session.get("ID")
        if not user_id:
            return JsonResponse({"status": 1, "errmsg": "没有登录!"})
        user = Users.objects.get(pk=user_id)

        # 2. 接收请求参数,判断参数的合法性
        addr_id = request.POST.get('addr_id')
        sku_ids = request.POST.getlist("sku_ids")
        transport = request.POST.get("transport")
        description = request.POST.get("description")

        # 合法性判断
        if not all([addr_id, sku_ids, transport]):
            return JsonResponse({"status": 2, "errmsg": "请求参数错误!"})

        # 判断收货地址是否存在
        try:
            address = UserAddress.objects.get(user_id=user_id,
                                              is_delete=False,
                                              pk=addr_id
                                              )
        except UserAddress.DoesNotExist:
            return JsonResponse({"status": 3, "errmsg": "收货地址不存在"})

        # 判断运输方式是否存在
        try:
            trans = Transport.objects.get(pk=transport, is_delete=False)
        except Transport.DoesNotExist:
            return JsonResponse({"status": 4, "errmsg": "请运输方式!"})

        # 3. 将数据保存到订单中
        # 保存订单基本信息
        # 准备订单编号
        order_sn = "{}{}{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), random.randrange(1000, 9999), user_id)
        # 收货人的地址
        address_info = "{} {} {} {}".format(address.hcity, address.hproper, address.harea, address.brief)

        # 设置事务的保存点
        save_point = transaction.savepoint()

        # 创建订单 判断是否成功
        try:
            orderinfo = OrderInfo.objects.create(order_sn=order_sn,
                                                 user=user,
                                                 receiver=address.username,
                                                 receiver_phone=address.phone,
                                                 address=address_info,
                                                 order_status=0,
                                                 transport=trans,
                                                 transport_price=trans.money,
                                                 description=description)
        except Exception as e:
            print(e)
            return JsonResponse({"status": 5, "errmsg": "创建订单失败!"})

        # 保存订单商品信息
        # 准备一个变量保存商品总金额
        order_goods_money = 0
        # 链接到redis
        cnn = get_redis_connection("default")
        # 准备car_key
        car_key = get_car_key(user_id)
        for sku_id in sku_ids:
            # 判断商品是否存在
            try:
                # 每次都锁定该商品
                goods_sku = GoodsSKU.objects.select_for_update().get(pk=sku_id)
                # goods_sku = GoodsSKU.objects.get(pk=sku_id)
            except GoodsSKU.DoesNotExist:
                # 回滚事务
                transaction.savepoint_rollback(save_point)
                return JsonResponse({"status": 6, "errmsg": "商品不存在!"})

            # 保存订单商品信息
            # 获取购物车中商品的数量
            try:
                count = cnn.hget(car_key, sku_id)
                count = int(count)
            except:
                # 回滚事务
                transaction.savepoint_rollback(save_point)
                return JsonResponse({"status": 10, "errmsg": "购物车中商品数量不存在"})

            # count = 9999
            # 判断库存是否足够
            if goods_sku.stock < count:
                # 回滚事务
                transaction.savepoint_rollback(save_point)
                return JsonResponse({"status": 7, "errmsg": "商品库存不足!"})

            # time.sleep(10)
            try:
                order_goods = OrderGoods.objects.create(order=orderinfo,
                                                        goods_sku=goods_sku,
                                                        price=goods_sku.price,
                                                        count=count)
            except:
                # 回滚事务
                transaction.savepoint_rollback(save_point)
                return JsonResponse({"status": 8, "errmsg": "创建订单商品失败!"})

            # 对应商品的库存 减少 销量增加
            goods_sku.stock -= count
            # GoodsSKU.objects.filter(pk=goods_sku.pk,stock=goods_sku.stock)
            goods_sku.sale_num += count
            goods_sku.save()

            # 商品总金额计算
            order_goods_money += goods_sku.price * count

        try:
            # 完善订单基本信息
            # 获取 订单总金额和商品总金额
            order_money = order_goods_money + trans.money
            orderinfo.order_money = order_money
            orderinfo.order_goods_money = order_goods_money
            orderinfo.save()
        except:
            # 回滚事务
            transaction.savepoint_rollback(save_point)
            return JsonResponse({"status": 9, "errmsg": "更新订单失败"})

        # 清空购物车 只清空对应的商品
        cnn.hdel(car_key, *sku_ids)
        # 整个订单创建成功, 提交事务
        transaction.savepoint_commit(save_point)

        return JsonResponse({"status": 0, "errmsg": "下单成功", "order_sn": order_sn})


# order
class OrderView(View):
    """
        显示订单页面
    """

    def get(self, request):  # 显示订单
        # 判断是否登录
        user_id = request.session.get("ID")
        if not user_id:
            return redirect(reverse("sp_user:login"))

        # 接收参数
        order_sn = request.GET.get("order_sn")

        # 查询订单信息 基本信息和订单商品信息
        try:
            orderinfo = OrderInfo.objects.get(user_id=user_id,
                                              order_status=0,
                                              is_delete=False,
                                              order_sn=order_sn,
                                              )
        except OrderInfo.DoesNotExist:
            # 如果订单不存在就跳转到个人中心 (显示订单列表)
            return redirect(reverse("sp_user:center"))

        # 获取订单商品信息
        order_goods = orderinfo.ordergoods_set.all()

        context = {
            "orderinfo": orderinfo,
            "order_goods": order_goods,
        }

        return render(request, 'sp_order/order.html', context)

    def post(self, request):  # 提交支付 ajax


        app_private_key_string = open(os.path.join(settings.BASE_DIR,"apps/sp_order/app_private_key.pem")).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR,"apps/sp_order/alipay_public_key.pem")).read()

        alipay = AliPay(
            appid="	2016092000558689",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False 调试的时候使用的沙箱 正式环境是正式地址
        )

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no="order_sn",
            total_amount="价格",
            subject="超级订单order_sn",
            return_url="支付完成返回的地址None",
            notify_url="通知自己服务器是否支付成功的地址None"  # 可选, 不填则使用默认notify url
        )

        pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
        return redirect(pay_url)

