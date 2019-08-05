from django.db import models

# Create your models here.
class Userprofile(models.Model):
    username=models.CharField("用户名",max_length=11,primary_key=True)
    nickname=models.CharField("昵称",max_length=30)
    email=models.EmailField("邮件")
    password=models.CharField("密码",max_length=64)
    sign=models.CharField("个性签名",max_length=50,null=True)
    info=models.CharField("个人描述",max_length=150,null=True)
    avatar=models.ImageField(upload_to="avatar/",null=True)

    class Meta:
        db_table="user_profile"