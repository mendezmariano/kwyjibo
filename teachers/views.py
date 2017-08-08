
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect

from kwyjibo.settings import *
from mailing.models import Mail

from .models import *
from .forms import *

# Create your views here.

# Constants
SUBJECT_EMAIL = "Tienes una correccion para ver en Kwyjibo"
CORRECTION_NOTIFICATION_MAIL_BODY = "Práctica: {practice}\n\nComentario del corrector.\n{comment}\n\nNota: {grade}"
CORRECTION_NOTIFICATION_MAIL_REPLY_ADDRESS = "no-response@kwyjibo.org"

# Authorized access mixin abstract class
class UserHasTeacherAccessLevel(AccessMixin):

    def __init__(self):
        self.raise_exception = True

    def test_teacher(self, *args, **kwargs):
        return Teacher.objects.filter(user = self.request.user).exists()

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.test_teacher(*args, **kwargs)
        if not user_test_result:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# Views
class RevisionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """Browse delivery's corrections made automatically"""

    def get(self, request, id_course, id_delivery):
        current_course = Course.objects.get(pk = id_course)
        courses = Course.objects.all()
        
        delivery = Delivery.objects.get(pk=id_delivery)
        automatic_correction = delivery.get_automatic_correction()
        return render(request, 'revision_details.html', {
            'current_course': current_course,
            'courses': courses,
            'automatic_correction': automatic_correction, 'practice': delivery.practice
        })



class CorrectionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """Teachers manual correction form flow"""

    def get(request, id_course, id_delivery):
        courses = Course.objects.all()
        current_course = courses.get(pk=id_course)
        
        delivery = Delivery.objects.get(pk=id_delivery)
        correction = Correction.objects.filter(delivery=delivery)
        if correction:
            form = CorrectionForm(instance=correction)
        else:
            form = CorrectionForm()
        return render(request, 'grade_delivery.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'delivery': delivery,
            'corrector': delivery.student.corrector,
        })

    def post(request, id_course, id_delivery):
        courses = Course.objects.all()
        current_course = courses.get(pk=id_course)
        
        teacher = Teacher.objects.get(user=request.user)
        delivery = Delivery.objects.get(pk=id_delivery)

        deletable_correction = Correction.objects.filter(delivery=delivery)
        correction = Correction(delivery=delivery)
        correction.corrector = teacher
        form = CorrectionForm(request.POST, instance=correction)
        if (form.is_valid()):
            form.save()
            delivery.student.corrector = teacher
            delivery.student.save()
            mail = Mail.objects.create(
                    subject = SUBJECT_EMAIL,
                    body = CORRECTION_NOTIFICATION_MAIL_BODY.fromat(
                        practice = correction.delivery.practice.uid,
                        comment = correction.public_comment,
                        grade = correction.grade,),
                    recipient = delivery.student.user.email,
                    reply_address = CORRECTION_NOTIFICATION_MAIL_REPLY_ADDRESS,
                )
            if deletable_correction:
                deletable_correction.delete()
            return redirect('teachers:dashboard', id_course = id_course)
        else:
            return render(request, 'grade_delivery.html', {
                'current_course' : current_course,
                'courses' : courses,
                'form': form,
                'delivery': delivery,
                'corrector': delivery.student.corrector,
            })


class NewCourseView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """This is for creating a new course"""

    def get(request, idcourse=None):
        courses = Course.objects.all()
        if idcourse is not None:
            current_course = courses.get(pk=idcourse)
        else:
            current_course = None
        
        form = CourseForm()
        return render(request, 'course_new.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
        })

    def post(request, idcourse=None):
        courses = Course.objects.all()
        if idcourse:
            current_course = courses.get(pk=idcourse)
        else:
            current_course = None
        
        form = CourseForm(request.POST)
        if (form.is_valid()):
            form.save()
            return redirect('teachers:dashboard', id_course = form.instance.pk)

        return render(request, 'course_new.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
        })


class CoursesView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """"""

    def get(request):
        courses_list = Course.objects.all().order_by('-name')
        paginator = Paginator(courses_list, MAX_PAGINATOR) # Show 25 courses per page
        page = request.GET.get('page')
        try:
            courses = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            courses = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            courses = paginator.page(paginator.num_pages)
        return render('courses.html', {"courses": courses},)


class EditCourseView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """This is for editing an already existant course"""
        
    def get(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        course = current_course
        form = CourseForm(instance=course)
        return render(request, 'course_edit.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course': course
        })
        
    def post(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        course = current_course
        form = CourseForm(request.POST, instance=course)
        if (form.is_valid()):
            form_edit = form.save(commit=False)
            form_edit.save()
            return redirect('teachers:dashboard', id_course = course.pk)
        return render(request, 'course_edit.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course': course
        })



class DeliveryListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idpractice):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        practice = Practice.objects.get(pk=idpractice)
        table_deliveries = []
        deliveries = Delivery.objects.filter(practice=practice).order_by('date')
        for delivery in deliveries:
            table_deliveries.append({'delivery': delivery, 'correction': delivery.correction})
        return render(request, 'delivery/listdelivery.html', {
            'current_course' : current_course,
            'courses' : courses,
            'table_deliveries': table_deliveries,
            'practice': practice,
        })


class StudentsDeliveryListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idpractice, idstudent):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        student = Student.objects.get(pk=idstudent)
        practice = Practice.objects.get(pk=idpractice)
        table_deliveries = []
        deliveries = Delivery.objects.filter(practice=practice,student__pk=idstudent)
        for delivery in deliveries:
            table_deliveries.append({'delivery': delivery, 'correction': delivery.correction})
        return render(request, 'delivery/listdeliveryperstudentperpractice.html', {
            'current_course' : current_course,
            'courses' : courses,
            'student' : student,
            'table_deliveries': table_deliveries,
            'practice': practice,
        })


class DeliveryDownloadView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, id_delivery):
        delivery = Delivery.objects.get(pk=id_delivery)
        filename = delivery.file.name.split('/')[-1]
        response = HttpResponse(delivery.file, content_type=TYPEZIP)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response        

