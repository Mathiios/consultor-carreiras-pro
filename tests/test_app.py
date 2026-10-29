"""Testes de fumaça da interface Streamlit (navegação do wizard e resultado)."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def iniciar() -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    return at


def clicar(at: AppTest, texto: str) -> AppTest:
    for botao in at.button:
        if texto in botao.label:
            botao.click().run()
            assert not at.exception, at.exception
            return at
    raise AssertionError(f"botão '{texto}' não encontrado: {[b.label for b in at.button]}")


def responder_objetivos(at: AppTest) -> AppTest:
    for radio in at.radio:
        radio.set_value(radio.options[0]).run()
        assert not at.exception, at.exception
    return at


def test_pagina_inicial_renderiza():
    at = iniciar()
    assert at.title
    assert "Consultor" in at.title[0].value
    assert at.session_state["etapa"] == 0
    assert any("Perfil pessoal" in markdown.value for markdown in at.subheader)


def test_navegacao_entre_etapas():
    at = iniciar()
    clicar(at, "Continuar")
    assert at.session_state["etapa"] == 1
    assert any("Afinidades" in markdown.value for markdown in at.subheader)

    clicar(at, "Continuar")
    assert at.session_state["etapa"] == 2
    assert any("Objetivos" in markdown.value for markdown in at.subheader)

    clicar(at, "Voltar")
    assert at.session_state["etapa"] == 1


def test_bloqueia_calculo_sem_respostas_obrigatorias():
    at = iniciar()
    clicar(at, "Continuar")
    clicar(at, "Continuar")
    clicar(at, "Ver meu resultado")
    assert at.session_state["etapa"] == 2
    assert at.error
    assert "responda" in at.error[0].value.lower()


def test_fluxo_completo_devolve_resultado():
    at = iniciar()
    clicar(at, "Continuar")

    # perfil visual/front-end: todas as afinidades em 1, exceto design
    for slider in at.slider:
        if "design" in slider.label.lower():
            slider.set_value(5).run()
            assert not at.exception, at.exception
        elif "horas" not in slider.label.lower():
            slider.set_value(1).run()

    at.selectbox[0].set_value("javascript").run()
    assert not at.exception, at.exception
    clicar(at, "Continuar")
    responder_objetivos(at)
    clicar(at, "Ver meu resultado")

    assert at.session_state["etapa"] == 3
    assert not at.exception, at.exception
    assert len(at.metric) >= 4
    assert any("lugar" in metrica.label for metrica in at.metric)
    assert at.dataframe or at.markdown


def test_resultado_mostra_plano_e_ranking():
    at = iniciar()
    clicar(at, "Continuar")
    clicar(at, "Continuar")
    responder_objetivos(at)
    clicar(at, "Ver meu resultado")

    assert not at.exception, at.exception
    textos = " ".join(markdown.value for markdown in at.markdown)
    rotulos = " ".join(expander.label for expander in at.expander)
    assert "Ranking completo" in textos
    assert "Skill gaps" in textos
    assert "Roadmap" in textos
    assert "Certificações" in textos
    assert "Como o motor" in rotulos


def test_botao_recomecar_volta_ao_inicio():
    at = iniciar()
    clicar(at, "Continuar")
    clicar(at, "Continuar")
    responder_objetivos(at)
    clicar(at, "Ver meu resultado")
    assert at.session_state["etapa"] == 3

    clicar(at, "Recomeçar")
    assert at.session_state["etapa"] == 0
    assert at.session_state["resp_logica"] == 3
