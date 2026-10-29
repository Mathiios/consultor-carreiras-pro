"""Consultor Avançado de Carreiras em TI.

Sistema especialista baseado em regras com pontuação ponderada.
"""

from .base_conhecimento import BaseConhecimento, ErroBaseConhecimento, carregar

__version__ = "2.0.0"

__all__ = ["BaseConhecimento", "ErroBaseConhecimento", "carregar"]
