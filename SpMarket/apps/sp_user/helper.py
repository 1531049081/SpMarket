#!D:\python\python.exe
import hashlib

from django.conf import settings


# 设置密码加密
def set_password(pwd):
    token = settings.SECRET_KEY
    password = token + pwd
    h = hashlib.sha1(password.encode("utf-8"))
    return h.hexdigest()
