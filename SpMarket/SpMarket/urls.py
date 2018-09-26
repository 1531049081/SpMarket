"""SpMarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from sp_goods.views import IndexView

urlpatterns = [
    # 127.0.0.1:8000
    url(r'^$', IndexView.as_view(), name="商城首页"),
    url(r'^admin/', admin.site.urls),
    # 上传部件自动调用的上传地址
    url(r'^ckeditor/', include("ckeditor_uploader.urls")),
    # 绑定 用户模块子路由
    url(r'^user/', include("sp_user.urls", namespace="sp_user")),
    # 绑定 商品模块子路由
    url(r'^goods/', include("sp_goods.urls", namespace="sp_goods")),
]
