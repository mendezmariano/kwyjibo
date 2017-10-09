#from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .models import *

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
                                'last_name': student.user.first_name,
                                'first_name': student.user.first_name,
                                'revision_status': revision.status,
                                'corrector': corrector,
                                'grade': correction_grade,
                                'comments': '',
                            })
                        has_successful_delivery = True

                if not student_deliveries:
                    table.append({
                            'uid': student.uid,
                            'last_name': student.user.first_name,
                            'first_name': student.user.first_name,
                            'revision_status': '-',
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
                                'last_name': student.user.first_name,
                                'first_name': student.user.first_name,
                                'revision_status': revision.status,
                                'corrector': student.corrector,
                                'grade': correction_grade,
                                'comments': _('ALL FAILED'),
                            })
        return table



        
