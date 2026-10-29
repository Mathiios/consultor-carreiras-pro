# Relatório — Sistema Especialista para Mapeamento, Compatibilidade e Trilha de Carreira em TI

**Autor:** Matheus Lima
**Disciplina:** Sistemas Especialistas / Inteligência Artificial
**Implementação:** Python 3.10+ · Streamlit · JSON como base de conhecimento
**Repositório:** `consultor-carreiras-pro`

---

## 1. Contextualização e objetivo

Sistemas especialistas clássicos sofrem com a rigidez das regras `SE–ENTÃO`: o mundo real raramente é
preto no branco. Este trabalho implementa um **sistema especialista baseado em regras com tratamento de
incerteza e pontuação ponderada**, aplicado ao problema de **orientação de carreira em TI**.

O sistema atua como um consultor avançado que:

1. coleta **graus de afinidade** (Likert 1–5), em vez de respostas binárias;
2. calcula uma **matriz de compatibilidade percentual** para 10 trilhas;
3. identifica **lacunas de competências** (skill gaps) em relação ao nível júnior;
4. gera um **plano de ação individualizado** com roadmap, certificações e portfólio.

Diferente de um quiz de personalidade, o resultado é **auditável**: cada ponto percentual pode ser
rastreado até a dimensão da matriz ou a regra que o produziu.

---

## 2. Fase 1 — Engenharia do conhecimento e modelagem JSON

### 2.1 Estrutura escolhida

A base de conhecimento é um único arquivo JSON (`data/regras_carreiras.json`) com sete blocos:

| Bloco | Conteúdo |
|---|---|
| `escala_likert` | mínimo, máximo e rótulos da escala (1–5) |
| `dimensoes` | 8 dimensões de afinidade (id, pergunta, ajuda, etapa) |
| `categoricas` | 4 questões de múltipla escolha (linguagem, entrega, objetivo, estilo) |
| `matriz_afinidade` | peso (0–5) de cada dimensão para cada uma das 10 trilhas |
| `regras` | 38 regras com condições, efeitos, **certeza** e explicação |
| `competencias` / `tecnologias` | 43 skills e 30 tecnologias que as comprovam |
| `trilhas` | competências exigidas, roadmap, certificações e projetos |

Manter o conhecimento fora do código permite **revisar pesos e regras sem tocar no motor** e
versionar a evolução do conhecimento junto com o restante do projeto.

### 2.2 Matriz de afinidade (peso 0–5)

| Dimensão | Back | Front | Ciência | Eng. Dados | Segurança | DevOps | Cloud | Mobile | QA | Produto |
|---|---|---|---|---|---|---|---|---|---|---|
| Lógica | 5 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 1 |
| Matemática | 1 | 0 | 5 | 4 | 2 | 1 | 1 | 0 | 2 | 2 |
| Visual | 1 | 5 | 1 | 0 | 0 | 0 | 0 | 4 | 1 | 3 |
| Infraestrutura | 2 | 0 | 2 | 5 | 4 | 5 | 5 | 0 | 2 | 1 |
| Dados | 3 | 1 | 5 | 5 | 2 | 2 | 2 | 1 | 3 | 3 |
| Segurança | 1 | 0 | 1 | 1 | 5 | 2 | 3 | 1 | 1 | 1 |
| Automação | 2 | 1 | 1 | 3 | 2 | 5 | 4 | 1 | 3 | 1 |
| Gestão | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 5 |

A matriz completa, as 38 regras e o detalhamento das trilhas estão em
[`Base_de_Conhecimento.md`](Base_de_Conhecimento.md), **gerado automaticamente** por
`tools/gerar_docs.py` a partir do JSON (evita documentação dessincronizada).

### 2.3 Regras e tratamento de incerteza

As 38 regras se dividem em:

| Tipo | Quantidade | Função |
|---|---|---|
| Reforço | 25 | combinações de afinidades que fortalecem uma trilha |
| Desambiguação | 7 | separam pares naturalmente confundíveis |
| Penalidade | 6 | punem perfis incoerentes (evitam recomendação ingênua) |

Cada regra carrega um **fator de certeza** (0,8–1,0), aplicado ao efeito:
`efeito_efetivo = delta × certeza`. Essa é a forma de "incerteza" adotada — inspirada nos
**fatores de certeza** de MYCIN (MYCIN-like), mas aplicada como soma ponderada por trilha.

Exemplos de desambiguação (o coração do trabalho):

- **D01** — matemática ≥ 4, dados ≥ 3 e infraestrutura ≤ 2 → Ciência de Dados `+5`, Engenharia `−3`
  (perfil analítico, sem veia de plataforma);
- **D02** — dados ≥ 4, infraestrutura ≥ 4 e automação ≥ 3 → Engenharia `+5`, Ciência `−2`
  (perfil de pipelines);
- **D03/D04** — separam DevOps (automatizar a entrega) de Cloud (projetar ambientes escaláveis);
- **D05** — ferramentas mobile com afinidade visual → Mobile `+5`, Front-end `−3`.

### 2.4 Validação da base

O carregador (`consultor_pro/base_conhecimento.py`) valida a consistência antes de o motor rodar:
matriz completa para todas as dimensões × trilhas, fontes e operadores válidos, trilhas existentes,
certeza em `(0, 1]`, competências e tecnologias referenciadas. Se o JSON estiver inconsistente,
o sistema **falha com mensagem explícita** em vez de produzir resultados silenciosamente errados.

---

## 3. Fase 2 — Motor de inferência com pontuação

### 3.1 Aderência base

Seja `r_d ∈ {1..5}` a resposta da dimensão `d`, normalizada em `n_d = (r_d − 1)/4`:

```
base(t) = 100 × Σ_d [ peso(d,t) × n_d ] / Σ_d peso(d,t)
```

Propriedades desejadas:

- respostas **neutras (3 em tudo)** ⇒ `base = 50%` para todas as trilhas (sem viés inicial);
- respostas máximas em tudo ⇒ `100%`;
- a diferenciação vem do **padrão**, não do "entusiasmo" geral.

### 3.2 Ajuste das regras

```
ajuste(t) = clamp( Σ_regras (delta × certeza), −20, +20 )
compat(t) = clamp( 0, 100, base(t) + ajuste(t) )
```

O **limite de ±20 p.p.** é uma decisão de projeto: as regras refinam o ranking, mas não podem, sozinhas,
transformar um perfil desalinhado em primeiro lugar. Isso torna o sistema mais estável e explicável.

### 3.3 Ranking, desempate e alertas

Ordenação: `(−compat, −base, ordem canônica)`. O desempate canônico garante **determinismo**
(mesmas respostas ⇒ mesmo resultado, testado em `test_avaliacao_e_deterministica`).

Alertas de incerteza:

| Condição | Alerta |
|---|---|
| margem 1º–2º < 3 p.p. | empate técnico |
| 1º < 45% | perfil pouco definido |
| todas as respostas iguais | respostas uniformes |
| nenhuma regra ativada | resultado só da matriz |
| ≥ 15 regras ativadas | perfil multifacetado |
| 1º ≥ 90% | compatibilidade muito alta (revisar lacunas) |

### 3.4 Exemplo de rastreabilidade (persona Gustavo)

| Componente | Valor |
|---|---|
| base (matriz) | 77,50% |
| R10 (infra + automação, certeza 0,90, delta 7) | +6,30 |
| R11 (automação + Linux, certeza 0,85, delta 7) | +5,95 |
| R12 (infra + escala, certeza 0,90, delta 3) | +2,70 |
| R19 (automação + processo, certeza 0,80, delta 2) | +1,60 |
| **compat final** | **94,0%** |

O motor também expõe, por dimensão, a **contribuição em pontos percentuais** — usado na interface
para explicar o resultado.

---

## 4. Fase 3 — Skill gaps e roadmap

### 4.1 Das tecnologias às competências

O usuário marca o que **já estudou** (nível 2) e o que **domina** (nível 4). Cada tecnologia mapeia
para competências com um nível relativo:

```json
"python": { "skills": { "python": 3, "logica_programacao": 2 } }
```

Assim, saber Python reduz lacunas em back-end, ciência e engenharia de dados simultaneamente.

### 4.2 Lacunas e criticidade

Para cada competência `c` da trilha recomendada:

```
lacuna(c)     = max(0, nivel_junior(c) − nivel_atual(c))
prioridade(c) = lacuna(c) × importancia(c)
horas(c)      = lacuna(c) × 12 h
```

Criticidade: **Crítica** (lacuna ≥ 2 e importância ≥ 4), **Alta** (lacuna ≥ 2 ou lacuna 1 com
importância ≥ 4), **Moderada**, **Leve**.

### 4.3 Cobertura e plano

```
cobertura = 100 × Σ_c [ min(atual(c)/exigido(c), 1) × importancia(c) ] / Σ_c importancia(c)
```

O plano é composto por:

1. **Fase 1 — Nivelamento**: tópicos das lacunas mais prioritárias (até 6) + horas somadas;
2. **Fases da trilha**: fundamentos → prática → portfólio → mercado (horas da base);
3. **Certificações** e **projetos de portfólio** específicos da trilha.

O prazo de cada fase é `ceil(horas / horas_semana)`, com proteção para carga horária inválida
(`max(1, horas)`), coberto por teste.

---

## 5. Fase 4 — Interface web (Streamlit)

Wizard em **3 etapas**, com barra de progresso e navegação para frente/voltar:

1. **Perfil pessoal** — nome, formação, experiência, horas de estudo/semana (contexto, não pontua);
2. **Afinidades técnicas** — 8 sliders Likert, linguagem de maior afinidade e tecnologias
   estudadas/dominadas;
3. **Objetivos de carreira** — entrega de valor, objetivo e estilo de trabalho (obrigatórios).

A tela de resultado apresenta:

- **Top 3** com percentual, diferença para o líder e barra de progresso;
- alertas de incerteza;
- **gráfico de barras** com o ranking das 10 trilhas;
- **radar comparativo** (usuário × perfil ideal derivado dos pesos da trilha);
- **tabela de skill gaps** + cobertura + prazo estimado;
- **roadmap** em expansores, certificações e projetos;
- seção **"Como o motor chegou a esse resultado"** (contribuições por dimensão e regras ativadas);
- **download** do resultado em JSON e botão de recomeçar.

A interface é testada com `streamlit.testing.v1.AppTest` (navegação, bloqueio de campos obrigatórios,
fluxo completo e reset).

---

## 6. Fase 5 — Testes de robustez e casos limite

### 6.1 Estratégia

| Camada | Ferramenta | O que cobre |
|---|---|---|
| Base de conhecimento | pytest | estrutura, matriz completa, JSON inválido, desacoplamento |
| Motor | pytest | intervalos 0–100, ordenação, determinismo, clamp, regras |
| Recomendação | pytest | lacunas, cobertura, prazos, casos degenerados |
| Personas | pytest | 13 perfis, 10 trilhas, 3 casos-limite |
| Interface | Streamlit AppTest | wizard, validação, resultado, reset |

**90 testes**, todos passando (`pytest`).

### 6.2 Personas e resultados

| Persona | Perfil | 1º lugar | % | 2º lugar | % |
|---|---|---|---|---|---|
| Ana | matemática + dados + IA | Ciência de Dados | 88,8 | Engenharia de Dados | 61,6 |
| Bruno | redes + investigação | Cibersegurança | 84,2 | Cloud | 63,4 |
| Carla | visual + JavaScript | Front-end | 80,1 | Mobile | 59,4 |
| Diego | gestão + negócio | Produto | 67,1 | Front-end | 40,9 |
| Eduardo | lógica + APIs | Back-end | 65,5 | Ciência de Dados | 52,5 |
| Fernanda | dados + infra + automação | Engenharia de Dados | 95,0 | QA | 83,7 |
| Gustavo | infra + automação + Linux | DevOps | 94,0 | Cloud | 84,9 |
| Helena | infra + escala, pouca automação | Cloud | 68,4 | DevOps | 60,1 |
| Igor | visual + mobile | Mobile | 68,8 | Front-end | 61,4 |
| Juliana | lógica + método + testes | QA | 60,1 | Back-end | 54,9 |
| Karina | dados **e** interface | Ciência de Dados | 70,8 | Front-end | **70,5** |
| Leandro | todas as notas 1 | Back-end | 0,0 | — | — |
| Marcos | quer IA, matemática nota 1 | Engenharia de Dados | 78,9 | QA | 74,8 |

### 6.3 Análise dos casos limite

**Empate (Karina).** Ciência de Dados 70,8% × Front-end 70,5% × Back-end 68,3%. O sistema detecta
margem de 0,3 p.p., emite *"Empate técnico"* e recomenda experimentar as duas trilhas — comportamento
desejado para perfis ambíguos, em vez de forçar uma resposta arbitrária.

**Perfil indefinido (Leandro).** Todas as notas 1: a matriz resulta em 0% em todas as trilhas. Em vez de
quebrar (divisão por zero) ou inventar uma recomendação forte, o sistema mantém o ranking determinístico
e emite três alertas (pouco definido, respostas uniformes, nenhuma regra ativada).

**Conflito lógico (Marcos).** Objetivo declarado de trabalhar com IA, mas matemática nota 1. A regra
**P01** aplica `−10 p.p.` em Ciência de Dados (certeza 1,0) e `−3 p.p.` em Engenharia; o resultado passa
a recomendar Engenharia de Dados. Isso demonstra o papel das **penalidades** no tratamento de
inconsistências entre objetivo declarado e afinidades reais.

**Distinção Ciência × Engenharia.** Teste dedicado (`test_distincao_ciencia_vs_engenharia_de_dados`)
comprova que o mesmo interesse por dados leva a trilhas diferentes conforme infraestrutura/automação:
perfil analítico → Ciência; perfil de plataforma → Engenharia.

**Desacoplamento.** Um teste modifica o JSON em tempo de execução (zera a matriz e dá peso apenas a uma
dimensão) e verifica que o resultado muda — provando que o conhecimento **não está hardcoded**.

---

## 7. Discussão

**Por que soma ponderada + regras, e não árvore de decisão?** Uma árvore produz uma única folha
(uma trilha) e não expressa "70% de compatibilidade". A soma ponderada gera um ranking contínuo,
enquanto as regras recuperam o conhecimento simbólico do especialista — especialmente nas
**desambiguações**, difíceis de capturar apenas com pesos lineares.

**Por que limitar o ajuste das regras?** Sem o limite, muitas regras disparadas em um perfil
"entusiasmado" saturariam todas as trilhas em 100%, destruindo o ranking. O clamp mantém a matriz como
sinal dominante e as regras como refinamento.

**Transparência como requisito.** Cada percentual é decomponível em `base + ajuste`, e cada ajuste é
decomponível em regras. Isso permite ao usuário discordar do resultado de forma informada — algo que
modelos de caixa-preta não oferecem.

---

## 8. Limitações e trabalhos futuros

- Pesos calibrados manualmente, sem aprendizado a partir de escolhas reais.
- Percentual é **aderência ao perfil**, não probabilidade de sucesso.
- Autoavaliação de competências é subjetiva.
- Base estática: exige revisão periódica do JSON.

Evoluções: aprendizado de pesos com dados reais, comparação lado a lado de trilhas, exportação do
roadmap em PDF e tradução da base.

---

## 9. Como reproduzir

```bash
pip install -r requirements.txt
streamlit run app.py          # interface
pytest                        # 90 testes
python tools/avaliar_personas.py
python tools/gerar_docs.py
```

Estrutura completa, fórmulas e capturas de tela estão no [`README`](../README.md).
