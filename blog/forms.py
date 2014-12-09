from django.core.urlresolvers import reverse_lazy
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory

from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from captcha.fields import ReCaptchaField

from .models import *

"""
This is a formset that will be passed to the template together with the 
BlogPostForm so that a user can upload multiple files to blogpost.
"""
AttachmentFormset = inlineformset_factory(BlogPost, 
    Attachment, 
    can_delete=True, 
    #exclude=('created', 'updated',),
    fields=('attachment', 'blogpost',),
    extra=2)

class AttachmentFormsetHelper(FormHelper):
    """
    This is just a helper for the AttachmentFormset defined above to make it crispier
    """
    def __init__(self, *args, **kwargs):
        super(AttachmentFormsetHelper, self).__init__(*args, **kwargs)
        self.html5_required = True
        self.form_class = 'form-horizontal'
        self.label_class = 'col-sm-2'
        self.field_class = 'col-sm-8'
        self.form_tag = False
        self.render_required_fields = True
        self.disable_csrf = True
        self.form_show_labels = False
        self.layout = Layout(
            'attachment',
        )

from crispy_forms.layout import Layout, HTML, Field
class BlogPostForm(forms.ModelForm):
    """
    A Model Form for BlogPost model to be used for creating new blogposts
    """
    class Meta:
        model = BlogPost
        exclude = ['slug', 'owner', 'lastaccessed', 'updated', ]
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_size = ' col-sm-offset-2'
        self.helper.html5_required = True
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', 'Submit'))
        #self.helper.add_input(Reset('rest', 'Reset', css_class='btn-warning'))
        super(BlogPostForm, self).__init__(*args, **kwargs)
        self.fields['category'].empty_label = ""

class CommentForm(forms.ModelForm):
    """
    A Model Form for making comments on a particular blogpost.
    http://django-crispy-forms.readthedocs.org/en/latest/form_helper.html
    """
    class Meta:
        model = Comment
        exclude = ['updated', ]

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'
        self.helper.html5_required = True
        self.helper.form_method = 'post'
        self.helper.form_action = reverse_lazy('create_comment')
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('rest', 'Reset', css_class='btn-warning'))

class ContactForm(forms.Form):
    """
    Generic Contact Form that uses Google ReCaptcha to prevent bots from spamming
    """
    name =  forms.CharField(max_length=64, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=64, required=True)
    message = forms.CharField(required=True, widget=forms.Textarea)
    captcha = ReCaptchaField(attrs={'theme' : 'clean'}) 
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'
        self.helper.html5_required = True
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.add_input(Reset('rest', 'Reset', css_class='btn-warning'))
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
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'
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