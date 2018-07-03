from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger
from django.http import HttpResponse

from organization.models import CityDict,CourseOrg,Teacher
from organization.forms import UserAskForm
from operation.models import UserFavorite,UserMessage
from course.models import Course

# Create your views here.

#   授课机构view
class OrgListView(View):
    """
    授课机构
    """
    def get(self,request):
        #   查找到所有的授课机构
        all_orgs = CourseOrg.objects.all()

        #   热门机构排序
        hot_org = all_orgs.order_by('-click_nums')[:3]

        #   取出所有的城市
        all_city = CityDict.objects.all()

        #   搜索功能
        search_keywords = request.GET.get('keywords','')
        if search_keywords:
            #   在name字段进行操作，做like语句的操作,i代表不区分大小写,
            #   or操作使用并集Q
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(
                address__icontains=search_keywords))

        #   取出筛选的城市,如果取不到，默认为空
        city_id = request.GET.get('city', '')
        #   如果选中了某个城市，也就是说前端传过来值
        if city_id:
            #   外键城市在数据表中的字段是city_id
            #   我们就在机构中进一步筛选
            all_orgs = all_orgs.filter(city_id=int(city_id))

        #   类别筛选
        category = request.GET.get('ct','')
        if category:
            #   在机构中做进一步筛选
            all_orgs = all_orgs.filter(category=category)

        #   排序
        sort = request.GET.get('sort','')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')

        #   机构统计,使用count函数
        org_nums = all_orgs.count()

        #   对课程机构进行分页
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page = 1
        #   这是指取出授课机构，每页显示2个
        fenye = Paginator(all_orgs,2)
        all_orgs = fenye.page(page)

        return render(request,'org-list.html',{
            'all_city':all_city,
            'all_orgs':all_orgs,
            'city_id':city_id,
            'category':category,
            'sort':sort,
            'org_nums':org_nums,
            'search_keywords':search_keywords,
            'hot_org':hot_org,
        })

#   学习咨询view
class AddUserAskView(View):
    """
    用户咨询
    """
    def post(self,request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse(
                '{"status":"success"}',
                content_type='application/json'
            )
        else:
            return HttpResponse(
                '{"status":"fail","msg":"您的手机号有误,请检查之后重新输入"}',
                content_type='application/json'
            )

#   机构详情view
class OrgHomeView(View):
    """
    机构详情页,机构首页
    """
    def get(self,request,org_id):
        #   向前端传值,表明当前页在机构首页
        current_page = 'home'
        #   根据ID取得课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        #   通过过滤出来的机构反查查找对应课程
        all_course = course_org.course_set.all()[:4]
        #   通过过滤出来的机构反查查找对应机构讲师
        all_teacher = course_org.teacher_set.all()
        #   向前端传值说明用户是否传值
        has_fav = False
        #   此处必须是用户登陆验证已通过才需要我们判断
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=course_org.id,fav_type=2):
                has_fav = True

        return render(request,'org-detail-homepage.html',{
            'current_page':current_page,
            'course_org':course_org,
            'all_course':all_course,
            'all_teacher':all_teacher,
            'has_fav':has_fav,
        })

#   机构课程列表页view
class OrgCourseView(View):
    """
    机构课程
    """
    def get(self,request,org_id):
        #   向前端传值,表明当前页在机构课程页
        current_page = 'course'
        #   根据ID取得课程机构
        course_org = CourseOrg.objects.get(id=org_id)
        #   根据课程机构反查课程
        all_course = course_org.course_set.all()
        #   向前端传值说明用户是否收藏
        has_fav = False
        #   此处必须要用户通过验证才需要我们去判断，
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=course_org.id,fav_type=2):
                has_fav = True

        #   注：如有需要，此处需做分页，此处懒得做

        return render(request,'org-detail-course.html',{
            'course_org':course_org,
            'current_page':current_page,
            'all_course':all_course,
            'has_fav':has_fav,
        })

#   机构介绍列表页view
class OrgDescView(View):
    """
    机构介绍
    """
    def get(self, request,org_id):
        #   向前端传值，表明当前页在机构介绍页
        current_page = 'desc'
        #   根据ID取得授课机构
        course_org = CourseOrg.objects.get(id=org_id)
        #   向前端传值说明用户是否收藏
        has_fav = False
        #   此处需用户通过验证时候才需判断
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=course_org.id,fav_type=2):
                has_fav = True

        return render(request, 'org-detail-desc.html',{
            'current_page':current_page,
            'course_org':course_org,
            'has_fav':has_fav,
        })

#   机构讲师列表页view
class OrgTeacherView(View):
    """
    机构讲师
    """
    def get(self,request,org_id):
        #   向前端传值，表明当前页在机构讲师页
        current_page = 'teacher'
        #   根据ID取得授课机构
        course_org = CourseOrg.objects.get(id=org_id)
        #   根据机构反查机构讲师
        all_teacher = course_org.teacher_set.all()
        #   向前端传值说明用户是否收藏,默认为Falsh
        has_fav = False
        #   此处判断需要用户通过验证
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=course_org.id,fav_type=2):
                has_fav = True

        return render(request,'org-detail-teachers.html',{
            'current_page':current_page,
            'course_org':course_org,
            'all_teacher': all_teacher,
            'has_fav':has_fav,
        })

#   添加收藏
class AddFavView(View):
    """
    用户收藏与取消收藏
    """
    def post(self,request):
        #   表明你收藏的不管是课程，机构，还是讲师，他们是以ID形式存在
        #   默认值取 0 是因为空字符串转int会报错
        id = request.POST.get('fav_id',0)
        #   取到你收藏的类别,此处数据库存储为数字，从前台提交的ajax请求中取
        type = request.POST.get('fav_type',0)

        #   收藏与已收藏取消操作
        #   此处需验证用户是否登录,即使没有登陆也会有一个匿名的user存在
        if not request.user.is_authenticated():
            #   未登录时返回json提示未登录，跳转登录页面在ajax中操作
            return HttpResponse('{"status":"fail","msg":"用户未登录"}',content_type='application/json')
        #   数据库中查找收藏记录
        exist_records = UserFavorite.objects.filter(user=request.user,fav_id=int(id),fav_type=int(type))
        #   如果存在记录已经存在,则说明用户操作是取消收藏
        if exist_records:
            #   删除记录
            exist_records.delete()
            #   如果收藏的类型是  1课程
            if int(type) == 1:
                #   fav_id保存的是用户的id
                #   根据fav_id获得对应的课程
                course = Course.objects.get(id=int(id))
                #   课程收藏数-1
                course.fav_nums -= 1
                #   如果课程数小于0,则赋值为0
                if course.fav_nums < 0:
                    course.fav_nums = 0
                #   提交到数据库
                course.save()
            #   如果收藏的类型为  2课程机构
            elif int(type) == 2:
                #   根据fav_id获取对应的课程机构
                org = CourseOrg.objects.get(id=int(id))
                #   课程收藏数 -1
                org.fav_nums -= 1
                #   如果课程收藏数小于0，则重新赋值为0
                if org.fav_nums < 0:
                    org.fav_nums =0
                #   提交到数据库
                org.save()
            #   如果收藏的类型为  3讲师
            elif int(type) == 3:
                #   根据fav_id获取对应的讲师
                teacher = Teacher.objects.get(id=int(id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"success","msg":"收藏"}',content_type='application/json')
        #   如果记录不存在，执行操作收藏
        else:
            #   实例化收藏表
            user_fav = UserFavorite()
            #   过滤掉未获取到的fav_id , fav_type的默认情况
            #   如果有，重新赋值为0
            if int(type) > 0 and int(id) > 0:
                user_fav.fav_id = int(id)
                user_fav.fav_type = int(type)
                user_fav.user = request.user
                user_fav.save()
                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums += 1
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=int(id))
                    org.fav_nums += 1
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=int(id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"success","msg":"已收藏"}',content_type='application/json')
            else:
                return HttpResponse('{"status":"fail","msg":"收藏失败"}',content_type='application/json')

#   课程讲师列表页
class TeacherListView(View):
    def get(self,request):
        #   过滤出所有的讲师
        all_teacher = Teacher.objects.all()
        #   人气排序
        sort = request.GET.get('sort','')
        if sort:
            if sort == 'hot':
                all_teacher = all_teacher.order_by("-click_nums")

        #   搜索功能
        search_keywords = request.GET.get('keywords','')
        if search_keywords:
            #   在name字段进行操作，做like语句操作，i 指代表不区分大小写
            #   or操作使用并集Q
            all_teacher = all_teacher.filter(
                Q(name__icontains=search_keywords) | Q(work_company__icontains=search_keywords))
        #   排行榜讲师
        rank_teachers = all_teacher.order_by("-fav_nums")[:3]
        #   共有多少讲师，使用count进行统计
        teacher_nums = all_teacher.count()

        #   讲师页分页实现，
        #   GET获取前台page参数
        #   如果是不合法的page页数，默认返回第一页（用户体验）
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page = 1
        #   此处是指从所有讲师中取出2个，进行分页
        fenye = Paginator(all_teacher,2)
        all_teacher = fenye.page(page)

        return render(request,'teachers-list.html',{
            'all_teacher':all_teacher,
            'sort':sort,
            'rank_teachers':rank_teachers,
            'teacher_nums':teacher_nums,
        })

#   教师详情页
class TeacherDetailView(View):
    def get(self,request,teacher_id):
        #   根据ID确认访问的是哪位讲师
        teacher = Teacher.objects.get(id=int(teacher_id))
        #   根据教师反查课程
        all_course = teacher.course_set.all()
        #   点击数增加，点一次加一次
        teacher.click_nums += 1
        teacher.save()
        #   讲师排行榜
        rank_teacher = Teacher.objects.all().order_by("-fav_nums")[:3]
        #   向前端传值说明用户是否收藏讲师,默认为Falsh
        has_fav_teacher = False
        #   此处判断需要用户通过验证
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=teacher.id,fav_type=3):
                has_fav_teacher = True
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=teacher.org.id,fav_type=2):
                has_fav_org = True

        return render(request,'teacher-detail.html',{
            'teacher':teacher,
            'all_course':all_course,
            'rank_teacher':rank_teacher,
            'has_fav_teacher':has_fav_teacher,
            'has_fav_org':has_fav_org,
        })