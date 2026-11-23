from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quem-somos/", views.quem_somos, name="quem_somos"),
    path("produtos/", views.produtos, name="produtos"),
    path("contato/", views.contato, name="contato"),
    path("cadastrar/", views.cadastrar_usuario, name="cadastrar"),
    path("login/", views.login_usuario, name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    # Rotas de Recuperação de Senha (usando o teu password_reset.html)
    path(
        "password_reset/",
        PasswordResetView.as_view(template_name="taverna/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="taverna/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="taverna/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="taverna/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Restante das tuas rotas...
    path(
        "adicionar-ao-pedido/<int:produto_id>/",
        views.adicionar_ao_pedido,
        name="adicionar_ao_pedido",
    ),
    path("meus-pedidos/", views.meus_pedidos, name="meus_pedidos"),
    path("pedido/editar/<int:item_id>/", views.editar_pedido, name="editar_pedido"),
    path(
        "pedido/remover/<int:item_id>/",
        views.remover_pedido,
        name="remover_pedido",
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("editar-perfil/", views.editar_perfil, name="editar_perfil"),
    path(
        "gerenciar/contatos/", views.gerenciar_contatos, name="gerenciar_contatos"
    ),
    path(
        "gerenciar/servicos/", views.gerenciar_servicos, name="gerenciar_servicos"
    ),
    path(
        "gerenciar/servicos/novo/",
        views.cadastrar_servico,
        name="cadastrar_servico",
    ),
    path(
        "gerenciar/servicos/editar/<int:servico_id>/",
        views.editar_servico,
        name="editar_servico",
    ),
    path(
        "gerenciar/servicos/excluir/<int:servico_id>/",
        views.excluir_servico,
        name="excluir_servico",
    ),
    path("gerenciar/equipe/", views.gerenciar_equipe, name="gerenciar_equipe"),
    path(
        "gerenciar/equipe/editar/<int:integrante_id>/",
        views.editar_integrante,
        name="editar_integrante",
    ),
    path(
        "gerenciar/equipe/excluir/<int:integrante_id>/",
        views.excluir_integrante,
        name="excluir_integrante",
    ),
    path("relatorios/", views.relatorios, name="relatorios"),
]