#!D:\python\python.exe
import hashlib

from django.conf import settings

# 设置密码加密
from django.shortcuts import redirect
from django.urls import reverse


def set_password(pwd):
    token = settings.SECRET_KEY
    password = token + pwd
    h = hashlib.sha1(password.encode("utf-8"))
    return h.hexdigest()


# 登录验证装饰器,用于验证是否登录
def verify_login_required(func):
    """
    :param func:  旧函数
    :return:
    """
    # 定义一个新函数
    def verify_login(request, *args, **kwargs):
        if request.session.get("ID") is None:
            # 没有登录
            return redirect(reverse("sp_user:login")) # 设置响应头 location: url
        else:
            return func(request, *args, **kwargs)

    # 返回新函数
    return verify_login
