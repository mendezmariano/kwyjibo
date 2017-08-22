
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext_lazy as _

from mailing.models import Mail

from .forms import *



LENGTHPASSWORD = 8
REDIRECTADMIN = "/admin"

SUBJECTMAIL = _("New SignUp at Kwyjibo")
BODYMAIL = _("Welcome to Kwyjibo! You have signed up successfully. You can now acces to the platform with the user: {username}.")

SUBJECTMAILRECOVERY = _("Recupero de password en Jarvis")
BODYMAILRECOVERY = _("Has pedido un recupero de password en Jarvis. Aquí están tus nuevos datos de acceso: '%s'/'%s'.")

SUBJECTMAILCHANGE = _("Cambio de password en Jarvis")
BODYMAILCHANGE = _("Has cambiado el password en Jarvis. Ya puedes acceder con el usuario '%s'. El password ingresado no se envia por cuestiones de seguridad.")



class IndexView(LoginRequiredMixin, View):

    def get(self, request, course_id = None):
        user = request.user
        if(Teacher.objects.filter(user_id=user.id)):
            if course_id:
                return redirect('teachers:dashboard', course_id = course_id)
            else: 
                course = Course.objects.all().order_by('-name')[:1][0]
                if course:
                    return redirect('teachers:dashboard', course_id = course.pk)
                return redirect('teachers:index')
        elif(user.is_superuser):
            return HttpResponseRedirect(REDIRECTADMIN)
        elif(Student.objects.filter(user_id=user.id).exists()):
            student = Student.objects.get(user_id=user.id)
            if (student.shifts.all().count() == 1):
                return redirect('students:assignments', course_id = student.shifts.all()[0].course.pk)
            else:
                return redirect('students:index')
        else:
            return render(request, 'index.html')


class SignUpView(View):

    def get(self, request):
        form = RegistrationForm()
        return render(request, 'registration/register.html', {
            'form': form,
        })

    def post(self, request):
        form = RegistrationForm(request.POST)
        if (form.is_valid()):
            user = User()
            user.username = form.data['username']
            user.first_name = form.data['first_name']
            user.last_name = form.data['last_name']
            user.set_password(form.data['password'])
            user.email = form.data['email']
            user.save()
            student = Student()
            student.user = user
            student.uid = form.data['username']
            student.save()
            if (Shift.objects.all().count() > 0):
                shift = Shift.objects.get(pk=form.data['shifts']);
                student.shifts.add(shift)
                student.save()
            
            mail = Mail()
            mail.save_mail(SUBJECTMAIL, BODYMAIL.format(username = user.username), user.email)
            return render(request, 'registration/registration-success.html')
        return render(request, 'registration/register.html', {'form': form,})


class ChangePasswordView(View):

    def get(self, request):
        if not request.user.is_authenticated():
            redirect('index')
        form = ChangePasswordForm()
        return render(request, 'registration/change_pass.html', {'form': form, })

    def post(self, request):
        if not request.user.is_authenticated():
            redirect('index')

        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.get(pk = request.user.pk)
            if user.check_password(data['current_password']):
                user.set_password(data['password'])
                user.save()
            else:
                bad_password = True
                return render(request, 'registration/change_password.html', {
                    'form': form,
                    'bad_password': bad_password
                })
            login(request, user)
            return redirect('index')
        return render(request, 'registration/change_password.html', {'form': form, })


def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    logout(request)
    return redirect('index')
