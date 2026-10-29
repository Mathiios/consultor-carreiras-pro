"""Consultor Avançado de Carreiras em TI.

Sistema especialista baseado em regras com pontuação ponderada.
"""

from .base_conhecimento import BaseConhecimento, ErroBaseConhecimento, carregar
from .motor import Compatibilidade, MotorInferencia, Resultado, avaliar, motor_padrao

__version__ = "2.0.0"

__all__ = [
    "BaseConhecimento",
    "Compatibilidade",
    "ErroBaseConhecimento",
    "MotorInferencia",
    "Resultado",
    "avaliar",
    "carregar",
    "motor_padrao",
]
