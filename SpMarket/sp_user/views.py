from django.shortcuts import render
from django.views import View


class RegisterView(View):
    # 注册功能
    def get(self, request):
        return render(request, "sp_user/reg.html")

    def post(self, request):
        pass


class LoginView(View):
    # 登录功能
    def get(self, request):
        return render(request, "sp_user/login.html")

    def post(self, request):
        pass


class CenterView(View):
    # 个人中心功能
    def get(self, request):
        return render(request, "sp_user/member.html")

    def post(self, request):
        pass


class AddressView(View):
    # 收货地址功能
    def get(self, request):
        pass

    def post(self, request):
        pass


class InfoView(View):
    # 个人资料功能
    def get(self, request):
        return render(request, "sp_user/infor.html")

    def post(self, request):
        pass


class LogoutView(View):
    # 退出功能
    def get(self, request):
        pass

    def post(self, request):
        pass
