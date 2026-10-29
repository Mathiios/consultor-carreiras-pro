"""Consultor Avançado de Carreiras em TI.

Sistema especialista baseado em regras com pontuação ponderada:

* :mod:`consultor_pro.base_conhecimento` — carrega e valida o JSON;
* :mod:`consultor_pro.motor` — calcula ranking de compatibilidade;
* :mod:`consultor_pro.recomendacao` — skill gaps e plano de ação.
"""

from .base_conhecimento import BaseConhecimento, ErroBaseConhecimento, carregar
from .motor import Compatibilidade, MotorInferencia, Resultado, avaliar, motor_padrao
from .recomendacao import Lacuna, PlanoAcao, analisar, niveis_por_skill

__version__ = "2.0.0"

__all__ = [
    "BaseConhecimento",
    "Compatibilidade",
    "ErroBaseConhecimento",
    "Lacuna",
    "MotorInferencia",
    "PlanoAcao",
    "Resultado",
    "analisar",
    "avaliar",
    "carregar",
    "motor_padrao",
    "niveis_por_skill",
]
