import hashlib
import json
import time
import jwt

from tools.login_check import login_check
from .models import *
from django.http import HttpResponse, JsonResponse


# Create your views here.
@login_check("PUT")
def users(request,username=None):
    if request.method=="POST":
        json_str=request.body
        if not json_str:
            result={"code":202,"error":"Please POST data!!"}
            return JsonResponse(result)
        #如果当前报错,请执行json_str=json_str.decode()
        json_obj=json.loads(json_str)
        username=json_obj.get("username")
        email=json_obj.get("email")
        password1=json_obj.get("password_1")
        password2=json_obj.get("password_2")

        if not username:
            result={"code":203,"error":"Please give me username!"}
            return JsonResponse(result)
        if not  email:
            result={"code":204,"error":"Please give me email!"}
            return JsonResponse(result)
        if not password1 or not password2:
            result={"code":205,"error":"Please give me password!"}
            return JsonResponse(result)
        if password1 != password2:
            result={"code":206,"error":"Please give me right password!"}
            return JsonResponse(result)

        #检查用户名是否存在
        old_user=Userprofile.objects.filter(username=username)
        if old_user:
            result={"code":207,"error":"The username is used!!!"}
            return JsonResponse(result)

        #密码散列
        p_m=hashlib.sha256()
        p_m.update(password1.encode())

        try:
            Userprofile.objects.create(
                username=username,
                nickname=username,
                email= email,
                password=p_m.hexdigest()
            )
        except Exception as e:
            print("---Create error is %s" % e)
            result={"code":500,"error":"Sorry,server is busy!"}
            return JsonResponse(result)

        token=make_token(username)
        result={"code":200,"username":username,
                                 "data":{"token":token.decode()}}
        return JsonResponse(result)

    elif request.method=="GET":
        if username:
            users=Userprofile.objects.filter(username=username)
            if not users:
                result={"code":208,"error":"The user is not existed"}
                return JsonResponse(result)
            user=users[0]
            if request.GET.keys():
                #当前请求有查询字符串
                data={}
                for key in request.GET.keys():
                    if key=="password":
                        continue
                    if  hasattr(user,key):
                        if key=="avatar":
                            data[key]=str(getattr(user,key))
                        else:
                            data[key]=getattr(user,key)
                result={"code":200,"username":username,"data":data}
                return JsonResponse(result)
            else:
                result = {"code": 200, "username": username,
                          "data":{"info":user.info,"sign":user.sign,
                                  "nickname":user.nickname,
                                  "avatar":str(user.avatar)}}
                return JsonResponse(result)
        else:
            users = Userprofile.objects.all()
            result=[]
            for user in users:
                d = {}
                d["username"]=user.username
                d["nickname"]=user.nickname
                d["sign"]=user.sign
                d["info"]=user.info
                d["email"]=user.email
                d["avatar"]=str(user.avatar)
                result.append(d)

            result={"code":200,"data":result}
            return JsonResponse(result)

    elif request.method=="PUT":
        # user=check_token(request)
        user=request.user
        # if not user:
        #     result={"code":209, "error":"The put need token"}
        #     return JsonResponse(result)
        json_str=request.body
        json_obj=json.loads(json_str)
        nickname=json_obj.get("nickname")
        if not nickname:
            result={"code":210, "error":"The nickname can not be none!"}
            return JsonResponse(result)
        sign=json_obj.get("sign")
        if sign is None:
            result={"code":212, "error":"The sign not in json!"}
            return JsonResponse(result)
        info =json_obj.get("info")
        if info is None:
            result={"code":212,"error":"The info not in json"}
            return JsonResponse(result)
        if user.username!=username:
            result={"code":213,"error":"wrong operation"}
            return JsonResponse(result)

        #修改个人信息
        user.sign=sign
        user.info =info
        user.nickname=nickname
        user.save()
        result={"code":200,"username":username}
        return JsonResponse(result)

@login_check("POST")
def user_avatar(request,username):
    if request.method!="POST":
        result={"code":214,"error":"please use POST!"}
        return JsonResponse(result)
    user=request.user
    if user.username!=username:
        result={"code":215,"error":"wrong!"}
        return JsonResponse(result)
    #获取上传图片，上传方式是表单提交
    avatar=request.FILES.get("avatar")
    if not avatar:
        result={"code":216,"error":"please give me avatar!"}
        return JsonResponse(result)
    user.avatar=avatar
    user.save()
    result = {"code": 200, "username":username}
    return JsonResponse(result)


def check_token(request):
    token=request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return None
    try:
        res=jwt.decode(token,"123456abcdef")
    except Exception as e:
        print("check_token error is %s" %(e))
        return None
    username=res["username"]
    users=Userprofile.objects.filter(username=username)
    return  users[0]

def make_token(username,expire=3600*24):
    key="123456abcdef"
    now_t=time.time()
    data={"username":username,"exp":int(now_t+expire)}
    return jwt.encode(data,key,algorithm="HS256")

