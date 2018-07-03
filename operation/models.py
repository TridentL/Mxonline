from django.db import models
from course.models import Course
from user_profile.models import UserProfile

# Create your models here.

#   我要学习表单
class UserAsk(models.Model):
    name = models.CharField(max_length=10,verbose_name='姓名')
    mobile = models.CharField(max_length=11,verbose_name="联系电话")
    course_name = models.CharField(max_length=10,verbose_name='课程名')
    add_time = models.DateField(auto_now_add=True,verbose_name="加入时间")

    def __str__(self):
        return '用户: {0},联系方式: {1}'.format(self.name,self.mobile)

    class Meta:
        verbose_name = '用户咨询'
        verbose_name_plural = verbose_name

#   用户对于课程的评论
class CourseComments(models.Model):

    #   涉及两个外键  1.用户  2.课程。import
    course = models.ForeignKey(Course,verbose_name="课程")
    user = models.ForeignKey(UserProfile,verbose_name='用户')
    comments = models.CharField(max_length=500,verbose_name="评论")
    add_time = models.DateField(auto_now_add=True,verbose_name="评论时间")

    def __str__(self):
        return '用户({0})对于《{1}》的评论:'.format(self.user,self.course)

    class Meta:
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name

#   用户对于课程，讲师，机构的收藏
class UserFavorite(models.Model):
    #   涉及四个外键。用户，课程，机构，讲师import
    #   自定义选择类型
    TYPE_CHOICES = (
        (1,'课程'),
        (2,'课程机构'),
        (3,'讲师')
    )

    #   用户
    user = models.ForeignKey(UserProfile,verbose_name="用户")

    #   借用别人的方法，原理暂待思考
    #   直接保存用户的ID
    fav_id = models.IntegerField(default=0)
    #   表明收藏的是哪种类型
    fav_type = models.IntegerField(
        choices=TYPE_CHOICES,
        default=1,
        verbose_name='收藏类型',
    )
    add_time = models.DateField(auto_now_add=True,verbose_name='加入时间')

    def __str__(self):
        return '用户({0})收藏了《{1}》'.format(self.user,self.fav_type)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = verbose_name

#   用户消息
class UserMessage(models.Model):
    #   我们的消息有两种：发给全员或发给某个用户
    #   解决方法之一为：为0发给全体用户，不为0发给某个用户的id
    user = models.IntegerField(default=0,verbose_name="接收用户")
    message = models.CharField(max_length=500,verbose_name="消息内容")

    #  判断用户是否已读：选布尔值，False为未读，True为已读
    has_read = models.BooleanField(default=False,verbose_name='是否已读')
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def __str__(self):
        return '用户({0})接收了《{1}》'.format(self.user,self.message)

    class Meta:
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name

#   用户课程表
class UserCourse(models.Model):
    #   用户课程涉及用户和课程两个外键，import
    course = models.ForeignKey(Course,verbose_name="课程")
    user = models.ForeignKey(UserProfile,verbose_name="用户")
    add_time = models.DateField(auto_now_add=True,verbose_name="加入时间")

    def __str__(self):
        return '用户({0})学习了《{1}》'.format(self.user,self.course)

    class Meta:
        verbose_name = '用户课程'
        verbose_name_plural = verbose_name