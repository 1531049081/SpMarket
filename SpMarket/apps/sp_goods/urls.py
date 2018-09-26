#!D:\python\python.exe
from django.conf.urls import url

from sp_goods.views import IndexView, CategoryView, DetailView

urlpatterns = [
    # 首页路由绑定
    url(r'^$', IndexView.as_view(), name='IndexView'),  # 首页
    # 商品列表页
    url(r'^category/$', CategoryView.as_view(), name='CategoryView'),  # 列表     (?P<cate_id>\d+)_(?P<order>\d).html
    # 商品详情页
    url(r'^detail/$', DetailView.as_view(), name='DetailView'),  # 详情      (?P<sku_id>\d+)
]
