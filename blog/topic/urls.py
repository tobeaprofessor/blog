from django.conf.urls import url

from topic import views

urlpatterns=[
    url(r"^/(?P<author_id>[\w]+)$",views.topics,name="topics")
]