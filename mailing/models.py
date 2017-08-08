from django.db import models
from django.utils import timezone

# Create your models here.

class Mail(models.Model):
    """
    
    Mail objects are the entities which represents the mail to send.
    
    """
    recipient = models.EmailField(max_length=256, blank=False, null=False)
    reply_address = models.EmailField(max_length=256, blank=False, null=False)
    subject = models.CharField(max_length=256, blank=False)
    body = models.TextField(max_length=8192, blank=False, null=False) # 8K... for bigger objects use: 16384 (16K)
    html = models.BooleanField(default = False)
    
    date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return ("Mail to " + self.recipient + " subject - " + self.subject)
      
    def save_mail(self, subject, body, recipient):
        self.body = body
        self.recipient = recipient
        self.subject = subject
        self.save()

