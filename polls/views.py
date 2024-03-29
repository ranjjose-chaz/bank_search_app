from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict

from polls.models import Banks
from polls.models import BankBranches

import requests
import os
import json
import jwt


# Standard Err Responses
NO_DATA_MATCHED = {"error": {"message": "No item matched"}}
TOKEN_INVALID = {"error": {"message": "JWT token invalid"}}
TOKEN_EXPIRED = {"error": {"message": "JWT token expired"}}
TOKEN_MISSING = {"error": {"message": "JWT token missing"}}
INVALID_PARAMS = {"error": {"message": "The request can't be processed"}} 


def validate_jwt(f):    
    def wrapper(*args, **kw):        
        token_header = args[0].META.get('HTTP_AUTHORIZATION')

        if not token_header:
            return JsonResponse(TOKEN_MISSING, status=401)

        try:
            jwt.decode(token_header, 'secret', algorithms=['HS256'])
        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse(TOKEN_EXPIRED, status=401)    
        except Exception as e:
            print(e)
            return JsonResponse(TOKEN_INVALID, status=401)

        return f(*args, **kw)      
    return wrapper




def start(request):
    return render(request, "index.html", {})	



@validate_jwt
def bank(request, ifsc=None):

    if ifsc:

        try:
            bank = BankBranches.objects.get(ifsc=ifsc)
        except BankBranches.DoesNotExist:
            return JsonResponse(NO_DATA_MATCHED, status=404)            
        return JsonResponse({"bank_id": bank.bank_id, "bank_name": bank.bank_name})
        
    return JsonResponse()    


@validate_jwt
def branches(request):
    bank_name = request.GET.get('bank_name')
    city = request.GET.get('city')
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    if bank_name and city and limit and offset and limit.isdigit() and offset.isdigit() and int(limit) > 1:
        limit = int(limit)
        offset = int(offset)        
        branch_list = BankBranches.objects.filter(city=city, bank_name=bank_name).order_by('ifsc')[offset:(offset+limit)]
        if not branch_list:
            return JsonResponse(NO_DATA_MATCHED, status=404)    
        return JsonResponse([model_to_dict(branch) for branch in branch_list], safe=False)
    return JsonResponse(INVALID_PARAMS, status=422)    
      
