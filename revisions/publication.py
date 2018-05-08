import json, requests

from django.utils.translation import ugettext_lazy as _

from teachers.models import *
from mailing.models import *

from .local_settings import *
from kwyjibo.settings import *

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
            body = PublishResultsVisitorMail.SUCCESSFUL_REVISION_MAIL_BODY
        else:
            body = PublishResultsVisitorMail.UNSUCCESSFUL_REVISION_MAIL_BODY

        data = '{start}"subject": "{subject}", "recipient": "{recipient}", "reply_address": "{reply_address}", "body": "body"{end}'.format(
            subject = PublishResultsVisitorMail.MAIL_SUBJECT,
            recipient = visitable.revision.delivery.student.user.email,
            reply_address = MAIL_NO_REPLY_ADDRESS,
            body = body,

            start = '{',
            end = '}',

        )

        #mail.save()
        r = requests.post(url = POST_MAIL_URL, data = data)

        print(" ...results published through mail.", r)
    


class PublishResultsVisitorWeb(PublishResultsVisitor):
    """
    This is the visitor in charge of publishing the results to the web.
    """
    
    def visit(self, visitable):
        print("Saving results...")
        
        # revision = Revision.objects.get(pk = visitable.revision.id)
        #visitable.revision.exit_value = visitable.exit_value
        #visitable.revision.captured_stdout = visitable.captured_stdout
        #visitable.revision.status = self.translate_exit_value_to_status(visitable.exit_value)

        #data = {
        #    'pk':visitable.revision.pk,
        #    'status':self.translate_exit_value_to_status(visitable.exit_value),
        #    'exit_value':visitable.exit_value,
        #    'captured_stdout': visitable.captured_stdout
        #}

        # FIXME: Handmade json is at least, cuestionable
        data = '{start}"pk": {data_pk}, "status": "{data_status}", "exit_value": {data_exit_value}, "captured_stdout": "{data_captured_stdout}"{end}'.format(
            data_pk = visitable.revision.pk,
            data_status = self.translate_exit_value_to_status(visitable.exit_value),
            data_exit_value = visitable.exit_value,
            data_captured_stdout = json.dumps(visitable.captured_stdout),

            start = '{',
            end = '}',

        ).encode("utf8")



        #visitable.revision.save()
        r = requests.post(url = POST_REVISION_URL, data = data)

        print(" ...results saved to the DB.", r)
    
