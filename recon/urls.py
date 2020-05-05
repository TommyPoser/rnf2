from django.conf.urls import url
from . import views

app_name = 'recon'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^recon/$', views.recon, name='recon'),
    url(r'^leave/$', views.leave_button, name='leave'),
    url(r'^shot/$', views.shot, name='shot'),
    url(r'^drag_and_drop/$', views.drag_and_drop, name='drag_and_drop'),

]