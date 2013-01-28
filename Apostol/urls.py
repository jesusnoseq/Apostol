#encoding:utf-8

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'Apostol.views.home', name='home'),
    #url(r'^', include('Apostol.urls')),
    url('^$', 'Principal.views.home'),
    
    url(r'^login/$','Principal.views.entrar'),
    url(r'^logout/$','Principal.views.salir'),
    url(r'^registro/$','Principal.views.registro'),
    url(r'^perfil/$','Principal.views.perfil'),

    url(r'^apuesta/nueva/$','Principal.views.nuevaApuesta'),
    url(r'^apuesta/(?P<id_apuesta>\d+)\/[-\w]*$','Principal.views.detalleApuesta'),
    
    url(r'^apuestas/admin/$','Principal.views.apuestasAdmin'),
    url(r'^apuestas/admin/borra/(?P<id_apuesta>\d+)\/[-\w]*$','Principal.views.borraApuesta'),
    url(r'^apuestas/admin/gana/(?P<id_apuesta>\d+)/(?P<opcion>\d+)/$','Principal.views.fijarGanador'),
    
    
    url(r'^categoria/nueva/$','Principal.views.nuevaCategoria'),
    url(r'^categoria/(?P<cat>\w{1,50})/$','Principal.views.apuestasCat'), #por categoria

    
    url(r'^anotaciones/$', direct_to_template, {'template': 'anotaciones.html'}),
    url(r'^about/$', direct_to_template, {'template': 'sobre.html'}),
    
    url('^404testing/$', direct_to_template, {'template': '404.html'}),
    #url(r'^login/$', 'auth.views.login_user'),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT,}),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

)
