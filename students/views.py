
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import render
from django.views.generic import View

# Create your views here.

from teachers.models import *

# Authorized access mixin abstract class
class UserIsStudentMixin(AccessMixin):

    def __init__(self):
        self.raise_exception = True

    def test_student(self, *args, **kwargs):
        #pk = kwargs['course_id']
        #course = Course.objects.get(pk = pk)
        return Student.objects.filter(user = self.request.user).exists()

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.test_student(*args, **kwargs)
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class IndexView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(request, course_id=None):
        return render(request, 'students/index.html', {
            'course_id': course_id,
        })


class CourseDetailView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(request, course_id):
        user = request.user
        course = Course.objects.get(pk=course_id)
        practices = course.get_practices().order_by('deadline')
        shift = Student.objects.get(user=user).shifts.filter(course = course)[0]
        return render(request, 'students/assignments.html', {
            'practices': practices,
            'shift': shift
        })
