"""kwyjibo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^signup$', views.SignUpView.as_view(), name='signup'),
    url(r'^change_password$', views.ChangePasswordView.as_view(), name='change_password'),

    url(r'^logout/?$', views.logout_page),
    # url(r'^login/?$', django.contrib.auth.views.login),
    
    # url(r'^recoverypass/?$', home.recovery_pass),
    # url(r'^changelenguaje/?$', home.change_lenguaje),
    # url(r'^i18n/', include('django.conf.urls.i18n')),
    # url(r'^forbidden/$', home.forbidden)


    url(r'^teachers/', include('teachers.urls')),
    url(r'^students/', include('students.urls')),

    url('^', include('django.contrib.auth.urls')),


]
