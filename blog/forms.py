from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from captcha.fields import ReCaptchaField

from .models import *

class AttachmentForm(forms.ModelForm):
    """
    Used to upload attachments to a BlogPost
    """

    class Meta:
        model = Attachment
        exclude = ['created', 'updated',]

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.html5_required = True
        self.helper.form_tag = False
        super(AttachmentForm, self).__init__(*args, **kwargs)

class BlogPostForm(forms.ModelForm):
    """
    A Model Form for BlogPost model to be used for creating new blogposts
    """
    class Meta:
        model = BlogPost
        exclude = ['slug', 'owner', 'lastaccessed', ]
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.html5_required = True
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', 'Submit'))
        #self.helper.add_input(Reset('rest', 'Reset', css_class='btn-warning'))
        super(BlogPostForm, self).__init__(*args, **kwargs)

class ContactForm(forms.Form):
    """
    Generic Contact Form that uses Google ReCaptcha to prevent bots from spamming
    """
    name =  forms.CharField(max_length=64, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=64, required=True)
    message = forms.CharField(required=True, widget=forms.Textarea)
    captcha = ReCaptchaField() 
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.html5_required = True
        self.helper.add_input(Submit('submit', 'Submit'))
        super(ContactForm, self).__init__(*args, **kwargs)

class LoginForm(AuthenticationForm):
    """
    A login form that inherits from Django's builtin AuthenticationForm, which has
    several utility methods and has the fields already defined. So I don't need to 
    redefine them here; instead, I simply customize those fields using crispy-forms
    """
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.form_action = '/login/'
        self.helper.form_show_labels = False
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Field('username', placeholder="Username"),
            Field('password', placeholder="Password"),
            FormActions(
                Submit('submit', 'Sign in', css_class='btn-submit'),
            )
        )
        super(LoginForm, self).__init__(*args, **kwargs)
    
    def confirm_login_allowed(self, user):
        """ 
        Because this form inherits from django's built-in AuthenticationForm
        this method is available to to be overwrriten as shown here to restrict
        access to who can actually login.
        """
        if not user.is_active:
            raise forms.ValidationError(_(u"This account is inactive."), code='inactive',)