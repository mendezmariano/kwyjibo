import requests

from django.utils.translation import ugettext_lazy as _

from teachers.models import *
from mailing.models import *

class PublishResultsVisitor:
    """
    
    Head of the visitor hierarchy. The visitors are in charge of publishing the
    results of the scripts run for the deliveries made.
    
    """

    def translate_exit_value_to_status(self, exit_value):
        switcher = {
            0: RevisionStatus.SUCCESSFUL,
            1: RevisionStatus.FAILED,
        }
        return switcher.get(exit_value, RevisionStatus.UNKNOWN)

    def visit(self, visitable):
        yield None



class PublishResultsVisitorMail(PublishResultsVisitor):
    """
    Implementation of the publishing visitor which posts a mail through the web interface to await sending
    """

    MAIL_SUBJECT = _('Automatic revision results')

    SUCCESSFUL_REVISION_MAIL_BODY = _('Execution successfull. Delivery passed and ready for manual inspection.')
    UNSUCCESSFUL_REVISION_MAIL_BODY = _('Execution failed. You must correct your work and try again.')
    
    def visit(self, visitable):
        print("Publishing results for mail...")
        visitable.revision.exit_value = visitable.exit_value
        visitable.revision.captured_stdout = visitable.captured_stdout
        visitable.revision.status = self.translate_exit_value_to_status(visitable.exit_value)

        mail = Mail()
        mail.subject = PublishResultsVisitorMail.MAIL_SUBJECT
        mail.recipient = visitable.revision.delivery.student.user.email
        final_status = self.translate_exit_value_to_status(visitable.exit_value)
        if(final_status == RevisionStatus.SUCCESSFUL):
            mail.body = PublishResultsVisitorMail.SUCCESSFUL_REVISION_MAIL_BODY
        else:
            mail.body = PublishResultsVisitorMail.UNSUCCESSFUL_REVISION_MAIL_BODY
        mail.save()
        print("Mail-body:")
        print(mail.body)
        print(" ...results published through mail.")
    


class PublishResultsVisitorWeb(PublishResultsVisitor):
    """
    This is the visitor in charge of publishing the results to the web.
    """
    
    def visit(self, visitable):
        print("Saving results...")
        
        # revision = Revision.objects.get(pk = visitable.revision.id)
        visitable.revision.exit_value = visitable.exit_value
        visitable.revision.captured_stdout = visitable.captured_stdout
        visitable.revision.status = self.translate_exit_value_to_status(visitable.exit_value)

        data = {
            'pk':visitable.revision.pk,
            'status':self.translate_exit_value_to_status(visitable.exit_value),
            'exit_value':visitable.exit_value,
            'captured_stdout': visitable.captured_stdout
        }

        revision.save()
        #r = requests.post(url = POST_END_POINT, data = data)

        print(" ...results saved to the DB.")
    
