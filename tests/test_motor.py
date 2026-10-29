"""Testes do motor de inferência: cálculo, bordas e desacoplamento da base."""

from __future__ import annotations

import json

import pytest

from consultor_pro import ErroBaseConhecimento, MotorInferencia, carregar
from consultor_pro.base_conhecimento import CAMINHO_PADRAO
from consultor_pro.motor import avaliar, motor_padrao
from tests.personas import PERSONAS, perfil, por_chave


@pytest.fixture(scope="module")
def base():
    return carregar()


@pytest.fixture(scope="module")
def motor(base):
    return MotorInferencia(base)


# ----------------------------------------------------------------------
# Integridade da base de conhecimento
# ----------------------------------------------------------------------
def test_base_tem_estrutura_minima(base):
    assert len(base.trilhas) == 10
    assert len(base.dimensoes) >= 8
    assert len(base.regras) >= 25
    assert len(base.tecnologias) >= 20
    assert base.ajuste_maximo_regras > 0
    assert base.escala_min == 1 and base.escala_max == 5


def test_base_cobre_todas_as_dimensoes_para_todas_as_trilhas(base):
    for dimensao in base.dimensoes:
        for trilha in base.trilhas:
            assert dimensao.id in base.matriz
            assert trilha in base.matriz[dimensao.id]


def test_base_json_invalida_falha_com_mensagem(tmp_path):
    bruto = json.loads(CAMINHO_PADRAO.read_text(encoding="utf-8"))
    bruto["matriz_afinidade"]["logica"]["inexistente"] = 3
    caminho = tmp_path / "quebrada.json"
    caminho.write_text(json.dumps(bruto), encoding="utf-8")

    with pytest.raises(ErroBaseConhecimento):
        carregar(caminho)


def test_base_json_com_regra_invalida_falha(tmp_path):
    bruto = json.loads(CAMINHO_PADRAO.read_text(encoding="utf-8"))
    bruto["regras"][0]["efeitos"][0]["trilha"] = "trilha_fantasma"
    caminho = tmp_path / "regra_invalida.json"
    caminho.write_text(json.dumps(bruto), encoding="utf-8")

    with pytest.raises(ErroBaseConhecimento):
        carregar(caminho)


def test_conhecimento_vem_do_json_e_nao_do_codigo(tmp_path, base):
    """Alterar o JSON deve alterar o resultado (base realmente desacoplada)."""
    bruto = json.loads(CAMINHO_PADRAO.read_text(encoding="utf-8"))
    # zera todos os pesos e dá nota máxima de afinidade visual para "produto"
    for dimensao in bruto["matriz_afinidade"]:
        for trilha in bruto["matriz_afinidade"][dimensao]:
            bruto["matriz_afinidade"][dimensao][trilha] = 0
    bruto["matriz_afinidade"]["visual"]["produto"] = 5

    caminho = tmp_path / "custom.json"
    caminho.write_text(json.dumps(bruto), encoding="utf-8")

    motor_custom = MotorInferencia(carregar(caminho))
    respostas = perfil(
        1, 1, 5, 1, 1, 1, 1, 5,
        linguagem="nenhuma", entrega="negocio", objetivo="liderar_negocio", estilo="pessoas",
    )
    resultado = motor_custom.avaliar(respostas)
    assert resultado.destaque.trilha == "produto"
    assert resultado.destaque.percentual == pytest.approx(100.0, abs=0.2)


# ----------------------------------------------------------------------
# Cálculo e invariantes
# ----------------------------------------------------------------------
@pytest.mark.parametrize("persona", PERSONAS, ids=[p.chave for p in PERSONAS])
def test_percentuais_sempre_no_intervalo(motor, persona):
    resultado = motor.avaliar(persona.respostas)
    assert len(resultado.compatibilidades) == 10
    for item in resultado.compatibilidades:
        assert 0 <= item.percentual <= 100
        assert 0 <= item.base <= 100
        assert abs(item.ajuste) <= motor.base.ajuste_maximo_regras + 0.01


@pytest.mark.parametrize("persona", PERSONAS, ids=[p.chave for p in PERSONAS])
def test_ranking_ordenado_e_top3(motor, persona):
    resultado = motor.avaliar(persona.respostas)
    percentuais = [item.percentual for item in resultado.compatibilidades]
    assert percentuais == sorted(percentuais, reverse=True)
    assert len(resultado.top3) == 3
    assert resultado.destaque is resultado.compatibilidades[0]


def test_avaliacao_e_deterministica(motor):
    respostas = por_chave("gustavo").respostas
    primeira = motor.avaliar(dict(respostas))
    segunda = motor.avaliar(dict(respostas))
    assert [(c.trilha, c.percentual) for c in primeira.compatibilidades] == [
        (c.trilha, c.percentual) for c in segunda.compatibilidades
    ]


def test_respostas_ausentes_usam_neutro(motor):
    resultado = motor.avaliar({})
    assert len(resultado.compatibilidades) == 10
    for item in resultado.compatibilidades:
        assert item.base == pytest.approx(50.0, abs=0.5)


def test_respostas_fora_da_escala_sao_limitadas(motor):
    extremo = motor.avaliar({d.id: 99 for d in motor.base.dimensoes})
    minimo = motor.avaliar({d.id: -5 for d in motor.base.dimensoes})
    assert extremo.respostas["logica"] == motor.base.escala_max
    assert minimo.respostas["logica"] == motor.base.escala_min


def test_respostas_invalidas_nao_quebram(motor):
    respostas = {"logica": "muito", "matematica": None, "linguagem": "rust"}
    resultado = motor.avaliar(respostas)
    assert resultado.respostas["linguagem"] is None
    assert resultado.respostas["logica"] == 3


def test_ajuste_das_regras_respeita_limite(motor):
    """Perfil que ativa muitas regras não pode estourar o limite configurado."""
    extremo = perfil(
        5, 5, 5, 5, 5, 5, 5, 5,
        linguagem="python", entrega="usuario", objetivo="prever_dados", estilo="criativo",
    )
    resultado = motor.avaliar(extremo)
    limite = motor.base.ajuste_maximo_regras
    for item in resultado.compatibilidades:
        assert abs(item.ajuste) <= limite + 0.01


# ----------------------------------------------------------------------
# Regras e casos de borda
# ----------------------------------------------------------------------
def test_todas_as_trilhas_sao_alcancaveis(motor):
    vencedoras = {motor.avaliar(p.respostas).destaque.trilha for p in PERSONAS}
    assert vencedoras == set(motor.base.trilhas)


def test_empate_tecnico_gera_alerta(motor):
    resultado = motor.avaliar(por_chave("karina").respostas)
    assert resultado.margem < 3
    assert any("Empate técnico" in alerta for alerta in resultado.alertas)


def test_penalidade_de_matematica_afasta_ciencia_de_dados(motor):
    resultado = motor.avaliar(por_chave("marcos").respostas)
    ciencia = resultado.por_trilha("ciencia_dados")
    assert resultado.destaque.trilha != "ciencia_dados"
    assert ciencia.ajuste < 0
    assert any(regra.regra.id == "P01" for regra in resultado.regras_disparadas)


def test_perfil_sem_afinidades_emite_alertas(motor):
    resultado = motor.avaliar(por_chave("leandro").respostas)
    assert any("pouco definido" in alerta for alerta in resultado.alertas)
    assert any("uniformes" in alerta for alerta in resultado.alertas)


def test_regras_disparadas_tem_efeito_aplicado(motor):
    resultado = motor.avaliar(por_chave("gustavo").respostas)
    assert resultado.regras_disparadas
    for regra in resultado.regras_disparadas:
        assert regra.efeitos_aplicados
        for delta in regra.efeitos_aplicados.values():
            assert abs(delta) <= regra.regra.peso_maximo + 0.01


def test_distincao_ciencia_vs_engenharia_de_dados(motor, base):
    """Fase 1: a trilha escolhida deve depender de infraestrutura/automação."""
    analitico = perfil(
        4, 5, 1, 1, 5, 1, 1, 1,
        linguagem="python", entrega="dados", objetivo="prever_dados", estilo="investigativo",
    )
    plataforma = perfil(
        4, 4, 1, 5, 5, 2, 5, 1,
        linguagem="sql", entrega="dados", objetivo="prever_dados", estilo="processo_metodo",
    )
    assert motor.avaliar(analitico).destaque.trilha == "ciencia_dados"
    assert motor.avaliar(plataforma).destaque.trilha == "engenharia_dados"


def test_atributos_de_visualizacao(motor):
    resultado = motor.avaliar(por_chave("ana").respostas)
    afinidades = resultado.afinidades_usuario()
    ideal = resultado.perfil_ideal("ciencia_dados")
    assert set(afinidades) == set(ideal)
    assert all(1 <= valor <= 5 for valor in afinidades.values())
    assert all(1 <= valor <= 5 for valor in ideal.values())
    assert resultado.resumo().endswith("% de compatibilidade")


def test_motor_padrao_reaproveita_instancia():
    assert motor_padrao() is motor_padrao()
    resultado = avaliar(por_chave("carla").respostas)
    assert resultado.destaque.trilha == "frontend"
