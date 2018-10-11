from django.conf.urls import url
from sp_order.views import EnsureOrderView, OrderView

urlpatterns = [
    url(r'^ensure/$', EnsureOrderView.as_view(), name="确认订单"),
    url(r'^order/$', OrderView.as_view(), name="显示订单"),
]
