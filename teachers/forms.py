import os

from django import forms

from django.contrib.auth.models import User
from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _

from kwyjibo.settings import *

from .model import Correction


class CorrectionForm(forms.ModelForm):
    
    class Meta:
        model = Correction
        exclude = ('delivery', 'corrector')


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        exclude = ('student', 'assignment', 'deliverDate','corrector')
        
    def clean_file(self):
        data = self.cleaned_data['file']
        detected_type = data.content_type
        filename = data.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()
        if ((detected_type in DELIVERY_ACCEPTED_MIMETYPES) or 
            (detected_type == OCTET_STREAM_MIMETYPE and ext == DELIVERY_ACCEPTED_EXTENTION)):
            return data
        else:
            raise forms.forms.ValidationError(_('The file must be a zip file.'))


class AssignmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        self.fields['uid'].error_messages['required'] = _('The name cannot be empty')
        self.fields['deadline'].error_messages['invalid'] = _('Invalid date format, please use YYYY-MM-DD')
    
    class Meta:
        model = Assignment
        exclude = ('course',)
        
    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        today = date(date.today().year, date.today().month, date.today().day)
        if (deadline <= today):
            raise forms.ValidationError(_('The deadline must be in the future'))
        else:
            return deadline
                
    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        exclude.remove('course') # allow checking against the missing attribute
        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError, e:
            self._update_errors(e.message_dict)


class EditAssignmentFileForm(forms.Form):
    
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 25, 'style': 'width: 100%;'}), label='')
    

class AssignmentFileForm(forms.ModelForm):

    class Meta:
        model = AssignmentFile
        exclude = ('assignment', )
    

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
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if(User.objects.filter(username=username)):
            raise forms.forms.ValidationError(_('The username is not available'))
    
    def clean_passwd_again(self):
        passwd = self.cleaned_data.get('passwd', None)
        passwd_again = self.cleaned_data.get('passwd_again', None)
        if(not (passwd == passwd_again)):
            raise forms.forms.ValidationError(_('Passwords do not match'))


class AssignmentScriptForm(forms.ModelForm):
    class Meta:
        model = Script
        exclude = ('assignment', )


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        exclude = ('course',)


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ('user',)
    
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    passwd = forms.CharField(widget=forms.PasswordInput(render_value=True), required=False, label=_("Password"))
    passwd_again = forms.CharField(widget=forms.PasswordInput(render_value=True), required=False, label=_("Repeat password"))
    
    def clean_passwd(self):
        uid = self.cleaned_data.get('uid', None)
        passwd = self.cleaned_data['passwd']
        if (uid is not None):
            if((not (User.objects.filter(username = uid).exists())) and (passwd == '')):
                raise forms.ValidationError(_('A password must be supplied'))

    def clean_passwd_again(self):
        passwd = self.data['passwd']
        passwd_again = self.cleaned_data['passwd_again']
        if((passwd or passwd_again) and (not (passwd == passwd_again)) ):
            raise forms.ValidationError(_('Passwords do not match'))



class StudentSearchForm(forms.Form):
    #criteria_search =  forms.ChoiceField(widget=forms.RadioSelect, choices=ESTADOS, label = "", required=True)
    data_search = forms.CharField(max_length=100, label="")


class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        exclude = ('user',)
        
    username = forms.CharField(max_length=100, label=_("Username") )
    first_name = forms.CharField(max_length=100, label=_("First Name"))
    last_name = forms.CharField(max_length=100, label=_("Last Name"))
    email = forms.EmailField(label="Email")
    passwd = forms.CharField(widget=forms.PasswordInput(render_value=True), required=False, label=_("Password"))
    passwd_again = forms.CharField(widget=forms.PasswordInput(render_value=True), required=False, label=_("Repeat password"))
        
    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if(User.objects.filter(username=username).exists()):
            raise forms.ValidationError(_('The username is not available'))
    
    def clean_passwd(self):
        username = self.cleaned_data.get('username', None)
        passwd = self.cleaned_data['passwd']
        if((not (User.objects.filter(username = username).exists())) and (passwd == '')):
            raise forms.ValidationError(_('A password must be supplied'))

    def clean_passwd_again(self):
        passwd = self.data['passwd']
        passwd_again = self.cleaned_data['passwd_again']
        if((passwd or passwd_again) and (not (passwd == passwd_again)) ):
            raise forms.ValidationError(_('Passwords do not match'))
