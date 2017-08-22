from django.conf.urls import url

from . import views

app_name = 'students'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name = 'index'),

    url(r'^assignment/(?P<course_id>\d+)/list/$', views.CourseDetailView.as_view(), name = 'assignments'),

    url(r'^assignment/(?P<course_id>\d+)/files/(?P<assignment_id>\d+)/$', views.AssignmentFilesView.as_view(), name = 'assignment_files'),
    url(r'^assignment/(?P<course_id>\d+)/files/(?P<assignment_id>\d+)/download/(?P<assignment_file_id>\d+)/$', views.DownloadAssignmentFileView.as_view(), name = 'download_assignment_file'),
    url(r'^assignment/(?P<course_id>\d+)/deliveries/(?P<assignment_id>\d+)/list/$', views.DeliveryListView.as_view(), name = 'delivery_list'),
    url(r'^assignment/(?P<course_id>\d+)/deliveries/(?P<assignment_id>\d+)/upload/$', views.NewDeliveryView.as_view(), name = 'new_delivery'),
    url(r'^assignment/(?P<course_id>\d+)/deliveries/(?P<assignment_id>\d+)/revision/(?P<delivery_id>\d+)/$', views.RevisionDetailsView.as_view(), name = 'revision_details'),
    url(r'^assignment/(?P<course_id>\d+)/deliveries/(?P<assignment_id>\d+)/correction/(?P<delivery_id>\d+)/$', views.CorrectionDetailsView.as_view(), name = 'correction_details'),

    #url(r'^delivery/(?P<iddelivery>\d+)/correction/$', views..as_view(), name = 'delivery_correction'),
    #url(r'^delivery/(?P<iddelivery>\d+)/revision/$', views..as_view(), name = 'delivery_revision'),

    #url(r'^suscription/$', views..as_view(), name = 'suscriptions'),
    #url(r'^suscription/(?P<idshift>\d+)/suscribe/$', views..as_view(), name = 'suscribe'),

]
