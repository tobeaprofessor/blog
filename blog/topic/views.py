import html
import json

from django.http import JsonResponse
from message.models import Message
from user.models import Userprofile
from .models import Topic

# Create your views here.
from tools.login_check import login_check, get_user_by_request


@login_check("POST","DELETE")
def topics(request,author_id):#因为数据库username为主键，author_id为username
    if  request.method=="POST":
        user=request.user
        if user.username!=author_id:
            result = {"code": 301, "error": "wrong!"}
            return JsonResponse(result)
        json_str=request.body
        if not json_str:
            result = {"code": 302, "error": "please give me data!"}
            return JsonResponse(result)
        json_obj=json.loads(json_str)
        title=json_obj.get("title")
        category=json_obj.get("category")
        limit=json_obj.get("limit")
        content=json_obj.get("content")
        content_text=json_obj.get("content_text")
        if not title:
            result = {"code": 303, "error": "please give me title!"}
            return JsonResponse(result)
        #防止xss cross site script攻击
        title=html.escape(title)
        if not category:
            result = {"code": 304, "error": "please give me category!"}
            return JsonResponse(result)
        if not limit:
            result = {"code": 305, "error": "please give me limit!"}
            return JsonResponse(result)
        if not content:
            result = {"code": 306, "error": "please give me content!"}
            return JsonResponse(result)
        if not content_text:
            result = {"code": 307, "error": "please give me content_text!"}
            return JsonResponse(result)
        introduce=content_text[:30]
        try:
            Topic.objects.create(
                title=title,
                category=category,
                limit=limit,
                introduce=introduce,
                content=content,
                author_id=author_id
            )
        except Exception as e:
            print("The error is %s"%e)
            result = {"code": 222, "error": "topic is busy"}
            return JsonResponse(result)
        result={"code": 200,"username":user.username}
        return JsonResponse(result)
    elif request.method=="GET":
        authors = Userprofile.objects.filter(username=author_id)
        if not authors:
            result={"code":301,"error":"author is not existed"}
            return JsonResponse(result)
        author=authors[0]
        category = request.GET.get("category")
        t_id = request.GET.get("t_id")
        #查找访问者
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username
        if t_id:
            #查询用户的指定文章
            t_id=int(t_id)
            is_self=False
            if visitor_username == author_id:
                is_self=True
                # 博主访问自己的博客
                try:
                    author_topic=Topic.objects.get(id=t_id)
                except Exception as e:
                    result={"code":311,"error":"no topic"}
                    return JsonResponse(result)
            else:
                # 陌生人访问博主的博客
                try:
                    author_topic = Topic.objects.get(
                        id=t_id,limit="public")
                except Exception as e:
                    result={"code":312,"error":"no topic!"}
                    return JsonResponse(result)
            res=make_topic_res(author,author_topic,is_self)
            return JsonResponse(res)
        else:
            if category in ["tec","no-tec"]:
                if visitor_username==author.username:
                    #博主访问自己的博客
                    author_topics=Topic.objects.filter(
                        author_id=author.username,category=category)
                else:
                    #陌生人访问博主的博客
                    author_topics=Topic.objects.filter(
                        author_id=author.username,limit="public",
                    category=category)
            else:
                if visitor_username==author.username:
                    #博主访问自己的博客
                    author_topics=Topic.objects.filter(
                        author_id=author.username)
                else:
                    #陌生人访问博主的博客
                    author_topics=Topic.objects.filter(
                        author_id=author.username,limit="public")
            res=make_topics_res(author,author_topics)
            return JsonResponse(res)
    elif request.method=="DELETE":
        user=request.user
        if user.username!=author_id:
            result={"code":404,"error":"wrong!"}
            return JsonResponse(result)
        topic_id=request.GET.get("topic_id")
        if not topic_id:
            result = {"code": 405, "error": "please give me topic_id!"}
            return JsonResponse(result)
        topics=Topic.objects.filter(id=topic_id,author_id=author_id)
        if not topics:
            result = {"code": 405, "error": "the topic is not existed!"}
            return JsonResponse(result)
        topic=topics[0]
        topic.delete()
        result = {"code":200}
        return JsonResponse(result)




def make_topics_res(author,author_topics):
    res={"code":200,"data":{}}
    topics_list = []
    for topic in author_topics:
        dic = {}
        dic["id"] = topic.id
        dic["title"] = topic.title
        dic["category"] = topic.category
        dic["created_time"] = \
            topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        dic["content"] = topic.content
        dic["introduce"] = topic.introduce
        dic["author"] = author.nickname
        topics_list.append(dic)
    res["data"]["nickname"]=author.nickname
    res["data"]["topics"]=topics_list
    return res

def make_topic_res(author,author_topic,is_self):
    if is_self:
        # 博主访问自己的博客
        #取出ID大于当前博客ID的数据的第一个->当前文章的下一篇
        next_topic=Topic.objects.filter(
            id__gt=author_topic.id,author=author).first()
        # 取出ID小于当前博客ID的数据的最后一个->当前文章的上一篇
        last_topic=Topic.objects.filter(
            id__lt=author_topic.id,author=author).last()
    else:
        # 陌生人访问博主的博客
        next_topic = Topic.objects.filter(
            id__gt=author_topic.id, author=author,
        limit="public").first()
        last_topic = Topic.objects.filter(
            id__lt=author_topic.id, author=author,
            limit="public").last()
    #生成下一个文章的id和title
    if next_topic:
        next_id=next_topic.id
        next_title=next_topic.title
    else:
        next_id = None
        next_title = None
    # 生成上一个文章的id和title
    if last_topic:
        last_id=last_topic.id
        last_title=last_topic.title
    else:
        last_id = None
        last_title = None
    result={"code":200,"data":{}}
    result["data"]["nickname"]=author.nickname
    result["data"]["title"]=author_topic.title
    result["data"]["category"]=author_topic.category
    result["data"]["created_time"]=\
        author_topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
    result["data"]["content"] = author_topic.content
    result["data"]["introduce"] = author_topic.introduce
    result["data"]["author"] = author.nickname
    result["data"]["next_id"] = next_id
    result["data"]["next_title"] = next_title
    result["data"]["last_id"] = last_id
    result["data"]["last_title"] = last_title

    all_messages=Message.objects.filter(
        topic=author_topic).order_by("-created_time")
    msg_dic={}
    msg_list=[]
    m_count=0
    for msg in all_messages:
        m_count+=1
        if msg.parent_message:
            #回复
            if msg.parent_message in msg_dic:
                msg_dic[msg.parent_message].append({
                    "msg_id":msg.id,
                    "publisher":msg.publisher.nickname,
                    "publisher_avatar":str(msg.publisher.avatar),
                    "content":msg.content,
                    "created_time": msg.created_time.strftime(
                        "%Y-%m-%d %H:%M:%S")
                })

            else:
                msg_dic[msg.parent_message] = []
                msg_dic[msg.parent_message].append({
                     'msg_id': msg.id, 'publisher': msg.publisher.nickname,
                     'publisher_avatar': str(msg.publisher.avatar),
                     'content': msg.content,
                     'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S')
                     })
        else:
            #留言
            msg_list.append({"id":msg.id,
            "content":msg.content,
            "publisher":msg.publisher.nickname,
            "publisher_avatar": str(msg.publisher.avatar),
            "created_time":msg.created_time.strftime("%Y-%m-%d %H:%M:%S"),
            "reply":[]})
    #关联 留言和对应的回复
    #msg_list ->[{留言相关的信息，reply:[]},]
    for m  in msg_list:
        if m["id"] in msg_dic:
            #证明当前的留言有回复信息
            m["reply"]=msg_dic[m["id"]]
    result["data"]["messages"] = msg_list
    result["data"]["messages_count"] = m_count
    return result


