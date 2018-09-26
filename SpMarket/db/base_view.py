#!D:\python\python.exe
from django.utils.decorators import method_decorator
from django.views import View

from sp_user.helper import verify_login_required


class BaseVerifyView(View):
    """
    基础视图类,只有需要验证的视图类才能继承
    """
    # 登录验证的装饰器
    @method_decorator(verify_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)