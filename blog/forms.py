from django import forms
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

class LoginForm(AuthenticationForm):
    """
    A login form that inherits from Django's builtin AuthenticationForm, which has
    several utility methods and has the fields already defined. So I don't need to 
    redefine them here; instead, I simply customize those fields using crispy-forms
    """
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.form_action = '/login/'
        self.helper.layout = Layout(
            Field('username', placeholder="username"),
            Field('password', placeholder="password"),
            FormActions(
                Submit('submit', 'Login', css_class='btn-submit'),
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
            raise forms.ValidationError("This account is inactive.", code='inactive',)