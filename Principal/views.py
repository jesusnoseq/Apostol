#encoding:utf-8

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers.json import simplejson
from django.utils import timezone
from Principal.models import Categoria, Apuesta, Participacion, Perfil
from Principal.forms import CategoriaForm, ApuestaForm, usuarioForm, ParticipacionForm, introducirDinero
from django.contrib.admin.views.decorators import staff_member_required



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
    participaciones=Participacion.objects.filter(user=request.user)
    return render_to_response('perfil.html',{'usuario':usuario,'participaciones':participaciones},
                              context_instance=RequestContext(request))



def home(request):
    apuestas = Apuesta.objects.filter(estado='a')
    entrar(request)
    return render_to_response('index.html',{'apuestas':apuestas},context_instance=RequestContext(request))



def apuestasCat(request,cat):
    categoria=Categoria.objects.get(slug=cat)
    apuestas = Apuesta.objects.filter(estado='a', categoria=categoria)#get_list_or_404(Apuesta, estado='a', categoria=categoria)
    return render_to_response('apuestas.html',{'apuestas':apuestas}, context_instance=RequestContext(request))



@login_required(login_url='/registro')
def detalleApuesta(request, id_apuesta):
    now=timezone.now() 
    mensaje=""
    apuesta= get_object_or_404(Apuesta, pk=id_apuesta)

    participaciones=Participacion.objects.filter(apuesta=apuesta).filter(user=request.user)
    ratios=apuesta.ratios()

    if apuesta.fecha_fin < timezone.now() or apuesta.estado=='c':
        mensaje="Apuesta finalizada."
        return render_to_response('apuestaDet.html',{'apuesta':apuesta,
                                                     'ratios':ratios,
                                                     'mensaje':mensaje,
                                                     'now':now,
                                                     'participaciones':participaciones},context_instance=RequestContext(request))
    if request.method=='POST':
        form=ParticipacionForm(request.POST)
        form.user=request.user
        form.apuesta=apuesta
        if form.is_valid():
            participacion = form.save(commit=False)
            user=Perfil.objects.get(user=request.user)
            participacion.user=request.user
            participacion.apuesta=apuesta
            participacion.save()
            user.dinero-=participacion.cantidad
            user.save()
            mensaje="Apuesta realizada"
    else:
        form=ParticipacionForm()

    return render_to_response('apuestaDet.html',{'apuesta':apuesta,
                                                 'ratios':ratios,
                                                 'mensaje':mensaje,
                                                 'formulario':form,
                                                 'participaciones':participaciones}, context_instance=RequestContext(request))



@staff_member_required
def nuevaCategoria(request):
    if request.method=='POST':
        formulario=CategoriaForm(request.POST,request.FILES)
        if formulario.is_valid():
            formulario.save()
            return render_to_response('mensaje.html',{'mensaje':'Categoria creada'},context_instance=RequestContext(request))
    else:
        formulario=CategoriaForm()
    return render_to_response('categoriaForm.html',{'formulario':formulario}, context_instance=RequestContext(request))



@staff_member_required
def nuevaApuesta(request):
    if request.method=='POST':
        formulario=ApuestaForm(request.POST,request.FILES)
        if formulario.is_valid():
            apuesta=formulario.save(commit=False)
            apuesta.user=request.user
            apuesta.save()
            return render_to_response('mensaje.html',{'mensaje':'Apuesta creada'},context_instance=RequestContext(request))
    else:
        formulario=ApuestaForm()
    return render_to_response('categoriaForm.html',{'formulario':formulario}, context_instance=RequestContext(request))



@staff_member_required
def apuestasAdmin(request):
    apuestas = Apuesta.objects.filter(estado='a')
    now=timezone.now() 
    return render_to_response('apuestasAdmin.html',{'apuestas':apuestas,'now':now}, context_instance=RequestContext(request))



@staff_member_required
def borraApuesta(request,id_apuesta):
    apuesta=get_object_or_404(Apuesta,pk=id_apuesta)
    participaciones=Participacion.objects.filter(apuesta=apuesta)
    for p in participaciones:
        usuario=Perfil.objects.get(user=p.user)
        usuario.dinero+=p.cantidad
        usuario.save()
        p.delete()
    apuesta.delete()
    response_data={'result':'ok'}
    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
    #return render_to_response('mensaje.html',{'mensaje':"Apuesta borrada."},context_instance=RequestContext(request))



@staff_member_required
def fijarGanador(request,id_apuesta,opcion):
    mensaje=""
    apuesta = get_object_or_404(Apuesta,pk=id_apuesta)
    apuesta.opcion_ganadora=opcion
    apuesta.estado='c'
    apuesta.save()
    ratios=apuesta.ratios()
 
    multiplicador=ratios[int(opcion)]
    if Participacion.objects.filter(opcion=opcion).filter(apuesta=apuesta).count()==0:
        mensaje="Opcion ganadora registrada. No hay ningun ganador."
    else:
        participaciones=Participacion.objects.filter(opcion=opcion).filter(apuesta=apuesta)
        for participante in participaciones:
            user=Perfil.objects.get(user=participante.user)
            user.dinero+=participante.cantidad*multiplicador
            user.save()
        mensaje="Opción ganadora registrada. El dinero ha sido repartido entre los ganadores."

    return render_to_response('mensaje.html',{'mensaje':mensaje},context_instance=RequestContext(request))


    
@staff_member_required
def agregaDinero(request):
    if request.method=='POST':
        formulario=introducirDinero(request.POST)
        if formulario.is_valid():
            formulario.save()
            return render_to_response('mensaje.html',{'mensaje':'Dinero introducido en el perfil del usuario'},context_instance=RequestContext(request))
    else:
        formulario=introducirDinero()
        
    return render_to_response('introduceDinero.html',{'formulario':formulario}, context_instance=RequestContext(request))
    
