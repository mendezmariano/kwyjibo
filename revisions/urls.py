from django.conf.urls import url

from . import views

app_name = 'revisions'
urlpatterns = [
    url(r'^revision/$', views.RevisionView.as_view(), name = 'revision'),
    url(r'^mail/$', views.MailView.as_view(), name = 'mail'),
]
