"""
Services to handle mailing
"""
import re, os, logging

from django.core.mail import send_mail
from django.utils import timezone

from mrm.settings import *

from .models import *
from .local_settings import *


class MailSender():
    """
    The actual class with the send() method. Exists separately so that it can be mocked for testing purpouses
    """

    def __init__(self):
        self.logger = logging.getLogger(APP_LOGGER_NAME)

    def send(self, mail):
        # AntiSpamService.log_mail(mail)
        if MAIL_SENDING_ENABLED:
            self.logger.info("mail sending enabled... sending mail. Mail: {mail}".format(mail = mail))
            result = send_mail(
                mail.subject,
                mail.body,
                mail.reply_address,
                [mail.recipient],
                fail_silently=False,
            )
            return result
        else:
            self.logger.info("mail sending disabled... not sending any mail. Mail: {mail}".format(mail = mail))
            return 1


class MailAsyncSender():
    """
    MailAsyncSender Used by the asynchronous task of sending pending mails.
    """

    def __init__(self):
        self.logger = logging.getLogger(APP_LOGGER_NAME)
        self.mail_sender = MailSender()

    def process_next_batch(self):
        """
        Gets oldest N communications with a pending status and attempts to send it.
        If it fails, it will leave it's status as ERROR, and if it succeds, as SENT.
        Returns a dict with 2 fields: sent and failed.
        """
        self.logger.info("MailAsyncSender :: processing next batch...")

        result = {
            'sent': 0,
            'failed': 0,
        }
        chunk = Mail.objects.filter(date__gt = timezone.now() - MAIL_SENDER_MAXIMUM_AGE)[:MAIL_SENDER_BATCH_SIZE]
        self.logger.info("MailAsyncSender :: loaded batch size: {chunk_size}".format(chunk_size = len(chunk)))
        for mail in chunk:
            self.logger.info("MailAsyncSender :: processing mail: {comm}".format(comm = mail))
            sending_result = self.mail_sender.send(mail)
            if(sending_result == 1):
                mail.status = MailStatus.SENT
                result['sent'] += 1
                self.logger.info("MailAsyncSender :: mail sending succeded.")
            else:
                mail.status = MailStatus.ERROR
                mail.error_details = sending_result
                result['failed'] += 1
                self.logger.info("MailAsyncSender :: mail sending failed.")
            mail.save()

        return result
