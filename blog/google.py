import os, logging, json, datetime, random, string
from apiclient.discovery import build

from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import Context, loader, RequestContext

from django.conf import settings

import httplib2
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.django_orm import Storage

from django.views.generic import View, FormView, TemplateView
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect,  ensure_csrf_cookie

from .models import *
class GoogleSingInView(TemplateView):
    template_name="plus.html"
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(csrf_protect)
    def get(self, request, *args, **kwargs):
        # Create a state token to prevent request forgery.
        # Store it in the session for later validation.
        #state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        #          for x in range(32))
        #request.session['be'] = state
        #request.session['me'] = "oauth2callback"
        return render(request, self.template_name, {})
        #print("GET STATE")
        #print(request.session['be'])
        #print("GET TEST")
        #print(request.session['me'])
        #return super(GoogleSingInView, self).get(request, *args, **kwargs)
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        #skope = "https://www.googleapis.com/auth/plus.login email"
        # https://www.googleapis.com/discovery/v1/apis/plus/v1/rest
        # https://developers.google.com/+/web/signin/server-side-flow
        #https://github.com/googleplus/gplus-quickstart-python/blob/master/signin.py
        code = request.POST.get("code", None)
        #print("POST STATE: ")
        #print(request.session['be'])
        #print("TEST")
        #print(request.session['me'])
        if code is None:
            return HttpResponse ("No Code")

        try:
            oauth_flow = flow_from_clientsecrets('blog/client_secrets.json', scope="")
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
            # https://google-api-python-client.googlecode.com/hg/docs/epy/oauth2client.client.OAuth2Credentials-class.html
            #return HttpResponse(credentials)
        except FlowExchangeError as e:
            return HttpResponse("Failed to upgrade the authorization code. 401 %s" % e)
            #return render(request, self.template_name, {})
            
        storage = Storage(Commenter, 'email', credentials.id_token['email'], 'credential')
        if storage.get() is None or credentials.invalid == True:
            storage.put(credentials)
            
            SERVICE = build('plus', 'v1')
            http = httplib2.Http()
            http = credentials.authorize(http)
            
            google_request = SERVICE.people().get(userId='me')
            result = google_request.execute(http=http)
            try:
                guser = Commenter.objects.get(email=credentials.id_token['email'])
                guser.plus_id = credentials.id_token['sub']
                guser.give_name = result['name']['givenName']
                guser.family_name = result['name']['familyName']
                guser.display_name = result['displayName']
                guser.is_plus_user = result['isPlusUser']
                guser.gender = result['gender']
                guser.image_url = result['image']['url']
                guser.save()
                return HttpResponse(json.dumps(result))
            except Commenter.DoesNotExist as e:
                print("ERROR")
                print(e)
                pass
            
        return HttpResponse(json.dumps(credentials.to_json()))
        