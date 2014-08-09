from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput()
    )
    next = forms.CharField(
        required=False
    )
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        self.helper.form_action = '/login/'
        self.helper.layout = Layout(
            Field('username', placeholder="username"),
            Field('password', placeholder="password"),
            Field('next'),
            FormActions(
                Submit('submit', 'Login', css_class='btn-submit'),
            )
        )
        super(LoginForm, self).__init__(*args, **kwargs)
"""
    def clean(self):
        self.confirm_login_allowed(self.user)

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.", code='inactive',)
"""
