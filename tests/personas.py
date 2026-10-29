"""Personas de validação do motor (Fase 5 — testes de robustez).

Cada persona representa um perfil real plausível de estudante/profissional.
O campo ``esperado`` lista as trilhas aceitáveis para o 1º lugar; as demais
são validadas apenas quanto a coerência (Top 3, percentuais, alertas).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def perfil(
    logica: int,
    matematica: int,
    visual: int,
    infra: int,
    dados: int,
    seguranca: int,
    automacao: int,
    gestao: int,
    linguagem: str,
    entrega: str,
    objetivo: str,
    estilo: str,
    estudadas: tuple[str, ...] = (),
    dominadas: tuple[str, ...] = (),
    horas: int = 10,
    meta: str = "Júnior",
) -> dict[str, Any]:
    return {
        "logica": logica,
        "matematica": matematica,
        "visual": visual,
        "infra": infra,
        "dados": dados,
        "seguranca": seguranca,
        "automacao": automacao,
        "gestao": gestao,
        "linguagem": linguagem,
        "entrega": entrega,
        "objetivo": objetivo,
        "estilo": estilo,
        "tecnologias_estudadas": list(estudadas),
        "tecnologias_dominadas": list(dominadas),
        "horas_semana": horas,
        "meta_senioridade": meta,
        "nome": "",
        "formacao": "Graduação em exatas (Eng., TI, Matemática)",
        "experiencia": "Estudante com projetos pessoais",
    }


@dataclass(frozen=True)
class Persona:
    chave: str
    nome: str
    descricao: str
    respostas: dict[str, Any]
    esperado: tuple[str, ...]
    observacao: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)


PERSONAS: tuple[Persona, ...] = (
    Persona(
        chave="ana",
        nome="Ana · Analítica",
        descricao="Forte em matemática e dados, pouca infraestrutura, quer prever com IA.",
        respostas=perfil(
            4, 5, 2, 1, 5, 1, 2, 2,
            linguagem="python",
            entrega="dados",
            objetivo="prever_dados",
            estilo="investigativo",
            estudadas=("python", "pandas", "sql"),
        ),
        esperado=("ciencia_dados",),
        tags=("dados",),
    ),
    Persona(
        chave="bruno",
        nome="Bruno · Segurança",
        descricao="Curte redes/Linux, investigação e proteção de sistemas.",
        respostas=perfil(
            4, 2, 1, 4, 2, 5, 3, 1,
            linguagem="linux",
            entrega="seguranca",
            objetivo="proteger",
            estilo="investigativo",
            estudadas=("linux", "redes"),
        ),
        esperado=("seguranca",),
        tags=("infra",),
    ),
    Persona(
        chave="carla",
        nome="Carla · Visual",
        descricao="Designer que migrou para programação, forte afinidade visual.",
        respostas=perfil(
            3, 1, 5, 1, 2, 1, 1, 2,
            linguagem="javascript",
            entrega="usuario",
            objetivo="criar_produtos",
            estilo="criativo",
            estudadas=("html_css", "javascript", "figma"),
        ),
        esperado=("frontend",),
        tags=("visual",),
    ),
    Persona(
        chave="diego",
        nome="Diego · Negócio",
        descricao="Perfil de gestão e comunicação, pouca mão na massa técnica.",
        respostas=perfil(
            2, 2, 3, 1, 2, 1, 1, 5,
            linguagem="nenhuma",
            entrega="negocio",
            objetivo="liderar_negocio",
            estilo="pessoas",
            estudadas=("jira_scrum",),
        ),
        esperado=("produto",),
        tags=("negocio",),
    ),
    Persona(
        chave="eduardo",
        nome="Eduardo · Back-end",
        descricao="Gosta de lógica profunda, APIs e modelagem de dados.",
        respostas=perfil(
            5, 3, 1, 2, 3, 2, 2, 1,
            linguagem="python",
            entrega="usuario",
            objetivo="criar_produtos",
            estilo="logica_profunda",
            estudadas=("python", "sql", "git"),
        ),
        esperado=("backend",),
        tags=("codigo",),
    ),
    Persona(
        chave="fernanda",
        nome="Fernanda · Engenharia de Dados",
        descricao="Dados + infraestrutura + automação de pipelines.",
        respostas=perfil(
            4, 4, 1, 4, 5, 2, 4, 1,
            linguagem="sql",
            entrega="dados",
            objetivo="prever_dados",
            estilo="processo_metodo",
            estudadas=("sql", "python", "spark"),
        ),
        esperado=("engenharia_dados",),
        tags=("dados", "infra"),
    ),
    Persona(
        chave="gustavo",
        nome="Gustavo · DevOps",
        descricao="Infraestrutura + automação + Linux no dia a dia.",
        respostas=perfil(
            4, 2, 1, 5, 3, 3, 5, 2,
            linguagem="linux",
            entrega="infraestrutura",
            objetivo="escalar_infra",
            estilo="processo_metodo",
            estudadas=("linux", "docker", "github_actions"),
        ),
        esperado=("devops",),
        tags=("infra",),
    ),
    Persona(
        chave="helena",
        nome="Helena · Cloud",
        descricao="Gosta de arquitetar ambientes e escala, menos de automatizar entrega.",
        respostas=perfil(
            3, 2, 1, 5, 2, 3, 3, 2,
            linguagem="linux",
            entrega="infraestrutura",
            objetivo="escalar_infra",
            estilo="processo_metodo",
            estudadas=("aws", "linux"),
        ),
        esperado=("cloud",),
        tags=("infra",),
    ),
    Persona(
        chave="igor",
        nome="Igor · Mobile",
        descricao="Visual + ferramentas mobile, quer criar produtos no celular.",
        respostas=perfil(
            4, 2, 4, 1, 1, 1, 1, 1,
            linguagem="mobile",
            entrega="usuario",
            objetivo="criar_produtos",
            estilo="criativo",
            estudadas=("flutter",),
        ),
        esperado=("mobile",),
        tags=("visual",),
    ),
    Persona(
        chave="juliana",
        nome="Juliana · QA",
        descricao="Lógica com forte preferência por método, testes e automação.",
        respostas=perfil(
            4, 2, 1, 2, 3, 2, 3, 2,
            linguagem="python",
            entrega="usuario",
            objetivo="criar_produtos",
            estilo="processo_metodo",
            estudadas=("pytest", "postman"),
        ),
        esperado=("qa",),
        tags=("processo",),
    ),
    Persona(
        chave="karina",
        nome="Karina · Ambígua (dados × web)",
        descricao="Gosta tanto de dados quanto de interface: caso limite de empate triplo.",
        respostas=perfil(
            4, 3, 4, 3, 5, 1, 3, 2,
            linguagem="python",
            entrega="dados",
            objetivo="prever_dados",
            estilo="investigativo",
            estudadas=("sql", "pandas"),
        ),
        esperado=("ciencia_dados", "frontend"),
        observacao="Top 3 praticamente empatado: o motor deve sinalizar empate técnico.",
        tags=("edge",),
    ),
    Persona(
        chave="leandro",
        nome="Leandro · Iniciante",
        descricao="Sem afinidades declaradas (todas as notas 1) e sem tecnologias.",
        respostas=perfil(
            1, 1, 1, 1, 1, 1, 1, 1,
            linguagem="nenhuma",
            entrega="usuario",
            objetivo="criar_produtos",
            estilo="pessoas",
        ),
        esperado=("backend", "qa", "frontend", "mobile", "produto", "devops", "cloud", "seguranca", "ciencia_dados", "engenharia_dados"),
        observacao="Caso limite: perfil indefinido, deve emitir alertas sem quebrar.",
        tags=("edge",),
    ),
    Persona(
        chave="marcos",
        nome="Marcos · Conflito (dados sem matemática)",
        descricao="Quer IA, mas declara pouca afinidade com matemática.",
        respostas=perfil(
            4, 1, 1, 4, 5, 2, 4, 1,
            linguagem="sql",
            entrega="dados",
            objetivo="prever_dados",
            estilo="processo_metodo",
            estudadas=("sql", "airflow"),
        ),
        esperado=("engenharia_dados", "devops", "backend", "qa", "ciencia_dados"),
        observacao="A regra P01 deve penalizar Ciência de Dados por falta de base matemática.",
        tags=("edge",),
    ),
)


def por_chave(chave: str) -> Persona:
    for persona in PERSONAS:
        if persona.chave == chave:
            return persona
    raise KeyError(chave)
