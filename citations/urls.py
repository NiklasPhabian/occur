from django.conf.urls import url, include
from . import views

# So that we can use {% url 'citations:store' %}
app_name = 'citations'

urlpatterns = [
    url(r'^stored/', views.stored, name='stored'),
    url(r'^details/(?P<citation_id>[0-9]+)/$', views.details, name='details'),
    url(r'^details/$', views.details, name='details'),
    url(r'^format_dap/$', views.format_dap, name='format_dap'),
    url(r'^crosscite/$', views.crosscite, name='crosscite'),
    url(r'^make_snippet/$', views.make_snippet, name='make_snippet'),
    url(r'^styles/$', views.styles, name='styles'),
    url(r'^identify/$', views.store, name='identify'),
    url(r'^stage/$', views.stage, name='stage'),
    url(r'^dereference/$', views.dereference, name='dereference'),
    url(r'^bib/', views.bib, name='bib'),
    url(r'^csljson/', views.csljson, name='csljson'),
]
