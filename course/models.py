from django.db import models
from organization.models import CourseOrg,Teacher

# Create your models here.

#   课程信息表
class Course(models.Model):
    #   自定义选择规则
    DEGREE_CHOICES = (
        ('cj','初级'),
        ('zj','中级'),
        ('gj','高级')
    )
    course_org = models.ForeignKey(CourseOrg,verbose_name="所属机构",null=True,blank=True)
    teacher = models.ForeignKey(Teacher,verbose_name='讲师',null=True,blank=True)
    name = models.CharField(max_length=10,verbose_name='课程名')
    is_banner = models.BooleanField(default=False,verbose_name='是否轮播')
    desc = models.CharField(max_length=520,verbose_name='课程描述')
    # TextField允许我们不输入长度。可以输入到无限大。暂时定义为TextFiled，之后更新为富文本
    # 修改imagepath,不能传y m 进来，不能加斜杠是一个相对路径，相对于setting中配置的mediaroot
    detail = models.TextField(verbose_name="课程详情")
    degree = models.CharField(choices=DEGREE_CHOICES,max_length=10,verbose_name="难度")
    #   使用分钟数做后台记录(存储最小单位),前台转换
    learn_times = models.IntegerField(default=0,verbose_name="学习时长(分钟数)")
    #   保存学习人数：从点击开始学习算起
    students = models.IntegerField(default=0,verbose_name="学习人数")
    fav_nums = models.IntegerField(default=0,verbose_name="收藏人数")
    category = models.CharField(max_length=20,verbose_name="课程类别")
    you_need_know = models.CharField(max_length=500,default="一颗勤学的心和坚持不懈的精神是本课程必要前提",verbose_name="课程须知")
    teacher_tell = models.CharField(max_length=300,default="按时交作业,不然叫家长",verbose_name="老师告诉你")
    tag = models.CharField(max_length=15,verbose_name="课程标签")
    course_img = models.ImageField(
        upload_to="course/%Y/%m",
        verbose_name="课程封面",
        max_length=100
    )
    #   保存点击量
    click_nums = models.IntegerField(default=0,verbose_name="点击数")
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def get_zj_nums(self):
        return self.lesson_set.all().count()
    get_zj_nums.short_description = '章节数'

    def go_to(self):
        from django.utils.safestring import mark_safe
        # 如果不mark safe。会对其进行转义
        return  mark_safe("<a href='http://blog.mtianyan.cn'>跳转</>")
    go_to.short_description = "跳转"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name

#   轮播图
class BannerCourse(Course):
    class Meta:
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        proxy = True

#   章节
class Lesson(models.Model):
    #   因为一个课程对应很多章节，在章节表中将课程设置为外键.
    course = models.ForeignKey(Course,verbose_name="课程")
    name = models.CharField(max_length=10,verbose_name="章节名")
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def __str__(self):
        return '《{0}》课程的章节 >> {1}'.format(self.course,self.name)

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

#   章节视频
class Video(models.Model):
    #   一个章节对应很多视频,所以讲章节设置为外键
    lesson = models.ForeignKey(Lesson,verbose_name="章节")
    name = models.CharField(max_length=10,verbose_name="视频名")
    url = models.CharField(max_length=100,default="https://www.cnblogs.com/Tridents/",verbose_name="访问地址")
    #   使用分钟做后台转换(存储最小单位)前台转换
    learn_times = models.IntegerField(default=0,verbose_name="学习时长(分钟数)")
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def __str__(self):
        return '《{0}》章节的视频 >> {1}'.format(self.lesson,self.name)

    class Meta:
        verbose_name = '章节视频'
        verbose_name_plural = verbose_name

#   课程资源
class CourseResource(models.Model):
    #   一个课程对应多个资源，所以在这里将课程设置为外键
    course = models.ForeignKey(Course,verbose_name="课程")
    name = models.CharField(max_length=10,verbose_name="名称")
    #   此处直接定义为文件类型的filed,后台有按钮可直接上传
    download = models.FileField(
        upload_to="course/resourse/%Y/%m",
        verbose_name="资源文件",
        max_length=100
    )
    add_time = models.DateField(auto_now_add=True,verbose_name="添加时间")

    def __str__(self):
        return '《{0}》课程的资源 >> {1}'.format(self.course,self.name)

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name