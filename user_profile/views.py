import json
from django.shortcuts import render
#   基于类实现需要继承的View
from django.views.generic.base import View
from django.contrib.auth import authenticate,logout,login
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
#   哈希密码加密
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator,PageNotAnInteger
from django.contrib.auth.backends import ModelBackend
#   并集运算
from django.db.models import Q
#   导入Django自带的mixin认证系统，所有未经身份验证的用户的请求将被重定向
#   到登录页面,类似于 login_required装饰器
from django.contrib.auth.mixins import LoginRequiredMixin
from operation.models import UserCourse


#   form表单验证 & 验证码
from user_profile.forms import ActiveForm,RegisterForm,LoginForm,ForgetForm,ModifyPwdForm,UserInfoForm,\
    UploadImageForm
from user_profile.models import UserProfile,Banner
#   发送邮件
from utils.send_email import send_register_eamil
from user_profile.models import EmailVerifyRecord
from operation.models import UserMessage,UserFavorite
from organization.models import CourseOrg,Teacher
from course.models import Course

# Create your views here.

#   自定义登录规则
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因 Q为使用并集查询
            user = UserProfile.objects.get(
                Q(username=username)|Q(email=username))
            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self,raw_password)密码校验方法
            #   如果用户密码通过校验，则返回user
            if user.check_password(password):
                return user
        except Exception as error:
            return None

#   首页Index的view
class IndexView(View):
    def get(self,request):
        #   取出轮播图
        all_banner = Banner.objects.all().order_by("index")[:5]
        #   正常位课程
        courses = Course.objects.filter(is_banner=False)[:6]
        #   轮播图课程取三个
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        #   课程机构
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request,'index.html',{
            'all_banner':all_banner,
            'courses':courses,
            'banner_courses':banner_courses,
            'course_orgs':course_orgs,
        })

#   全局404处理view
def page_not_found(request):
    from django.shortcuts import render_to_response
    return render_to_response("404.html",{})


#   全局500处理函数
def page_error(request):
    from django.shortcuts import render_to_response
    return render_to_response("500.html", {})

#   登陆view
class LoginView(View):
    #   直接调用免去request.method == 'GET'判断
    def get(self,request):
        #   render就是渲染html返回用户
        #   render三变量：request请求 模板名称 一个字典包含返回前端的值
        redirect_url = request.GET.get('next','')
        return render(request,'login.html',{
            'redirect_url':redirect_url,
        })

    def post(self,request):
        # 类实例化需要一个字典参数dict:request.POST就是一个QueryDict所以直接传入
        # POST中的username,password，会对应到form中
        login_form = LoginForm(request.POST)

        # is_valid判断我们字段是否有错执行我们原有逻辑，验证失败跳回login页面
        if login_form.is_valid():
            # 取不到时为空，username，password为前端页面name值
            username = request.POST.get('username','')
            password = request.POST.get('password','')

            #   验证成功返回user对象，失败返回None
            user = authenticate(username=username,password=password)

            #   如果不为None，说明验证成功
            if user is not None:
                #   只有当用户激活时才可以登录
                if user.is_active:
                    # login() 两参数：request, user
                    # 实际是对request写了一部分东西进去，然后在render的时候：
                    # request是要render回去的。这些信息也就随着返回浏览器。完成登录
                    login(request,user)
                    # 跳转到首页 user request会被带回到首页
                    # 此处适用于后边儿收藏功能未登录时跳转登录页面记忆路径功能，
                    # 增加重定向回原网页。
                    redirect_url = request.POST.get('next','')
                    if redirect_url:
                        return HttpResponseRedirect(redirect_url)
                    return HttpResponseRedirect(reverse('index'))
                #   用户未激活跳转登录界面，前端提示未激活
                else:
                    return render(request,'login.html',{
                        'msg':'用户名未激活,请前往邮箱进行激活'
                    })
            #   仅用户名或密码判断错误
            else:
                return render(request,'login.html',{
                    'msg':'用户名或密码错误'
                })

        else:
            return render(request,'login.html',{
                'login_form':login_form,
            })

#   注册view
class RegisterView(View):
    #   get方法直接返回页面
    def get(self,request):
        #   返回验证码
        register_form = RegisterForm()
        return render(request,'register.html',{
            'register_form':register_form,
        })
    #   post提交数据处理
    def post(self,request):
        #   实例化form,验证表单数据
        register_form = RegisterForm(request.POST)
        #   如果表单数据通过了验证
        if register_form.is_valid():
            user_name = request.POST.get('email','')
            #   检查用户名是否已存在于数据库
            #   如果用户名已经存在，则返回提示
            if UserProfile.objects.filter(email=user_name):
                return render(request,'register.html',{
                    'msg':'用户名已存在',
                    'register_form':register_form,
                })

            pass_word = request.POST.get('password','')

            #   实例化一个UserProfile对象，将表单数据存入数据库
            new_user = UserProfile()
            new_user.username = user_name
            new_user.email = user_name

            #   默认激活状态为False
            new_user.is_active = False

            #   加密password保存
            new_user.password = make_password(pass_word)
            #   保存提交
            new_user.save()

            #   写入欢迎注册信息
            user_message = UserMessage()
            user_message.user = new_user.id
            user_message.message = "欢迎注册rongbaoer慕课小站!!"
            user_message.save()

            #   发送注册激活邮件
            send_register_eamil(user_name,'register')

            #   跳转到登陆页面
            return render(request,'register.html',{
                'register_form':register_form,
                'msg':'激活链接已发送，请注意查收'
            })
        #   邮箱注册form失败
        else:
            return render(request,'register.html',{
                'register_form':register_form,
            })

#   退出view
class LogoutView(View):
    def get(self,request):
        #   Django自带的退出函数
        logout(request)
        #   重定向到首页
        return HttpResponseRedirect(reverse('index'))

#   激活view
class ActiveUserView(View):
    def get(self,request,active_code):
        #   查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        #   如果不为空则代表有用户
        active_form = ActiveForm(request.GET)
        if all_record:
            for record in all_record:
                #   获取对应的邮箱
                email = record.email
                #   查找到邮箱对应的user
                user = UserProfile.objects.get(email=email)
                #   此处仅仅只是将数据库中的is_active字段设置为True，并未做具体页面渲染，
                #   如考虑用户体验，可使用激活页面激活
                user.is_active = True
                user.save()

                #   激活成功跳转到登陆页面
                return render(request,'active_success.html')
        #   验证码验证失败
        else:
            return render(request,'active_fail.html',{
                'active_form':active_form,
                'msg':'您的激活链接无效',
            })

#   忘记密码view
class ForgetPwdView(View):
    #   艹，老规矩，直接get返回页面
    def get(self,request):
        forget_form = ForgetForm()
        return render(request,'forgetpwd.html',{
            'forget_form':forget_form,
        })

    #   post方法实现
    def post(self,request):
        forget_form = ForgetForm(request.POST)
        #   form验证合法判断
        if forget_form.is_valid():
            email = request.POST.get('email','')
            #   发送找回密码邮件
            send_register_eamil(email,'forget')
            #   发送成功提示并返回登录页面
            return render(request,'login.html',{
                'msg':'密码重置邮件已发送，请前往邮箱查收'
            })

        #   表单验证失败
        else:
            return render(request,'forgetpwd.html',{
                'forget_form': forget_form,
            })

#   重置密码view
class ResetView(View):
    def get(self,request,active_code):
        #   查询邮箱验证码记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        #   如果不为空也就是有用户
        active_form = ActiveForm(request.GET)
        if all_record:
            for record in all_record:
                #   获取对应的邮箱
                email = record.email
                #   将email值传回
                return render(request,'password_reset.html',{'email':email})
        #   验证码验证失败
        else:
            return render(request,'forgetpwd.html',{
                'msg':'您的重置密码链接无效，请重新请求',
                'active_form':active_form,
            })

#   修改密码view
class ModifyPwdView(View):
    def post(self,request):
        modifypwd_form = ModifyPwdForm(request.POST)
        if modifypwd_form.is_valid():
            pwd1 = request.POST.get('password1','')
            pwd2 = request.POST.get('password2','')
            email = request.POST.get('email','')
            #   如果两次输入密码不一致，返回错误信息
            if pwd1 != pwd2:
                return render(request,'password_reset.html',{
                    'msg':'密码输入不一致',
                    'email':email,
                })
            #   如果密码一致
            user = UserProfile.objects.get(email=email)
            #   重新写入密码,并且加密
            user.password = make_password(pwd2)
            #   提交保存到数据库
            user.save()
            #   重定向到登陆页面
            return render(request,'login.html',{
                'msg':'密码修改成功，请重新登陆'
            })
        #   表单验证失败说明密码位数不够
        else:
            email = request.POST.get('email','')
            return render(request,'password_reset.html',{
                'modifypwd_form':modifypwd_form,
                'email':email,
            })

#   用户中心view & 修改个人资料
class UserInfoView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self,request):
        return render(request,'usercenter-info.html')

    def post(self,request):
        # 不像用户咨询是一个新的。需要指明instance。
        # 不然无法修改，而是新增用户
        user_info_form = UserInfoForm(request.POST,instance=request.user)
        if user_info_form.is_valid():
            #   提交新数据
            user_info_form.save()
            return HttpResponse(
                '{"status":"success"}',
                content_type='application/json')
        else:
            #   通过json的dumps方法把字典转换成json字符串
            return HttpResponse(
                json.dumps(
                    user_info_form.errors),
                content_type='application/json')

#   用户中心修改头像
class UploadImageView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self,request):
        # 这时候用户上传的文件就已经被保存到imageform了 ，
        # 为modelform添加instance值直接保存
        image_form = UploadImageForm(request.POST,request.FILES,instance=request.user)
        print(image_form)
        if image_form.is_valid():
            #   提交数据
            image_form.save()
            return HttpResponse(
                '{"status":"success"}',
                content_type='application/json'
            )
        else:
            return HttpResponse(
                '{"status":"fail"}',
                content_type='application/json'
            )

#   用户中心修改密码
class UpdatePwdView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            # 如果两次密码不相等，返回错误信息
            if pwd1 != pwd2:
                return HttpResponse(
                    '{"status":"fail", "msg":"密码不一致"}',
                    content_type='application/json')
            # 如果密码一致
            user = request.user
            # 加密成密文
            user.password = make_password(pwd2)
            # save保存到数据库
            user.save()
            return HttpResponse(
                '{"status":"success"}',
                content_type='application/json')
        # 验证失败说明密码位数不够。
        else:
            # 通过json的dumps方法把字典转换为json字符串
            return HttpResponse(
                json.dumps(
                    modify_form.errors),
                content_type='application/json')

#   用户中心修改邮箱
class UpdateEmailView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self,request):
        email = request.POST.get('email','')
        code = request.POST.get('code','')
        #   查询邮箱和验证码是否存在
        existed_records = EmailVerifyRecord.objects.filter(
            email=email,code=code,send_type="update_email")
        #   如果记录存在
        if existed_records:
            user = request.user
            user.email = email
            user.save()

            return HttpResponse(
                '{"status":"success"}',
                content_type='application/json'
            )
        #   记录不存在
        else:
            return HttpResponse(
                '{"email":"验证码不存在"}',
                content_type='application/json'
            )

#   修改邮箱发送验证码处理
class SendEmailCodeView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self,request):
        print(request.GET)
        #   获取需要发送的邮箱账户
        email = request.GET.get('email','')
        #   不能是已经注册过的邮箱
        if UserProfile.objects.filter(email=email):
            return HttpResponse(
                '{"email":"邮箱已存在"}',
                content_type='application/json'
            )
        #   发送邮件
        send_register_eamil(email,'update_email')
        return HttpResponse(
            '{"status":"success"}',
            content_type='application/json'
        )

#   用户中心我的课程
class MyCourseView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self,request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request,'usercenter-mycourse.html',{
            'user_courses':user_courses,
        })

#   用户中心我收藏的课程机构
class MyFavOrgView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self,request):
        #   创建空列表存放授机构
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user,fav_type=2)
        #   fav_org仅仅只是存放了id，还需要通过id找到机构对象
        for fav_org in fav_orgs:
            #   取出fav_id也就是机构的id
            org_id = fav_org.fav_id
            #   通过机构id获取这个机构对象
            org = CourseOrg.objects.get(id=int(org_id))
            #   将获取到的机构追加到机构列表中存储
            org_list.append(org)

        return render(request,'usercenter-fav-org.html',{
            'org_list':org_list,
        })

#   用户中心我收藏的授课教师
class MyFavTeacherView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self,request):
        #   常见空列表存储讲师
        teacher_list = []
        #   从收藏表中查询收藏的讲师
        fav_teachers = UserFavorite.objects.filter(user=request.user,fav_type=3)
        #   fav_teacher仅仅只是存放了teacher的id，还需要根据ID值找到讲师对象
        for fav_teacher in fav_teachers:
            #   取出fav_id也就是讲师的id
            teacher_id = fav_teacher.fav_id
            #   通过讲师id取得这个讲师对象，
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request,'usercenter-fav-teacher.html',{
            'teacher_list':teacher_list,
        })

#   用户中心我收藏的公开课程
class MyFavCourseView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self,request):
        #   创建空列表，存放公开课程
        course_list = []
        #   从收藏表中查询收藏的公开课程
        fav_courses = UserFavorite.objects.filter(user=request.user,fav_type=1)
        #   fav_courses仅仅只是存放了课程的id，还需要根据id获取课程对象
        for fav_course in fav_courses:
            #   取出fav_id，也就是公开课的id
            course_id = fav_course.fav_id
            #   根据fav_id获取对应的课程对象
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request,'usercenter-fav-course.html',{
            'course_list':course_list,
        })

#   用户中心我的消息
class MyMessageView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self,request):
        #   取得全部消息
        all_message = UserMessage.objects.filter(user__in=[request.user.id,0])
        #   对消息中心进行分页
        #   get前台的page参数，获取不到，默认取第一页1
        #   用户进入消息页面，清空未读消息记录
        all_unread_message = UserMessage.objects.filter(user__in=[request.user.id,0],has_read=False)
        for unread_message in all_unread_message:
            unread_message.has_read = True
            unread_message.save()
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page = 1
        fenye = Paginator(all_message,2)
        all_message = fenye.page(page)

        return render(request,'usercenter-message.html',{
            'all_message':all_message,
        })