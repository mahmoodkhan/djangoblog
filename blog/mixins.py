import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from .models import *
from .forms import *

class BlogPostMixin(View):
    """
    A mixin that renders BlogPost form on GET request and processes it on POST request.
    """
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

class JSONMixin(object):
    """
    To process forms that works with AJAX
    To send the data to server and return the list of errors if the data didn't pass the validation.
    """
    def render_to_response(self, context, **httpresponse_kwargs):
        return self.get_json_response(
            self.convert_context_to_json(context),
            **httpresponse_kwargs
        )

    def get_json_response(self, content, **httpresponse_kwargs):
        return HttpResponse(
            content,
            content_type='application/json',
            **httpresponse_kwargs
        )

    def convert_context_to_json(self, context):
        """
        To serialize a Django form and return JSON object with its fields and errors
        """
        form = context.get('form')
        to_json = {}
        options = context.get('options', {})
        to_json.update(options=options)
        to_json.update(success=context.get('success', False))
        fields = {}
        for field_name, field in form.fields.items():
            if isinstance(field, DateField) and isinstance(form[field_name].value(), datetime.date):
                fields[field_name] = unicode(form[field_name].value().strftime('%d.%m.%Y'))
            else:
                fields[field_name] = form[field_name].value() and unicode(form[field_name].value()) or form[field_name].value()
            to_json.update(fields=fields)
            if form.errors:
                errors = {
                    'non_field_errors': form.non_field_errors(),
                }
                fields = {}
                for field_name, text in form.errors.items():
                    fields[field_name] = text
                errors.update(fields=fields)
                to_json.update(errors=errors)
            return json.dumps(to_json)