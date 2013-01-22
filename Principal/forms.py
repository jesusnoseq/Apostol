#encoding:utf-8

from django import forms
from django.forms import ModelForm
from django.contrib.localflavor import es
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from Principal.models import *


class CategoriaForm(ModelForm):
    class Meta:
        model=Categoria
        
class ApuestaForm(forms.Form):
    titulo = forms.CharField(max_length=250)
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), empty_label=None)
    opciones = forms.CharField(widget=forms.Textarea,help_text="Pon las distintas opciones de la apuesta separadas por comas.")
    descripcion = forms.CharField(widget=forms.Textarea)
    fecha_inicio = datetime.now()
    fecha_fin =forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    #estado = forms.ChoiceField(Apuesta.ESTADOS)
    #visibilidad = forms.ChoiceField(Apuesta.VISIBILIDAD)
    #tipo = forms.ChoiceField(Apuesta.TIPO)
    #usuario= forms.ModelChoiceField(queryset=User.objects.all(), empty_label=None,)#, widget=forms.MultipleHiddenInput
    #imagen = forms.ImageField(required=False)
    
    def save(self):
        if self.is_valid():
            data=self.cleaned_data
            data["estado"]='a'
            data["visibilidad"]='pu'
            #data["tipo"]='gpe'
            a = Apuesta.objects.create(titulo=data['titulo'], opciones=data['opciones'], descripcion=data['descripcion'], user=data['usuario'], categoria=data['categoria'], fecha_fin=data['fecha_fin'], estado=data['estado'], visibilidad=data['visibilidad'] )
        return a.save()
    
    def clean_fecha_fin(self):
        fecha_fin_valid = self.cleaned_data['fecha_fin']
        if (fecha_fin_valid-timedelta(hours=1)) < timezone.now() :
            raise forms.ValidationError("La apuesta debe tener al menos una hora de duracion.")
   
        return fecha_fin_valid

class usuarioForm(UserCreationForm):#forms.Form):
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs= {'class':'datepicker'}))
    #telefono =es.forms.ESPhoneNumberField()

    #exclude = ('user','dinero')
    #class Meta:
    #    model = Usuario
    def save(self, commit=True):
        user=super(usuarioForm, self).save(commit)
        d=self.cleaned_data
        usuario=Perfil.objects.create(user=user,fecha_nacimiento=d["fecha_nacimiento"])
        return usuario
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento_valid = self.cleaned_data['fecha_nacimiento']
        fecha_nacimiento_valid=(fecha_nacimiento_valid+timedelta(days=6574))
        print fecha_nacimiento_valid, date.today()
        if fecha_nacimiento_valid >= date.today() :
            raise forms.ValidationError("El usuario debe ser mayor de edad.")
        return fecha_nacimiento_valid

class ParticipacionForm(ModelForm):
    #widgets = {'cantidad ': forms.IntegerField(attrs={'class': 'slide'}), }
    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        us=self.user
        usuario=Perfil.objects.get(user=us)
        
        if cantidad>usuario.dinero:
            raise forms.ValidationError("¡No tienes suficiente dinero!")
        if cantidad<=0:
            raise forms.ValidationError("Tienes que apostar una cantidad positiva de dinero.")
        return cantidad
    
    def clean_opcion(self):
        opcion = self.cleaned_data['opcion']
        nops=len(self.apuesta.getOpciones())
        if opcion<0 or opcion>=nops:
            raise forms.ValidationError("Elije una opcion valida.")
        return opcion
    
    class Meta:
        model=Participacion
        exclude = ('user','apuesta','timestamp')
        
    

