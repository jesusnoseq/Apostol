#encoding:utf-8

from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.forms import UserCreationForm
from Principal.models import Categoria, Apuesta, Participacion, Perfil



class CategoriaForm(ModelForm):
    class Meta:
        model=Categoria



class ApuestaForm(ModelForm):
    
    def clean_fecha_fin(self):
        fecha_fin_valid = self.cleaned_data['fecha_fin']
        if (fecha_fin_valid-timedelta(hours=1)) < timezone.now() :
            raise forms.ValidationError("La apuesta debe tener al menos una hora de duracion.")
        return fecha_fin_valid

    class Meta:
        model=Apuesta
        exclude=('user','fecha_inicio','estado','visibilidad','opcion_ganadora')
        widgets = {
            'fecha_fin': forms.SplitDateTimeWidget(),
            'opciones': forms.Textarea(attrs={'title': "Pon las distintas opciones de la apuesta separadas por comas.",})
        }

    
    
    
class usuarioForm(UserCreationForm):
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs= {'class':'datepicker'}))
    #telefono =es.forms.ESPhoneNumberField()

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
        


class introducirDinero(forms.Form):
    cantidad = forms.IntegerField(min_value=1)
    perfil = forms.ModelChoiceField(queryset=Perfil.objects.all(), empty_label=None)
    def save(self):
        if self.is_valid():
            perfil=self.cleaned_data["perfil"]
            cantidad=self.cleaned_data["cantidad"]
            perfil.dinero+=cantidad
            perfil.save()

