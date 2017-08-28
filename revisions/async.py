import kronos

from services import RevisionBatchService

@kronos.register('*/5 * * * *')
def run_revisions():
    service = RevisionBatchService()
    service.run_batch()
