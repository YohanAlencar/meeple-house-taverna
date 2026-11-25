from django.contrib import admin
from .models import Categoria, Produto, ContatoMensagem, ItemPedido

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(ContatoMensagem)
admin.site.register(ItemPedido)from django.contrib import admin
from .models import Categoria, ContatoMensagem, Integrante, ItemPedido, Produto

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(ContatoMensagem)
admin.site.register(ItemPedido)
admin.site.register(Integrante)