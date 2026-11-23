from django.contrib import admin
from .models import Categoria, Produto, ContatoMensagem, ItemPedido

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(ContatoMensagem)
admin.site.register(ItemPedido)