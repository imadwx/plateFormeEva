from django.contrib import admin

# Register your models here.


from .models import EvaluationMultQ
from .models import QuestionType
from .models import ProfileUser


admin.site.register(EvaluationMultQ)
admin.site.register(QuestionType)
admin.site.register(ProfileUser)