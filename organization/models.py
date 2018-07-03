from django.db import models
from DjangoUeditor.models import UEditorField

# Create your models here.

#   课程机构
class CourseOrg(models.Model):
    #   自定义机构类别规则
    ORG_CHOICES = (
        ('pxjg','培训机构'),
        ('gx','高校'),
        ('gr','个人')
    )

    name = models.CharField(max_length=10,verbose_name="机构名称")
    #   机构描述
    desc = models.TextField(max_length=520,verbose_name="机构描述")
    #   机构类别
    category = models.CharField(max_length=100,choices=ORG_CHOICES,verbose_name='机构类别')
    tag = models.CharField(max_length=10,verbose_name="机构标签")
    click_nums = models.IntegerField(default=0,verbose_name="点击数")
    fav_nums = models.IntegerField(default=0,verbose_name="收藏数")
    image = models.ImageField(
        upload_to="org/%Y/%m",
        verbose_name="机构Logo",
        max_length=100
    )
    address = models.CharField(max_length=100,verbose_name="机构地址")
    city = models.ForeignKey('CityDict',verbose_name="所属地区")
    students = models.IntegerField(default=0,verbose_name="学习人数")
    course_nums = models.IntegerField(default=0,verbose_name="课程数")
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def __str__(self):
        return '课程机构：{0}'.format(self.name)

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

#   城市
class CityDict(models.Model):
    name = models.CharField(max_length=10,verbose_name="城市")
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name

#   讲师
class Teacher(models.Model):
    org = models.ForeignKey(CourseOrg,verbose_name="所属机构")
    image = models.ImageField(
        upload_to="teacher/%Y/%m",
        verbose_name="上传头像",
        max_length=100
    )
    name = models.CharField(max_length=10,verbose_name="教师名称")
    work_years = models.CharField(max_length=10,verbose_name="工作年限")
    age = models.CharField(max_length=10,verbose_name="年龄")
    work_company = models.CharField(max_length=50, verbose_name="就职公司")
    work_position = models.CharField(max_length=50, verbose_name="公司职位")
    points = models.CharField(max_length=50, verbose_name="教学特点")
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏数")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=u"添加时间")

    def __str__(self):
        return '教师：{0}'.format(self.name)

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name