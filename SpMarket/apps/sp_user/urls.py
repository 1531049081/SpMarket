from django.conf.urls import url

from sp_user.views import (RegisterView,
                           LoginView,
                           CenterView,
                           AddressView,
                           InfoView,
                           LogoutView,
                           info,
                           SendCodeView,
                           upload_head,
                           AddressAddView)

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name="register"),  # 注册
    url(r'^login/$', LoginView.as_view(), name="login"),  # 登录
    url(r'^center/$', CenterView.as_view(), name="center"),  # 个人中心
    url(r'^address/$', AddressView.as_view(), name="address"),  # 收货地址
url(r'^address/add/$', AddressAddView.as_view(), name="address_add"),  # 添加收货地址
    url(r'^info/$', InfoView.as_view(), name="info"),  # 个人资料
    # url(r'^info/$', info, name="info"),  # 个人资料
    url(r'^logout/$', LogoutView.as_view(), name="logout"),  # 退出
    url(r'^SendCodeView/$', SendCodeView.as_view(), name="SendCodeView"),  # 发送验证码
    url(r'^upload_head/$', upload_head, name="upload_head"),  # 上传头像
]
