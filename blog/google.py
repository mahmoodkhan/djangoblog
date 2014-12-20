import os, logging, json, datetime #httplib2
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

from django.views.generic import View
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.decorators import login_required

#CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
#logger = logging.getLogger("epro")
#FLOW = flow_from_clientsecrets(
#    CLIENT_SECRETS,
#    scope='https://www.googleapis.com/auth/plus.login', #'https://www.googleapis.com/auth/drive',
#    redirect_uri='http://localhost:8000/oauth2callback/')


class MyView(View):
    template_name="plus.html"
    
    def get(self, request, *args, **kwargs):
        #self.object = self.get_object()
        return render(request, self.template_name, {'test': "OK"})
    """        
    def get(self, request):
        # <view logic>
        return HttpResponse('result')
   """ 