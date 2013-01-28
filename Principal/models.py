#encoding:utf-8

from django.utils import timezone
from datetime import datetime,date, timedelta
from django.db import models
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.template import defaultfilters
from django.utils.functional import empty

class Perfil(models.Model):
    user = models.ForeignKey(User, unique=True)
    dinero = models.FloatField(default=100.0)
    fecha_nacimiento = models.DateField()
    #direccion = models.CharField(max_length=250,blank=True)
    #telefono = models.IntegerField(blank=True,max_length=9)
    #pais = models.CharField(max_length=100,blank=True)
    class Meta:
        verbose_name_plural='Perfiles'
    def __unicode__(self):
        return u"%s" % self.user.username

    def clean(self):
        fecha_nacimiento_valid = self.fecha_nacimiento
        fecha_nacimiento_valid=(fecha_nacimiento_valid+timedelta(days=6574))
        if fecha_nacimiento_valid >= date.today():
            raise ValidationError("El usuario debe ser mayor de edad.")
        return super(Perfil,self).clean()



class Categoria(models.Model):
    slug = models.SlugField(blank=False,unique=True)
    nombre = models.CharField(max_length=250,unique=True)
    imagen = models.ImageField(upload_to='imgCategoria',blank=True)
    #subcategoria = models.ForeignKey(Categoria, blank=True)
    def get_absolute_url(self):
        return "/categoria/%s/" % self.slug
    def __unicode__(self):
        return u'%s' % self.nombre


    
class Apuesta(models.Model):
    ESTADOS = (
               #('b','borrador'),
               ('a',"abierta"), 
               ('c',"cerrada"), 
               )
    VISIBILIDAD = (
                   ('pu',"publica"), 
                   ('pr',"privada"),
                   )
    """TIPO = (
            ('e',"entero"),
            ('l',"lista"),
            ('f',"fecha"),
            ('c',"cadena"),
            )"""
    titulo = models.CharField(max_length=250)
    opciones = models.TextField()
    descripcion = models.TextField()
    #imagen = models.ImageField(upload_to='imgApuestas',blank=True)
    user = models.ForeignKey(User)
    categoria = models.ForeignKey(Categoria)
    fecha_inicio = models.DateTimeField(auto_now=True)#blank=True)#auto_now=True
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=2, choices=ESTADOS, default='a')
    visibilidad = models.CharField(max_length=2, choices=VISIBILIDAD, default='pu')
    #tipo = models.CharField(max_length=3, choices=TIPO, default='gpe')
    opcion_ganadora=models.SmallIntegerField(null=True,blank=True)
    class Meta:
        ordering = ['fecha_fin'] # el que menos tiempo le queda primero
    def __unicode__(self):
        return u"%s" % self.titulo
    def get_absolute_url(self):
        return "/apuesta/%i/%s" % (self.id, defaultfilters.slugify(self.titulo))
    def getOpciones(self):
        return [i.strip() for i in self.opciones.split(',')]
    def getVerboseWinOption(self):
        return self.getOpciones()[self.opcion_ganadora]
    def getNparticipantes(self):
        return Participacion.objects.filter(apuesta=self).count();
    def ratios(self):
        participaciones=Participacion.objects.filter(apuesta=self)
        n=Participacion.objects.filter(apuesta=self).count()
        #print "Participaciones: "+str(n)
        if n==0:
            return 0
        nOpciones=len(self.getOpciones())
        dineroClasificado=[0]*nOpciones
        for par in participaciones:
            dineroClasificado[par.opcion]+=par.cantidad
        dineroTotal=0
        #print "Dinero clasificado"
        #print dineroClasificado
        for d in dineroClasificado:
            dineroTotal+=d
        #print "dinero total:"+str(dineroTotal)
        ratios=[0]*nOpciones
        i=0
        if dineroTotal==0:
            return 0
        for d in dineroClasificado:
            if d==0:
                ratios[i]='0'
            else:
                ratios[i]=100/((d/dineroTotal)*100)
            i+=1
        #print ratios,dineroTotal,n
        return ratios
    def optionsWithRatios(self):
        pack=zip(self.getOpciones(), self.ratios())
        return pack
        
        

    def clean(self):
        if len(self.getOpciones())<2:
            raise ValidationError("Número de opciones no validas. Pon las distintas opciones de la apuesta separadas por comas.")
        if len(self.getOpciones()) != len(set(self.getOpciones())):
            raise ValidationError("No se permiten opciones repetidas.")
        if self.opcion_ganadora:
            opcion_ganadora_valid = self.opcion_ganadora
            max_opcions=len(self.getOpciones())
            if opcion_ganadora_valid >= max_opcions or opcion_ganadora_valid<0:
                raise ValidationError("Opcion ganadora no valida.")
        return super(Apuesta,self).clean()

class Participacion(models.Model):
    user = models.ForeignKey(User)
    apuesta = models.ForeignKey(Apuesta)
    timestamp = models.DateTimeField(auto_now=True)
    cantidad = models.FloatField(null=False)
    opcion = models.SmallIntegerField(null=False)
    class Meta:
        verbose_name_plural='Participaciones'
    def getVerboseOption(self):
        return self.apuesta.getOpciones()[self.opcion]
        #return Apuesta.objects.get(self.apuesta).getOpciones()[self.opcion]
    def __unicode__(self):
        return u"%s apuesta en %s: %ium a la opcion (%s)" % (self.user.username, self.apuesta, self.cantidad,self.opcion)

