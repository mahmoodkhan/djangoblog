from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.core.serializers.python import Serializer
from django.utils.encoding import smart_text

from django.shortcuts import render
from django.utils import timezone
from django.conf import settings

from django.views.generic import RedirectView, FormView, DetailView, CreateView, TemplateView
from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, YearArchiveView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from django.db.models import Q

from django.http import HttpResponseBadRequest

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from oauth2client import xsrfutil

from .models import *
from .forms import *
from .mixins import *

from ratelimit.mixins import RatelimitMixin

class HomeView(ListView):
    """
    This is the home view, which subclasses ListView,a built-in view, for listing
    the 5 most recent blog-posts.
    """
    model = BlogPost
    template_name="blog/index.html"
    context_object_name = 'blogposts'
    paginate_by = 4

    def get_queryset(self, **kwargs):
        where = {'private': False, 'published': True}
        #print(self.kwargs)
        if self.kwargs:
            where.update(self.kwargs)
        return BlogPost.objects.filter(**where)[:50]

    def get_context_data(self, **kwargs):
        messages.set_level(self.request, messages.DEBUG)
        #messages.success(self.request, self.request.GET['category'], None)
        #messages.debug(self.request, 'Debug world.')
        #messages.info(self.request, 'Info world.')
        #messages.success(self.request, 'Success world.')
        #messages.warning(self.request, 'Warning world.')
        #messages.error(self.request, 'Error <a href="#">world.</a>', extra_tags="safe")
        context = super(HomeView, self).get_context_data(**kwargs)
        return context

class CreateCommentView(AjaxableResponseMixin, CreateView):
    """
    Creates comments made on blogpost entries.
    """
    model = Comment
    form_class = CommentForm

    def post(self, request, *args, **kwargs):

        # Make sure the request session is still intact and hasn't been tempered with.
        if not xsrfutil.validate_token(settings.SECRET_KEY, request.session['state'], None):
            return HttpResponseBadRequest()

        if request.POST.get("commenter") is None:
            return HttpResponseBadRequest()
        return super(CreateCommentView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('detailpost', kwargs={ "pk": self.object.blogpost.pk })


class HiddenBlogPost(LoginRequired, ListView):
    """
    A view that shows hidden posts only to the authenticated users
    """
    model = BlogPost
    template_name="blog/index.html"
    context_object_name = 'blogposts'

    """
    Convert string representation of a boolean to actual boolean. If the value passed in
    is not a valid string representation of a boolean then just ignore it by returning
    the function without any value
    """
    def get_boolean_from_param(self, val):
        if val == 'False' or val == 'false' or val == 'off':
            return False
        elif val == 'True' or val == 'true' or val == 'on':
            return True
        else:
            return None

    def get_queryset(self, **kwargs):
        where = {}
        for k,v in self.kwargs.items():
            where[k] = self.get_boolean_from_param(v) if self.get_boolean_from_param(v) is not None else v
        return BlogPost.objects.filter(**where)[:5]


class BlogPostUpdateView(BlogPostMixin, UpdateView):
    """
    A view that updates existing blogposts. The form_valid and form_invalid methods
    are handled in in BlogPostMixin because that code is shared between this view and
    the CreateView for blogpost.
    """
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BlogPostUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BlogPostUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()
        self.object.updated = timezone.now()
        return super(BlogPostUpdateView, self).form_valid(form)

class BlogPostCreateView(AjaxableResponseMixin,
    SuccessMessageMixin, BlogPostMixin, CreateView):
    """
    A view that creates new blogposts. the form_valid and form_invalid is
    handled in the BlogPostMixin because the code in those methods is the
    same in this view and in the UpdateView.
    """
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'
    success_message = "%(title)s was created successfully"
    #success_url = reverse_lazy('list_notes')

    def get(self, request, *args, **kwargs):
        self.object = None
        return super(BlogPostCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(BlogPostCreateView, self).post(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        """
        For ModelForms, to access fields from the saved object this method is overriden
        """
        return self.success_message % dict(cleaned_data, title=self.object.title)

class BlogPostDetail(DetailView):
    """
    Show a read-only detailed view of the blogpost object with all its attributes.
    """
    model = BlogPost

    def get_context_data(self, **kwargs):
        """
        This method is used to provide additional context to be passed to the template.
        """
        self.request.session['state'] = xsrfutil.generate_token(settings.SECRET_KEY, None)

        # Call the base implementation first to get a context
        context = super(BlogPostDetail, self).get_context_data(**kwargs)

        # Add in the attachments linked to this blogpost
        context['attachments'] = Attachment.objects.filter(blogpost=self.object.pk)

        comments = Comment.objects.filter(blogpost__pk=self.object.pk).order_by('created')
        context['comments'] = comments

        #print(self.request.session.get('cid', 0))
        try:
            context['commentform'] = CommentForm(initial={'blogpost': self.kwargs['pk']})
        except Exception as e:
            print(e)
            pass
        return context

    def get_object(self):
        """
        The method that retrieves the object, so I override it to update
        the lastaccessed datetime field
        """
        object = super(BlogPostDetail, self).get_object()
        object.lastaccessed = timezone.now()
        #object.save(skip_updated=True)
        object.save()
        return object

class BlogPostArchiveIndexView(ArchiveIndexView):
    """
    A top-level index page showing the "latest" objects, by date.
    """
    queryset = BlogPost.objects.filter(published=True).filter(private=False)
    date_field = "pub_date"
    allow_future = True

class BlogPostYearArchiveView(YearArchiveView):
    """
    Annual View of BlogPosts by pub_date.
    """
    queryset = BlogPost.objects.filter(published=True).filter(private=False)
    date_field = "pub_date"
    make_object_list = True
    allow_future = True

class BlogPostMonthArchiveView(MonthArchiveView):
    """
    Monthly view of Blogposts by pub_date
    """
    queryset = BlogPost.objects.filter(published=True).filter(private=False)
    date_field = "pub_date"
    allow_future = True
    paginate_by=12
    #month_format='%m' # month number

class SearchView(ListView):
    """
    This is inheriting from haystack.SearchView so that I can override the extra_context
    method and provide the blogpost_archive_info
    """
    model = BlogPost
    template_name="blog/index.html"
    context_object_name = 'blogposts'

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        # Had to do the following
        # 1. create fulltext index summary_index on feedback_feedback(summary);
        # 2. create fulltext index description_index on feedback_feedback(description)
        args = ( Q( title__search = search ) | Q( content__search = search ), )
        #kwargs = prepare_query_params(self.request.GET)
        #qs = BlogPost.objects.filter(*args)# if search else (), **kwargs)
        qs = BlogPost.objects.filter(content__search=search)
        return qs


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
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [settings.MY_EMAIL,],
        )
        messages.success(self.request, "Thank you for your feedback")
        return super(ContactView, self).form_valid(form)

class AboutView(TemplateView):
    template_name='about.html'

class LoginView(RatelimitMixin, FormView):
    """
    Provides a Login View so users can login
    """
    template_name = 'login.html'
    form_class = LoginForm
    ratelimit_key = 'ip'
    ratelimit_rate = '2/m'
    ratelimit_block = True

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
