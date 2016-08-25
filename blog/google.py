import os, logging, json, datetime, random, string, httplib2

from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import Context, loader, RequestContext
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.conf import settings

#from oauth2client import xsrfutil
from oauth2client.contrib import xsrfutil
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
#from oauth2client.django_orm import Storage
#from oauth2client.contrib.django_util import storage
from oauth2client.contrib.django_util.storage import (DjangoORMStorage as Storage)

from apiclient.discovery import build

from .models import *
from .forms import *
from .mixins import *

class CommenterUpdateView(AjaxableResponseMixin, UpdateView):
    """
    Provides a way to update the Commenter record manually
    """
    model = Commenter
    form_class = CommenterForm
    template_name="blog/commenter_form_inner.html"
    success_message = "%(given_name)s record was updated successfully"

    def get_form_kwargs(self):
        kwargs = super(CommenterUpdateView, self).get_form_kwargs()
        kwargs.update({'id': self.object.id})
        return kwargs

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, given_name=self.object.given_name)

class ShowGoogleUsers(ListView):
    """
    Provides a list of everyone who has logged in to the site
    """
    model = Commenter
    template_name = "plus_users.html"
    context_object_name = 'gusers'

    def get_context_data(self, **kwargs):
        """
        TODO: This method is just a test that can be deleted
        """
        context = super(ShowGoogleUsers, self).get_context_data(**kwargs)
        try:
            commenter = Commenter.objects.get(email='mkhan1484@gmail.com')
            gstorage = Storage(GoogleCredentialsModel, 'commenter', commenter, 'credential')
            credentials = gstorage.get()
            if credentials is None:
                context['me'] = "No credentials found!"
            else:
                http = httplib2.Http()
                http = credentials.authorize(http)

                SERVICE = build('plus', 'v1', http=http)
                google_request = SERVICE.people().get(userId=credentials.id_token['sub'])
                result = google_request.execute()
                #context['me'] = result
                context['me'] = credentials.to_json()
        except Commenter.DoesNotExist as e:
            context['me'] = "Commenter does not exist"
        except AccessTokenRefreshError as e:
            context['me'] = "Unable to refresh access token"

        return context

class GoogleSingInView(TemplateView):
    """
    Shows the Google+ sign-in button and when processes the POST data from the Google+
    Sign-in button
    """
    template_name="plus.html"


    @method_decorator(ensure_csrf_cookie)
    @method_decorator(csrf_protect)
    def get(self, request, *args, **kwargs):
        """
        The view is protected with csrf because its cookie value is required for the AJAX
        POST request when user clicks on the sign-in button
        """

        #For added security to make sure that the request's session is intact between
        #the GET (showing the sign-in button" to the POST (submitting the sign-in)
        self.request.session['state'] = xsrfutil.generate_token(settings.SECRET_KEY, None)

        return super(GoogleSingInView, self).get(request, *args, **kwargs)

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        """
        Process the POST data sent via AJAX after user clicks on the sign-in button.
        """
        # retrive the one-time  Google generated code after user granted permission to the app.
        code = request.POST.get("code", None)
        print("code:" + code)
        #print(request.session['test'])
        # Make sure the request session is still intact and hasn't been tempered with.
        if not xsrfutil.validate_token(settings.SECRET_KEY, str(request.session['state']), None):
            return HttpResponseBadRequest()

        # if there is no one-time Google generated code then return
        if code is None:
            return HttpResponse ("No Code")

        # Exchange the one-time Google generated code for an AccessToken and RefreshToken.
        # Remember that RefreshToken is only generated once during the initial granting of
        # permission by the user.
        try:
            oauth_flow = flow_from_clientsecrets('blog/client_secrets.json', scope="")
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError as e:
            return HttpResponse("Failed to upgrade the authorization code. 401 %s" % e)

        commenter, created = Commenter.objects.get_or_create(email=credentials.id_token['email'], defaults={'plus_id': credentials.id_token['sub']})

        request.session['cid'] = commenter.pk

        # retrieve the credentials object from the database based on the user's email
        gstorage = Storage(GoogleCredentialsModel, 'commenter', commenter, 'credential')

        # if the credentials object does not exist or is invalid then store it
        if gstorage.get() is None or credentials.invalid == True:
            gstorage.put(credentials)

        # if the commenter did not exist before, then save his/her basic profile
        if created:
            SERVICE = build('plus', 'v1')
            http = httplib2.Http()
            http = credentials.authorize(http)

            google_request = SERVICE.people().get(userId='me')
            result = google_request.execute(http=http)
            try:
                commenter.given_name = result['name']['givenName'] if ('name' in result and 'givenName' in result['name']) else None
                commenter.family_name = result['name']['familyName'] if ('name' in result and 'familyName' in result['name']) else None
                commenter.display_name = result['displayName'] if 'displayName' in result else None
                commenter.is_plus_user = result['isPlusUser'] if 'isPlusUser' in result else None
                commenter.gender = result['gender'] if 'gender' in result else None
                commenter.image_url = result['image']['url'] if ('image' in result and 'url' in result['image']) else None
                commenter.language = result['language'] if 'language' in result else None
                commenter.birthday = result['birthday'] if 'birthday' in result else None
                commenter.age_range_min = result['ageRange']['min'] if ('ageRange' in result and 'min' in result['ageRange']) else None
                commenter.age_range_max = result['ageRange']['max'] if ('ageRange' in result and 'max' in result['ageRange']) else None
                commenter.save()
            except Commenter.DoesNotExist as e:
                print(e)

        #return HttpResponse(json.dumps(credentials.to_json()))
        return HttpResponse(json.dumps({"commenter_id": commenter.pk}))