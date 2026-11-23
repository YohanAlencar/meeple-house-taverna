import os
from supabase import Client, create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

ultimo_erro_supabase = None

print("--- A TENTAR LIGAR AO SUPABASE ---", flush=True)
print("URL:", SUPABASE_URL, flush=True)

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(">>> CLIENTE SUPABASE CRIADO COM SUCESSO! <<<", flush=True)
    except Exception as e:
        ultimo_erro_supabase = f"Erro ao criar cliente: {e}"
        print(">>> ERRO CRÍTICO AO CRIAR CLIENTE SUPABASE:", e, flush=True)
else:
    ultimo_erro_supabase = "SUPABASE_URL ou SUPABASE_KEY vazios no ambiente."
    print(
        ">>> AVISO: SUPABASE_URL ou SUPABASE_KEY não configurados no ambiente. <<<",
        flush=True,
    )


def buscar_integrantes():
    """Busca os integrantes cadastrados no Supabase."""
    global ultimo_erro_supabase
    try:
        if supabase:
            response = supabase.table("integrantes").select("*").execute()
            print("Resposta do Supabase ao buscar:", response.data, flush=True)
            if response.data:
                ultimo_erro_supabase = None
                return response.data
            ultimo_erro_supabase = "Supabase respondeu, mas a tabela 'integrantes' está vazia (sem linhas ou bloqueada por RLS)."
        else:
            if not ultimo_erro_supabase:
                ultimo_erro_supabase = "Cliente supabase é None."
    except Exception as e:
        ultimo_erro_supabase = f"Erro em buscar_integrantes: {e}"
        print("ERRO em buscar_integrantes:", e, flush=True)

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
            print("Inserção executada:", resposta, flush=True)
            return resposta.data
    except Exception as e:
        print("ERRO em adicionar_integrante:", e, flush=True)
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
            print("Atualização executada:", resposta, flush=True)
            return resposta.data
    except Exception as e:
        print("ERRO em atualizar_integrante:", e, flush=True)
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
            print("Remoção executada:", resposta, flush=True)
            return resposta.data
    except Exception as e:
        print("ERRO em deletar_integrante:", e, flush=True)
    return None