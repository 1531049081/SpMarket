from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import JsonResponse

from db.base_view import BaseVerifyView
from sp_car.helper import get_car_key
from sp_goods.models import GoodsSKU
from django_redis import get_redis_connection

"""
添加购物车
"""


# addCar
class AddCarView(View):
    def get(self, request):
        pass

    def post(self, request):
        # 1.判断用户是否登录
        user_id = request.session.get("ID")
        if user_id is None:
            return JsonResponse({"error": 1, "msg": "还没有登录哦!"})

        # 2.接收请求参数
        sku_id = request.POST.get("sku_id")
        count = request.POST.get("count")

        # 3. 判断参数合法性
        # 必须为整数
        try:
            sku_id = int(sku_id)
            count = int(count)
        except Exception as e:
            return JsonResponse({"error": 2, "msg": "参数错误!"})
        # 商品必须存在
        try:
            goods_sku = GoodsSKU.objects.get(pk=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"error": 3, "msg": "商品不存在"})
        # 库存判断
        if goods_sku.stock < count:
            return JsonResponse({"error": 4, "msg": "库存不足!"})

        # 将购物车数据添加到redis中
        # 连接redis
        cnn = get_redis_connection("default")
        # 操作redis
        # 准备key
        car_key = get_car_key(user_id)
        # 添加数据到购物车
        cnn.hincrby(car_key, sku_id, count)
        # 获取购物车中的总的数量
        # 保存到redis中的数据是二进制编码,需要解码才能使用
        car_values = cnn.hvals(car_key)
        total = 0
        for v in car_values:
            # print(v.decode("utf-8"))   # int(v)
            total += int(v)
        # print(car_values)
        return JsonResponse({'error': 0, "msg": "添加成功", "total": total})


"""
减购物车
"""


# del_car
class DelCarView(View):
    def get(self, request):
        pass

    def post(self, request):
        # 1. 判断用户是否登录
        user_id = request.session.get("ID")
        if user_id is None:
            return JsonResponse({"error": 1, "msg": "没有登录,请登录!"})

        # 2. 接收请求参数
        sku_id = request.POST.get("sku_id")
        count = -1

        # 判断参数合法性
        # 1.都要是整数
        try:
            sku_id = int(sku_id)
        except:
            return JsonResponse({"error": 2, "msg": "参数错误!"})

        # 2.商品必须要存在
        try:
            goods_sku = GoodsSKU.objects.get(pk=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({"error": 3, "msg": "商品不存在!"})

        # 从购物车中减去商品数量
        # 链接redis
        cnn = get_redis_connection("default")
        # 操作redis
        # 准备key
        car_key = get_car_key(user_id)
        # 从购物车的数量减
        cnn.hincrby(car_key, sku_id, count)
        # 如果商品sku_id对应的数量为0,就从购物车中删除该商品sku_id
        count = cnn.hget(car_key, sku_id)
        if int(count) < 1:
            cnn.hdel(car_key, sku_id)

        # 获取购物车中的总的商品的数量
        car_values = cnn.hvals(car_key)  # 保存到redis中的数据是 二进制编码了, 需要解码才能使用
        total = 0
        for v in car_values:
            total += int(v)

        return JsonResponse({"error": 0, "msg": "减少成功", "total": total})


# 购物车展示
# car
class CarShowView(BaseVerifyView):
    def get(self, request):
        """
            获取购物车数据
                购物车中的商品数据
                所有商品的总数量和总价格
        """
        user_id = request.session.get('ID')
        # 准备两个变量
        total_price = 0  # 总价格
        total_count = 0  # 总数量

        # 1. 购物车中的总价格和总数量
        # 连接redis
        cnn = get_redis_connection("default")
        # 从redis中获取购物车信息
        # 准备car_key
        car_key = get_car_key(user_id)
        # 取数据
        cars = cnn.hgetall(car_key)  # 字典 ,遍历字典
        # print(cars)
        # 准备一个变量,列表保存多个商品
        goodsList = []
        for sku_id, count in cars.items():
            # print(sku_id,count)
            sku_id = int(sku_id)  # 商品id
            count = int(count)  # 商品数量
            # 获取商品数据
            goods_sku = GoodsSKU.objects.get(pk=sku_id)

            # 需要购物车中商品的数量,在goods_sku对象上添加一个属性
            goods_sku.count = count

            # 将该商品保存到列表中
            goodsList.append(goods_sku)

            # 处理总价格和总数量
            total_count += count
            total_price += goods_sku.price*count

        # 2.所有商品的总价格和总数量

        # 构造列表,渲染数据
        context = {
            "goodsList": goodsList,
            "total_price": total_price,
            "total_count": total_count,
            "footer":3
        }
        return render(request, "sp_car/shopcart.html", context)

    def post(self, request):
        pass
