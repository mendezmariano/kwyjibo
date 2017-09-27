import os, shutil

from zipfile import ZipFile

from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from kwyjibo.settings import *
from mailing.models import Mail

from .models import *
from .forms import *

# Create your views here.

# Constants
CORRECTION_NOTIFICATION_MAIL_SUBJECT = _("You have a new correction in Kwyjibo")
CORRECTION_NOTIFICATION_MAIL_BODY = _("Assignment: {assignment}\n\nCorrector's comment.\n{comment}\n\nGrade: {grade}")
CORRECTION_NOTIFICATION_MAIL_REPLY_ADDRESS = "no-response@kwyjibo.org"

STUDENT_CREATION_MAIL_SUBJECT = _("New user on Kwyjibo")
STUDENT_CREATION_MAIL_BODY = _("A new user on Kwyjibo has been created for you. Your access information is Username: {username} and Password: {password}")
STUDENT_CREATION_MAIL_REPLY_ADDRESS = "no-response@kwyjibo.org"

MAX_PAGINATOR_SIZE = 25

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
        #print("args: {args}".format(args = args))
        #print("kwargs: {kwargs}".format(kwargs = kwargs))
        return super().dispatch(request, *args, **kwargs)


# Views
class RevisionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """Browse delivery's corrections made automatically"""

    def get(self, request, course_id, delivery_id):
        current_course = Course.objects.get(pk = course_id)
        courses = Course.objects.all()
        
        delivery = Delivery.objects.get(pk=delivery_id)
        revision = Revision.objects.filter(delivery = delivery)[0]
        return render(request, 'teachers/revision_details.html', {
            'current_course': current_course,
            'courses': courses,
            'delivery': delivery,
            'revision': revision,
            'assignment': delivery.assignment,
            'delivery_detail': delivery.file.name.split('/')[-1],
        })



class CorrectionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """Teachers manual correction form flow"""

    def get(self, request, course_id, delivery_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        delivery = Delivery.objects.get(pk=delivery_id)
        correction = Correction.objects.filter(delivery=delivery)
        if correction:
            form = CorrectionForm(instance=correction[0])
        else:
            form = CorrectionForm()
        return render(request, 'teachers/grade_delivery.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'assignment': delivery.assignment,
            'delivery': delivery,
            'delivery_detail': delivery.file.name.split('/')[-1],
            'revision': delivery.revision,
            'corrector': delivery.student.corrector,
        })

    def post(self, request, course_id, delivery_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        teacher = Teacher.objects.get(user=request.user)
        delivery = Delivery.objects.get(pk=delivery_id)

        previous_correction = Correction.objects.filter(delivery=delivery)
        if not previous_correction:
            correction = Correction(delivery=delivery)
        else:
            correction = previous_correction[0]
        correction.corrector = teacher
        form = CorrectionForm(request.POST, instance=correction)
        if (form.is_valid()):
            form.save()
            delivery.student.corrector = teacher
            delivery.student.save()
            mail = Mail.objects.create(
                    subject = CORRECTION_NOTIFICATION_MAIL_SUBJECT,
                    body = CORRECTION_NOTIFICATION_MAIL_BODY.format(
                        assignment = correction.delivery.assignment.uid,
                        comment = correction.feedback,
                        grade = correction.grade,),
                    recipient = delivery.student.user.email,
                    reply_address = CORRECTION_NOTIFICATION_MAIL_REPLY_ADDRESS,
                )
            return redirect('teachers:dashboard', course_id = course_id)
        else:
            return render(request, 'teachers/grade_delivery.html', {
                'current_course' : current_course,
                'courses' : courses,
                'form': form,
                'assignment': delivery.assignment,
                'delivery': delivery,
                'delivery_detail': delivery.file.name.split('/')[-1],
                'revision': delivery.revision,
                'corrector': delivery.student.corrector,
            })


class NewCourseView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """This is for creating a new course"""

    def get(self, request, course_id=None):
        courses = Course.objects.all()
        if course_id is not None:
            current_course = courses.get(pk=course_id)
        else:
            current_course = None
        
        form = CourseForm()
        return render(request, 'teachers/new_course.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
        })

    def post(self, request, course_id=None):
        courses = Course.objects.all()
        if course_id:
            current_course = courses.get(pk=course_id)
        else:
            current_course = None
        
        form = CourseForm(request.POST)
        if (form.is_valid()):
            form.save()
            return redirect('teachers:dashboard', course_id = form.instance.pk)

        return render(request, 'teachers/new_course.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
        })


class CoursesView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request):
        courses_list = Course.objects.all().order_by('-name')
        paginator = Paginator(courses_list, MAX_PAGINATOR_SIZE) # Show 25 courses per page
        page = request.GET.get('page')
        try:
            courses = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            courses = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            courses = paginator.page(paginator.num_pages)
        return render(request, 'teachers/courses.html', {"courses": courses},)


class EditCourseView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    """This is for editing an already existant course"""
        
    def get(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        course = current_course
        form = CourseForm(instance=course)
        return render(request, 'teachers/edit_course.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course': course
        })
        
    def post(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        course = current_course
        form = CourseForm(request.POST, instance=course)
        if (form.is_valid()):
            entity = form.save()
            return redirect('teachers:dashboard', course_id = course.pk)
        return render(request, 'teachers/edit_course.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course': course
        })



class DeliveryListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, assignment_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        assignment = Assignment.objects.get(pk=assignment_id)
        table_deliveries = []
        deliveries = Delivery.objects.filter(assignment=assignment).order_by('date')
        for delivery in deliveries:
            correction = Correction.objects.filter(delivery=delivery)
            table_deliveries.append({'delivery': delivery, 'correction': correction})
        return render(request, 'teachers/delivery_full_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'table_deliveries': table_deliveries,
            'assignment': assignment,
        })


class StudentsDeliveryListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, assignment_id, student_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        student = Student.objects.get(pk=student_id)
        assignment = Assignment.objects.get(pk=assignment_id)
        table_deliveries = []
        deliveries = Delivery.objects.filter(assignment=assignment,student__pk=student_id)
        for delivery in deliveries:
            table_deliveries.append({'delivery': delivery, 'correction': delivery.correction})
        return render(request, 'teachers/delivery_partial_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'student' : student,
            'table_deliveries': table_deliveries,
            'assignment': assignment,
        })


class DeliveryDownloadView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, delivery_id):
        delivery = Delivery.objects.get(pk=delivery_id)
        student = delivery.student
        assignment = delivery.assignment

        filename = '{assignment}_{student_uid}_{date}.zip'.format(
            assignment = assignment,
            student_uid = student.uid,
            date = delivery.date.isoformat(sep='T')
        )
        
        response = HttpResponse(delivery.file, content_type=DELIVERY_ACCEPTED_MIMETYPE)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


class DeliveryDetailView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, delivery_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        delivery = Delivery.objects.get(pk=delivery_id);
        correction = Correction.objects.filter(delivery=delivery)
        return render(request, 'teachers/delivery_detail.html', 
                      {'current_course' : current_course,
                       'courses' : courses,
                       'delivery': delivery, 'correction':correction})


# 'Private' method to load up the files that will be browseable.
# TODO: Rehacer esto... huele a que algo está complicado acá.
def walk_directory(files_list, path, relative_path):
    tuples = []
    for walk_tuple in os.walk(path):
        tuples.append(walk_tuple)
    
    (path, directories, filenames) = tuples[0]
    for filename in filenames:
        if(relative_path is None):
            files_list.append(filename)
        else:
            files_list.append(os.path.join(relative_path, filename))
    for directory in directories:
        if(relative_path is None):
            walk_directory(files_list, os.path.join(path, directory), directory)
        else:
            walk_directory(files_list, os.path.join(path, directory), os.path.join(relative_path, directory))


class DeliveryBrowseView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, delivery_id, file_to_browse):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        delivery = Delivery.objects.get(pk=delivery_id);
        extraction_dir = os.path.join(MEDIA_ROOT, BROWSE_DELIVERIES_PATH, str(delivery.pk))
        print("Accessing dir: ", extraction_dir)
        if (not os.path.exists(extraction_dir)):
            zipfile = ZipFile(delivery.file)
            zipfile.extractall(extraction_dir)
        
        files_list = []
        walk_directory(files_list, extraction_dir, None)
        
        if (file_to_browse is None):
            file_content = None
        else:
            # Y si es un pdf??? Arreglar esto.
            file_path = os.path.join(extraction_dir, file_to_browse)
            with open(file_path, 'r') as content_file:
                raw_content = content_file.read()
                utf8_content = raw_content.encode('utf8')
                file_content = raw_content
                #file_content = content_file.read().replace('\n', '\\n').encode('utf8')
        return render(request, 'teachers/delivery_browse.html', {
            'current_course' : current_course,
            'courses' : courses,
            'assignment': delivery.assignment,
            'delivery': delivery,
            'delivery_detail': delivery.file.name.split('/')[-1],
            'revision': delivery.revision,
            'files_list': files_list,
            'file_content': file_content,
        })


class DeliveryExploreView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, delivery_id):
        delivery = Delivery.objects.get(pk=delivery_id);

        browse_path = os.path.join(MEDIA_ROOT, BROWSE_DELIVERIES_PATH)

        if(os.path.exists(os.path.join(browse_path, str(delivery_id)))):
            shutil.rmtree(browse_path, str(delivery_id))

        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        extraction_dir = os.path.join(browse_path, str(delivery.pk))
        if (not os.path.exists(extraction_dir)):
            zipfile = ZipFile(delivery.file)
            zipfile.extractall(extraction_dir)
        
        files_list = []
        walk_directory(files_list, extraction_dir, None)

        file_content = None
        return render(request, 'teachers/delivery_browse.html', {
            'current_course' : current_course,
            'courses' : courses,
            'assignment': delivery.assignment,
            'delivery': delivery,
            'delivery_detail': delivery.file.name.split('/')[-1],
            'revision': delivery.revision,
            'files_list': files_list,
            'file_content': file_content,
        })


class DashboardView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id=None):
        courses = Course.objects.all()
        if course_id is None:
            try:
                current_course = courses.latest('pk')
            except:
                current_course = None
        else:
            current_course = courses.get(pk=course_id)
        table_contents = []
        for course in courses:
            table_contents.append({'pk': course.pk, 'name': course.name, 'count': course.get_student_count()})
        table_deliveries = []
        teacher = Teacher.objects.get(user=request.user) 
        students = Student.objects.filter(corrector=teacher)
        for student in students:
            deliveries = Delivery.objects.filter(student=student, assignment__course=current_course)
            for delivery in deliveries:
                correction = Correction.objects.filter(delivery=delivery)
                status = delivery.revision.status
                if (status == RevisionStatus.SUCCESSFUL.name):
                    table_deliveries.append({'delivery': delivery, 'correction':correction})
        return render(request, 'teachers/dashboard.html', {
            'current_course' : current_course,
            'courses' : courses,
            'table_contents': table_contents, 
            'table_deliveries': table_deliveries
        })


class NewAssignmentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    
    def get(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        form = AssignmentForm()
        return render(request, 'teachers/assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course_id': course_id,
        })
            
    def post(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        form = AssignmentForm(request.POST, request.FILES)
        if (form.is_valid()):
            assignment = form.save(commit = False)
            assignment.course = current_course
            assignment.save()
            return redirect('teachers:dashboard', course_id = course_id)
        return render(request, 'teachers/assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course_id': course_id,
        })

class EditAssignmentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    
    def get(self, request, course_id , assignment_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        assignment = Assignment.objects.get(pk=assignment_id)
        form = AssignmentForm(instance=assignment)
        return render(request, 'teachers/assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course_id': course_id,
        })
            
    def post(self, request, course_id , assignment_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        assignment = Assignment.objects.get(pk=assignment_id)
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if (form.is_valid()):
            assignment = form.save()
            return redirect('teachers:dashboard', course_id = course_id)
        return render(request, 'teachers/assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course_id': course_id,
        })


class UploadAssignmentsScriptView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id , assignment_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        assignment = Assignment.objects.get(pk=assignment_id)
        script = Script.objects.filter(assignment = assignment)
        script_text = ''
        if(script):
            script = script[0]
            form = AssignmentScriptForm(instance=script)
            script_file = open(os.path.join(MEDIA_ROOT, script.file.name), "r")
            try:
                script_text = script_file.read()
            except:
                script_text = _("File cannot be read. Is it text?")
            script_file.close()
        else:
            form = AssignmentScriptForm()
        return render(request, 'teachers/assignment_script.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'assignment': assignment,
            'course_id': course_id,
            'script': script,
            'script_text': script_text
        })

    def post(self, request, course_id , assignment_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        assignment = Assignment.objects.get(pk=assignment_id)
        script_text = ''
        if (Script.objects.filter(assignment=assignment).exists()):
            script_instance = Script.objects.get(assignment=assignment)
        else:
            script_instance = Script(assignment=assignment)
        form = AssignmentScriptForm(request.POST, request.FILES, instance=script_instance)
        if (form.is_valid()):
            form_edit = form.save()
            return redirect('teachers:assignment_script', course_id = course_id, assignment_id = assignment_id)
        return render(request, 'teachers/assignment_script.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'assignment': assignment,
            'course_id': course_id,
            'script_text': script_text
        })


class AssignmentsFilesListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id , assignment_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        assignment = Assignment.objects.get(pk = assignment_id)
        assignment_files = assignment.assignmentfile_set.all()
        form = AssignmentFileForm()
        return render(request, 'teachers/upload_assignment_file.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course_id':course_id,
            'assignment_name':assignment.uid,
            'assignment':assignment,
            'assignment_files': assignment_files
        })

    def post(self, request, course_id , assignment_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        assignment = Assignment.objects.get(pk = assignment_id)
        assignment_files = assignment.assignmentfile_set.all()
        assignment_file_instance = AssignmentFile(assignment=assignment)
        form = AssignmentFileForm(request.POST, request.FILES, instance=assignment_file_instance)
        if (form.is_valid()):
            form_edit = form.save()
            return redirect('teachers:assignment_files', course_id = course_id, assignment_id = assignment_id)

        return render(request, 'teachers/upload_assignment_file.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course_id':course_id,
            'assignment_name':assignment.uid,
            'assignment_files': assignment_files
        })


class AssignmentsFileDownloadView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, assignment_id, assignment_file_id):
        assignment_file = AssignmentFile.objects.get(pk=assignment_file_id)
        filename = assignment_file.file.name.split('/')[-1]
        response = HttpResponse(assignment_file.file)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


class AssignmentsFileDeleteView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, assignment_id, assignment_file_id):
        assignment_file = AssignmentFile.objects.get(pk=assignment_file_id)
        if not (int(course_id) == assignment_file.assignment.course.pk and int(assignment_id) == assignment_file.assignment.pk):
            return HttpResponseBadRequest()
        assignment_file.delete()
        return redirect('teachers:assignment_files', course_id = course_id, assignment_id = assignment_id)


class DeleteAssignmentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, assignment_id):
        assignment = Assignment.objects.get(pk=assignment_id)
        delivery_list = Delivery.objects.filter(assignment = assignment)
        if (delivery_list or course_id != assignment.course.pk):
            return HttpResponseBadRequest
        assignment.delete()
        return redirect('teachers:dashboard', course_id = course_id)



class NewShiftView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        courses = Course.objects.all()

        form = ShiftForm(initial={'course':course})
        return render(request, 'teachers/new_shift.html', {
            'current_course': course,
            'courses': courses,
            'form': form,
            'course_id':course_id
        })


    def post(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        courses = Course.objects.all()

        course = Course.objects.get(pk = course_id)
        shift = Shift(course = course)
        form = ShiftForm(request.POST, instance = shift)
        if (form.is_valid()):
            shift.save()
            return redirect('teachers:dashboard', course_id = course_id)
        return render(request, 'teachers/new_shift.html', {
            'current_course': course,
            'courses': courses,
            'form': form,
            'course_id':course_id
        })


class EditShiftView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, shift_id):
        course = Course.objects.get(pk=course_id)
        courses = Course.objects.all()
        
        shift = Shift.objects.get(pk=shift_id)
        if (int(course_id) != shift.course.pk):
            return HttpResponseBadRequest()

        form = ShiftForm(instance = shift)
        return render(request, 'teachers/edit_shift.html', {
            'current_course': course,
            'courses': courses,
            'shift': shift,
            'form': form,
            'course_id':shift.course.id
        })

    def post(self, request, course_id, shift_id):
        course = Course.objects.get(pk=course_id)
        courses = Course.objects.all()

        course = Course.objects.get(pk = course_id)
        shift = Shift.objects.filter(course = course)
        if ((not shift.exists()) or int(course_id) != shift[0].course.pk):
            return HttpResponseBadRequest()
        shift = shift[0]
        form = ShiftForm(request.POST, instance = shift)
        if (form.is_valid()):
            shift.save()
            return redirect('teachers:dashboard', course_id = course_id)
        return render(request, 'teachers/edit_shift.html', {
            'current_course': course,
            'courses': courses,
            'shift': shift,
            'form': form,
            'course_id':shift.course.id
        })


class DeleteShiftView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, shift_id):
        shift = Shift.objects.get(pk=shift_id)
        list_student = shift.get_students()
        if (list_student or course_id != shift.course.pk):
            return HttpResponseBadRequest
        shift.delete()
        return redirect('teachers:dashboard', course_id = course_id)


class StudentsFullListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
        
    def get(self, request):
        student_list = Student.objects.all().order_by('uid')
        paginator = Paginator(student_list, MAX_PAGINATOR_SIZE) # Show 10 students per page
        page = request.GET.get('page')
        try:
            students = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            students = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            students = paginator.page(paginator.num_pages)
        return render('students.html', {"students": students})


class StudentsCourseListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        students = Student.objects.filter(shifts__course = current_course).order_by('uid')
        listable_students = []
        for student in students:
            student_dict = {'pk' : student.pk,
                            'uid' : student.uid,
                            'full_name' : student.get_full_name(),
                            'email' : student.user.email,
                            'shift' : student.get_shift(current_course),}
            if student.corrector is not None:
                student_dict.update({'corrector' : student.corrector.user.last_name})
            listable_students.append(student_dict)
        return render(request, 'teachers/student_list.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'students': listable_students
        })


class StudentsShiftListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, shift_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        shift = Shift.objects.get(pk = shift_id)
        students = shift.student_set.order_by('uid')
        listable_students = []
        for student in students:
            student_dict = {'pk' : student.pk,
                            'uid' : student.uid,
                            'full_name' : student.get_full_name(),
                            'email' : student.user.email,
                            'shift' : student.get_shift(current_course),}
            if student.corrector is not None:
                student_dict.update({'corrector' : student.corrector.user.last_name})
            listable_students.append(student_dict)
        return render(request, 'teachers/student_list.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'shift' : shift,
            'students': listable_students
        })


class StudentDetailView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, student_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        student = Student.objects.get(pk=student_id)
        return render(request, 'teachers/student_detail.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'student': student,
        })


class NewStudentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, shift_id=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        form = StudentForm(initial={'shifts': [shift_id]})
        return render(request, 'teachers/new_student.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'shift_id': shift_id
        })

    def post(self, request, course_id, shift_id=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        form = StudentForm(request.POST)
        if (form.is_valid()):
            user = User.objects.create(
                username = form.data['uid'],
                email = form.data['email'],
                first_name = form.data['first_name'],
                last_name = form.data['last_name'],
            )
            user.set_password(form.data['passwd'])
            user.save()

            form.instance.user = user
            form.save()
            
            mail = Mail()
            mail = Mail.objects.create(
                    subject = STUDENT_CREATION_MAIL_SUBJECT,
                    body = STUDENT_CREATION_MAIL_BODY.format(
                            username = user.username,
                            password = form.data['passwd'],
                        ),
                    recipient = user.email,
                    reply_address = STUDENT_CREATION_MAIL_REPLY_ADDRESS,
                )
            student = Student.objects.get(uid=user.username)
            return redirect('teachers:student_detail', course_id = course_id, student_id = student.pk)
        return render(request, 'teachers/new_student.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'shift_id': shift_id,
        })


class EditStudentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, student_id, shift_id=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        student = Student.objects.get(pk=student_id)
        form = StudentForm(
            instance=student,
            initial={'email': student.user.email, 'first_name': student.user.first_name, 'last_name': student.user.last_name}
        )
        return render(request, 'teachers/edit_student.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'shift_id': shift_id
        })

    def post(self, request, course_id, student_id, shift_id=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        student = Student.objects.get(pk=student_id)     
        form = StudentForm(request.POST, instance=student,
                           initial={'email': student.user.email, 'first_name': student.user.first_name, 'last_name': student.user.last_name})
        
        if (form.is_valid()):
            if (form.data['passwd'] != ''):
                student.user.set_password(form.data['passwd'])
            student.user.email = form.data['email']
            student.user.first_name = form.data['first_name']
            student.user.last_name = form.data['last_name']
            student.user.save()
            form.save()
            return redirect('teachers:student_detail', course_id = course_id, student_id = student.pk)
        return render(request, 'teachers/edit_student.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'shift_id': shift_id
        })


class EditUnenrolledStudentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, student_id):
        student = Student.objects.get(pk=student_id)     
        form = StudentForm(instance=student)
        return render(request, 'teachers/student/editstudent.html', {'form': form})

    def get(self, request, student_id):
        student = Student.objects.get(pk=student_id)     
        form = StudentForm(request.POST, instance=student)
        if (form.is_valid()):
            form.save()
            return redirect('teachers:students', course_id = None)
        return render(request, 'teachers/student/editstudent.html', {'form': form})


class PendingDeliveriesListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        final_list = []
        assignments = current_course.assignments.all()
        shifts = Shift.objects.filter(course=current_course)
        #para cada Assignment del curso...
        for assignment in assignments:
            student_shift_list = []
            #recorro los turnos de donde voy a sacar los alumnos
            for shift in shifts:
                students = shift.get_students()
                #para cada alumno...
                for student in students:
                    #cuento las entregas satisfactorias del estudiante para la Assignment que estoy analizando.
                    successfull_deliveries = Delivery.objects.filter(student=student, assignment=assignment, revision__status = 1).count()
                    if (successfull_deliveries==0):
                        student_shift_list.append({'student': student, 'shift':shift})
            if len(student_shift_list) > 0:
                final_list.append({'assignment': assignment, 'student_shift_list':student_shift_list})            
        return render(request, 'teachers/pending_deliveries.html', {
            'current_course' : current_course,
            'courses' : courses,
            'final_list': final_list
        })



class StudentsDeliveriesListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, student_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        student = Student.objects.get(pk=student_id)
        deliveries = Delivery.objects.filter(student=student, assignment__course=current_course).order_by('date')
        table_deliveries = []
        for delivery in deliveries:
            correction = Correction.objects.filter(delivery=delivery)
            table_deliveries.append({'delivery': delivery, 'correction':correction})
        return render(request, 'teachers/student_deliveries.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'table_deliveries': table_deliveries,
            'student':student
        })



class StudentSearchView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        form = StudentSearchForm()
        students = []
        return render(request,'teachers/student_search.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'query': data,
            'students': students
        })

    def post(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        students = []
        form = StudentSearchForm(request.POST)
        data = form.data['data_search']
        students = Student.objects.filter(Q(uid__icontains = data) | Q(user__first_name__icontains = data) | 
                                              Q(user__last_name__icontains = data))
        return render(request,'teachers/student_search.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'query': data,
            'students': students
        })



class ListSuscriptionsView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id, shift_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        shift = Shift.objects.get(pk=shift_id)
        suscriptions = Suscription.objects.filter(shift=shift, state="Pending").order_by('suscription_date')
        suscriptions_solve = Suscription.objects.filter(shift=shift).order_by('suscription_date')
        suscriptions_solve = suscriptions_solve.exclude(state="Pending")
        return render(request, 'teachers/suscription_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'suscriptions': suscriptions,
            'suscriptions_solve': suscriptions_solve,
            'shift': shift
        })


class AcceptBatchSuscriptionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def post(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        suscription_list = request.POST.getlist('suscription')
        for suscrip_id in suscription_list:
            suscription = Suscription.objects.get(pk=suscrip_id)
            suscription.state = "Accept"
            suscription.resolveDate = date.today()
            suscription.save()
            student = Student.objects.get(pk=suscription.student.pk)
            student.shifts.add(suscription.shift)
        return redirect('teachers:pending_suscriptions', course_id)

class RejectBatchSuscriptionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def post(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)
        
        suscription_list = request.POST.getlist('suscription')
        for suscrip_id in suscription_list:
            suscription = Suscription.objects.get(pk=suscrip_id)
            suscription.state = "Reject"
            suscription.resolveDate = date.today()
            suscription.save()
        return redirect('teachers:pending_suscriptions', course_id)

class ListPendingSuscriptionsView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(self, request, course_id):
        courses = Course.objects.all()
        current_course = courses.get(pk=course_id)

        shifts = Shift.objects.filter(course = current_course)
        table_suscription_shift = []
        for shift in shifts:
            suscriptionPending = shift.suscription_set.filter(state='pending')
            if suscriptionPending:
                table_suscription_shift.append({'shift':shift, 'suscriptionPending':suscriptionPending})
        
        suscriptions = Suscription.objects.filter(shift__course=current_course, state="Pending").order_by('suscription_date')
        suscriptions_solve = Suscription.objects.filter(shift__course=current_course).order_by('suscription_date')
        suscriptions_solve = suscriptions_solve.exclude(state="Pending")
        
        return render(request, 'teachers/pending_suscription_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'table_suscription_shift': table_suscription_shift,
            'suscriptions': suscriptions,
            'suscriptions_solve': suscriptions_solve
        })

