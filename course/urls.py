from django.conf.urls import url
from course.views import CourseListView,CourseDetailView,CourseLessonView,CourseVideoView,CourseCommentView,\
    AddCommentView

urlpatterns = [
    #   公开课程列表
    url(r'^list/$',CourseListView.as_view(),name='list'),

    #   课程详情页
    url(r'^course/(?P<course_id>\d+)/$',CourseDetailView.as_view(),name='course_detail'),

    #   课程章节信息页
    url(r'^lesson/(?P<course_id>\d+)/$',CourseLessonView.as_view(),name='course_lesson'),

    #   课程视频列表页
    url(r'^video/(?P<video_id>\d+)/$',CourseVideoView.as_view(),name='course_video'),

    #   课程评论列表页
    url(r'^comment/(?P<course_id>\d+)/$',CourseCommentView.as_view(),name='course_comment'),

    #   添加评论
    url(r'^add_comment/$',AddCommentView.as_view(),name='add_comment'),

]