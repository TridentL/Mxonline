from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from course.models import Course,CourseResource,Video
from operation.models import UserFavorite,UserCourse,CourseComments,UserMessage

# Create your views here.

#   课程列表页view
class CourseListView(View):
    def get(self,request):
        #   获取全部课程,以时间顺序进行降序排序
        all_course = Course.objects.all().order_by("-add_time")

        #   右侧热门课程推荐
        hot_courses = Course.objects.all().order_by("-students")[:3]

        #   搜索功能
        search_keywords = request.GET.get('keywords','')
        if search_keywords:
            #   在name字段进行操作,做like语句的操作, i 代表不区分大小写
            all_course = Course.objects.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(detail__icontains=search_keywords))

        #   课程进行排序
        sort = request.GET.get('sort','')
        if sort:
            if sort == "hot":
                all_course = all_course.order_by("-click_nums")
            elif sort == "students":
                all_course = all_course.order_by("-students")

        #   对课程进行分页
        #   获取前台的page参数
        #   如果获取不到，或者获取的是不合法的page，默认设置为1
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page = 1

        #   这里指从全部课程中取出6个元素进行分页，每页展示6个
        fenye = Paginator(all_course,6)
        all_course = fenye.page(page)

        return render(request,'course-list.html',{
            'all_course':all_course,
            'hot_courses':hot_courses,
            'search_keywords':search_keywords,
            'sort':sort,
        })

#   课程详情页view
class CourseDetailView(View):
    def get(self,request,course_id):
        #   根据前端传过来的ID过滤对象的课程
        courses = Course.objects.get(id=int(course_id))
        #   是否收藏课程(机构)
        has_fav_course = False
        has_fav_org = False

        #   必须是用户通过登录验证才需要判断
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user,fav_id=courses.id,fav_type=1):
                has_fav_course = True
            elif UserFavorite.objects.filter(user=request.user,fav_id=courses.course_org.id,fav_type=2):
                has_fav_org = True

        #   课程数点击数增加
        courses.click_nums += 1
        courses.save()

        tag = courses.tag
        if tag:
            #   需要从1开始不然不会推荐自己?
            relate_courses = Course.objects.filter(tag=tag)[:2]
        else:
            relate_courses = []

        return render(request,'course-detail.html',{
            'courses':courses,
            'has_fav_course':has_fav_course,
            'has_fav_org':has_fav_org,
            'relate_courses':relate_courses,
        })

#   课程章节信息view
class CourseLessonView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'
    def get(self,request,course_id):
        #   根据前端传过来的ID值和数据表中自动为我们创建好的表的id值
        #   获取指定课程
        course = Course.objects.get(id=int(course_id))
        #   查询用户是否已经学习了这门课，
        #   如果未开始学习这门课，则加入到用户课程表
        user_courses = UserCourse.objects.filter(user=request.user,course=course)
        if not user_courses:
            user_courses = UserCourse(user=request.user,course=course)
            course.students += 1
            course.save()
            user_courses.save()
        #   查询课程资源,通过课程定位课程资源
        all_resources = CourseResource.objects.filter(course=course)
        #   选出学了这门课的学生关系
        user_courses = UserCourse.objects.filter(course=course)
        #   列表式取出从关系中取出用户id
        user_ids = [user_course.user_id for user_course in user_courses]
        #   这些用户学了的课程，外键会自动生成id,取到字段
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #   列表式取出所有课程的id
        course_ids = [user_course.course_id for user_course in all_user_courses]
        #   获取该课程用户学过的其他课程并排除掉登陆用户学习过的课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums").exclude(id=course.id)[:4]

        return render(request,'course-video.html',{
            'course':course,
            'all_resources':all_resources,
            'relate_courses':relate_courses,
        })

#   课程视频播放view
class CourseVideoView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'
    def get(self,request,video_id):
        #   根据前端传来的ID值到数据库取出对应的视频
        video = Video.objects.get(id=int(video_id))
        #   根据视频反查找到课程
        course = video.lesson.course
        #   查询用户是否学习了该课程，如果还未学习，则加入到用户课程表
        user_course = UserCourse.objects.filter(user=request.user,course=course)
        if not user_course:
            user_course = UserCourse(user=request.user,course=course)
            user_course.save()
        #   查询课程资源
        all_resources = CourseResource.objects.filter(course=course)
        #   选出学习了这门课的学生  <QuerySet [<UserCourse: 用户(管理员)学习了《服务器集群技术》>]>
        user_courses = UserCourse.objects.filter(course=course)
        #   从关系中取出用户id  [1]
        user_ids = [user_course.user_id for user_course in user_courses]
        #   这些用户学了的课程，会自动生成关联外键id  <QuerySet [<UserCourse: 用户(管理员)学习了《服务器集群技术》>, <UserCourse: 用户(管理员)学习了《Python全栈开发》>]>
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #   取出所有学习过课程的id  [1, 2]
        courses_ids = [user_course.course_id for user_course in all_user_courses]
        #   获取学过该课程用户学过的其他课程  <QuerySet [<Course: Python全栈开发>]>
        relate_courses = Course.objects.filter(id__in=courses_ids).order_by("-click_nums").exclude(id=course.id)[:4]

        return render(request,'course-play.html',{
            'video':video,
            'course':course,
            'relate_courses':relate_courses,
            'all_resources':all_resources,
        })

#   课程评论view
class CourseCommentView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'
    def get(self,request,course_id):
        #   通过ID值获取对应课程
        course = Course.objects.get(id=int(course_id))
        #   课程资源
        all_resources = CourseResource.objects.filter(course=course)
        #   取出这门课程的全部课程
        all_comments = CourseComments.objects.filter(course=course).order_by("add_time")
        #   选出与这门课有关系的用户
        user_courses = UserCourse.objects.filter(course=course)
        #   从关系中取出用户id
        user_ids = [user_course.user_id for user_course in user_courses]
        #   这些用户学习了的课程，外键会自动生成id,通过id取得字段
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        #   取出所有课程的id
        course_ids = [user_course.course_id for user_course in all_user_courses]
        #   获取学过该课程的用户的其他课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums").exclude(id=course.id)[:4]

        return render(request,'course-comment.html',{
            'course':course,
            'all_resources':all_resources,
            'relate_courses':relate_courses,
            'all_comments':all_comments,
        })

#   ajax添加评论
class AddCommentView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'
    def post(self,request):
        #   判断用户是否登录，未登录返回json提示未登录,跳转到登陆页面
        if not request.user.is_authenticated():
            return JsonResponse('{"status":"fail","msg":"用户未登录"}',content_type='application/json')
        course_id = request.POST.get('course_id',0)
        comments = request.POST.get('comments','')
        if int(course_id) > 0 and comments:
            course_comments = CourseComments()
            #   get每次只能取出一条数据，如果有多条会抛出异常，没有数据也报异常
            #   filter取出的是一个数据的列表，queryset，没有数据返回空的queryset也不会报错
            course = Course.objects.get(id=int(course_id))
            #   外键存入数据
            course_comments.course = course
            course_comments.user = request.user
            course_comments.comments = comments
            course_comments.save()
            return HttpResponse('{"status":"success","msg":"评论成功"}',content_type='application/json')
        else:
            return HttpResponse('{"status":"fail","msg":"评论失败"}',content_type='application/json')