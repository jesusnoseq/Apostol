from django import template
from datetime import datetime
import re
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from Principal.models import Categoria

register = template.Library()


#@register.tag('getCategorias')
#@register.tag(name='getCategorias')
@register.inclusion_tag('menu.html')
def getCategorias():
    cat = get_list_or_404(Categoria)
    return {'categorias':cat}