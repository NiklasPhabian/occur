from django.urls import re_path, include
from . import views

# So that we can use {% re_path 'accounts:sign_up' %}
app_name = 'sitepages'

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^home/', views.home, name='home'),
    re_path(r'^about/', views.about, name='about'),

]
