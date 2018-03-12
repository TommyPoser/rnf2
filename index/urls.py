from django.conf.urls import url
from . import views

app_name = 'index'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^register_user/$', views.register_user, name='register_user'),
    url(r'^switch_player/$', views.switch_player, name='switch_player'),

]