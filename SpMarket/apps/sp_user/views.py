from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from sp_user.forms import RegisterForm, LoginForm


class RegisterView(View):
    # 注册功能
    def get(self, request):
        # 使用form渲染页面
        form = RegisterForm()
        return render(request, "sp_user/reg.html", {"form": form})

    def post(self, request):
        # 1.接收数据
        # 2.处理数据
        form = RegisterForm(request.POST)
        # 3.响应
        if form.is_valid():
            form.save()
            # 注册成功,跳转到登录页面
            return redirect(reverse("sp_user:login"))
        # 注册失败,回到注册页面,提示错误信息
        return render(request, "sp_user/reg.html", {
            "form": form
        })


class LoginView(View):
    # 登录功能
    def get(self, request):
        login_form = LoginForm()
        return render(request, "sp_user/login.html", {"form": login_form})

    def post(self, request):
        # 1.接收数据
        # 2.处理数据
        login_form = LoginForm(request.POST)
        # 3.响应
        if login_form.is_valid():
            # 验证成功,保存登录标识到session
            user = login_form.cleaned_data.get('user')
            request.session["ID"] = user.pk
            request.session["phone"] = user.phone
            # 设置有效期,关闭浏览则结束
            request.session.set_expiry(0)
            # 跳转到用户中心
            return redirect(reverse('sp_user:center'))
        # 验证失败
        return render(request, "sp_user/login.html", {"form": login_form})


class CenterView(View):
    # 个人中心功能
    def get(self, request):
        phone = request.session.get('phone')

        context = {
            'phone': phone
        }

        return render(request, "sp_user/member.html",context)

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
