import json
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import requests

from .models import Categoria, ContatoMensagem, ItemPedido, Produto
from .supabase_client import (
    adicionar_integrante,
    atualizar_integrante,
    buscar_integrantes,
    deletar_integrante,
)

PRODUTOS_API_FALLBACK = [
    {
        "id": 1,
        "title": "Fjallraven - Foldsack No. 1 Backpack",
        "price": 109.95,
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
    },
    {
        "id": 2,
        "title": "Mens Casual Premium Slim Fit T-Shirts",
        "price": 22.3,
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_.jpg",
    },
    {
        "id": 3,
        "title": "Mens Cotton Jacket",
        "price": 55.99,
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/71li-ujtlUL._AC_UX679_.jpg",
    },
    {
        "id": 4,
        "title": "Mens Casual Slim Fit",
        "price": 15.99,
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/71YXzeOuslL._AC_UY879_.jpg",
    },
]


def home(request):
    return render(request, "taverna/home.html")


def quem_somos(request):
    integrantes = buscar_integrantes()
    return render(request, "taverna/quem_somos.html", {"integrantes": integrantes})


def produtos(request):
    produtos_locais = Produto.objects.filter(ativo=True)

    produtos_api = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            "https://fakestoreapi.com/products?limit=4",
            headers=headers,
            timeout=8,
        )
        print("Status FakeStoreAPI:", response.status_code, flush=True)
        if response.status_code == 200:
            dados = response.json()
            if isinstance(dados, list) and len(dados) > 0:
                produtos_api = dados
                print("Qtd produtos API:", len(produtos_api), flush=True)
        else:
            print(
                "FakeStoreAPI bloqueou/retornou status diferente de 200; usando fallback.",
                flush=True,
            )
    except Exception as e:
        print("ERRO na FakeStoreAPI:", repr(e), flush=True)

    if not produtos_api:
        produtos_api = PRODUTOS_API_FALLBACK

    return render(
        request,
        "taverna/produtos.html",
        {
            "produtos": produtos_locais,
            "produtos_locais": produtos_locais,
            "produtos_api": produtos_api,
        },
    )


def contato(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        mensagem = request.POST.get("mensagem")

        if nome and email and mensagem:
            ContatoMensagem.objects.create(
                nome=nome,
                email=email,
                telefone=telefone,
                mensagem=mensagem,
            )
            messages.success(
                request,
                "Sua mensagem foi enviada com sucesso para os mestres da taverna!",
            )
            return redirect("contato")

    return render(request, "taverna/contato.html")


def cadastrar_usuario(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Aventureiro registrado com sucesso!")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "taverna/cadastrar.html", {"form": form})


def login_usuario(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect(reverse("admin:index"))
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect(reverse("admin:index"))
            return redirect("dashboard")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm(request)

    return render(request, "taverna/login.html", {"form": form})


@login_required
def adicionar_ao_pedido(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    item, criado = ItemPedido.objects.get_or_create(
        usuario=request.user,
        produto=produto,
        defaults={"quantidade": 1},
    )
    if not criado:
        item.quantidade += 1
        item.save()

    messages.success(
        request,
        f'"{produto.nome}" foi adicionado aos seus pedidos com sucesso!',
    )
    return redirect("produtos")


@login_required
def meus_pedidos(request):
    pedidos = ItemPedido.objects.filter(usuario=request.user).select_related(
        "produto"
    )
    total_geral = sum(item.subtotal() for item in pedidos)

    return render(
        request,
        "taverna/meus_pedidos.html",
        {
            "pedidos": pedidos,
            "itens_carrinho": pedidos,
            "total_geral": total_geral,
        },
    )


@login_required
def editar_pedido(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, usuario=request.user)
    if request.method == "POST":
        try:
            nova_qtd = int(request.POST.get("quantidade", 1))
            if nova_qtd > 0:
                item.quantidade = nova_qtd
                item.save()
                messages.success(request, "Quantidade atualizada com sucesso!")
            else:
                item.delete()
                messages.success(request, "Item removido dos seus pedidos!")
        except ValueError:
            messages.error(request, "Quantidade inválida.")
        return redirect("meus_pedidos")

    return render(request, "taverna/editar_pedido.html", {"item": item})


@login_required
def remover_pedido(request, item_id):
    item = get_object_or_404(ItemPedido, id=item_id, usuario=request.user)
    item.delete()
    messages.success(request, "Item removido com sucesso!")
    return redirect("meus_pedidos")


@login_required
def dashboard(request):
    return render(request, "taverna/dashboard.html")


@login_required
def editar_perfil(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.email = request.POST.get("email", "")
        request.user.save()
        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect("editar_perfil")

    return render(request, "taverna/editar_perfil.html")


@login_required
def gerenciar_contatos(request):
    contatos = ContatoMensagem.objects.all().order_by("-data_envio")
    return render(
        request, "taverna/gerenciar_contatos.html", {"contatos": contatos}
    )


@login_required
def gerenciar_servicos(request):
    servicos = Produto.objects.all().select_related("categoria")
    categorias = Categoria.objects.all()

    q = request.GET.get("q")
    cat = request.GET.get("categoria")
    status = request.GET.get("status")

    if q:
        servicos = servicos.filter(nome__icontains=q)
    if cat:
        servicos = servicos.filter(categoria_id=cat)
    if status == "ativo":
        servicos = servicos.filter(ativo=True)
    elif status == "inativo":
        servicos = servicos.filter(ativo=False)

    total_servicos = Produto.objects.count()
    total_ativos = Produto.objects.filter(ativo=True).count()
    total_inativos = Produto.objects.filter(ativo=False).count()

    contexto = {
        "servicos": servicos,
        "categorias": categorias,
        "total_servicos": total_servicos,
        "total_ativos": total_ativos,
        "total_inativos": total_inativos,
    }
    return render(request, "taverna/gerenciar_servicos.html", contexto)


@login_required
def cadastrar_servico(request):
    categorias = Categoria.objects.all()
    if request.method == "POST":
        nome = request.POST.get("nome")
        descricao = request.POST.get("descricao")
        preco = request.POST.get("preco")
        categoria_id = request.POST.get("categoria")
        estoque = request.POST.get("estoque", 0)
        foto = request.POST.get("foto")
        ativo = request.POST.get("ativo") == "on"

        if nome and preco and categoria_id:
            categoria = get_object_or_404(Categoria, id=categoria_id)
            Produto.objects.create(
                nome=nome,
                descricao=descricao,
                preco=preco,
                categoria=categoria,
                estoque=estoque,
                foto=foto,
                ativo=ativo,
            )
            messages.success(request, "Serviço/Jogo cadastrado com sucesso!")
            return redirect("gerenciar_servicos")

    return render(
        request, "taverna/cadastrar_servico.html", {"categorias": categorias}
    )


@login_required
def editar_servico(request, servico_id):
    servico = get_object_or_404(Produto, id=servico_id)
    categorias = Categoria.objects.all()

    if request.method == "POST":
        servico.nome = request.POST.get("nome")
        servico.descricao = request.POST.get("descricao")
        servico.preco = request.POST.get("preco")
        categoria_id = request.POST.get("categoria")
        servico.categoria = get_object_or_404(Categoria, id=categoria_id)
        servico.estoque = request.POST.get("estoque", 0)
        servico.foto = request.POST.get("foto")
        servico.ativo = request.POST.get("ativo") == "on"
        servico.save()

        messages.success(request, "Serviço/Jogo atualizado com sucesso!")
        return redirect("gerenciar_servicos")

    return render(
        request,
        "taverna/editar_servico.html",
        {"servico": servico, "categorias": categorias},
    )


@login_required
def excluir_servico(request, servico_id):
    servico = get_object_or_404(Produto, id=servico_id)
    servico.delete()
    messages.success(request, "Serviço/Jogo removido com sucesso!")
    return redirect("gerenciar_servicos")


@login_required
def gerenciar_equipe(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        cargo = request.POST.get("cargo")
        biografia = request.POST.get("biografia")
        foto_url = request.POST.get("foto_url")
        if nome:
            inserido = adicionar_integrante({
                "nome": nome,
                "cargo": cargo,
                "biografia": biografia,
                "foto_url": foto_url,
            })
            if inserido:
                messages.success(
                    request, "Novo integrante adicionado ao Supabase!"
                )
            else:
                messages.warning(
                    request,
                    "Não foi possível adicionar o integrante. Veja o terminal.",
                )
            return redirect("gerenciar_equipe")

    integrantes = buscar_integrantes()
    return render(
        request, "taverna/gerenciar_equipe.html", {"integrantes": integrantes}
    )


@login_required
def editar_integrante(request, integrante_id):
    integrantes = buscar_integrantes()
    integrante_atual = next(
        (i for i in integrantes if str(i.get("id")) == str(integrante_id)), None
    )

    if integrante_atual is None and request.method == "GET":
        messages.error(request, "Integrante não encontrado.")
        return redirect("gerenciar_equipe")

    if request.method == "POST":
        dados_atualizados = {
            "nome": request.POST.get("nome"),
            "cargo": request.POST.get("cargo"),
            "biografia": request.POST.get("biografia"),
            "foto_url": request.POST.get("foto_url"),
        }

        try:
            target_id = int(integrante_id)
        except ValueError:
            target_id = integrante_id

        atualizado = atualizar_integrante(target_id, dados_atualizados)
        if atualizado:
            messages.success(
                request, "Integrante atualizado com sucesso no Supabase!"
            )
        else:
            messages.warning(
                request,
                "Nenhuma linha foi alterada no Supabase. Veja o terminal.",
            )

        return redirect("gerenciar_equipe")

    return render(
        request,
        "taverna/editar_integrante.html",
        {"integrante": integrante_atual},
    )


@login_required
def excluir_integrante(request, integrante_id):
    try:
        target_id = int(integrante_id)
    except ValueError:
        target_id = integrante_id

    removido = deletar_integrante(target_id)
    if removido:
        messages.success(request, "Integrante removido do Supabase!")
    else:
        messages.warning(
            request, "Nenhum integrante foi removido. Veja o terminal."
        )
    return redirect("gerenciar_equipe")


@login_required
def relatorios(request):
    total_servicos = Produto.objects.count()
    servicos_ativos = Produto.objects.filter(ativo=True).count()
    servicos_inativos = Produto.objects.filter(ativo=False).count()

    categorias_qs = Categoria.objects.annotate(total=Count("produto")).order_by(
        "nome"
    )
    categorias_labels = [cat.nome for cat in categorias_qs]
    categorias_valores = [cat.total for cat in categorias_qs]

    contexto = {
        "total_servicos": total_servicos,
        "servicos_ativos": servicos_ativos,
        "servicos_inativos": servicos_inativos,
        "categorias_labels_json": json.dumps(categorias_labels),
        "categorias_valores_json": json.dumps(categorias_valores),
    }
    return render(request, "taverna/relatorios.html", contexto)