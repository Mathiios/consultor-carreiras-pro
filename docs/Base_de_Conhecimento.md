# Base de Conhecimento — Consultor Avançado de Carreiras em TI

> Documento gerado automaticamente a partir de `data/regras_carreiras.json` (versão 2.0.0). **Não edite à mão.**

- Trilhas: **10**
- Dimensões de afinidade: **8**
- Questões categóricas: **4**
- Regras ponderadas: **38**
- Competências mapeadas: **43**
- Tecnologias de entrada no portfólio: **30**
- Limite de ajuste das regras: **±20 p.p.**

## 1. Dimensões de afinidade (escala Likert 1–5)

| ID | Dimensão | Pergunta | Escala |
|---|---|---|---|
| logica | Raciocínio lógico e algoritmos | Gosto de resolver problemas de lógica e escrever algoritmos | 1–5 |
| matematica | Matemática e estatística | Tenho afinidade com matemática, probabilidade e estatística | 1–5 |
| visual | Design e interfaces | Gosto de criar telas, layouts e cuidar da experiência visual | 1–5 |
| infra | Infraestrutura e redes | Tenho interesse em servidores, redes e ambientes de execução | 1–5 |
| dados | Dados e análise | Gosto de explorar, limpar e organizar grandes volumes de dados | 1–5 |
| seguranca | Segurança e investigação | Tenho interesse em encontrar falhas e proteger sistemas | 1–5 |
| automacao | Automação de processos | Gosto de automatizar tarefas, builds e entregas | 1–5 |
| gestao | Gestão e pessoas | Gosto de priorizar decisões, negociar e coordenar pessoas | 1–5 |

## 2. Questões categóricas

### `linguagem` — Linguagem/ferramenta de maior afinidade

Qual linguagem ou ferramenta você mais se identifica hoje?

| Valor | Rótulo |
|---|---|
| python | Python |
| javascript | JavaScript / TypeScript |
| sql | SQL e bancos de dados |
| linux | Linux / Redes |
| mobile | Kotlin / Swift / Flutter |
| nenhuma | Nenhuma / sou iniciante |

### `entrega` — Tipo de entrega de valor

Que tipo de valor você prefere entregar no trabalho?

| Valor | Rótulo |
|---|---|
| usuario | O produto final para o usuário |
| infraestrutura | A infraestrutura que sustenta o sistema |
| seguranca | A segurança contra invasões |
| dados | Dados e modelos que geram decisões |
| negocio | O negócio e a estratégia do produto |

### `objetivo` — Objetivo de carreira

Qual é o seu principal objetivo profissional?

| Valor | Rótulo |
|---|---|
| criar_produtos | Criar produtos que as pessoas usem |
| proteger | Proteger sistemas e dados |
| escalar_infra | Sustentar escala e disponibilidade |
| prever_dados | Prever e decidir com dados/IA |
| liderar_negocio | Liderar pessoas e decisões de negócio |

### `estilo` — Estilo de trabalho

Como você prefere que seja o seu dia a dia?

| Valor | Rótulo |
|---|---|
| logica_profunda | Foco profundo em lógica e construção |
| criativo | Criação visual e experimentação |
| investigativo | Investigação e análise de causas |
| processo_metodo | Processo, método e organização |
| pessoas | Contato com pessoas e negociação |

## 3. Matriz de afinidade (peso de cada dimensão por trilha)

| Dimensão | 🛠️ backend | 🎨 frontend | 🧠 ciencia_dados | 🏗️ engenharia_dados | 🛡️ seguranca | ⚙️ devops | ☁️ cloud | 📱 mobile | 🧪 qa | 📊 produto |
|---|---|---|---|---|---|---|---|---|---|---|
| Raciocínio lógico e algoritmos | 5 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 1 |
| Matemática e estatística | 1 | 0 | 5 | 4 | 2 | 1 | 1 | 0 | 2 | 2 |
| Design e interfaces | 1 | 5 | 1 | 0 | 0 | 0 | 0 | 4 | 1 | 3 |
| Infraestrutura e redes | 2 | 0 | 2 | 5 | 4 | 5 | 5 | 0 | 2 | 1 |
| Dados e análise | 3 | 1 | 5 | 5 | 2 | 2 | 2 | 1 | 3 | 3 |
| Segurança e investigação | 1 | 0 | 1 | 1 | 5 | 2 | 3 | 1 | 1 | 1 |
| Automação de processos | 2 | 1 | 1 | 3 | 2 | 5 | 4 | 1 | 3 | 1 |
| Gestão e pessoas | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 5 |

Peso **0** significa que a dimensão não influencia a trilha; pesos maiores aumentam a contribuição da resposta para aquela trilha.

## 4. Regras ponderadas

Cada regra ativada aplica `delta × certeza` pontos percentuais à trilha. O ajuste total por trilha é limitado a ±20 p.p.

### 4.1 Regras de reforço

| ID | Regra | Certeza | SE (condições) | ENTÃO (efeito em p.p.) |
|---|---|---|---|---|
| R01 | Lógica aplicada a produto | 0.90 | Raciocínio lógico e algoritmos ≥ 4 **E** Tipo de entrega de valor = O produto final para o usuário | backend: +6 (+5.4 com certeza)<br>mobile: +2 (+1.8 com certeza) |
| R02 | Lógica com Python | 0.85 | Raciocínio lógico e algoritmos ≥ 4 **E** Linguagem/ferramenta de maior afinidade = Python | backend: +5 (+4.2 com certeza)<br>ciencia_dados: +3 (+2.5 com certeza)<br>engenharia_dados: +3 (+2.5 com certeza) |
| R03 | Visual com foco no usuário | 0.90 | Design e interfaces ≥ 4 **E** Tipo de entrega de valor = O produto final para o usuário | frontend: +7 (+6.3 com certeza)<br>mobile: +3 (+2.7 com certeza) |
| R04 | Visual com JavaScript | 0.85 | Design e interfaces ≥ 3 **E** Linguagem/ferramenta de maior afinidade = JavaScript / TypeScript | frontend: +6 (+5.1 com certeza) |
| R05 | Visual com ferramentas mobile | 0.90 | Design e interfaces ≥ 4 **E** Linguagem/ferramenta de maior afinidade = Kotlin / Swift / Flutter | mobile: +8 (+7.2 com certeza)<br>frontend: -2 (-1.8 com certeza) |
| R06 | Matemática e dados | 0.90 | Matemática e estatística ≥ 4 **E** Dados e análise ≥ 4 | ciencia_dados: +7 (+6.3 com certeza)<br>engenharia_dados: +4 (+3.6 com certeza) |
| R07 | Matemática com objetivo preditivo | 0.85 | Matemática e estatística ≥ 4 **E** Objetivo de carreira = Prever e decidir com dados/IA | ciencia_dados: +6 (+5.1 com certeza) |
| R08 | Dados com SQL | 0.90 | Dados e análise ≥ 4 **E** Linguagem/ferramenta de maior afinidade = SQL e bancos de dados | engenharia_dados: +7 (+6.3 com certeza)<br>ciencia_dados: +2 (+1.8 com certeza) |
| R09 | Dados com infraestrutura | 0.85 | Dados e análise ≥ 4 **E** Infraestrutura e redes ≥ 4 | engenharia_dados: +6 (+5.1 com certeza)<br>cloud: +3 (+2.5 com certeza) |
| R10 | Infraestrutura com automação | 0.90 | Infraestrutura e redes ≥ 4 **E** Automação de processos ≥ 4 | devops: +7 (+6.3 com certeza)<br>cloud: +4 (+3.6 com certeza) |
| R11 | Automação com Linux | 0.85 | Automação de processos ≥ 4 **E** Linguagem/ferramenta de maior afinidade = Linux / Redes | devops: +7 (+6.0 com certeza)<br>seguranca: +2 (+1.7 com certeza) |
| R12 | Infraestrutura com objetivo de escala | 0.90 | Infraestrutura e redes ≥ 4 **E** Objetivo de carreira = Sustentar escala e disponibilidade | cloud: +7 (+6.3 com certeza)<br>devops: +3 (+2.7 com certeza) |
| R13 | Segurança com Linux | 0.90 | Segurança e investigação ≥ 4 **E** Linguagem/ferramenta de maior afinidade = Linux / Redes | seguranca: +7 (+6.3 com certeza)<br>devops: +2 (+1.8 com certeza) |
| R14 | Segurança com objetivo de proteção | 0.90 | Segurança e investigação ≥ 4 **E** Objetivo de carreira = Proteger sistemas e dados | seguranca: +6 (+5.4 com certeza) |
| R15 | Segurança sobre infraestrutura | 0.80 | Segurança e investigação ≥ 4 **E** Infraestrutura e redes ≥ 3 | seguranca: +4 (+3.2 com certeza)<br>cloud: +2 (+1.6 com certeza) |
| R16 | Gestão com objetivo de liderança | 0.90 | Gestão e pessoas ≥ 4 **E** Objetivo de carreira = Liderar pessoas e decisões de negócio | produto: +8 (+7.2 com certeza) |
| R17 | Gestão orientada a negócio | 0.85 | Gestão e pessoas ≥ 3 **E** Tipo de entrega de valor = O negócio e a estratégia do produto | produto: +6 (+5.1 com certeza) |
| R18 | Lógica com processo | 0.80 | Raciocínio lógico e algoritmos ≥ 4 **E** Estilo de trabalho = Processo, método e organização | qa: +7 (+5.6 com certeza)<br>backend: +1 (+0.8 com certeza) |
| R19 | Automação com processo | 0.80 | Automação de processos ≥ 3 **E** Estilo de trabalho = Processo, método e organização | qa: +6 (+4.8 com certeza)<br>devops: +2 (+1.6 com certeza) |
| R20 | Perfil investigativo voltado à segurança | 0.85 | Estilo de trabalho = Investigação e análise de causas **E** Segurança e investigação ≥ 3 | seguranca: +5 (+4.2 com certeza)<br>ciencia_dados: +2 (+1.7 com certeza) |
| R21 | Perfil investigativo voltado a dados | 0.80 | Estilo de trabalho = Investigação e análise de causas **E** Dados e análise ≥ 4 | ciencia_dados: +4 (+3.2 com certeza)<br>engenharia_dados: +2 (+1.6 com certeza) |
| R22 | Perfil criativo com afinidade visual | 0.85 | Estilo de trabalho = Criação visual e experimentação **E** Design e interfaces ≥ 4 | frontend: +6 (+5.1 com certeza)<br>mobile: +3 (+2.5 com certeza) |
| R23 | Perfil de foco lógico | 0.85 | Estilo de trabalho = Foco profundo em lógica e construção **E** Raciocínio lógico e algoritmos ≥ 4 | backend: +5 (+4.2 com certeza)<br>engenharia_dados: +1 (+0.8 com certeza) |
| R24 | Perfil orientado a pessoas | 0.85 | Estilo de trabalho = Contato com pessoas e negociação **E** Gestão e pessoas ≥ 3 | produto: +6 (+5.1 com certeza) |
| R25 | Dados com automação | 0.80 | Dados e análise ≥ 4 **E** Automação de processos ≥ 4 | engenharia_dados: +5 (+4.0 com certeza)<br>devops: +2 (+1.6 com certeza) |

### 4.2 Regras de desambiguação

| ID | Regra | Certeza | SE (condições) | ENTÃO (efeito em p.p.) |
|---|---|---|---|---|
| D01 | Ciência × Engenharia: modelagem | 0.90 | Matemática e estatística ≥ 4 **E** Dados e análise ≥ 3 **E** Infraestrutura e redes ≤ 2 | ciencia_dados: +5 (+4.5 com certeza)<br>engenharia_dados: -3 (-2.7 com certeza) |
| D02 | Ciência × Engenharia: pipelines | 0.90 | Dados e análise ≥ 4 **E** Infraestrutura e redes ≥ 4 **E** Automação de processos ≥ 3 | engenharia_dados: +5 (+4.5 com certeza)<br>ciencia_dados: -2 (-1.8 com certeza) |
| D03 | DevOps × Cloud: entrega | 0.85 | Automação de processos ≥ 4 **E** Tipo de entrega de valor = A infraestrutura que sustenta o sistema **E** Objetivo de carreira ≠ Sustentar escala e disponibilidade | devops: +5 (+4.2 com certeza)<br>cloud: -2 (-1.7 com certeza) |
| D04 | Cloud × DevOps: escala | 0.85 | Infraestrutura e redes ≥ 4 **E** Objetivo de carreira = Sustentar escala e disponibilidade **E** Automação de processos ≤ 3 | cloud: +5 (+4.2 com certeza)<br>devops: -2 (-1.7 com certeza) |
| D05 | Front-end × Mobile: nativo | 0.90 | Linguagem/ferramenta de maior afinidade = Kotlin / Swift / Flutter **E** Design e interfaces ≥ 3 | mobile: +5 (+4.5 com certeza)<br>frontend: -3 (-2.7 com certeza) |
| D06 | QA × Back-end | 0.80 | Raciocínio lógico e algoritmos ≥ 4 **E** Estilo de trabalho = Processo, método e organização **E** Automação de processos ≥ 3 | qa: +7 (+5.6 com certeza)<br>backend: -3 (-2.4 com certeza) |
| D07 | Produto × perfis técnicos | 0.80 | Gestão e pessoas ≥ 4 **E** Raciocínio lógico e algoritmos ≤ 2 | produto: +5 (+4.0 com certeza)<br>backend: -2 (-1.6 com certeza)<br>ciencia_dados: -2 (-1.6 com certeza) |

### 4.3 Regras de penalidade (perfis conflitantes)

| ID | Regra | Certeza | SE (condições) | ENTÃO (efeito em p.p.) |
|---|---|---|---|---|
| P01 | Penalidade: IA/previsão sem base matemática | 1.00 | Matemática e estatística ≤ 2 **E** Objetivo de carreira = Prever e decidir com dados/IA | ciencia_dados: -10 (-10.0 com certeza)<br>engenharia_dados: -3 (-3.0 com certeza) |
| P02 | Penalidade: escala sem afinidade de infraestrutura | 0.95 | Infraestrutura e redes ≤ 2 **E** Objetivo de carreira = Sustentar escala e disponibilidade | cloud: -8 (-7.6 com certeza)<br>devops: -4 (-3.8 com certeza) |
| P03 | Penalidade: liderança sem afinidade de gestão | 0.95 | Gestão e pessoas ≤ 2 **E** Objetivo de carreira = Liderar pessoas e decisões de negócio | produto: -8 (-7.6 com certeza) |
| P04 | Penalidade: segurança sem afinidade | 0.90 | Segurança e investigação ≤ 2 **E** Objetivo de carreira = Proteger sistemas e dados | seguranca: -6 (-5.4 com certeza) |
| P05 | Penalidade: produto sem afinidade com pessoas | 0.85 | Gestão e pessoas ≤ 2 **E** Tipo de entrega de valor = O negócio e a estratégia do produto | produto: -5 (-4.2 com certeza) |
| P06 | Penalidade: front-end sem afinidade visual | 0.85 | Design e interfaces ≤ 2 **E** Tipo de entrega de valor = O produto final para o usuário **E** Linguagem/ferramenta de maior afinidade = JavaScript / TypeScript | frontend: -5 (-4.2 com certeza) |

## 5. Trilhas, competências e roadmap

### 🛠️ Desenvolvimento Back-end

APIs, regras de negócio e integração com bancos de dados.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Lógica de programação | 3/5 | 5/5 |
| Python | 3/5 | 5/5 |
| APIs REST | 3/5 | 5/5 |
| SQL | 3/5 | 4/5 |
| Git e GitHub | 3/5 | 3/5 |
| Contêineres (Docker) | 2/5 | 3/5 |
| Testes automatizados | 2/5 | 2/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos | 60h | lógica e estruturas de dados, Python, Git/GitHub, SQL básico |
| 2 | Construção de APIs | 80h | HTTP e REST, FastAPI/Flask, modelagem de banco, autenticação JWT |
| 3 | Projeto de portfólio | 50h | API completa com testes, Dockerfile e deploy, README técnico |
| 4 | Mercado | 30h | certificação introdutória, contribuições open source, simulação de entrevistas |

**Certificações:** AWS Certified Cloud Practitioner, Python Institute PCAP

**Projetos de portfólio:**

- **API de gestão de tarefas** — CRUD + autenticação + testes automatizados + deploy em contêiner.
- **Integração com serviço externo** — API que consome um serviço público, trata falhas e expõe métricas.

### 🎨 Desenvolvimento Front-end & UI/UX

Interfaces responsivas, experiência do usuário e frameworks reativos.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| HTML e CSS | 3/5 | 5/5 |
| JavaScript/TypeScript | 3/5 | 5/5 |
| React | 3/5 | 5/5 |
| UX/UI Design | 2/5 | 4/5 |
| Acessibilidade (a11y) | 2/5 | 3/5 |
| Git e GitHub | 3/5 | 3/5 |
| Lógica de programação | 2/5 | 3/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos web | 60h | HTML semântico, CSS flexbox/grid, JavaScript ES6+, Git |
| 2 | Framework e design | 80h | React (hooks e estado), design system, responsividade, acessibilidade |
| 3 | Projeto de portfólio | 50h | SPA consumindo API pública, testes de componente, deploy (Vercel/Netlify) |
| 4 | Mercado | 30h | portfólio visual, estudos de caso de UX, LinkedIn/GitHub |

**Certificações:** Meta Front-End Developer, Google UX Design

**Projetos de portfólio:**

- **Dashboard responsivo** — Interface com gráficos, filtros e layout adaptável, consumindo API pública.
- **Redesign acessível** — Reformular uma tela real aplicando WCAG e testes de usabilidade.

### 🧠 Ciência de Dados e Machine Learning

Estatística, modelagem preditiva e inteligência artificial.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Python | 3/5 | 5/5 |
| Estatística | 3/5 | 5/5 |
| Manipulação de dados (pandas) | 3/5 | 5/5 |
| Machine Learning | 3/5 | 5/5 |
| SQL | 3/5 | 4/5 |
| Visualização de dados | 2/5 | 4/5 |
| Git e GitHub | 2/5 | 3/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Base quantitativa | 70h | estatística descritiva e inferência, probabilidade, Python para dados, pandas |
| 2 | Modelagem | 90h | regressão e classificação, validação cruzada, métricas, feature engineering |
| 3 | Projeto de portfólio | 60h | notebook completo, dataset real, storytelling e visualização |
| 4 | Mercado | 30h | MLflow/versionamento, artigo técnico no Medium, Kaggle |

**Certificações:** Google Advanced Data Analytics, AWS Certified Machine Learning – Specialty

**Projetos de portfólio:**

- **Previsão de churn** — Modelo com análise exploratória, comparação de algoritmos e relatório de impacto.
- **Detecção de anomalias** — Identificar padrões fora do normal em dados de transações.

### 🏗️ Engenharia de Dados

Pipelines ETL/ELT, arquitetura de dados e Data Lakes.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| SQL | 4/5 | 5/5 |
| ETL/ELT | 3/5 | 5/5 |
| Modelagem de dados | 3/5 | 5/5 |
| Python | 3/5 | 4/5 |
| Processamento distribuído (Spark) | 2/5 | 4/5 |
| Orquestração (Airflow) | 2/5 | 4/5 |
| Git e GitHub | 3/5 | 3/5 |
| Contêineres (Docker) | 2/5 | 3/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos de dados | 70h | SQL avançado, modelagem dimensional, Python para ETL, Git |
| 2 | Pipelines | 90h | Airflow, Spark, camadas bronze/prata/ouro, qualidade de dados |
| 3 | Projeto de portfólio | 60h | pipeline ponta a ponta, orquestração, dashboard final |
| 4 | Mercado | 30h | dbt, catálogos de dados, certificação de nuvem |

**Certificações:** AWS Certified Data Engineer – Associate, Databricks Certified Data Engineer Associate

**Projetos de portfólio:**

- **Pipeline de dados público** — Ingestão agendada de uma API pública, transformação em camadas e consumo analítico.
- **Data warehouse dimensional** — Modelar star schema com fatos/dimensões e consultas otimizadas.

### 🛡️ Cibersegurança (Security / Pentesting)

Defesa cibernética, vulnerabilidades, criptografia e redes seguras.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Redes de computadores | 3/5 | 5/5 |
| Linux | 3/5 | 5/5 |
| Testes de invasão (pentest) | 2/5 | 5/5 |
| Criptografia | 2/5 | 3/5 |
| Monitoramento e SIEM | 2/5 | 3/5 |
| Shell scripting | 2/5 | 3/5 |
| Lógica de programação | 2/5 | 2/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos | 70h | redes TCP/IP, Linux, shell scripting, criptografia básica |
| 2 | Ofensiva e defensiva | 90h | OWASP Top 10, pentest web, análise de logs, resposta a incidentes |
| 3 | Projeto de portfólio | 50h | relatório de pentest em laboratório, CTF documentado, hardening de servidor |
| 4 | Mercado | 30h | certificação de entrada, bug bounty, comunidade |

**Certificações:** CompTIA Security+, eJPT (INE Security)

**Projetos de portfólio:**

- **Relatório de pentest** — Análise de uma aplicação vulnerável com evidências, impacto e recomendações.
- **Laboratório de detecção** — Ambiente com logs centralizados e alertas para ataques comuns.

### ⚙️ DevOps & SRE

Automação de processos, CI/CD, contêineres e confiabilidade.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Linux | 3/5 | 5/5 |
| CI/CD | 3/5 | 5/5 |
| Contêineres (Docker) | 3/5 | 5/5 |
| Kubernetes | 3/5 | 4/5 |
| Git e GitHub | 3/5 | 4/5 |
| Shell scripting | 3/5 | 4/5 |
| Observabilidade | 2/5 | 3/5 |
| Infraestrutura como código | 2/5 | 3/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos | 60h | Linux, Git, shell, redes básicas |
| 2 | Automação | 90h | Docker, GitHub Actions, Kubernetes, pipelines de teste e deploy |
| 3 | Confiabilidade | 60h | métricas e logs, alertas, SLOs, Terraform |
| 4 | Mercado | 30h | certificação Kubernetes/AWS, projetos open source, postmortems |

**Certificações:** CKA (Certified Kubernetes Administrator), AWS Certified Solutions Architect – Associate

**Projetos de portfólio:**

- **Pipeline completo** — App com testes, build de imagem, deploy automatizado e rollback.
- **Observabilidade** — Stack de métricas/logs com dashboard e alertas para um serviço real.

### ☁️ Computação em Nuvem (Cloud Architecture)

Arquiteturas escaláveis, migração e gestão de custos em AWS/Azure/GCP.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Fundamentos de nuvem (AWS/Azure/GCP) | 3/5 | 5/5 |
| Arquitetura em nuvem | 3/5 | 5/5 |
| Redes de computadores | 2/5 | 4/5 |
| Infraestrutura como código | 2/5 | 4/5 |
| Linux | 3/5 | 3/5 |
| FinOps e custos | 2/5 | 3/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos | 60h | modelos de serviço, regiões/zonas, IAM, redes na nuvem |
| 2 | Arquitetura | 90h | alta disponibilidade, escalabilidade, balanceamento, IaC com Terraform |
| 3 | Projeto de portfólio | 60h | aplicação multi-AZ, monitoramento, estimativa de custos |
| 4 | Mercado | 30h | certificação associate, well-architected review, FinOps |

**Certificações:** AWS Solutions Architect – Associate, Microsoft Azure Fundamentals (AZ-900)

**Projetos de portfólio:**

- **Aplicação escalável** — Deploy multi-AZ com balanceador, banco gerenciado e monitoramento.
- **Migração documentada** — Plano de migração de um app legado para nuvem com análise de custos.

### 📱 Desenvolvimento Mobile

Aplicativos nativos ou multiplataforma (Flutter/React Native).

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Desenvolvimento mobile | 3/5 | 5/5 |
| Lógica de programação | 3/5 | 4/5 |
| APIs REST | 2/5 | 3/5 |
| UX/UI Design | 2/5 | 3/5 |
| Git e GitHub | 3/5 | 3/5 |
| Publicação de apps | 2/5 | 3/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos | 60h | linguagem (Dart/Kotlin/Swift), componentes, navegação, Git |
| 2 | Integração | 80h | consumo de APIs, estado, armazenamento local, notificações |
| 3 | Projeto de portfólio | 60h | app completo, testes, build de produção |
| 4 | Publicação | 30h | Play Console/App Store, políticas, ASO |

**Certificações:** Google Associate Android Developer, Flutter Certified Application Developer

**Projetos de portfólio:**

- **App com API real** — Aplicativo com autenticação, listagem, cache offline e publicação em teste.
- **UI Kit reutilizável** — Componentes padronizados com tema claro/escuro e acessibilidade.

### 🧪 Engenharia de Qualidade e Testes (QA)

Testes automatizados, confiabilidade e processos de qualidade.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Testes manuais e de aceitação | 3/5 | 5/5 |
| Testes automatizados | 2/5 | 5/5 |
| Testes de API | 2/5 | 4/5 |
| Qualidade em pipeline | 2/5 | 3/5 |
| Lógica de programação | 2/5 | 3/5 |
| Git e GitHub | 2/5 | 2/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos de teste | 50h | casos de teste, critérios de aceite, bug report, pirâmide de testes |
| 2 | Automação | 80h | pytest, Cypress, testes de API com Postman, mocks |
| 3 | Qualidade no pipeline | 50h | CI com quality gates, cobertura, análise estática |
| 4 | Mercado | 30h | ISTQB CTFL, testes de performance, acessibilidade |

**Certificações:** ISTQB CTFL, Cypress Certified Automation Tester

**Projetos de portfólio:**

- **Suíte de testes completa** — Automatizar testes de um sistema open source com relatório de cobertura.
- **Pipeline com quality gate** — CI que bloqueia merge quando testes ou cobertura falham.

### 📊 Gestão de Produtos (Product Management)

Ponte entre negócio, design e tecnologia, com priorização e métricas.

**Competências para o nível júnior:**

| Competência | Nível exigido | Importância |
|---|---|---|
| Product Discovery | 3/5 | 5/5 |
| Métodos ágeis | 3/5 | 5/5 |
| Roadmap e priorização | 2/5 | 5/5 |
| Gestão de stakeholders | 3/5 | 4/5 |
| Métricas de produto | 2/5 | 4/5 |
| SQL | 1/5 | 2/5 |

**Roadmap:**

| Fase | Título | Horas | Tópicos |
|---|---|---|---|
| 1 | Fundamentos de produto | 50h | problema x solução, personas, MVP, métricas de produto |
| 2 | Descoberta e priorização | 70h | entrevistas, hipóteses, RICE/WSJF, OKRs |
| 3 | Projeto de portfólio | 50h | one-pager de produto, roadmap de 3 meses, caso com dados reais |
| 4 | Mercado | 30h | certificação ágil, comunidade de produto, simulação de case |

**Certificações:** Professional Scrum Product Owner I (PSPO I), Google Project Management

**Projetos de portfólio:**

- **Caso de produto** — One-pager com problema, persona, métrica de sucesso e roadmap priorizado.
- **Análise de funil** — Investigar quedas de conversão com dados e propor experimentos.

## 6. Tecnologias e competências que elas comprovam

| Tecnologia | Competências (nível relativo) |
|---|---|
| Python | Python (3), Lógica de programação (2) |
| JavaScript | JavaScript/TypeScript (3), Lógica de programação (2) |
| HTML/CSS | HTML e CSS (3), Acessibilidade (a11y) (1) |
| React | React (3), JavaScript/TypeScript (2), HTML e CSS (1) |
| Node.js | APIs REST (2), JavaScript/TypeScript (2) |
| Figma | UX/UI Design (3), Acessibilidade (a11y) (1) |
| SQL | SQL (3), Modelagem de dados (2) |
| pandas | Manipulação de dados (pandas) (3), Python (2), Estatística (2) |
| scikit-learn | Machine Learning (3), Estatística (2), Python (2) |
| Power BI | Visualização de dados (3), SQL (1) |
| Apache Spark | Processamento distribuído (Spark) (3), ETL/ELT (2), Modelagem de dados (1) |
| Apache Airflow | Orquestração (Airflow) (3), ETL/ELT (2), Python (1) |
| Docker | Contêineres (Docker) (3), CI/CD (1) |
| Kubernetes | Kubernetes (3), Contêineres (Docker) (2), Observabilidade (2) |
| Linux | Linux (3), Shell scripting (3), Redes de computadores (1) |
| Redes (TCP/IP) | Redes de computadores (3), Shell scripting (1) |
| Wireshark | Redes de computadores (2), Monitoramento e SIEM (2), Testes de invasão (pentest) (1) |
| Burp Suite | Testes de invasão (pentest) (3), APIs REST (2) |
| AWS | Fundamentos de nuvem (AWS/Azure/GCP) (3), Arquitetura em nuvem (2), FinOps e custos (2) |
| Terraform | Infraestrutura como código (3), Arquitetura em nuvem (2), Fundamentos de nuvem (AWS/Azure/GCP) (1) |
| Flutter | Desenvolvimento mobile (3), Lógica de programação (1) |
| React Native | Desenvolvimento mobile (3), React (1), JavaScript/TypeScript (1) |
| Kotlin (Android) | Desenvolvimento mobile (3), Publicação de apps (1) |
| pytest | Testes automatizados (3), Python (2), Lógica de programação (1) |
| Cypress | Testes automatizados (3), JavaScript/TypeScript (1), Testes de API (1) |
| Postman | Testes de API (3), APIs REST (2) |
| Git | Git e GitHub (3) |
| GitHub Actions | CI/CD (3), Git e GitHub (1), Shell scripting (1) |
| Jira/Scrum | Métodos ágeis (3), Product Discovery (1) |
| Analytics (GA4) | Métricas de produto (3), Visualização de dados (1) |
