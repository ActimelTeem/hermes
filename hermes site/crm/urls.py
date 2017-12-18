from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.orders, name='orders'),
    url(r'^order/(?P<order_id>\d+)/$', views.order_detail, name='order_detail'),
    url(r'^order/new/$', views.order_new, name='order_new'),
    url(r'^order/(?P<order_id>\d+)/edit/$', views.order_edit, name='order_edit')
]