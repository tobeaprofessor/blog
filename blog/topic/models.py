from django.db import models
from user.models import Userprofile

# Create your models here.
class Topic(models.Model):
    title=models.CharField("文章标题",max_length=50)
    category=models.CharField("文章分类",max_length=20)
    limit=models.CharField("文章权限",max_length=10)
    introduce=models.CharField("文章简介",max_length=90)
    content=models.TextField("文章内容")
    created_time=models.DateTimeField("创建时间",auto_now_add=True)
    modified_time=models.DateTimeField("修改时间",auto_now=True)
    author=models.ForeignKey(Userprofile)

    class Meta:
        db_table="topic"