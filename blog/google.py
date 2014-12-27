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
                guser.plus_id = credentials.id_token['sub'] if 'sub' in credentials.id_token else None
                guser.given_name = result['name']['givenName'] if ('name' in result and 'givenName' in result['name']) else None
                guser.family_name = result['name']['familyName'] if ('name' in result and 'familyName' in result['name']) else None
                guser.display_name = result['displayName'] if 'displayName' in result else None
                guser.is_plus_user = result['isPlusUser'] if 'isPlusUser' in result else None
                guser.gender = result['gender'] if 'gender' in result else None
                guser.image_url = result['image']['url'] if ('image' in result and 'url' in result['image']) else None
                guser.language = result['language'] if 'language' in result else None
                guser.birthday = result['birthday'] if 'birthday' in result else None
                guser.age_range_min = result['ageRange']['min'] if ('ageRange' in result and 'min' in result['ageRange']) else None
                guser.age_range_max = result['ageRange']['max'] if ('ageRange' in result and 'max' in result['ageRange']) else None
                guser.save()
                return HttpResponse(json.dumps(result))
            except Commenter.DoesNotExist as e:
                print("ERROR")
                print(e)
                pass
            
        return HttpResponse(json.dumps(credentials.to_json()))
"""
Data Loaded: {
    "kind": "plus#person", 
    "url": "https://plus.google.com/103475622359731419372", 
    "language": "en", 
    "ageRange": {"min": 21}, 
    "gender": "other", 
    "displayName": "Mahmood Khan", 
    "circledByCount": 0, 
    "isPlusUser": true, 
    "emails": [{"type": "account", "value": "mahmoodullah@gmail.com"}], 
    "verified": false, 
    "name": {"familyName": "Khan", "givenName": "Mahmood"}, 
    "etag": "RqKWnRU4WW46-6W3rWhLR9iFZQM/GN5N5w9AXv7HMr3ONqHag6YZMQo", 
    "objectType": "person", 
    "id": "103475622359731419372", 
    "birthday": "1980-01-01", 
    "image": {
        "url": "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg?sz=50", 
        "isDefault": true
    }
}

Data Loaded: {
    "verified": false, 
    "name": {"givenName": "Mahmood", "familyName": "Khan"}, 
    "gender": "male", 
    "kind": "plus#person", 
    "language": "en", 
    "objectType": "person", 
    "url": "https://plus.google.com/103475622359731419372", 
    "isPlusUser": true, 
    "ageRange": {"min": 21}, 
    "image": {
        "isDefault": true, "url": "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg?sz=50"
    }, 
    "displayName": "Mahmood Khan", 
    "etag": "\"RqKWnRU4WW46-6W3rWhLR9iFZQM/uRTQM9CGPsBnX1Y2QCmmuquLAgo\"", 
    "circledByCount": 0, 
    "emails": [{"type": "account", "value": "mahmoodullah@gmail.com"}], 
    "id": "103475622359731419372"
}"
"""