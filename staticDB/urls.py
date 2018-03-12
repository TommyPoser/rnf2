from django.conf.urls import url
from . import views

app_name = 'staticDB'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^consume_items/$', views.consume_items, name='consume_items'),
    url(r'^weapons/$', views.weapons, name='weapons'),
    url(r'^armors/$', views.armors, name='armors'),
    url(r'^shields/$', views.shields, name='shields'),

]
