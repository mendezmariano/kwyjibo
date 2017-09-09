import json

from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponse, HttpResponseBadRequest, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt

from teachers.models import *
from mailing.models import *

class JSONloader(object):
    def dict_from_body(self, body):
        print(" -> Request body received: ", body)
        return json.loads(body)


@method_decorator(csrf_exempt, name='dispatch')
class RevisionView(View):

    def __init__(self):
        super(RevisionView, self).__init__()
        self.json_loader = JSONloader()

    def post(self, request):
        
        post_dict = self.json_loader.dict_from_body(request.body.decode('ascii'))

        pk = post_dict["pk"]
        status = post_dict["status"]
        exit_value = post_dict["exit_value"]
        stdout = post_dict["captured_stdout"]

        if (not pk or not status or exit_value is None or not stdout):
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
class MailView(View):

    def __init__(self):
        super(MailView, self).__init__()
        self.json_loader = JSONloader()

    def post(self, request):
        post_dict = self.json_loader.dict_from_body(request.body.decode('ascii'))

        recipient = post_dict["recipient"]
        reply_address = post_dict["reply_address"]
        subject = post_dict["subject"]
        body = post_dict["body"]
        # html = post_dict["html"]

        if (not recipient or not reply_address or not subject or not body):
            return HttpResponseBadRequest()

        mail = Mail()
        mail.subject = subject
        mail.recipient = recipient
        mail.body = body
        mail.reply_address = reply_address
        mail.save()

        return HttpResponse()
