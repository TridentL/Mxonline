import xadmin
from organization.models import CourseOrg,CityDict,Teacher
# Register your models here.
xadmin.site.register(CourseOrg)
xadmin.site.register(CityDict)
xadmin.site.register(Teacher)