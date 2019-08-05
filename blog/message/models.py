from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import Userprofile


class Message(models.Model):
    topic=models.ForeignKey(Topic)
    publisher=models.ForeignKey(Userprofile)
    content = models.CharField("内容",max_length=90)
    created_time=models.DateTimeField(auto_now_add=True)
    #父级Message id,默认为0,0->留言  非0->回复
    parent_message=models.IntegerField(default=0)

    class Meta:
        db_table="message"