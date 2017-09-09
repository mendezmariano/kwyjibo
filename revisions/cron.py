import kronos

from .services import RevisionBatchService

@kronos.register('* * * * *')
def run_revisions():
    print("Running revisions...")
    service = RevisionBatchService()
    service.run_batch()
