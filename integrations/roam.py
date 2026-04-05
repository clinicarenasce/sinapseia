"""
Roam Research integration — placeholder for future implementation.

The Roam API is currently invite-only / in limited beta.
This module exposes the same interface so the UI can display it
as "coming soon" without crashing.
"""


def tem_roam_config():
    return False


def salvar_roam(conteudo, nome_inteligente, nome_custom, callbacks):
    callbacks["on_erro"]("Integracao com Roam Research em desenvolvimento. Em breve!")
