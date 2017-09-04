from django.utils import timezone

MAIL_SENDING_ENABLED = False

MAIL_SENDER_MAXIMUM_AGE = timezone.timedelta(hours = 120)
MAIL_SENDER_BATCH_SIZE  = 50