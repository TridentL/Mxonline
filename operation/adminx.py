import xadmin
from operation.models import UserAsk,UserCourse,UserFavorite,UserMessage,CourseComments
# Register your models here.
xadmin.site.register(UserAsk)
xadmin.site.register(UserCourse)
xadmin.site.register(UserFavorite)
xadmin.site.register(UserMessage)
xadmin.site.register(CourseComments)