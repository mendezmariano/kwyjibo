from kwyjibo.settings import *


REVISION_BATCH_SIZE = 1
REVISION_TIMEOUT = 30 # seconds
REVISION_OUTPUT_MAX_LENGTH = 10000 # Model length in DB is 10240. I'm just being cautious here.
TRUNCATION_MESSAGE = "\\n //data truncated for being too long//"

JAIL_ROOT = '/var/chroot'
EXECUTION_ROOT = '/tmp/kwyjibo'

POST_REVISION_URL = 'http://{endpoint}/revisions/revision/'.format(endpoint = POST_END_POINT)
POST_MAIL_URL = 'http://{endpoint}/revisions/mail/'.format(endpoint = POST_END_POINT)

