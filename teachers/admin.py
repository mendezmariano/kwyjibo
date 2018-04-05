from django.contrib import admin

# Register your models here.

from .models import *

class CourseAdmin(admin.ModelAdmin):
    """Utility for Django Admin tools.
    
    Util class that indicates the django admin how to order the courses when 
    listed.
    
    """
    
    ordering = ['-name',]

class StudentAdmin(admin.ModelAdmin):

    list_display = ('uid', 'user', 'get_full_name', )


    
admin.site.register(Teacher)
admin.site.register(Course, CourseAdmin)
admin.site.register(Shift)
admin.site.register(Assignment)
admin.site.register(AssignmentFile)
admin.site.register(Script)
admin.site.register(Student, StudentAdmin)
admin.site.register(Suscription)
admin.site.register(Delivery)
admin.site.register(Correction)
admin.site.register(Revision)
