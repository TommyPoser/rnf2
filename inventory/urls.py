from django.conf.urls import url
from . import views

app_name = 'inventory'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^drag_and_drop/$', views.drag_and_drop, name='drag_and_drop'),
    url(r'^make_item/$', views.make_item, name='make_item'),
    url(r'^equip/(?P<item_id>\d+)$', views.equip, name='equip'),
    url(r'^unequip/(?P<item_id>\d+)$', views.unequip, name='unequip'),

]