from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from db.base_view import BaseVerifyView
from sp_user.forms import RegisterForm, LoginForm, AddressAddForm
from sp_user.helper import verify_login_required
from sp_user.models import Users, UserAddress


class RegisterView(View):
    # 注册功能
    def get(self, request):
        # 使用form渲染页面
        form = RegisterForm()
        return render(request, "sp_user/reg.html", {"form": form})

    def post(self, request):
        # 1.接收数据
        session_code = request.session.get("random_code")
        # 强制转换成真正的字典
        data = request.POST.dict()
        data["session_code"] = session_code
        # 2.处理数据
        form = RegisterForm(data)
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
            # 获取到跳转的位置
            if request.GET.get('next', None):
                return redirect(request.GET.get('next'))
            return redirect(reverse('sp_user:center'))
        # 验证失败
        return render(request, "sp_user/login.html", {"form": login_form})


class CenterView(BaseVerifyView):
    # 个人中心功能
    def get(self, request):
        phone = request.session.get('phone')
        context = {
            'phone': phone,
            "footer": 5
        }
        return render(request, "sp_user/member.html", context)

    def post(self, request):
        pass


class AddressView(BaseVerifyView):
    # 收货地址功能
    def get(self, request):
        pass

    def post(self, request):
        pass


class InfoView(BaseVerifyView):
    # 个人资料功能

    def get(self, request):
        # 验证用户是否登录
        # 判断session中是否有用户id
        user_id = request.session.get('ID')
        # 查询当前用户信息
        user = Users.objects.filter(pk=user_id).first()
        context = {
            "user": user
        }
        return render(request, "sp_user/infor.html", context)

    def post(self, request):
        # 1接收数据
        user_id = request.session.get('ID')
        data = request.POST
        file = request.FILES['head']
        # 2处理数据
        # 更新用户头像
        user = Users.objects.get(pk=user_id)
        user.head = file
        user.save()
        # 3响应
        return redirect(reverse("sp_user:center"))


# 单独使用一个视图函数处理图片上传
@csrf_exempt #移除令牌限制
def upload_head(request):
    if request.method == "POST":
        # 获取用户id
        user_id = request.session.get('ID')
        # 获取用户对象
        user = Users.objects.get(pk=user_id)
        # 保存图片
        user.head = request.FILES['file']  # 通过键获取文件
        user.save()
        return JsonResponse({"error": 0})
    else:
        return JsonResponse({"error": 1})


# 函数形式登录验证装饰器
@verify_login_required
def info(request):
    return render(request, "sp_user/infor.html")


class LogoutView(View):
    # 退出功能
    def get(self, request):
        pass

    def post(self, request):
        pass


class SendCodeView(View):
    """
    发送短信验证码
    """

    def post(self, request):
        # 1.接收数据
        phone = request.POST.get("tel", "")
        # 2.处理数据
        # 手机号码格式判断
        import re
        # 设置验证的正则规则
        phone_re = re.compile("^1[3-9]\d{9}$")
        # 匹配手机号码
        res = re.search(phone_re, phone)
        if res is None:
            # 手机号码格式错误
            return JsonResponse({"status": "400", "msg": "手机号码格式错误"})

        # 号码是否已注册
        res = Users.objects.filter(phone=phone).exists()
        if res:
            return JsonResponse({"status": "400", "msg": "手机号码已注册"})

        # 生成随机验证码
        import random
        random_code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        # print(random_code)

        # 发送验证码 阿里云  开发阶段模拟
        print("===code========={}=====".format(random_code))

        # 将生成的随机码保存到session中
        request.session['random_code'] = random_code
        request.session.set_expiry(60)

        # 3.响应 json,告知是否发送成功
        return JsonResponse({"status": "200"})



# address/
class AddressView(BaseVerifyView):
    """
        展示用户收货地址
    """

    def get(self, request):
        # 当前登录用户的id
        user_id = request.session.get("ID")
        # 从数据库中查询 当前用户的所有的未删除的收货地址
        address_list = UserAddress.objects.filter(user_id=user_id, is_delete=False).order_by("-isDefault")

        # 渲染数据到页面
        context = {
            "address_list": address_list,
        }
        return render(request, "sp_user/address.html", context)

    def post(self, request):
        """
            设置默认的收货地址
        """
        # 1. 接收参数 收货地址的主键pk addr_id
        user_id = request.session.get("ID")
        addr_id = request.POST.get("addr_id", 0)
        # 2. 处理参数
        # 将其他的设置为false
        UserAddress.objects.filter(user_id=user_id).update(isDefault=False)
        # 将该用户的 对应的收货地址的id设置为默认
        rows = UserAddress.objects.filter(user_id=user_id, pk=addr_id).update(isDefault=True)
        if rows == 0:
            return JsonResponse({"error": 1, "msg": "设置失败!"})
            # 3. 响应
        return JsonResponse({"error": 0})


# address/add/
class AddressAddView(BaseVerifyView):
    """
        收货地址添加
    """

    def get(self, request):
        return render(request, "sp_user/address_add.html")

    def post(self, request):
        # 1. 接收参数
        # 单独获取当前登录用户的 记录
        user_id = request.session.get("ID")
        data = request.POST
        # 2. 处理参数
        form = AddressAddForm(data)
        if form.is_valid():
            form.instance.user_id = user_id

            # 判断当前用户的收货地址的数量
            count = UserAddress.objects.filter(user_id=user_id, is_delete=False).count()
            if count == 6:
                return JsonResponse({"error": 1, "errors": {"phone": ["收货地址只能添加6个!"]}})

            # 默认的收货地址只能有一个, 如果当前添加的收货地址为True,当前用户其它收货地址都为False
            if form.cleaned_data.get("isDefault"):
                UserAddress.objects.filter(user_id=user_id).update(isDefault=False)

            form.save()
            return JsonResponse({"error": 0})
        else:
            # 3. 响应
            # form.errors['phone'][0]
            return JsonResponse({"error": 1, "errors": form.errors})
