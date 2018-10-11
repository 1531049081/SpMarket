from django.conf.urls import url

from sp_car.views import AddCarView, DelCarView, CarShowView

urlpatterns = [
    url(r'^addCar/$', AddCarView.as_view(), name="addCar"),  # 添加购物车
    url(r'^del_car/$', DelCarView.as_view(), name="del_car"),  # 减购物车
    url(r'^$', CarShowView.as_view(), name="购物车首页"),  # 购物车显示
]
