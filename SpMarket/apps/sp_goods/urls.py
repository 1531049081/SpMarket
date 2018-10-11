#!D:\python\python.exe
from django.conf.urls import url
from django.views.decorators.cache import cache_page

from sp_goods.views import IndexView, CategoryView, DetailView

urlpatterns = [
    # 首页路由绑定
    url(r'^$', cache_page(60*60)(IndexView.as_view()), name='IndexView'),  # 首页
    # 商品列表页
    url(r'^category/(?P<cate_id>\d+)_(?P<order>\d)/$',cache_page(60)(CategoryView.as_view()) , name='CategoryView'),  # 列表     (?P<cate_id>\d+)_(?P<order>\d).html
    # 商品详情页
    url(r'^detail/(?P<sku_id>\d+)/$', DetailView.as_view(), name='DetailView'),  # 详情
]
