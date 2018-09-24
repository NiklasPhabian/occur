from django.conf.urls import url, include
from . import views

# So that we can use {% url 'citations:store' %}
app_name = 'citations'

urlpatterns = [
    url(r'^api/', views.api, name='api'),
    url(r'^stored/', views.stored, name='stored'),
    url(r'^details/(?P<citation_id>[0-9]+)/$', views.details, name='details'),
    url(r'^details/$', views.details, name='details'),
    url(r'^bib/', views.bib, name='bib'),
    url(r'^csljson/', views.csljson, name='csljson'),
    url(r'^format/$', views.format, name='format'),
    url(r'^snippet/$', views.snippet, name='snippet'),
    url(r'^styles/$', views.styles, name='styles'),
    url(r'^store/$', views.store, name='store'),
    url(r'^resolve_doi/$', views.resolve_doi, name='resolve_doi'),
    url(r'^crosscite/$', views.crosscite, name='crosscite'),
    url(r'^stage/$', views.stage, name='stage'),
    url(r'^dereference/$', views.dereference, name='dereference'),
]
