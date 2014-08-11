from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, HttpResponse, render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth import authenticate, login, logout
from django.views.generic import RedirectView, FormView, View
from .models import *
from .forms import *


def index(request):
    #get the blog posts that are published
    posts = Post.objects.filter(published=True)
    
    # now return the rendered template
    return render(request, 'blog/index.html', {'posts': posts})

def post(request, slug):
    # get the Post object
    post = get_object_or_404(Post, slug=slug)
    
    # now return the rendered template
    return render(request, 'blog/post.html', {'post': post})

def about(request):
    return HttpResponse("OK")
    
class LoginView(FormView):
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
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(LoginView, self).get_initial()
        initial['username'] = self.request.GET.get('username', '')
        return initial
    
    def form_valid(self, form):
        """
        This method is called after successful submission of the form
        """
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
        return super(LoginView, self).form_valid(form)
    
    def form_invalid(self, form):
        """
        This method is called after the form submission has failed
        """
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