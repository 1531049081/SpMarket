from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from sp_goods.models import GoodsSKU, Category


class IndexView(View):
    """首页"""

    def get(self, request):
        # sku 商品
        goods_skus = GoodsSKU.objects.filter(is_delete=False)
        # 组装成字典
        context = {
            "goods_skus": goods_skus,
            "footer":1
        }
        return render(request, 'sp_goods/index.html', context)

    def post(self, request):
        pass


"""
1查询所有商品
2查询所有分类,并显示
3点击某个分类,显示对应分类下的商品
4排序
"""


class CategoryView(View):
    """分类列表页"""
    def get(self, request, cate_id=0, order=1):
        cate_id = int(cate_id)
        # 查询所有分类,并显示
        order = int(order)
        categorys = Category.objects.filter(is_delete=False)
        # sku 全部商品
        # goods_skus = GoodsSKU.objects.filter(is_delete=False)
        # 获取对应分类下的商品
        if cate_id == 0:
            # 默认展示第一个分类
            category = categorys.first()
            # 当cate_id =0时,则等于该分类的pk
            cate_id = category.pk
        else:
            # 获取传入分类id对应的分类
            category = Category.objects.get(pk=cate_id)

        # goods_skus = category.goodssku_set.all().order_by('id')

        # 映射的关系
        order_by_rule = ["id", "-sale_num", "-price", "price", "-create_time"]
        goods_skus = category.goodssku_set.all().order_by(order_by_rule[order])

        # 获取该用户购物车中商品的总数
        user_id = request.session.get('ID', None)
        # 准备变量保存总数量
        total = 0
        if user_id:
            cnn = get_redis_connection('default')
            # 购物车的键
            car_key = "car_%s" % user_id
            car_values = cnn.hvals(car_key)
            for v in car_values:
                total += int(v)

        # 组成字典
        context = {
            "goods_skus": goods_skus,
            "categorys": categorys,
            "cate_id": cate_id,
            "order": order,
            "total": total,
        }

        return render(request, 'sp_goods/category.html', context)

    def post(self, request):
        pass


class DetailView(View):
    """商品详情"""

    def get(self, request, sku_id):
        try:
            # 1.接收数据
            sku_id = int(sku_id)
            # 2.处理数据
            goods_sku = GoodsSKU.objects.get(pk=sku_id)
            # 3.响应
            context = {
                "goods_sku": goods_sku
            }
            return render(request, 'sp_goods/detail.html', context)
        except:
            return redirect(reverse('sp_goods:IndexView'))

    def post(self, request):
        pass
