from captcha.fields import CaptchaField

from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _

from kwyjibo.settings import *

from teachers.models import *


ERRORUIDVALIDATION = _("userPasswordNotExist")
ERRORPASSWDNOTMATCH = _("passwordsNotMatch")


class LoginForm(forms.Form):
    """
    Registrtion form for new Student
    """
    name = forms.CharField(max_length=100)
    passwd = forms.CharField(widget=forms.PasswordInput(render_value=True))
    


class RecoveryForm(forms.Form):
    uid = forms.CharField(max_length=32, label=_("Username"))
    email = forms.EmailField()
    
    def clean_uid(self):
        uid = self.data.get('uid','')
        email = self.data.get('email','')
        if(not (User.objects.filter(username = uid, email = email))):
            raise forms.ValidationError(_('The email is not registered for a user'))


class RegistrationForm(forms.Form):
    """
    Registrtion form for new Student
    """
    username = forms.CharField(max_length=32, label=_("Username"))
    passwd = forms.CharField(widget=forms.PasswordInput(render_value=True), label=_("Password"))
    passwd_again = forms.CharField(widget=forms.PasswordInput(render_value=True), label=_("Repeat password"))

    first_name = forms.CharField(max_length=100, label=_("First Name"))
    last_name = forms.CharField(max_length=100, label=_("Last Name"))
    email = forms.EmailField()
    shifts = forms.ModelChoiceField(queryset=Shift.objects.all() , empty_label=_("Select Shift"), label=_("shift"))

    captcha = CaptchaField()


    def clean_username(self):
        username = self.cleaned_data['username']
        if(User.objects.filter(username=username)):
            raise forms.forms.ValidationError(_('The username is not available'))
    
    def clean_passwd_again(self):
        passwd = self.cleaned_data.get('passwd', None)
        passwd_again = self.cleaned_data.get('passwd_again', None)
        if(not (passwd == passwd_again)):
            raise forms.forms.ValidationError(_('Passwords do not match'))


class ChangePasswordForm(forms.Form):

    uid = forms.CharField(max_length=32, label=_("uidChangePassword"))
    oldpasswd = forms.CharField(widget=forms.PasswordInput(render_value=True), label=_("oldPassword"))
    passwd = forms.CharField(widget=forms.PasswordInput(render_value=True), label=_("newPassword"))
    passwd_again = forms.CharField(widget=forms.PasswordInput(render_value=True), label=_("repeatPassword"))
    
    def clean_uid(self):
        uid = self.cleaned_data['uid']
        if(not (User.objects.filter(username=uid))):
            raise forms.ValidationError(ERRORUIDVALIDATION)
        else:
            user = User.objects.get(username=uid)
            if (not user.check_password(self.data['oldpasswd'])):
                raise forms.ValidationError(ERRORUIDVALIDATION)
    
    def clean_passwd_again(self):
        passwd = self.cleaned_data.get('passwd', None)
        passwd_again = self.cleaned_data.get('passwd_again', None)
        if(not (passwd == passwd_again)):
            raise forms.ValidationError(ERRORPASSWDNOTMATCH)

