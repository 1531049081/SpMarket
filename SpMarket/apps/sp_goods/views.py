from django.shortcuts import render

# Create your views here.
from django.views import View

from sp_goods.models import GoodsSKU


class IndexView(View):
    """首页"""

    def get(self, request):
        # sku 商品
        goods_skus = GoodsSKU.objects.filter(is_delete=False)

        # 组装成字典
        context = {
            "goods_skus": goods_skus
        }
        return render(request, 'sp_goods/index.html', context)

    def post(self, request):
        pass


class CategoryView(View):
    """分类列表页"""

    def get(self, request):
        # sku 商品
        goods_skus = GoodsSKU.objects.filter(is_delete=False)

        # 组装成字典
        context = {
            "goods_skus": goods_skus
        }

        return render(request, 'sp_goods/category.html', context)

    def post(self, request):
        pass


class DetailView(View):
    """商品详情"""

    def get(self, request):
        return render(request, 'sp_goods/detail.html')

    def post(self, request):
        pass
