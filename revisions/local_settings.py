from kwyjibo.settings import *


REVISION_BATCH_SIZE = 1
REVISION_TIMEOUT = 30 # seconds

JAIL_ROOT = '/var/chroot'
EXECUTION_ROOT = '/tmp/kwyjibo'

POST_REVISION_URL = 'http://{endpoint}/revisions/revision/'.format(endpoint = POST_END_POINT)
POST_MAIL_URL = 'http://{endpoint}/revisions/mail/'.format(endpoint = POST_END_POINT)

