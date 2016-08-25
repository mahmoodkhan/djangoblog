import json

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import models

from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
from .utils import *

class LoginRequired(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """ this is fired up first regardless of what http method is used """
        return super(LoginRequired, self).dispatch(*args, **kwargs)


class BlogPostMixin(View):
    """
    A mixin that renders BlogPost form on GET request and processes it on POST request.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """ this is fired up first regardless of what http method is used """
        return super(BlogPostMixin, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates either a blank form when called from a view
        that subclasses CreateView (in which case self.object = None should be set in its get method)
        Or it instantiates an edit form that has the BlogPost and AttachmentFormset data loaded
        if it is called from a view that subclasses UpdateView (in which ase the the self.object = self.get_object() should be
        set in its get method)
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        attachments = Attachment.objects.filter(blogpost=self.object)
        attachments_formset = AttachmentFormset(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form,
                                        attachments_formset = attachments_formset))
    def post(self, request, *args, **kwargs):
        """
        Handles POST request, instantiating the BlogPost form instance as well as the Attachment
        formset with the passed POST variables and then checks the validity.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        attachments_formset = AttachmentFormset(self.request.POST, self.request.FILES, instance=form.instance)
        if form.is_valid() and attachments_formset.is_valid():
            form.instance.owner = self.request.user
            blogpost = form.save(commit=False)
            if blogpost.published:
                blogpost.pub_date = timezone.now()
            blogpost.save()
            attachments_formset.save()
            return self.form_valid(form)
        else:
            context = self.get_context_data()
            context['form'] = form
            context['attachment_form'] = attachments_formset
            context['attachment_helper'] = AttachmentFormsetHelper()
            #return self.form_invalid(form)
            return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        #context = RequestContext(self.request)
        context = super(BlogPostMixin, self).get_context_data(**kwargs)
        try:
            context['form'] = kwargs['form']
            context['attachment_form'] = kwargs['attachments_formset']
            context['attachment_helper'] = AttachmentFormsetHelper()
        except Exception as e:
            pass
        return context

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            #return JsonResponse(form.errors, status=400)
            return response
        else:
            return response
    """
    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'object': JsonSerializer().serialize([self.object,]),
            }
            return JsonResponse(data)
        else:
            return response