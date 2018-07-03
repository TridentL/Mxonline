from django.conf.urls import url
from organization.views import OrgListView,AddUserAskView,OrgHomeView,OrgCourseView,OrgTeacherView,OrgDescView,\
    AddFavView,TeacherListView,TeacherDetailView

urlpatterns = [
    #   授课机构列表
    url(r'^list/$',OrgListView.as_view(),name='org_list'),

    #   学习咨询
    url(r'^add_ask/$',AddUserAskView.as_view(),name='add_ask'),

    #   机构详情页，
    url(r'^home/(?P<org_id>\d+)/$',OrgHomeView.as_view(),name='org_home'),

    #   机构课程列表
    url(r'^course/(?P<org_id>\d+)/$',OrgCourseView.as_view(),name='org_course'),

    #   机构介绍列表页
    url(r'^desc/(?P<org_id>\d+)/$',OrgDescView.as_view(),name='org_desc'),

    #   机构讲师列表
    url(r'^teacher/(?P<org_id>\d+)/$',OrgTeacherView.as_view(),name='org_teacher'),

    #   添加收藏
    url(r'^add_fav/$',AddFavView.as_view(),name='add_fav'),

    #   讲师列表url配置
    url(r'^teacher/list/$',TeacherListView.as_view(),name='teacher_list'),

    #   教师详情url配置
    url(r'teacher/detail/(?P<teacher_id>\d+)/$',TeacherDetailView.as_view(),name='teacher_detail'),
]