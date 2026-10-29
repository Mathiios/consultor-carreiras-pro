"""Validação do motor contra personas reais (Fase 5)."""

from __future__ import annotations

import pytest

from consultor_pro import MotorInferencia, analisar, carregar
from tests.personas import PERSONAS


@pytest.fixture(scope="module")
def base():
    return carregar()


@pytest.fixture(scope="module")
def motor(base):
    return MotorInferencia(base)


@pytest.mark.parametrize("persona", PERSONAS, ids=[p.chave for p in PERSONAS])
def test_persona_recebe_trilha_esperada(motor, persona):
    resultado = motor.avaliar(persona.respostas)
    assert resultado.destaque.trilha in persona.esperado, (
        f"{persona.nome}: esperado {persona.esperado}, "
        f"obtido {[(c.trilha, c.percentual) for c in resultado.top3]}"
    )


@pytest.mark.parametrize("persona", PERSONAS, ids=[p.chave for p in PERSONAS])
def test_persona_gera_plano_coerente(base, motor, persona):
    resultado = motor.avaliar(persona.respostas)
    plano = analisar(base, resultado)

    assert plano.trilha == resultado.destaque.trilha
    assert 0 <= plano.cobertura <= 100
    assert plano.fases
    assert plano.semanas_estimadas >= 1
    assert plano.horas_totais > 0


def test_cobertura_de_todas_as_trilhas(base, motor):
    vencedoras = {motor.avaliar(p.respostas).destaque.trilha for p in PERSONAS}
    assert len(vencedoras) == 10, f"trilhas não cobertas: {set(base.trilhas) - vencedoras}"


def test_caso_ambiguo_tem_top3_apertado(motor):
    resultado = motor.avaliar(PERSONAS[10].respostas)  # Karina
    tres_primeiros = [item.percentual for item in resultado.top3]
    assert tres_primeiros[0] - tres_primeiros[2] < 5
    assert resultado.alertas


def test_percentuais_de_personas_sao_plausiveis(motor):
    for persona in PERSONAS:
        if "edge" in persona.tags:
            continue
        resultado = motor.avaliar(persona.respostas)
        assert resultado.destaque.percentual >= 60, (
            f"{persona.nome} ficou com {resultado.destaque.percentual:.1f}%"
        )
