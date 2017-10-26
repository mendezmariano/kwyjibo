#from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .models import *


class AbstractCsvFlattener(object):
    """AbstractCsvFlattener"""

    def header(self):
        pass

    def flatten(self, item):
        pass


class AssignmentSummaryFlattener(AbstractCsvFlattener):
    """
    AffiliateAccountStatusFlattener converts an affiliate into a flattened version of the model.
    It is intended for exporting information and mmaking reports.
    """

    def __init__(self):
        super(AffiliateAccountStatusFlattener, self).__init__()
        self.headers = [
            "Uid",
            "Last name",
            "First name",
            "Revision status",
            "Corrector",
            "Grade",
            "Comments",
        ]


    def header(self):
        return self.headers

    def flatten(self, row):
        return [
            row.uid,
            row.last_name,
            row.first_name,
            row.revision.status,
            row.corrector,
            row.grade,
            row.comments,
        ]


class ReportGenerator(object):
    """Generates the necesasary reports for a given course."""

    def generate_assignment_summary(self, assignment):
        # student_queryset = Student.objects.filter( Q(shift__course = assignment.course) )
        table = []
        course = assignment.course
        for shift in course.shift_set.all():
            for student in shift.student_set.all():
                has_successful_delivery = False
                student_deliveries = assignment.delivery_set.filter(student = student).order_by('-date')
                for delivery in student_deliveries:
                    revision = delivery.revision
                    if revision.status == RevisionStatus.SUCCESSFUL.name:

                        correction = None
                        correction_qset = Correction.objects.filter(delivery = delivery)
                        if correction_qset.exists():
                            correction = correction_qset[0]

                        correction_grade = correction.grade if correction else '-'
                        corrector = correction.corrector if correction else student.corrector
                        table.append({
                                'uid': student.uid,
                                'last_name': student.user.last_name,
                                'first_name': student.user.first_name,
                                'revision': revision,
                                'corrector': corrector,
                                'grade': correction_grade,
                                'comments': '',
                            })
                        has_successful_delivery = True
                        break;

                if not student_deliveries:
                    table.append({
                            'uid': student.uid,
                            'last_name': student.user.last_name,
                            'first_name': student.user.first_name,
                            'revision': '-',
                            'corrector': student.corrector,
                            'grade': '-',
                            'comments': _('NO DELIVERIES'),
                        })
                else:
                    if not has_successful_delivery:
                        delivery = student_deliveries[0] # The most recent
                        revision = delivery.revision

                        correction = None
                        correction_qset = Correction.objects.filter(delivery = delivery)
                        if correction_qset.exists():
                            correction = correction_qset[0]

                        correction_grade = correction.grade if correction else '-'
                        corrector = correction.corrector if correction else student.corrector
                        table.append({
                                'uid': student.uid,
                                'last_name': student.user.last_name,
                                'first_name': student.user.first_name,
                                'revision': revision,
                                'corrector': student.corrector,
                                'grade': correction_grade,
                                'comments': _('ALL FAILED'),
                            })
        return sorted(table, key=lambda k: k['last_name'])

        
