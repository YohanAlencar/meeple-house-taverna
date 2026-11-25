from django.db.models import Sum
from .models import ItemPedido


def carrinho_context(request):
    if request.user.is_authenticated:
        total = (
            ItemPedido.objects.filter(usuario=request.user).aggregate(
                total=Sum("quantidade")
            )["total"]
            or 0
        )
    else:
        total = 0

    return {"total_itens_carrinho": total}