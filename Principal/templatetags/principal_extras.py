from django import template
from Principal.models import Categoria

register = template.Library()

@register.inclusion_tag('menu.html')
def getCategorias():
    cat = Categoria.objects.all()
    return {'categorias':cat}