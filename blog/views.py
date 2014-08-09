from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, HttpResponse, render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth import authenticate, login, logout
from django.views.generic import RedirectView
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
    

def mylogin(request):
    form = LoginForm(request.POST or None)
    print(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        nextpage = form.cleaned_data['next']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse('Account is disabled')
        else:
            return HttpResponse("Invalid Credentials")
    params = {
        'form': form
    }
    #if request.user.is_authenticated():
    #    return HttpResponseRedirect('/')
    return render_to_response(
                    'login.html', 
                    params, 
                    context_instance=RequestContext(request)
    )

class LogoutView(RedirectView):
    """
    A view that logout user and redirect to homepage
    """
    def get_redirect_url(self, *args, **kwargs):
        """
        Logout user and redirect to target url
        """
        if self.request.user.is_authenticated():
            logout(self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)

def mylogout(request):
    logout(request)
    return HttpResponseRedirect('/login/')