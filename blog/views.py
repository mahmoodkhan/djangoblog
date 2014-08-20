from django.core.urlresolvers import reverse
from django.core.mail import send_mail

from django.shortcuts import render, get_object_or_404, HttpResponse, render_to_response
from django.template import Context, loader, RequestContext

from django.utils.decorators import method_decorator
from django.utils import timezone

from django.views.generic import RedirectView, FormView, View, DetailView, CreateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import *
from .forms import *


class HomeView(ListView):
    """
    This is the home view, which subclasses ListView,a built-in view, for listing
    the 5 most recent blog-posts.
    """
    model = BlogPost
    template_name="blog/index.html"
    context_object_name = 'blogposts'
    queryset = BlogPost.objects.filter(published=True).filter(private=False)
    
    def get_context_data(self, **kwargs):
        messages.set_level(self.request, messages.DEBUG)
        messages.debug(self.request, 'Debug world.')
        messages.info(self.request, 'Info world.')
        messages.success(self.request, 'Success world.')
        messages.warning(self.request, 'Warning world.')
        messages.error(self.request, 'Error <a href="#">world.</a>', extra_tags="safe")
        context = super(HomeView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['code'] = """
        <code class="python">
            @register.filter(name='cut')
            def cut(value, arg):
                return value.replace(arg, '')

            @register.filter
            def lower(value):
                return value.lower()
        </code>
        """
        return context

class BlogPostUpdate(UpdateView):
    """
    A view that updates a given BlogPost
    """
    model = BlogPost
    template_name_suffix = '_update_form'
    form_class = BlogPostForm
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """ this is fired up first regardless of what http method is used """
        return super(BlogPostUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        # The current logged in user is the blogpost owner 
        form.instance.owner = self.request.user
        
        # do not yet commit the blogpost
        blogpost = form.save(commit=False)
        
        # get all of the attachments that are uploaded for the blogpost
        attachments_formset = AttachmentFormset(self.request.POST, self.request.FILES, instance=blogpost)
        
        # If the attachments formset is valid then save the blogpost followed by attachments
        if attachments_formset.is_valid():
            blogpost.save()
            attachments_formset.save()
        return super(BlogPostUpdate, self).form_valid(form)

    def form_invalid(self, form):
        #return super(BlogPostCreate, self).form_invalid(form)
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        """ Add the attachments formset and crispy helper to the template file """
        context = super(BlogPostUpdate, self).get_context_data(**kwargs)
        context['attachment_form'] = AttachmentFormset(initial=self.get_initial())
        context['attachment_helper'] = AttachmentFormsetHelper()
        return context



class BlogPostDetail(DetailView):
    model = BlogPost
    
    def get_context_data(self, **kwargs):
        """
        This method is used to provide additional context to be passed to the template.
        """
        # Call the base implementation first to get a context
        context = super(BlogPostDetail, self).get_context_data(**kwargs)
        # Add in the attachments linked to this blogpost
        context['attachments'] = Attachment.objects.filter(blogpost=self.object.pk)
        # return the modified context to be passed onto the template
        return context
    
    def get_object(self):
        """ 
        The method that retrieves the object, so I override it to update 
        the lastaccessed datetime field 
        """ 
        object = super(BlogPostDetail, self).get_object()
        object.lastaccessed = timezone.now()
        object.save()
        return object


class BlogPostCreate(SuccessMessageMixin, CreateView):
    """
    For creating new blogposts by inheriting Django builtin Class-Based-View, CreateView
    """
    model = BlogPost
    form_class = BlogPostForm
    success_message = "%(title)s was created successfully"
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """ this is fired up first regardless of what http method is used """
        return super(BlogPostCreate, self).dispatch(*args, **kwargs)
        
    def form_valid(self, form):
        # The current logged in user is the blogpost owner 
        form.instance.owner = self.request.user
        
        # do not yet commit the blogpost
        blogpost = form.save(commit=False)
        
        # get all of the attachments that are uploaded for the blogpost
        attachments_formset = AttachmentFormset(self.request.POST, self.request.FILES, instance=blogpost)
        
        # If the attachments formset is valid then save the blogpost followed by attachments
        if attachments_formset.is_valid():
            blogpost.save()
            attachments_formset.save()
        return super(BlogPostCreate, self).form_valid(form)
    
    def form_invalid(self, form):
        #return super(BlogPostCreate, self).form_invalid(form)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """ Add the attachments formset and crispy helper to the template file """
        context = super(BlogPostCreate, self).get_context_data(**kwargs)
        context['attachment_form'] = AttachmentFormset(initial=self.get_initial())
        context['attachment_helper'] = AttachmentFormsetHelper()
        return context

    def get_success_message(self, cleaned_data):
        """
        For ModelForms, to access fields from the saved object this method is overriden
        """
        return self.success_message % dict(cleaned_data,
                                       title=self.object.title)

class ContactView(FormView):
    """ 
    A class based view that inherits from FormView, a generic view in Django, to provide
    a Contact form for site visitors to use to get contact the site owner
    """
    form_class = ContactForm
    template_name = 'contact.html'
    success_url = '/'
    
    def form_valid(self, form):
        message = "{name} / {email} said: " .format(
            name = form.cleaned_data.get('name'),
            email = form.cleaned_data.get('email'))
        message += "\n\n{0}".format(form.cleaned_data.get('message'))
        send_mail(
            subject=form.cleaned_data.get('subject').strip(),
            message = message,
            from_email = 'me@example.com',
            recipient_list = ['mkhan@mercycorps.org',],
        )
        return super(ContactFormView, self).form_valid(form)

class LoginView(FormView):
    """
    Provides a Login View so users can login
    """
    template_name = 'login.html'
    form_class = LoginForm
    
    def get(self, request, *args, **kwargs):
        """
        This method is not necessarily needed for FormView but I need it because I need to
        set initial value for the field, next, which is only defined in the template not 
        in the form object.
        If the field 'next' was defined in the form object, then I could have set its
        value in the get_initial function like I do for username
        """
        
        """ create an instance of the form with initial data """
        form = self.form_class(initial=self.get_initial())
        
        """data passed to the template"""
        params = {
            'form': form,
            'next': request.GET.get('next', '/')
        }
        
        return render(request, self.template_name, params)
    
    def get_success_url(self):
        """ 
        Instead of setting a static "success_url" attribute at the class level above,
        I overworte this method to determine where user should be redirected to based on
        the "next" parameter sent from the login form.
        """
        return self.request.POST.get("next", "/")

    def get_initial(self, **kwargs):
        """ Returns the initial data to use for forms on this view.  """
        initial = super(LoginView, self).get_initial()
        initial['username'] = self.request.GET.get('username', '')
        return initial
    
    def form_valid(self, form):
        """ This method is called after successful submission of the form """
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
        return super(LoginView, self).form_valid(form)
    
    def form_invalid(self, form):
        """  This method is called after the form submission has failed  """
        return super(LoginView, self).form_invalid(form)


class LogoutView(RedirectView):
    """
    A view that logout user and redirect to homepage
    """
    
    """ Whether the redirect should be permanent. If True, the HTTP status code returned. """
    permanent = False
    
    """ If True, then the GET query string is appended to the URL of new location. """
    query_string = True
    
    """ The name of the URL pattern to redirect to """
    pattern_name = 'home'
    
    def get_redirect_url(self, *args, **kwargs):
        """
        Logout user and redirect to target url
        """
        if self.request.user.is_authenticated():
            logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)