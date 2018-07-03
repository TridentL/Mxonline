from django import forms
from operation.models import UserAsk
import re

#   此处我们使用进阶版本的ModelForm,它可以向model一样save
class UserAskForm(forms.ModelForm):

    class Meta:
        model = UserAsk
        fields = ('name','mobile','course_name',)

    #   手机号的正则验证, clean_字段名 用作字典字段验证
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            forms.ValidationError("手机号格式有误",code="mobile_invalid")