from django.urls import re_path, include
from . import views

# So that we can use {% re_path 'accounts:sign_up' %}
app_name = 'accounts'

urlpatterns = [
    re_path(r'^signup/', views.sign_up, name='sign_up'),
    re_path(r'^login/', views.log_in, name='log_in'),
    re_path(r'^logout/', views.log_out, name='log_out'),
]
