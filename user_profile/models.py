from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

#   创建用户类
class UserProfile(AbstractUser):
    #   自定义性别选择规则
    SEX_CHOICES = (
        ('male','男'),
        ('female','女')
    )
    #   昵称
    nick_name = models.CharField(max_length=10,verbose_name='昵称',default='')
    #   出生日期，可以为空
    birthday = models.DateField(verbose_name='出生日期',default="1996-01-01")
    #   性别只能男和女,默认为女
    sex = models.CharField(
        max_length=6,
        verbose_name = '性别',
        choices=SEX_CHOICES,
        default='female'
    )
    #   地址
    address = models.CharField(max_length=100,verbose_name="地址",blank=True,null=True)
    #   电话,可为空
    mobile = models.CharField(max_length=11,verbose_name='电话',null=True,blank=True)
    #   头像,默认使用default.png
    head_image = models.ImageField(upload_to='head_image/%Y/%m',default='/static/img/default.png',verbose_name='上传头像')

    def __str__(self):
        return self.nick_name

    #   定义用户未读消息处理
    def unread_nums(self):
        from operation.models import UserMessage
        #    __in 指存在于一个list范围内,类似于Q并集,但是指同时包含两个条件
        return UserMessage.objects.filter(user__in=[self.id,0],has_read=False).count()

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

#   邮箱验证码
class EmailVerifyRecord(models.Model):
    #   自定义发送选择
    SEND_CHOICES = (
        ('register','注册'),
        ('forget','找回密码'),
        ('update_email','修改邮箱')
    )
    #   验证码
    code = models.CharField(max_length=20,verbose_name='验证码')
    #   邮箱
    email = models.EmailField(max_length=30,verbose_name="邮箱")
    #   发送类型
    send_type = models.CharField(
        choices=SEND_CHOICES,
        max_length=20,
        verbose_name="验证码类型"
    )
    #   发送时间
    send_time = models.DateField(auto_now_add=True,verbose_name="发送时间")

    def __str__(self):
        return '{0}({1})'.format(self.code,self.email)

    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = verbose_name

#   轮播图
class Banner(models.Model):
    title = models.CharField(max_length=100,verbose_name="标题")
    image = models.ImageField(upload_to='banner/%Y/%m',verbose_name="轮播图",max_length=100)
    url = models.URLField(max_length=100,verbose_name="访问地址")
    #   默认Index很大靠后，想要靠前修改index值
    index = models.IntegerField(default=100,verbose_name="顺序")
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def __str__(self):
        return '{0}(位于第{1}位)'.format(self.title,self.index)

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name