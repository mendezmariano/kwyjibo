import os

from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.generic import View

# Create your views here.

from teachers.models import *

from .forms import *

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

    def get(self, request):
        if(len(request.user.student_set.all()) > 0): # if an authenticated user "accidentally" access this section, he doesn't get an exception
            shifts = request.user.student_set.get(uid=request.user.username).shifts.all()
            return render(request, 'students/index.html', {
                'shifts': shifts
            })
        else:
            return HttpResponse('Unauthorized', status=401)


class CourseDetailView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(self, request, course_id):
        user = request.user
        course = Course.objects.get(pk=course_id)
        assignments = course.assignments.all().order_by('deadline')
        shift = Student.objects.get(user=user).shifts.filter(course = course)[0]
        return render(request, 'students/assignments.html', {
            'course': course,
            'assignments': assignments,
            'shift': shift
        })


class AssignmentFilesView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(self, request, course_id, assignment_id):
        assignment = Assignment.objects.get(pk = assignment_id)
        assignment_files = assignment.assignmentfile_set.all()
        return render(request, 'students/assignment_files.html', {
            'assignment_files': assignment_files,
            'assignment': assignment,
            'course': assignment.course
        })


class DownloadAssignmentFileView(LoginRequiredMixin, UserIsStudentMixin, View):
    
    def get(self, request, course_id, assignment_id, assignment_file_id):
        assignment_file = AssignmentFile.objects.get(pk=assignment_file_id)
        assignment = assignment_file.assignment
        course = assignment.course
        if not (course.pk==int(course_id) and assignment.pk==int(assignment_id)):
            return HttpResponseBadRequest()

        filename, file_extension = os.path.splitext(assignment_file.file.name)
        #filename = assignment_file.file.name.split('/')[-1]
        
        filename = assignment_file.name.replace(" ", '_')
        response = HttpResponse(assignment_file.file)
        response['Content-Disposition'] = 'attachment; filename=%s%s' % (filename, file_extension)
        return response


class DeliveryListView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(self, request, course_id, assignment_id):
        student_id = request.user.student_set.get(uid=request.user.username).pk
        student = Student.objects.get(pk=student_id)
        assignment = Assignment.objects.get(pk=assignment_id)
        course = assignment.course

        if not (course.pk==int(course_id)):
            return HttpResponseBadRequest()

        deliveries = Delivery.objects.filter(student=student, assignment=assignment)
        return render(request, 'students/delivery_list.html', {
            'course': course,
            'student' : student,
            'assignment': assignment,
            'deliveries': deliveries
        })


class NewDeliveryView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(self, request, course_id, assignment_id):
        student_id = request.user.student_set.get(uid=request.user.username).pk
        student = Student.objects.get(pk=student_id)
        assignment = Assignment.objects.get(pk=assignment_id)
        course = assignment.course

        if (course.pk!=int(course_id)):
            return HttpResponseBadRequest()
        if (assignment.is_expired()):
            return redirect('students:assignments', course_id = course_id)

        form = DeliveryForm()
        return render(request, 'students/new_delivery.html', {
            'form': form,
            'course': course,
            'student' : student,
            'assignment': assignment,
        })

    def post(self, request, course_id, assignment_id):
        student_id = request.user.student_set.get(uid=request.user.username).pk
        student = Student.objects.get(pk=student_id)
        assignment = Assignment.objects.get(pk=assignment_id)
        course = assignment.course

        if (course.pk != int(course_id) or assignment.is_expired()):
            return HttpResponseBadRequest()

        delivery = Delivery(student=student, assignment=assignment)
        form = DeliveryForm(request.POST, request.FILES, instance=delivery)
        if (form.is_valid()):
            form.save()
            revision = Revision()
            revision.delivery = form.instance
            revision.save()
            return redirect('students:delivery_list', course_id = course_id, assignment_id = assignment_id)

        return render(request, 'students/new_delivery.html', {
            'form': form,
            'course': course,
            'student' : student,
            'assignment': assignment,
        })


class RevisionDetailsView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(self, request, course_id, assignment_id, delivery_id):
        student_id = request.user.student_set.get(uid=request.user.username).pk
        student = Student.objects.get(pk=student_id)
        assignment = Assignment.objects.get(pk=assignment_id)
        course = assignment.course

        if ((course.pk!=int(course_id)) or (assignment.pk != int(assignment_id))):
            return HttpResponseBadRequest()

        delivery = Delivery.objects.get(pk=delivery_id)
        revision = delivery.revision
        return render(request, 'students/revision_details.html', {
            'course': course,
            'student' : student,
            'assignment': assignment,
            'delivery': delivery,
            'delivery_detail': delivery.file.name.split('/')[-1],
            'revision': revision,
        })


class CorrectionDetailsView(LoginRequiredMixin, UserIsStudentMixin, View):

    def get(self, request, course_id, assignment_id, delivery_id):
        student_id = request.user.student_set.get(uid=request.user.username).pk
        student = Student.objects.get(pk=student_id)
        assignment = Assignment.objects.get(pk=assignment_id)
        course = assignment.course
        delivery = Delivery.objects.get(pk=delivery_id)
        correction_qset = Correction.objects.filter(delivery=delivery)

        if ((course.pk!=int(course_id)) or (assignment.pk != int(assignment_id)) or (not correction_qset)):
            return HttpResponseBadRequest()

        correction = correction_qset[0]
        return render(request, 'students/correction_details.html', {
            'course': course,
            'student' : student,
            'assignment': assignment,
            'delivery': delivery,
            'delivery_detail': delivery.file.name.split('/')[-1],
            'correction': correction,
        })
