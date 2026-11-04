from django.contrib import admin
from.models import student,classRoom,Teacher,Attendance,Examination,Feepayment
# Register your models here.
admin.site.register(student)
admin.site.register(classRoom)
admin.site.register(Teacher)
admin.site.register(Attendance)
admin.site.register(Examination)
admin.site.register(Feepayment)