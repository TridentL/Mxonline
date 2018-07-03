from django.conf.urls import url

from user_profile.views import UserInfoView,MyCourseView,MyFavOrgView,MyFavTeacherView,MyFavCourseView,\
    MyMessageView,UploadImageView,UpdatePwdView,UpdateEmailView,SendEmailCodeView

urlpatterns = [
    #   用户信息
    url(r'^info/$',UserInfoView.as_view(),name='user_info'),

    #   用户中心头像上传
    url(r'^image/upload/$',UploadImageView.as_view(),name='image_upload'),

    # 用户个人中心修改密码
    url(r'^update/pwd/$', UpdatePwdView.as_view(), name="update_pwd"),

    #   邮箱验证码发送
    url(r'^sendemail_code/$',SendEmailCodeView.as_view(),name='sendemail_code'),

    #   用户中心修改邮箱
    url(r'^update_email/$',UpdateEmailView.as_view(),name='update_email'),

    #   用户中心我的课程
    url(r'^mycourse/$',MyCourseView.as_view(),name='mycourse'),

    #   用户中心我的收藏的课程机构
    url(r'^myfav/org/$',MyFavOrgView.as_view(),name='myfav_org'),

    #   用户中心我的收藏的授课教师
    url(r'^myfav/teacher/$',MyFavTeacherView.as_view(),name='myfav_teacher'),

    #   用户中心我的收藏的公开课程
    url(r'^myfav/course/$',MyFavCourseView.as_view(),name='myfav_course'),

    #   用户中心我的消息
    url(r'^my_message/$',MyMessageView.as_view(),name='my_message'),

]