from django.conf.urls import url

from . import views

app_name = 'students'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name = 'index'),

    url(r'^assignment/(?P<course_id>\d+)/list/$', views.CourseDetailView.as_view(), name = 'assignments'),

    #url(r'^assignment/(?P<assignment_id>\d+)/files/$', views..as_view(), name = 'assignment_files'),
    #url(r'^assignment/(?P<assignment_id>\d+)/files/(?P<assignment_file_id>\d+)/download/$', views..as_view(), name = 'download_assignment_file'),
    #url(r'^assignment/(?P<assignment_id>\d+)/deliveries/upload/$', views..as_view(), name = 'new_delivery'),

    #url(r'^delivery/(?P<iddelivery>\d+)/correction/$', views..as_view(), name = 'delivery_correction'),
    #url(r'^delivery/(?P<iddelivery>\d+)/revision/$', views..as_view(), name = 'delivery_revision'),

    #url(r'^suscription/$', views..as_view(), name = 'suscriptions'),
    #url(r'^suscription/(?P<idshift>\d+)/suscribe/$', views..as_view(), name = 'suscribe'),

]
