import xadmin
from course.models import Course,Lesson,Video,CourseResource
# Register your models here.
xadmin.site.register(Course)
xadmin.site.register(Lesson)
xadmin.site.register(Video)
xadmin.site.register(CourseResource)