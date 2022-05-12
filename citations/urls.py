from django.urls import re_path, include
from . import views

# So that we can use {% re_path 'citations:store' %}
app_name = 'citations'

urlpatterns = [
    re_path(r'^stored/', views.stored, name='stored'),
    re_path(r'^details/(?P<citation_id>[0-9]+)/$', views.details, name='details'),
    re_path(r'^details/$', views.details, name='details'),
    re_path(r'^format_dap/$', views.format_dap, name='format_dap'),
    re_path(r'^crosscite/$', views.crosscite, name='crosscite'),
    re_path(r'^make_snippet/$', views.make_snippet, name='make_snippet'),
    re_path(r'^styles/$', views.styles, name='styles'),
    re_path(r'^identify/$', views.store, name='identify'),
    re_path(r'^stage/$', views.stage, name='stage'),
    re_path(r'^dereference/$', views.dereference, name='dereference'),
    re_path(r'^bib/', views.bib, name='bib'),
    re_path(r'^csljson/', views.csljson, name='csljson'),
]
