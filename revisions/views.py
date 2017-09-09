from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from teachers.models import *
from mailing.models import *

@method_decorator(csrf_exempt, name='dispatch')
class Revision(View):

    def post(self, request):
        
        pk = request.POST.get("id", "")
        status = request.POST.get("status", "")
        exit_value = request.POST.get("exit_value", "")
        stdout = request.POST.get("captured_output", "")

        print("pk:", pk)
        print("status:", status)
        print("exit_value:", exit_value)
        print("stdout:", stdout)

        if (not pk or not status or not exit_value or not stdout):
            print("invalid input")
            return HttpResponseBadRequest()

        revision = Revision.objects.get(pk = pk)
        if not revision:
            print("Revision for id not found")
            return HttpResponseBadRequest()

        revision.status = status
        revision.exit_value = exit_value
        revision.captured_stdout = stdout

        revision.save()

        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class Mail(View):

    def post(self, request):
        
        recipient = request.POST.get("recipient", "")
        reply_address = request.POST.get("reply_address", "")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        # html = request.POST.get("html", False)

        if (not recipient or not reply_address or not subject or not body):
            return HttpResponseBadRequest()

        mail = Mail()
        mail.subject = subject
        mail.recipient = recipient
        mail.body = body
        mail.reply_address = reply_address
        mail.save()

        return HttpResponse()
