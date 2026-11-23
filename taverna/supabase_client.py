import os
from supabase import Client, create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

print("--- A TENTAR LIGAR AO SUPABASE ---")
print("URL:", SUPABASE_URL)

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(">>> CLIENTE SUPABASE CRIADO COM SUCESSO! <<<")
    except Exception as e:
        print(">>> ERRO CRÍTICO AO CRIAR CLIENTE SUPABASE:", e)
else:
    print(">>> AVISO: SUPABASE_URL ou SUPABASE_KEY não configurados no ambiente. <<<")


def buscar_integrantes():
    """Busca os integrantes cadastrados no Supabase."""
    try:
        if supabase:
            response = supabase.table("integrantes").select("*").execute()
            print("Resposta do Supabase ao buscar:", response.data)
            if response.data:
                return response.data
    except Exception as e:
        print("ERRO em buscar_integrantes:", e)

    return [
        {
            "id": 1,
            "nome": "Mariana",
            "cargo": "PO",
            "biografia": "Responsável por gerenciar o projeto.",
            "foto_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=60",
        },
        {
            "id": 2,
            "nome": "Felipe",
            "cargo": "Desenvolvedor",
            "biografia": "Responsável pelo desenvolvimento.",
            "foto_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&auto=format&fit=crop&q=60",
        },
        {
            "id": 3,
            "nome": "Juliano",
            "cargo": "Desenvolvedor",
            "biografia": "Responsável pela arquitetura.",
            "foto_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&auto=format&fit=crop&q=60",
        },
    ]


def adicionar_integrante(dados):
    try:
        if supabase:
            resposta = supabase.table("integrantes").insert(dados).execute()
            print("Inserção executada:", resposta)
            return resposta.data
    except Exception as e:
        print("ERRO em adicionar_integrante:", e)
    return None


def atualizar_integrante(integrante_id, dados):
    try:
        if supabase:
            resposta = (
                supabase.table("integrantes")
                .update(dados)
                .eq("id", integrante_id)
                .execute()
            )
            print("Atualização executada:", resposta)
            return resposta.data
    except Exception as e:
        print("ERRO em atualizar_integrante:", e)
    return None


def deletar_integrante(integrante_id):
    try:
        if supabase:
            resposta = (
                supabase.table("integrantes")
                .delete()
                .eq("id", integrante_id)
                .execute()
            )
            print("Remoção executada:", resposta)
            return resposta.data
    except Exception as e:
        print("ERRO em deletar_integrante:", e)
    return None