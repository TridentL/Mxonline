from django import forms
from captcha.fields import CaptchaField

from user_profile.models import UserProfile


#   登录表单验证
class LoginForm(forms.Form):
    #   用户名不能为空
    username = forms.CharField(required=True)
    #   密码不能小于5位
    password = forms.CharField(min_length=5,required=True)

#   验证码form & 注册表单form
class RegisterForm(forms.Form):
    #   此处email与前端name保持一致
    email = forms.EmailField(required=True)
    #   密码不能小于5位
    password = forms.CharField(min_length=5,required=True)
    #   应用验证码,自定义错误输出的key必须与异常一致
    captcha = CaptchaField(error_messages={"invalid":"验证码错误"})

#   激活时验证码实现
class ActiveForm(forms.Form):
    #   激活时不对邮箱密码做验证
    #   应用验证码  自定义错误输出key必须与异常一致
    captcha = CaptchaField(error_messages={"invalid":"验证码错误"})

#   忘记密码实现
class ForgetForm(forms.Form):
    #   此处email与前端name保持一致
    email = forms.EmailField(required=True)
    #   应用验证码，自定义错误输出key必须与异常一致
    captcha = CaptchaField(error_messages={"invalid":"验证码错误"})

#   重置密码实现
class ModifyPwdForm(forms.Form):
    #   密码不能小于5位
    password1 = forms.CharField(min_length=5,required=True)
    password2 = forms.CharField(min_length=5,required=True)

#   用于个人中心修改个人信息
class UserInfoForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        #   fields是把UserProfile中的字段拿过来，你用什么就拿什么
        #   比如UserProfile中有nick_name, sex等等字段，在UserInfoForm中
        #   可以不用在定义了，直接写在fields = ('nick_name', 'sex',...)就可以了
        #   具体详见官方文档
        #   此处birthday前端时间必须重新格式化为 date:"Y-m-d"，否则无法提交单条数据
        fields = ('nick_name','sex','address','mobile','birthday',)

#   用于修改头像
class UploadImageForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('head_image',)