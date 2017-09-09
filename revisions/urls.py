from django.conf.urls import url

from . import views

app_name = 'revisions'
urlpatterns = [
    url(r'revision^$', views.Revision.as_view(), name = 'revision'),
    url(r'mail^$', views.Mail.as_view(), name = 'mail'),
]
