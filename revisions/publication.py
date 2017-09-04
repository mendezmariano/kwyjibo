
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
        return switcher.get(argument, RevisionStatus.UNKNOWN)

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
        mail.subject = MAIL_SUBJECT
        mail.recipient = visitable.revision.user_mail
        final_status = self.translate_exit_value_to_status(visitable.exit_value)
        if(final_status == RevisionStatus.SUCCESSFUL):
            mail.body = SUCCESSFUL_REVISION_MAIL_BODY
        else:
            mail.body = UNSUCCESSFUL_REVISION_MAIL_BODY
        mail.save()
        print(" ...results published through mail.")
    


class PublishResultsVisitorWeb(PublishResultsVisitor):
    """
    This is the visitor in charge of publishing the results to the web.
    """
    
    def visit(self, visitable):
        print("Saving results...")
        visitable.revision.exit_value = visitable.exit_value
        visitable.revision.captured_stdout = visitable.captured_stdout
        visitable.revision.status = self.translate_exit_value_to_status(visitable.exit_value)
        visitable.revision.save()
        print(" ...results saved to the DB.")
    