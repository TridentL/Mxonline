import xadmin
from user_profile.models import EmailVerifyRecord,Banner
from xadmin import views
# Register your models here.

xadmin.site.register(EmailVerifyRecord)
xadmin.site.register(Banner)

class GlobalSetting(object):
    menu_style = 'accordion'

xadmin.site.register(views.CommAdminView,GlobalSetting)
