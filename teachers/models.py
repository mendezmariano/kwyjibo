import mimetypes

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from _utils.models import ChoiceEnum

from kwyjibo.settings import *

# Constants
TYPE_EDITABLE = 'text'

MSG_EXEPTION = 'Teacher cannot be saved without an authentication register.\
                Please, give the teacher an associated user so he can login.'

# Create your models here.

class Teacher(models.Model):
    """
    
    Professors or Teachers who dictates the lectures and grade the Students' 
    work are the target class of this application. They are in charge of 
    creating the assignments, evaluating them and giving feedback to the 
    Students who take their course. This is one of the profiles considered by 
    this application. For the purpouse of authentication, a User, from the 
    django.auth module is associated with them, granting them a username and
    password to login to the site.
    
    """
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    rank = models.CharField(_('Rank'), max_length = 50)
    
    def __str__(self):
        """Stringify the Teacher"""
        return "{last_name}, {first_name}".format(last_name = self.user.last_name, first_name = self.user.first_name)
    
    def save(self, force_insert=False, force_update=False, using=None):
        """Extends parent. Checks for the existance of the login user"""
        if(self.user is None):
            raise Exception(msg=MSG_EXEPTION)
        models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using)
        
    def get_full_name(self):
        return self.user.first_name + " " + self.user.last_name


class Course(models.Model):
    """Course class representing a term
    
    The Course is understood as the series of lessons in the subject which sums
    up to be the whole content expected to be aquired by the students during
    their learning. It is concibed to last for one term (year, semester, etc)
    
    """
    
    name = models.CharField(max_length = 32, unique=True)
    
    def __str__(self):
        """Stringify the Course"""
        return self.name
    
    def student_count(self):
        shifts_query_set = self.shift_set.all()
        count = 0
        for shift in shifts_query_set:
            count += shift.student_set.all().count()
        return count
    
    def get_student_count(self):
        shifts = self.shift_set.all()
        total = 0;
        for shift in shifts:
            total = total + shift.student_set.count()
        return total
    
    def add_student(self, student):
        self.student_set.add(student)
    
    def remove_student(self, student):
        self.student_set.remove(student)
    
    def get_assignments(self):
        return self.assignment_set.all()
    
    class Meta:
        """
        Meta class to indicate the expected ordering of this objects when 
        querying on this class.
        """
        ordering = ('-name',)


class Shift(models.Model):
    """
    Within a Course, an agroupation of studentes that might not share the day
    of the week, the classroom or the teachers.
    """
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    class Meta:
        """Metadata class indicating how this objects must be unique"""
        unique_together = (("name", "course"),)
    
    def __str__(self):
        """Stringify the Course"""
        return "{course}-{shift}".format(course = self.course.name, shift = self.name)
    
    def get_students(self, uid=None, name=None, email=None):
        partial_query = self.student_set.all()
        if(uid):
            partial_query = partial_query.filter(uid=uid)
        if(name):
            partial_query = partial_query.filter(name=name)
        if(email):
            partial_query = partial_query.filter(email=email)
        return partial_query

    def get_students_count(self):
        return (self.student_set.count())
    
    def remove_student(self, student):
        self.student_set.remove(student)


class Assignment(models.Model):
    """Assignment.
    
    This class, probably poorly named, represents the assignments given to the
    Students to do in order to pass the Course.
    
    """
    
    uid = models.CharField(_('Name'), max_length=32)
    course = models.ForeignKey(Course, related_name='assignments')
    deadline = models.DateField()
    blocker = models.BooleanField()
    
    class Meta:
        """Metadata class indicating how this objects must be unique"""
        unique_together = (("uid", "course"),)
    
    def __str__(self):
        """Stringify the Assignment or assignment"""
        return self.uid
    
    def is_expired(self):
        if ((self.deadline < date.today()) and self.blocker):
            return True
        else:
            return False

    def get_successfull_deliveries_count(self):
        return self.delivery_set.filter(revision__status = RevisionStatus.SUCCESSFUL, assignment = self).count()

    def get_failed_deliveries_count(self):
        #return self.delivery_set.filter(~Q(revision__status = RevisionStatus.SUCCESSFUL), assignment = self).count()
        return self.delivery_set.filter(revision__status = RevisionStatus.FAILED, assignment = self).count()

    def get_students_pending_deliveries_count(self):
        students = Student.objects.filter(shifts__course = self.course).count()
        students_delivery_succesfull = Student.objects.filter(delivery__revision__status = RevisionStatus.SUCCESSFUL, delivery__assignment = self).distinct().count()
        return students - students_delivery_succesfull
        
    # for the dashboard view
    def get_completion_percentage(self):
        deliveries_queryset = self.delivery_set.filter(revision__status = RevisionStatus.SUCCESSFUL, assignment = self).all()
        print(deliveries_queryset)
        students = []
        for delivery in deliveries_queryset:
            if delivery.student.pk not in students:
                students.append(delivery.student.pk)
        print(students)
        shifts = self.course.shift_set.all()
        total_students = 0
        for shift in shifts:
            total_students += shift.student_set.all().count()
        print("{successfull} / {total}".format(successfull = len(students), total = total_students))
        print("percentage: {percent}".format(percent = 100 * len(students) / total_students))
        if total_students == 0:
            return 0
        return 100 * len(students) / total_students
        
    def get_remaining_percentage(self):
        return 100 - self.get_completion_percentage()
    
    def count_deliveries(self):
        return self.delivery_set.count()


class AssignmentFile(models.Model):
    """
    
    This class is the holder for the assignment file associated with each assignment.
    
    """
    assignment = models.ForeignKey(Assignment)
    name =  models.CharField(max_length=32)
    file = models.FileField(upload_to = ASSIGNMENT_FILES_PATH)
    
    def __str__(self):
        """Stringify the Assignment or assignment"""
        return (str(self.name))


    def isEditable(self):
        mime = str(mimetypes.guess_type(self.file.name)[0])
        pos = mime.find(TYPE_EDITABLE)
        if (pos == 0):
            return True
        return False


class Script(models.Model):
    """
    
    This class is the holder for the scripts associated with each assignment that
    will be run to check the deliveries in an automatic way.
    
    """
    
    assignment = models.OneToOneField(Assignment, on_delete=models.CASCADE)
    file = models.FileField(upload_to = SCRIPT_FILES_PATH, max_length=128)

    def __str__(self):
        return "script for assignment {assignment}".format(assignment = str(self.assignment))


class Student(models.Model):
    """
    
    The Students are the people, undergraduates, who are taking a course and
    aim to pass the subject. This is one of the main entities of this software.
    They are supposed to register and apply to be enrolled in the Course they
    are taking. Once accepted, they can see their assignments, download their
    descriptions. Once they have solved them, they will perform a Delivery and
    expect the corresponding feedback or Correction.
    
    For the purpouse of authentication, a User, from the django.auth module is
    associated with them, granting them a username and password to login to the
    site.
    
    """
    
    uid = models.CharField(unique=True, max_length = 32,verbose_name=_("Padron"))
    shifts = models.ManyToManyField(Shift, blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    corrector = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        """Stringify the Student"""
        return self.uid
    
    def get_full_name(self):
        return "{first_name} {last_name}".format(first_name = self.user.first_name, last_name = self.user.last_name)

    def first_name(self):
        return self.user.first_name
    
    def last_name(self):
        return self.user.last_name

    def get_shift(self, course):
        for shift in self.shifts.all():
            if shift.course == course:
                return shift


class Suscription(models.Model):
    """
    
    The Subscriptions are actually the reflection of the action, performed by a
    Student, of applying to be enrrolled to a given Course. It is not the 
    enrollement, only the request to be accepted. It can either be aproved or
    discarded.
    
    """
    
    shift = models.ForeignKey(Shift)
    student = models.ForeignKey(Student)
    state = models.CharField(max_length = 32)
    suscription_date = models.DateField(default = timezone.now)
    resolve_date = models.DateField(null=True)
    
    def __str__(self):
        """Stringify the Suscription"""
        return _("{id} - Suscription to {shift} of {student}").format(id = self.pk, shift = self.shift, student = self.student)


class Delivery(models.Model):
    """Delivery class.
    
    It is the object or artifact that the Student presents as his work for a
    given assignment. In this case it is considered required to be a zip 
    package.
     
    """
    file = models.FileField( upload_to = DELIVERY_FILES_PATH)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    date = models.DateTimeField(default = timezone.now)
    corrector = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        """Stringify the Delivery"""
        return (str(self.assignment) + " - " + str(self.student) + " - " + str(self.date))
    
    def full_date(self):
        return self.date.strftime('%Y-%m-%d %H:%M:%S')
    
    class Meta:
        ordering = ('-date', )



class Correction(models.Model):
    """Correction or grade granted. 
    
    It is the grade granted by the Teacher to the Student and a comment giving
    feedback for the Delivery made by the latter.
    """
    
    feedback = models.TextField(_('Feedback'), max_length=2000)
    comments = models.TextField(_('Comments'), max_length=2000)
    grade = models.DecimalField(_('Grade'), max_digits=4, decimal_places=2, default=Decimal(0.00))
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE)
    corrector = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        """Stringify the Correction"""
        return ("Grade: " + str(self.grade) + " - Public Comment: " + self.feedback)


class RevisionStatus(ChoiceEnum):
    """docstring for RevisionStatus"""

    PENDING = 'PENDING'
    FAILED = 'FAILED'
    SUCCESSFUL = 'SUCCESSFUL'
    UNKNOWN = 'UNKNOWN'


    _BADGES = {
        'PENDING': 'label-warning',
        'FAILED': 'label-important',
        'SUCCESSFUL': 'label-success',
        'UNKNOWN': 'label-important'
    }

    def __str__(self):
        return self.name

    def get_label(self):
        return _(self.name.lower())

    def get_badge(self):
        return RevisionStatus._BADGES[self];


class Revision(models.Model):
    """    
    Revision objects are the entities which represents the automatic check that
    Kwyjibo can run on the deliveries made by the Students/Undergraduates.
    """
    
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name='revision')
    captured_stdout = models.CharField(max_length=10240, blank=True)
    exit_value = models.IntegerField(default=0)
    status = models.CharField(
        _('Status'),
        max_length=16,
        choices=RevisionStatus.choices(),
        default=RevisionStatus.PENDING,
    )


    def __str__(self):
        """Stringify the Revision"""
        # return ("Revision | exit value: " + str(self.exit_value) + " - status: " + str(self.status))
        return _("Revision | exit value: {exit_value} - status: {status}").format(exit_value = self.exit_value, status = self.status)

    def get_status(self):
        """Returns a status raw value as a human readable value"""
        return self.status.get_label()

    def status_label(self):
        """Returns a status raw value as a human readable value"""
        return _(self.status.lower())

    _BADGES = {
        'PENDING': 'label-warning',
        'FAILED': 'label-important',
        'SUCCESSFUL': 'label-success',
        'UNKNOWN': 'label-important'
    }
    def status_badge_style(self):
        """Returns a status raw value as a human readable value"""
        return Revision._BADGES[self.status]

    
    def get_delivery_file(self):
        return self.delivery.file.path
    
    def get_correction_script(self):
        script = self.delivery.assignment.get_script()
        if script is not None:
            return script.file.path
        else:
            return None
