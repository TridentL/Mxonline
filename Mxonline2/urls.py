"""Mxonline2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
import xadmin

from user_profile.views import IndexView,LoginView,RegisterView,LogoutView,ActiveUserView,ForgetPwdView,\
    ResetView,ModifyPwdView

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    #   首页url配置
    url(r'^$',IndexView.as_view(),name='index'),

    #   user_profile    app的url配置
    url(r'^users/',include('user_profile.urls',namespace='users')),

    #   登录页面跳转url不要直接调用，而只是指向这个函数对象
    #   基于类方法实现登陆
    url(r'^login/$',LoginView.as_view(),name='login'),

    #   基于类方法实现注册
    url(r'^register/$',RegisterView.as_view(),name='register'),

    #   基于类方法实现退出
    url(r'^logout/$',LogoutView.as_view(),name='logout'),

    #   验证码的url配置
    url(r'^captcha/',include('captcha.urls')),

    #   激活用户url
    url(r'^active/(?P<active_code>.*)/$',ActiveUserView.as_view(),name='user_active'),

    #   忘记密码url
    url(r'^forget/$',ForgetPwdView.as_view(),name='forget_pwd'),

    #   重置密码url
    url(r'^reset/(?P<active_code>.*)/$',ResetView.as_view(),name='reset_pwd'),

    #   修改密码url
    url(r'^modify_pwd/$',ModifyPwdView.as_view(),name='modify_pwd'),

    #   公开课app的url
    url(r'^course/',include('course.urls',namespace='course')),

    #   课程机构app的url
    url(r'^org/',include('organization.urls',namespace='org')),
]

#   全局404配置
handler404 = "user_profile.views.page_not_found"
handler500 = "user_profile.views.page_error"