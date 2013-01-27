#encoding:utf-8
#from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404 
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.serializers.json import simplejson
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.utils import timezone
from datetime import datetime, date, timedelta

from Principal.models import *
from Principal.forms import *


# Create your views here.
def entrar(request):
    state="Error al logearse, vuelva a intentarlo."
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "Bienvenido %s" % username
            else:
                state = "Tu cuenta no esta activa, contacta con el administrador."
        else:
            state = "Tu nombre de usuario y/o contraseña no son correctas."
    return render_to_response('mensaje.html',{'mensaje':state},context_instance=RequestContext(request))


@login_required(login_url='/')
def salir(request):
    logout(request)
    state='Sesion cerrada.'
    return render_to_response('mensaje.html',{'mensaje':state},context_instance=RequestContext(request))

def registro(request):
    if request.method=='POST':
        formulario = usuarioForm(request.POST)#UserCreationForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect('/')
    else:
        formulario = usuarioForm()
    return render_to_response('registro.html',{'formulario':formulario},
                              context_instance=RequestContext(request))


@login_required(login_url='/registro')
def perfil(request):
    usuario=Perfil.objects.get(user=request.user)
    return render_to_response('perfil.html',{'usuario':usuario},
                              context_instance=RequestContext(request))

def sobre(request):
    return render_to_response('sobre.html',{},
                              context_instance=RequestContext(request))

def home(request):
    cats= get_list_or_404(Categoria)
    apuestas = get_list_or_404(Apuesta, estado='a')
    entrar(request)
    return render_to_response('index.html',{'apuestas':apuestas},context_instance=RequestContext(request))

def nuevaCategoria(request):
    formulario=CategoriaForm(request.POST)
    if formulario.is_valid():
        formulario.save()
        return render_to_response('index.html',{'mensaje':'Categoria creada'},context_instance=RequestContext(request))
        
    return render_to_response('categoriaForm.html',{'formulario':formulario}, context_instance=RequestContext(request))

def nuevaApuesta(request):
    formulario=ApuestaForm(request.POST,request.FILES)
    
    if formulario.is_valid():
        formulario.cleaned_data["usuario"] = request.user
        apuesta=formulario.save()
        return render_to_response('mensaje.html',{'mensaje':'Apuesta creada'},context_instance=RequestContext(request))
        
    return render_to_response('categoriaForm.html',{'formulario':formulario}, context_instance=RequestContext(request))


def apuestas(request):
    apuestas = Apuesta.objects.filter(estado='a')
    return render_to_response('apuestas.html',{'apuestas':apuestas}, context_instance=RequestContext(request))

def apuestasCat(request,cat):
    categoria=Categoria.objects.get(slug=cat)
    apuestas = Apuesta.objects.filter(estado='a', categoria=categoria)#get_list_or_404(Apuesta, estado='a', categoria=categoria)
    return render_to_response('apuestas.html',{'apuestas':apuestas}, context_instance=RequestContext(request))


def apuestasUser(request):
    apuestas = Apuesta.objects.filter(user=request.user)
    return render_to_response('apuestas.html',{'apuestas':apuestas}, context_instance=RequestContext(request))


def borraApuesta(request,id_apuesta):
    apuesta=get_object_or_404(Apuesta,pk=id_apuesta)
    participaciones=Participacion.objects.filter(apuesta=apuesta)
    for p in participaciones:
        usuario=Perfil.objects.get(user=p.user)
        usuario.dinero+=p.cantidad
        usuario.save()
        p.delete()
    mensaje="Apuesta borrada."
    apuesta.delete()

    return HttpResponseRedirect('/')

def fijarGanador(request,id_apuesta,opcion):
    #repartir pasta
    apuestas = get_list_or_404(Apuesta, estado='a')
    return render_to_response('apuestas.html',{'apuestas':apuestas}, context_instance=RequestContext(request))


@login_required(login_url='/registro')
def detalle_apuesta(request, id_apuesta):
    mensaje =""
    apuesta= get_object_or_404(Apuesta, pk=id_apuesta)
    #ratios, dinero, participaciones= 
    print apuesta.getOpciones()
    participaciones=Participacion.objects.filter(apuesta=apuesta).filter(user=request.user)
    ratios=apuesta.ratios()
    #"ratio"
    #calcualteRatios(id_apuesta)
    #-timedelta(hours=1)) < timezone.now() 
    if apuesta.fecha_fin < timezone.now():
        mensaje="Apuesta finalizada."
        return render_to_response('apuestaDet.html',{'apuesta':apuesta,
                                                     'ratios':ratios,
                                                     'mensaje':mensaje,
                                                     'participaciones':participaciones},context_instance=RequestContext(request))
    form=ParticipacionForm(request.POST)
    form.user=request.user
    form.apuesta=apuesta
    if form.is_valid():
        participacion = form.save(commit=False)
        participacion.user=request.user
        participacion.apuesta=apuesta
        participacion.save()
        user=Perfil.objects.get(user=request.user)
        user.dinero-=participacion.cantidad
        user.save()
        mensaje="Apuesta realizada"

    return render_to_response('apuestaDet.html',{'apuesta':apuesta,
                                                 'ratios':ratios,
                                                 'mensaje':mensaje,
                                                 'formulario':form,
                                                 'participaciones':participaciones},context_instance=RequestContext(request))
    #return render_to_response('apuestaDet.html',{'apuesta':apuesta,
    #                                             'ratios':ratios,
    #                                             'mensaje':mensaje,
    #                                             'participaciones':participaciones},context_instance=RequestContext(request))
"""
def calcualteRatios(id_apuesta):
    ap= get_object_or_404(Apuesta, pk=id_apuesta)
    participaciones=Participacion.objects.filter(apuesta=ap)
    n=Participacion.objects.filter(apuesta=ap).count()
    if n==0:
        return 0
    nOpciones=len(ap.opciones.split())
    dineroClasificado=[0]*nOpciones
    for par in participaciones:
        ###########################################################################################
        ############## CAMBIAR el 0 del indice por int(par.opcion)
        ###########################################################################################
        dineroClasificado[0]=+par.cantidad
        #print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee %s" % str(int(par.opcion))
    dineroTotal=0
    for d in dineroClasificado:
        dineroTotal+=d
    ratios=[0]*nOpciones
    i=0
    if dineroTotal==0:
        return 0
    for d in dineroClasificado:
        if d!=0:
            ratios[i]=100/(d/dineroTotal)
        i+=1
    print ratios,dineroTotal,n
    return ratios,dineroTotal,n
    """
        
#return render_to_response('my_template.html',
#                          my_data_dictionary,
#                          context_instance=RequestContext(request))