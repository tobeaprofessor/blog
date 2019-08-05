import jwt
from django.http import JsonResponse
from user.models import Userprofile

TOKEN_KEY="123456abcdef"

def login_check(*methods):
    def _login_check(func):
        def wrapper(request,*args,**kwargs):
            token=request.META.get("HTTP_AUTHORIZATION")
            if not methods:
                #如果当前没有传任何参数，则直接返回视图函数
                return func(request,*args,**kwargs)
            else:
                #检查当前request.method 是否在参数列表里
                if not request.method in methods:
                    return func(request, *args, **kwargs)
            if not token:
                result={"code":109,"error":"please give me token"}
                return JsonResponse(result)
            try:
                res=jwt.decode(token,TOKEN_KEY)
            except Exception as e:
                print("login check is error %s"%e)
                result={"code":108,"error":"THE token is wrong!!!"}
                return JsonResponse(result)
            #token校验成功
            username=res["username"]
            try:
                user=Userprofile.objects.get(username=username)
            except:
                user=None
            if not user:
                result={"code":110,"error":"The user is not existed"}
                return JsonResponse(result)
            #将user赋值给request
            request.user=user

            return func(request,*args,**kwargs)
        return wrapper
    return _login_check

def get_user_by_request(request):
    token=request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return None
    try:
        res=jwt.decode(token,TOKEN_KEY)
    except:
        return None
    username=res["username"]
    try:
        user=Userprofile.objects.get(username=username)
    except:
        return None
    return user
