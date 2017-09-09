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
        data = json.loads(body)
        data_dict = QueryDict('', mutable=True)
        for key, value in data.iteritems():
            if isinstance(value, list):
                # need to iterate through the list and upate
                # so that the list does not get wrapped in an
                # additional list.
                for x in value:
                    data_dict.update({key: x})
            else:
                data_dict.update({key: value})
        return data_dict


@method_decorator(csrf_exempt, name='dispatch')
class Revision(View):

    def __init__(self):
        super(Revision, self).__init__()
        self.json_loader = JSONloader()

    def post(self, request):
        
        print("Request post: ", request.POST)
        print("Request body: ", request.body)

        post_dict = self.json_loader.dict_from_body(request.body.decode('ascii'))

        pk = post_dict["pk"]
        status = post_dict["status"]
        exit_value = post_dict["exit_value"]
        stdout = post_dict["captured_output"]

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

    def __init__(self):
        super(Mail, self).__init__()
        self.json_loader = JSONloader()

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
