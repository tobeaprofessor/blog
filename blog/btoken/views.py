import hashlib
import json
import time

import jwt
from django.http import JsonResponse
from django.shortcuts import render
from user.models import Userprofile

# Create your views here.
from user.views import make_token


def tokens(request):
    """
    创建token->登录
    :param request:
    :return:
    """
    if not request.method=="POST":
        result={"code":201,"error":"Please use POST!"}
        return JsonResponse(result)
    json_str=request.body
    if not json_str:
        result = {"code": 202, "error": "Please give me json!"}
        return JsonResponse(result)
    json_obj=json.loads(json_str)
    username=json_obj.get("username")
    if not username:
        result = {"code": 203, "error": "Please give me username!"}
        return JsonResponse(result)
    password=json_obj.get("password")
    if not password:
        result = {"code": 205, "error": "Please give me password!"}
        return JsonResponse(result)
    users=Userprofile.objects.filter(username=username)
    if not users:
        result = {"code": 208, "error": "The username or password is wrong!"}
        return JsonResponse(result)

    p_m=hashlib.sha256()
    p_m.update(password.encode())
    hash_password=p_m.hexdigest()
    if users[0].password!=hash_password:
        result = {"code": 209, "error": "The username or password is wrong!"}
        return JsonResponse(result)

    result={"code": 200,"username":username,"data":{"token":make_token(username).decode()}}
    return JsonResponse(result)



