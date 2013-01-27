#encoding:utf-8

from django.utils import timezone
from datetime import datetime,date, timedelta
from django.db import models
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.template import defaultfilters

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
    #@permalink
    def get_absolute_url(self):
        return "/categoria/%s/" % self.slug
    def __unicode__(self):
        return u'%s' % self.nombre


    
class Apuesta(models.Model):
    ESTADOS = (
               ('b','borrador'),
               ('a',"abierta"), 
               ('c',"cerrada"), 
               ('er',"esperando resolusion"), 
               ('t',"terminada"), 
               ('ca',"cancelada"), 
               )
    VISIBILIDAD = (
                   ('pu',"publica"), 
                   ('pr',"privada"),
                   )
    """TIPO = (
            ('gpe',"gana/pierde/empata"),
            ('gp',"gana/pierde"), 
            ('e',"entero"),
            ('de',"doble entero"), 
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
    opcion_ganadora=models.SmallIntegerField(null=True)
    class Meta:
        ordering = ['-fecha_fin']
    def __unicode__(self):
        return u"%s" % self.titulo
    def get_absolute_url(self):
        return "/apuesta/%i/%s" % (self.id, defaultfilters.slugify(self.titulo))
    def getOpciones(self):
        return [i.strip() for i in self.opciones.split(',')]
    def getNParticipantes(self):
        return Participacion.objects.filter(apuesta=self).count()
    def ratios(self):
        participaciones=Participacion.objects.filter(apuesta=self)
        n=Participacion.objects.filter(apuesta=self).count()
        print "Participaciones: "+str(n)
        if n==0:
            return 0
        nOpciones=len(self.getOpciones())
        dineroClasificado=[0]*nOpciones
        for par in participaciones:
            ###########################################################################################
            ############## CAMBIAR el 0 del indice por int(par.opcion)
            ###########################################################################################
            dineroClasificado[par.opcion]+=par.cantidad
            #print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee %s" % str(int(par.opcion))
        dineroTotal=0
        print "Dinero clasificado"
        print dineroClasificado
        for d in dineroClasificado:
            dineroTotal+=d
        print "dinero total:"+str(dineroTotal)
        ratios=[0]*nOpciones
        i=0
        if dineroTotal==0:
            return 0
        for d in dineroClasificado:
            if d==0:
                ratios[i]='No hay participantes'
            else:
                ratios[i]=100/((d/dineroTotal)*100)
            i+=1
        print ratios,dineroTotal,n
        return ratios,dineroTotal,n

    def clean(self):
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
    def __unicode__(self):
        return u"%s apuesta en %s: %ium a la opcion (%s)" % (self.user.username, self.apuesta, self.cantidad,self.opcion)
    """def clean(self):
        opcion_valid = self.opcion
        print self.apuesta
        #apuesta=Apuesta.objects.get(self.apuesta)
        #max_opcions=len(apuesta.getOpciones())
        if opcion_valid >= max_opcions or opcion_valid<0:
            raise ValidationError("Opcion no valida.")
        return super(Participacion,self).clean()"""

