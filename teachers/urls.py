from django.conf.urls import url

from . import views

app_name = 'teachers'
urlpatterns = [

    #url(r'^$', views.HomeView.as_view(), name='home'),
    #url(r'^new/$', views.NewOrganizationView.as_view(), name='new'),
    #url(r'^(?P<pk>[0-9]+)/$', views.DashboardView.as_view(), name='dashboard'),

    url(r'^(?P<course_id>[0-9]+)/$', views.DashboardView.as_view(), name='dashboard'),
    # DEPRECATED
    # url(r'^(?P<course_id>\d+)$', 'index'),

    url(r'^course/list/?$', views.CoursesView.as_view(), name='index'),
    url(r'^course/first/$', views.NewCourseView.as_view(), name = 'first_course'),
    url(r'^course/(?P<course_id>\d+)/new/$', views.NewCourseView.as_view(), name = 'new_course'),
    url(r'^course/(?P<course_id>\d+)/edit/$', views.EditCourseView.as_view(), name='edit_course'),
    # DEPRECATED
    # url(r'^course/detailcourse/(?P<course_id>\d+)$', views..as_view(), name = 'detailcourse'),
    
    url(r'^assignments/(?P<course_id>\d+)/new$', views.NewAssignmentView.as_view(), name = 'new_assignment'),
    url(r'^assignments/(?P<course_id>\d+)/delete/(?P<assignment_id>\d+)/$', views.DeleteAssignmentView.as_view(), name = 'delete_assignment'),
    url(r'^assignments/(?P<course_id>\d+)/edit/(?P<assignment_id>\d+)/$', views.EditAssignmentView.as_view(), name = 'edit_assignment'),
    url(r'^assignments/(?P<course_id>\d+)/script/(?P<assignment_id>\d+)/$', views.UploadAssignmentsScriptView.as_view(), name = 'assignment_script'),
    url(r'^assignments/(?P<course_id>\d+)/file/(?P<assignment_id>\d+)/$', views.AssignmentsFilesListView.as_view(), name='assignment_files'),
    url(r'^assignments/(?P<course_id>\d+)/file/(?P<assignment_id>\d+)/download/(?P<assignment_file_id>\d+)/$', views.AssignmentsFileDownloadView.as_view(), name = 'assignment_file_download'),
    url(r'^assignments/(?P<course_id>\d+)/file/(?P<assignment_id>\d+)/delete/(?P<assignment_file_id>\d+)/$', views.AssignmentsFileDeleteView.as_view(), name = 'assignment_file_delete'),
    # DEPRECATED
    # url(r'^assignments/?$', views..as_view(), name = 'index'),
    # url(r'^assignments/(?P<course_id>\d+)/editfile/(?P<assignment_file_id>\d+)/$', views..as_view(), name = 'edit'),

    
    url(r'^students/?$', views.StudentsFullListView.as_view(), name = 'students'),
    url(r'^students/(?P<course_id>\d+)/list/$', views.StudentsCourseListView.as_view(), name = 'student_list'),
    url(r'^students/(?P<course_id>\d+)/list/(?P<shift_id>\d+)/$', views.StudentsShiftListView.as_view(), name = 'student_shift_list'),
    url(r'^students/(?P<course_id>\d+)/search/$', views.StudentSearchView.as_view(), name = 'student_search'),
    url(r'^students/(?P<course_id>\d+)/new/$', views.NewStudentView.as_view(), name = 'new_student'),
    url(r'^students/(?P<course_id>\d+)/new/(?P<shift_id>\d+)$', views.NewStudentView.as_view(), name = 'new_student_in_shift'),
    url(r'^students/(?P<course_id>\d+)/detail/(?P<student_id>\d+)/$', views.StudentDetailView.as_view(), name = 'student_detail'),
    url(r'^students/(?P<course_id>\d+)/edit/(?P<student_id>\d+)/$', views.EditStudentView.as_view(), name = 'edit_student'),
    url(r'^students/(?P<course_id>\d+)/edit/(?P<student_id>\d+)/(?P<shift_id>\d+)/$', views.EditStudentView.as_view(), name = 'edit_student'),
    url(r'^students/(?P<course_id>\d+)/edit/(?P<student_id>\d+)/$', views.EditUnenrolledStudentView.as_view(), name = 'edit_unenrolled_student'),
    url(r'^students/(?P<course_id>\d+)/deliveries/pending/$', views.PendingDeliveriesListView.as_view(), name = 'pending_deliveries'),
    url(r'^students/(?P<course_id>\d+)/deliveries/(?P<student_id>\d+)/list/$', views.StudentsDeliveriesListView.as_view(), name = 'student_deliveries'),


    url(r'^shifts/(?P<course_id>\d+)/new/?$', views.NewShiftView.as_view(), name = 'new_shift'),
    url(r'^shifts/(?P<course_id>\d+)/edit/(?P<shift_id>\d+)/?$', views.EditShiftView.as_view(), name = 'edit_shift'),
    url(r'^shifts/(?P<course_id>\d+)/delete/(?P<shift_id>\d+)/?$', views.DeleteShiftView.as_view(), name = 'delete_shift'),


    url(r'^deliveries/(?P<course_id>\d+)/assignment/(?P<assignment_id>\d+)/$', views.DeliveryListView.as_view(), name = 'assignment_deliveries'),
    url(r'^deliveries/(?P<course_id>\d+)/assignment/(?P<assignment_id>\d+)/student/(?P<student_id>\d+)/$', views.StudentsDeliveryListView.as_view(), name = 'assignment_deliveries_for_student'),
    url(r'^deliveries/(?P<course_id>\d+)/download/(?P<delivery_id>\d+)/$', views.DeliveryDownloadView.as_view(), name = 'download_delivery'),
    url(r'^deliveries/(?P<course_id>\d+)/detail/(?P<delivery_id>\d+)/$', views.DeliveryDetailView.as_view(), name = 'delivery_detail'),
    url(r'^deliveries/(?P<course_id>\d+)/browse/(?P<delivery_id>\d+)/(?P<file_to_browse>[\w\-\./]+)/$', views.DeliveryBrowseView.as_view(), name = 'browse_delivery'),
    url(r'^deliveries/(?P<course_id>\d+)/explore/(?P<delivery_id>\d+)/$', views.DeliveryExploreView.as_view(), name = 'explore_delivery'),
    url(r'^deliveries/(?P<course_id>\d+)/revisions/(?P<delivery_id>\d+)/$', views.RevisionView.as_view(), name = 'delivery_revision'),
    url(r'^deliveries/(?P<course_id>\d+)/correction/(?P<delivery_id>\d+)/$', views.CorrectionView.as_view(), name = 'correction'),


    url(r'^suscriptions/(?P<course_id>\d+)/list/(?P<shift_id>\d+)/$', views.ListSuscriptionsView.as_view(), name = 'suscriptions'),
    url(r'^suscriptions/(?P<course_id>\d+)/accept/$', views.AcceptBatchSuscriptionView.as_view(), name = 'accept_suscriptions'),
    url(r'^suscriptions/(?P<course_id>\d+)/reject/$', views.RejectBatchSuscriptionView.as_view(), name = 'reject_suscriptions'),
    url(r'^suscriptions/(?P<course_id>\d+)/pending/$', views.ListPendingSuscriptionsView.as_view(), name='pending_suscriptions'),




    #url(r'^export/(?P<course_id>\d+)/$', 'choose'),
    #url(r'^export/download/(?P<course_id>\d+)/$', 'download'),
]


