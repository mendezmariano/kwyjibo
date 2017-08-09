from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.exceptions import BadRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect

from zipfile import ZipFile

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
            'automatic_correction': automatic_correction, 'assignment': delivery.assignment
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
                    subject = CORRECTION_NOTIFICATION_MAIL_SUBJECT,
                    body = CORRECTION_NOTIFICATION_MAIL_BODY.fromat(
                        assignment = correction.delivery.assignment.uid,
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
            entity = form.save()
            return redirect('teachers:dashboard', id_course = course.pk)
        return render(request, 'course_edit.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'course': course
        })



class DeliveryListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idassignment):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        assignment = Assignment.objects.get(pk=idassignment)
        table_deliveries = []
        deliveries = Delivery.objects.filter(assignment=assignment).order_by('date')
        for delivery in deliveries:
            table_deliveries.append({'delivery': delivery, 'correction': delivery.correction})
        return render(request, 'delivery_full_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'table_deliveries': table_deliveries,
            'assignment': assignment,
        })


class StudentsAndAssignmentDeliveryListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idassignment, idstudent):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        student = Student.objects.get(pk=idstudent)
        assignment = Assignment.objects.get(pk=idassignment)
        table_deliveries = []
        deliveries = Delivery.objects.filter(assignment=assignment,student__pk=idstudent)
        for delivery in deliveries:
            table_deliveries.append({'delivery': delivery, 'correction': delivery.correction})
        return render(request, 'delivery_partial_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'student' : student,
            'table_deliveries': table_deliveries,
            'assignment': assignment,
        })


class DeliveryDetailView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, iddelivery):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        delivery = Delivery.objects.get(pk=iddelivery);
        correction = Correction.objects.filter(delivery=delivery)
        return render(request, 'delivery_detail.html', 
                      {'current_course' : current_course,
                       'courses' : courses,
                       'delivery': delivery, 'correction':correction})



class DeliveryDownloadView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, id_delivery):
        delivery = Delivery.objects.get(pk=id_delivery)
        student = delivery.student
        assignment = delivery.assignment

        filename = '{assignment}_{student_uid}_{date}.zip'.format(
            assignment = assignment,
            student_uid = student.uid,
            date = delivery.date.isoformat(sep='T', timespec='seconds')
        )
        
        response = HttpResponse(delivery.file, content_type=DELIVERY_ACCEPTED_MIMETYPE)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


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

    def get(request, idcourse, iddelivery, file_to_browse=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        delivery = Delivery.objects.get(pk=iddelivery);
        extraction_dir = os.path.join(BROWSE_DELIVERIES_PATH, str(delivery.pk))
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
                file_content = content_file.read()
        return render(request, 'delivery_browse.html', {
            'current_course' : current_course,
            'courses' : courses,
            'delivery': delivery,
            'files_list': files_list,
            'file_content': file_content,
        })


class HomeView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse=None):
        courses = Course.objects.all()
        if idcourse is None:
            try:
                current_course = courses.latest('pk')
            except:
                current_course = None
        else:
            current_course = courses.get(pk=idcourse)
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
                status = delivery.get_automatic_correction().get_status()
                if (status == "successfull"):
                    table_deliveries.append({'delivery': delivery, 'correction':correction})
        return render(request, 'dashboard.html', {
            'current_course' : current_course,
            'courses' : courses,
            'table_contents': table_contents, 
            'table_deliveries': table_deliveries
        })


class NewAssignmentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    
    def get(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        form = AssignmentForm()
        return render(request, 'assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idcourse': idcourse,
        })
            
    def post(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        form = AssignmentForm(request.POST, request.FILES)
        if (form.is_valid()):
            assignment = form.save(commit = False)
            assignment.course = current_course
            assignment.save()
            return redirect('teachers:dashboard', id_course = idcourse)
        return render(request, 'assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idcourse': idcourse,
        })

class EditAssignmentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
    
    def get(request, idcourse , idassignment):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        assignment = Assignment.objects.get(pk=idassignment)
        form = AssignmentForm(instance=assignment)
        return render(request, 'assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idcourse': idcourse,
        })
            
    def post(request, idcourse , idassignment):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        assignment = Assignment.objects.get(pk=idassignment)
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if (form.is_valid()):
            assignment = form.save()
            return redirect('teachers:dashboard', id_course = idcourse)
        return render(request, 'assignment.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idcourse': idcourse,
        })


class UploadAssignmentsScriptView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse , idassignment):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        assignment = Assignment.objects.get(pk=idassignment)
        script_text = ''
        if(assignment.get_script()):
            form = AssignmentScriptForm(instance=assignment.get_script())
            script_file = open(assignment.get_script().file.name, "r")
            script_text = script_file.read()
            script_file.close()
        else:
            form = AssignmentScriptForm()
        return render(request, 'assignment_script.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'assignment': assignment,
            'idcourse': idcourse,
            'script_text': script_text
        })

    def post(request, idcourse , idassignment):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        assignment = Assignment.objects.get(pk=idassignment)
        script_text = ''
        if (Script.objects.filter(assignment=assignment).exists()):
            script_instance = Script.objects.get(assignment=assignment)
        else:
            script_instance = Script(assignment=assignment)
        form = AssignmentScriptForm(request.POST, request.FILES, instance=script_instance)
        if (form.is_valid()):
            form_edit = form.save()
            return redirect('teachers:assignment_script', id_course = idcourse, idassignment = idassignment)
        return render(request, 'assignment_script.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'assignment': assignment,
            'idcourse': idcourse,
            'script_text': script_text
        })


class AssignmentsFilesListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse , idassignment):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        assignment = Practice.objects.get(pk = idassignment)
        assignmentFiles = assignment.get_assignment_file()
        form = AssignmentFileForm()
        return render(request, 'assignment/uploadFile.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idcourse':idcourse,
            'assignment_name':assignment.uid,
            'assignmentFiles': assignmentFiles
        })

    def post(request, idcourse , idassignment):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        assignment = Practice.objects.get(pk = idassignment)
        assignmentFiles = assignment.get_assignment_file()
        assignment_file_instance = AssignmentFile(assignment=assignment)
        form = AssignmentFileForm(request.POST, request.FILES, instance=assignment_file_instance)
        if (form.is_valid()):
            form_edit = form.save()
            return redirect('teachers:assignment_files', id_course = idcourse, idassignment = idassignment)

        return render(request, 'assignment/uploadFile.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idcourse':idcourse,
            'assignment_name':assignment.uid,
            'assignmentFiles': assignmentFiles
        })


class AssignmentsFileDeleteView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idassignment, id_assignment_file):
        assignment_file = AssignmentFile.objects.get(pk=id_assignment_file)
        if not (idcourse == assignment_file.assignment.course.pk and idassignment == assignment_file.assignment):
            raise BadRequest()
        assignment_file.delete()
        return redirect('teachers:assignment_files', id_course = idcourse, idassignment = idassignment)


class DeleteAssignmentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idassignment):
        assignment = Practice.objects.get(pk=idassignment)
        delivery_list = Delivery.objects.filter(assignment = assignment)
        if (delivery_list or idcourse != assignment.course.pk):
            raise BadRequest()
        assignment.delete()
        return redirect('teachers:dashboard', id_course = idcourse)



class NewShiftView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse):
        course = Course.objects.get(pk=idcourse)
        courses = Course.objects.all()

        form = ShiftForm(initial={'course':course})
        return render(request, 'shift_new.html', {
            'current_course': course,
            'courses': courses,
            'form': form,
            'idcourse':idcourse
        })


    def post(request, idcourse):
        course = Course.objects.get(pk=idcourse)
        courses = Course.objects.all()

        course = Course.objects.get(pk = idcourse)
        shift = Shift(course = course)
        form = ShiftForm(request.POST, instance = shift)
        if (form.is_valid()):
            shift.save()
            return redirect('teachers:dashboard', id_course = idcourse)
        return render(request, 'shift_new.html', {
            'current_course': course,
            'courses': courses,
            'form': form,
            'idcourse':idcourse
        })


class EditShiftView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idshift):
        course = Course.objects.get(pk=idcourse)
        courses = Course.objects.all()
        
        shift = Shift.objects.get(pk=idshift)
        if (idcourse != shift.course.pk):
            raise BadRequest()

        form = ShiftForm(instance = shift)
        return render(request, 'shift_edit.html', {
            'current_course': course,
            'courses': courses,
            'shift': shift,
            'form': form,
            'idcourse':shift.course.id
        })

    def post(request, idcourse, idshift):
        course = Course.objects.get(pk=idcourse)
        courses = Course.objects.all()

        course = Course.objects.get(pk = idcourse)
        shift = Shift(course = course)
        if (idcourse != shift.course.pk):
            raise BadRequest()

        form = ShiftForm(request.POST, instance = shift)
        if (form.is_valid()):
            shift.save()
            return redirect('teachers:dashboard', id_course = idcourse)
        return render(request, 'shift_edit.html', {
            'current_course': course,
            'courses': courses,
            'shift': shift,
            'form': form,
            'idcourse':shift.course.id
        })


class DeleteShiftView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idshift):
        shift = Shift.objects.get(pk=idshift)
        list_student = shift.get_students()
        if (list_student or idcourse != shift.course.pk):
            raise BadRequest()
        shift.delete()
        return redirect('teachers:dashboard', id_course = idcourse)


class StudentsFullListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):
        
    def get(request):
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

    def get(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

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
        return render(request, 'student_list.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'students': listable_students
        })


class StudentsShiftListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idshift):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        shift = Shift.objects.get(pk = idshift)
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
        return render(request, 'student_list.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'shift' : shift,
            'students': listable_students
        })



class StudentDetailView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idstudent):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        student = Student.objects.get(pk=idstudent)
        return render(request, 'student_detail.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'student': student,
        })


class NewStudentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idshift=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        form = StudentForm(initial={'shifts': [idshift]})
        return render(request, 'student_new.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idshift': idshift
        })

    def post(request, idcourse, idshift=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        form = StudentForm(request.POST)
        if (form.is_valid()):
            user = User.objects.create(
                username = form.data['username'],
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
                    body = STUDENT_CREATION_MAIL_BODY.fromat(
                            username = user.username,
                            password = form.data['passwd'],
                        ),
                    recipient = user.email,
                    reply_address = STUDENT_CREATION_MAIL_REPLY_ADDRESS,
                )
            student = Student.objects.get(uid=user.username)
            return redirect('teachers:student_detail', id_course = idcourse, idstudent = student.pk)
        return render(request, 'student_new.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idshift': idshift,
        })


class EditStudentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idstudent, idshift=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        student = Student.objects.get(pk=idstudent)
        form = StudentForm(instance=student, initial={'email': student.user.email, 'first_name': student.user.first_name, 'last_name': student.user.last_name})
        return render(request, 'student_edit.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idshift': idshift
        })

    def get(request, idcourse, idstudent, idshift=None):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        student = Student.objects.get(pk=idstudent)     
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
            return redirect('teachers:student_detail', id_course = idcourse, idstudent = student.pk)
        return render(request, 'student_edit.html', {
            'current_course' : current_course,
            'courses' : courses,
            'form': form,
            'idshift': idshift
        })


class EditUnenrolledStudentView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idstudent):
        student = Student.objects.get(pk=idstudent)     
        form = StudentForm(instance=student)
        return render(request, 'student/editstudent.html', {'form': form})

    def get(request, idstudent):
        student = Student.objects.get(pk=idstudent)     
        form = StudentForm(request.POST, instance=student)
        if (form.is_valid()):
            form.save()
            return redirect('teachers:students', id_course = None)
        return render(request, 'student/editstudent.html', {'form': form})


class PendingDeliveriesListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def pendingdeliveries(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        final_list = []
        practices = current_course.get_practices()
        shifts = Shift.objects.filter(course=current_course)
        #para cada Practice del curso...
        for practice in practices:
            student_shift_list = []
            #recorro los turnos de donde voy a sacar los alumnos
            for shift in shifts:
                students = shift.get_students()
                #para cada alumno...
                for student in students:
                    #cuento las entregas satisfactorias del estudiante para la Practice que estoy analizando.
                    successfull_deliveries = Delivery.objects.filter(student=student, practice=practice, automaticcorrection__status = 1).count()
                    if (successfull_deliveries==0):
                        student_shift_list.append({'student': student, 'shift':shift})
            if len(student_shift_list) > 0:
                final_list.append({'practice': practice, 'student_shift_list':student_shift_list})            
        return render(request, 'pending_deliveries.html', {
            'current_course' : current_course,
            'courses' : courses,
            'final_list': final_list
        })



class StudentsDeliveriesListView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idstudent):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        student = Student.objects.get(pk=idstudent)
        deliveries = Delivery.objects.filter(student=student, practice__course=current_course).order_by('deliverDate', 'deliverTime')
        table_deliveries = []
        for delivery in deliveries:
            correction = Correction.objects.filter(delivery=delivery)
            table_deliveries.append({'delivery': delivery, 'correction':correction})
        return render(request, 'student_deliveries.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'table_deliveries': table_deliveries,
            'student':student
        })



class StudentSearchView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        form = StudentSearchForm()
        students = []
        return render(request,'student_search.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'query': data,
            'students': students
        })

    def post(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        students = []
        form = StudentSearchForm(request.POST)
        data = form.data['data_search']
        students = Student.objects.filter(Q(uid__icontains = data) | Q(user__first_name__icontains = data) | 
                                              Q(user__last_name__icontains = data))
        return render(request,'student_search.html', {
            'current_course' : current_course,
            'courses' : courses, 
            'query': data,
            'students': students
        })



class ListSuscriptionsView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse, idshift):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        shift = Shift.objects.get(pk=idshift)
        suscriptions = Suscription.objects.filter(shift=shift, state="Pending").order_by('suscriptionDate')
        suscriptions_solve = Suscription.objects.filter(shift=shift).order_by('suscriptionDate')
        suscriptions_solve = suscriptions_solve.exclude(state="Pending")
        return render(request, 'suscription_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'suscriptions': suscriptions,
            'suscriptionsSolve': suscriptions_solve,
            'shift': shift
        })


class AcceptBatchSuscriptionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def post(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        suscription_list = request.POST.getlist('suscription')
        for suscrip_id in suscription_list:
            suscription = Suscription.objects.get(pk=suscrip_id)
            suscription.state = "Accept"
            suscription.resolveDate = date.today()
            suscription.save()
            student = Student.objects.get(pk=suscription.student.pk)
            student.shifts.add(suscription.shift)
        return redirect('teachers:pending_suscriptions', idcourse)

class RejectBatchSuscriptionView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def post(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)
        
        suscription_list = request.POST.getlist('suscription')
        for suscrip_id in suscription_list:
            suscription = Suscription.objects.get(pk=suscrip_id)
            suscription.state = "Reject"
            suscription.resolveDate = date.today()
            suscription.save()
        return redirect('teachers:pending_suscriptions', idcourse)

class ListPendingSuscriptionsView(LoginRequiredMixin, UserHasTeacherAccessLevel, View):

    def get(request, idcourse):
        courses = Course.objects.all()
        current_course = courses.get(pk=idcourse)

        shifts = Shift.objects.filter(course = current_course)
        table_suscription_shift = []
        for shift in shifts:
            suscriptionPending = shift.suscription_set.filter(state='pending')
            if suscriptionPending:
                table_suscription_shift.append({'shift':shift, 'suscriptionPending':suscriptionPending})
        
        suscriptions = Suscription.objects.filter(shift__course=current_course, state="Pending").order_by('suscriptionDate')
        suscriptions_solve = Suscription.objects.filter(shift__course=current_course).order_by('suscriptionDate')
        suscriptions_solve = suscriptions_solve.exclude(state="Pending")
        
        return render(request, 'pending_suscription_list.html', {
            'current_course' : current_course,
            'courses' : courses,
            'table_suscription_shift': table_suscription_shift,
            'suscriptions': suscriptions,
            'suscriptionsSolve': suscriptions_solve
        })
        
        