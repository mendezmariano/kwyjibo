import os, psutil, signal

from threading import Timer
from django.contrib.auth.models import User

from kwyjibo.settings import *
from teachers.models import *

from .local_settings import *
from .setup import EnviromentSetupService
from .execution import SafeCodeRunner
from .publication import *

from zipfile import BadZipFile

class RevisionBatchService(object):
    """
    Service in charge of revising the students' deliveries
    """

    def __init__(self):
        super(RevisionBatchService, self).__init__()
        self.revision_runner = RevisionRunnerService()
    
    def run_batch(self):
        revisions = Revision.objects.filter(status = RevisionStatus.PENDING).order_by('-delivery__date')[:REVISION_BATCH_SIZE]
        print("Running revisions...")
        for revision in revisions:
            User.objects.all()
            self.revision_runner.run(revision)
            # revision.save()


class RevisionRunnerService(object):
    """
    Service in charge of running a single given Revision and returning it's results
    """

    def __init__(self):
        super(RevisionRunnerService, self).__init__()
        self.env_setup_service = EnviromentSetupService()
        self.safe_code_runner = SafeCodeRunner()
        self.publish_result_visitors = (PublishResultsVisitorWeb(), 
                                        PublishResultsVisitorMail(),)


    def run(self, revision):
        print("Now processing revision <{id} - {date}::{student} / {assignment}>".format(
            id = revision.pk,
            date = revision.delivery.date.isoformat(),
            student = revision.delivery.student.get_full_name(),
            assignment = revision.delivery.assignment.uid,
        ))
        assignment = revision.delivery.assignment
        script = assignment.script
        
        result = None
        # Prepare
        try:
            self.env_setup_service.setup(revision, JAIL_ROOT + EXECUTION_ROOT)

            # Run
            result = self.safe_code_runner.execute(EXECUTION_ROOT + "/" + os.path.basename(script.file.path))
        except BadZipFile as e:
            result = ScriptResult()
            result.exit_value = 1
            result.captured_stdout = "No se pudo extraer el archivo zip. Comprima su entrega nuevamente y suba una nueva entrega. Si el problema persiste, comuníquese con el administrador del sitio."

        result.revision = revision

        # Share the results
        for publisher in self.publish_result_visitors:
            result.accept(publisher) # One of this publishers must save the results

        print(" -> results: ", result)
        print(" ...finished processing revision <{id} - {date}::{student} / {assignment}>".format(
            id = revision.pk,
            date = revision.delivery.date,
            student = revision.delivery.student.get_full_name(),
            assignment = revision.delivery.assignment.uid,
        ))
