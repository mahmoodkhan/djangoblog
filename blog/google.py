import os, logging, json, datetime, random, string #httplib2
#from apiclient.discovery import build

from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import Context, loader, RequestContext
#from .models import CredentialsModel, PrMasterlistUrls
from django.conf import settings

#from oauth2client import xsrfutil
#from oauth2client.client import AccessTokenRefreshError
#from oauth2client.client import flow_from_clientsecrets
#from oauth2client.client import FlowExchangeError
#from oauth2client.django_orm import Storage
import httplib2
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from django.views.generic import View, FormView, TemplateView
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

#CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
#logger = logging.getLogger("epro")
#FLOW = flow_from_clientsecrets(
#    CLIENT_SECRETS,
#    scope='https://www.googleapis.com/auth/plus.login', #'https://www.googleapis.com/auth/drive',
#    redirect_uri='http://localhost:8000/oauth2callback/')


class GoogleSingInView(TemplateView):
    template_name="plus.html"
    
    def get(self, request, *args, **kwargs):
        # Create a state token to prevent request forgery.
        # Store it in the session for later validation.
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                  for x in range(32))
        request.session['be'] = state
        request.session['me'] = "oauth2callback"
        #return render(request, self.template_name, {})
        print("GET STATE")
        print(request.session['be'])
        print("GET TEST")
        print(request.session['me'])
        return super(GoogleSingInView, self).get(request, *args, **kwargs)
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        code = request.POST.get("code", None)
        print("POST STATE: ")
        print(request.session['be'])
        print("TEST")
        print(request.session['me'])

        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
            return credentials
        except:
            return HttpResponse("Failed to upgrade the authorization code. 401")
            #return render(request, self.template_name, {})