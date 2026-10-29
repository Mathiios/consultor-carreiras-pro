"""Testes do módulo de lacunas (skill gaps) e plano de ação."""

from __future__ import annotations

import pytest

from consultor_pro import MotorInferencia, analisar, carregar, niveis_por_skill
from tests.personas import perfil, por_chave


@pytest.fixture(scope="module")
def base():
    return carregar()


@pytest.fixture(scope="module")
def motor(base):
    return MotorInferencia(base)


def test_niveis_por_skill_mapeia_tecnologias(base):
    niveis = niveis_por_skill(base, estudadas=["python"], dominadas=["sql"])
    assert niveis["python"] == 2
    assert niveis["sql"] >= 3
    assert niveis["logica_programacao"] >= 1


def test_niveis_com_tecnologia_desconhecida_ignoram(base):
    assert niveis_por_skill(base, ["rust", "cobol"]) == {}


def test_iniciante_tem_lacunas_em_todas_as_competencias(base, motor):
    persona = por_chave("leandro")
    resultado = motor.avaliar(persona.respostas)
    plano = analisar(base, resultado)
    trilha = base.trilhas[plano.trilha]
    assert len(plano.lacunas) == len(trilha.competencias)
    assert plano.forcas == []
    assert plano.cobertura == pytest.approx(0.0, abs=0.1)


def test_tecnologias_reduzem_lacunas_e_aumentam_cobertura(base, motor):
    respostas = dict(por_chave("carla").respostas)
    sem_conhecimento = analisar(base, motor.avaliar({**respostas, "tecnologias_estudadas": []}))
    com_conhecimento = analisar(
        base,
        motor.avaliar(
            {**respostas, "tecnologias_estudadas": ["html_css", "javascript", "react", "git"]}
        ),
    )
    assert com_conhecimento.cobertura > sem_conhecimento.cobertura
    assert len(com_conhecimento.lacunas) < len(sem_conhecimento.lacunas)


def test_dominio_completo_zera_lacunas(base, motor):
    toda_a_trilha = [
        "python", "nodejs", "sql", "docker", "git", "postman", "pytest", "github_actions"
    ]
    respostas = {
        **por_chave("eduardo").respostas,
        "tecnologias_estudadas": [],
        "tecnologias_dominadas": toda_a_trilha,
    }
    plano = analisar(base, motor.avaliar(respostas), trilha="backend")
    assert plano.lacunas == []
    assert plano.cobertura > 90
    assert plano.proximos_passos()[0].startswith("Você já cobre")


def test_plano_tem_fases_ordenadas_e_estimativas(base, motor):
    respostas = por_chave("ana").respostas
    plano = analisar(base, motor.avaliar(respostas), horas_semana=12)

    assert plano.trilha == "ciencia_dados"
    assert plano.horas_semana == 12
    assert [fase.ordem for fase in plano.fases] == list(range(1, len(plano.fases) + 1))
    assert plano.fases[0].tipo == "nivelamento"
    assert all(fase.horas > 0 and fase.topicos for fase in plano.fases)
    assert plano.semanas_estimadas == pytest.approx(
        plano.horas_totais / 12, abs=1.0
    )
    assert plano.certificacoes and plano.projetos and plano.tecnologias


def test_carga_horaria_invalida_e_protegida(base, motor):
    respostas = {**por_chave("bruno").respostas, "horas_semana": 0}
    plano = analisar(base, motor.avaliar(respostas))
    assert plano.horas_semana == 1
    assert plano.semanas_estimadas >= 1
    assert all(fase.semanas(plano.horas_semana) >= 1 for fase in plano.fases)


def test_lacunas_ordenadas_por_prioridade(base, motor):
    plano = analisar(base, motor.avaliar(por_chave("igor").respostas))
    prioridades = [lacuna.prioridade for lacuna in plano.lacunas]
    assert prioridades == sorted(prioridades, reverse=True)
    assert all(lacuna.criticidade in {"Crítica", "Alta", "Moderada", "Leve"} for lacuna in plano.lacunas)


def test_plano_de_trilha_especifica(base, motor):
    """O plano pode ser gerado para qualquer trilha do Top 3, não só a 1ª."""
    resultado = motor.avaliar(por_chave("gustavo").respostas)
    segunda = resultado.compatibilidades[1].trilha
    plano = analisar(base, resultado, trilha=segunda)
    assert plano.trilha == segunda
    assert plano.nome_trilha == base.trilhas[segunda].nome


def test_meta_de_senioridade_e_respeitada(base, motor):
    respostas = {**por_chave("helena").respostas, "meta_senioridade": "Pleno"}
    plano = analisar(base, motor.avaliar(respostas))
    assert plano.meta == "Pleno"


def test_sem_tecnologias_e_sem_horas_usa_padrao(base, motor):
    respostas = {
        "logica": 4, "matematica": 4, "visual": 1, "infra": 3,
        "dados": 4, "seguranca": 1, "automacao": 2, "gestao": 1,
        "linguagem": "python", "entrega": "dados", "objetivo": "prever_dados",
        "estilo": "investigativo",
    }
    plano = analisar(base, motor.avaliar(respostas))
    assert plano.horas_semana == 10
    assert plano.lacunas
