from django.conf.urls import url
from . import views

app_name = 'map'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^generate/$', views.generate_map, name='generate'),
    url(r'^travel/$', views.travel, name='travel'),

]