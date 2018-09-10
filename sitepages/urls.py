from django.conf.urls import url, include
from . import views

# So that we can use {% url 'accounts:sign_up' %}
app_name = 'sitepages'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^home/', views.home, name='home'),
    url(r'^about/', views.about, name='about'),

]
