# AIZI ENGINEERING AI

# ROADMAP DO PROJETO

**Versão:** 1.0
**Data:** 13/08/2026
**Status:** Roadmap inicial oficial

---

# 1. OBJETIVO

Este documento define a sequência de evolução do AIZI Engineering AI.

O roadmap existe para responder:

> **O que será construído, em qual ordem e com qual objetivo?**

O projeto será desenvolvido de forma incremental.

Cada fase deverá produzir uma base funcional para a próxima.

---

# 2. VISÃO GERAL

A evolução planejada será:

```text
FASE 0
Fundação e documentação
        ↓
FASE 1
Base técnica
        ↓
FASE 2
Dados e cadastro
        ↓
FASE 3
BOM e estrutura de produto
        ↓
FASE 4
Desenhos técnicos
        ↓
FASE 5
Geometria e diagnóstico
        ↓
FASE 6
Desenvolvimento de chapas
        ↓
FASE 7
Planejamento de corte
        ↓
FASE 8
Integração dos motores
        ↓
FASE 9
Interface
        ↓
FASE 10
Inteligência artificial
        ↓
FASE 11
Automação industrial
        ↓
FASE 12
Escala da plataforma
```

---

# 3. FASE 0 — FUNDAÇÃO

**Status:** EM ANDAMENTO / CONCLUÍDA PARCIALMENTE

## Objetivo

Estabelecer a base documental e estrutural do projeto.

## Entregas

* `_CONTEXT.md`
* `ARQUITETURA.md`
* `DECISOES.md`
* `ROADMAP.md`
* mecanismo `aizi_context.py`
* estrutura inicial de diretórios.

## Resultado esperado

O projeto deve possuir uma referência central capaz de explicar:

* o que é o AIZI;
* como funciona;
* quais decisões foram tomadas;
* qual será a sequência de desenvolvimento.

## Critério de conclusão

Os documentos devem existir e o `aizi_context.py` deve conseguir consolidá-los.

---

# 4. FASE 1 — BASE TÉCNICA

**Status:** PRÓXIMA ETAPA

## Objetivo

Garantir que a estrutura Python do projeto seja organizada e executável.

## Atividades

* validar ambiente virtual;
* validar dependências;
* organizar módulos;
* definir convenções;
* estruturar testes;
* estruturar logs;
* padronizar tratamento de erros;
* validar execução dos módulos existentes.

## Dependências principais

```text
Python
PyMuPDF
SQLAlchemy
openpyxl
customtkinter
```

Outras dependências serão adicionadas conforme necessidade.

## Resultado esperado

O projeto deverá executar de forma previsível a partir do ambiente configurado.

---

# 5. FASE 2 — MODELO DE DADOS

**Status:** PLANEJADA

## Objetivo

Criar a base de dados interna do AIZI.

## Entidades iniciais

```text
Projeto
Produto
Peça
Material
Arquivo Técnico
Configuração
```

## Atividades

* validar modelos;
* validar relacionamentos;
* estruturar banco;
* criar repositories;
* criar operações CRUD;
* criar testes;
* separar dados externos do modelo interno.

## Resultado esperado

O AIZI deverá possuir uma representação própria dos dados industriais.

---

# 6. FASE 3 — IMPORTAÇÃO E CADASTRO

**Status:** EM DESENVOLVIMENTO

## Objetivo

Permitir que dados existentes sejam incorporados ao AIZI.

## Fontes

### TOTVS

Importação de:

* produtos;
* componentes;
* estruturas;
* quantidades;
* descrições;
* unidades;
* custos;
* NCM;
* demais campos disponíveis.

### Excel

Importação de cadastros e parâmetros quando necessário.

### CSV

Suporte a arquivos estruturados utilizados nos processos atuais.

## Resultado esperado

O AIZI deverá conseguir trabalhar com o cadastro industrial sem depender diretamente do arquivo original.

---

# 7. FASE 4 — MOTOR DE BOM

**Status:** EM DESENVOLVIMENTO

## Objetivo

Construir uma representação confiável da estrutura dos produtos.

## Atividades

* importar BOM;
* identificar produto pai;
* identificar componentes;
* interpretar níveis;
* explodir estrutura;
* calcular quantidades;
* relacionar cadastro;
* gerar árvore;
* validar inconsistências.

## Resultado esperado

Exemplo:

```text
PRODUTO
│
├── CONJUNTO
│   ├── PEÇA
│   ├── PEÇA
│   └── PEÇA
│
└── COMPONENTE
```

O motor deverá servir de base para os demais processos.

---

# 8. FASE 5 — LOCALIZAÇÃO DE DESENHOS

**Status:** PLANEJADA

## Objetivo

Relacionar peças e produtos aos respectivos desenhos técnicos.

## Atividades

* identificar códigos;
* localizar arquivos;
* validar caminhos;
* identificar versões;
* registrar arquivos técnicos;
* calcular hash;
* relacionar desenho ↔ peça.

## Resultado esperado

Para uma peça conhecida, o AIZI deverá conseguir identificar o desenho correspondente quando ele existir na base de arquivos.

---

# 9. FASE 6 — EXTRAÇÃO DE DESENHOS

**Status:** EM DESENVOLVIMENTO

## Objetivo

Extrair informações técnicas dos desenhos PDF.

## Primeira tecnologia

PyMuPDF.

## Informações

* textos;
* números;
* linhas;
* vetores;
* coordenadas;
* contornos;
* páginas;
* dimensões.

## Atividades

* estabilizar `extrator_desenho.py`;
* melhorar identificação de textos;
* melhorar identificação de números;
* preservar coordenadas;
* identificar objetos vetoriais;
* gerar dados estruturados.

## Resultado esperado

O AIZI deverá transformar um PDF técnico em dados que possam ser processados pelos próximos motores.

---

# 10. FASE 7 — DIAGNÓSTICO DE DESENHO

**Status:** EM DESENVOLVIMENTO

## Objetivo

Transformar dados extraídos em diagnóstico técnico.

## Atividades

* identificar dimensões;
* identificar material;
* identificar espessura;
* identificar dobras;
* identificar raios;
* identificar ângulos;
* relacionar informações;
* determinar confiança;
* identificar ambiguidades.

## Resultado esperado

Exemplo:

```text
Componente: 046

Dimensão:
672 x 163 mm

Material:
A36

Espessura:
6.35 mm

Dobras:
2

Status:
VALIDADO / NECESSITA INTERPRETAÇÃO
```

---

# 11. FASE 8 — MOTOR GEOMÉTRICO

**Status:** EM DESENVOLVIMENTO

## Objetivo

Construir uma representação geométrica confiável da peça.

## Atividades

* identificar contornos;
* calcular área;
* calcular perímetro;
* identificar vértices;
* identificar segmentos;
* identificar arcos;
* separar geometrias;
* calcular proporções;
* identificar candidatos;
* criar ranking.

## Resultado esperado

O sistema deverá identificar automaticamente a geometria mais provável da peça.

---

# 12. FASE 9 — ESCALA E IDENTIFICAÇÃO DA PEÇA

**Status:** EM DESENVOLVIMENTO

## Objetivo

Resolver corretamente a relação entre desenho, geometria e dimensões reais.

## Atividades

* calcular escala;
* comparar dimensões;
* comparar proporções;
* comparar área;
* comparar perímetro;
* avaliar candidatos;
* calcular score;
* validar resultado.

## Resultado esperado

O sistema deverá conseguir dizer:

```text
Candidato selecionado:
Componente 046

Score:
130.00

Escala:
1.058438

Erro de proporção:
0.00%
```

Quando não houver segurança:

```text
NECESSITA VALIDAÇÃO
```

---

# 13. FASE 10 — DESENVOLVIMENTO DE CHAPA

**Status:** EM DESENVOLVIMENTO

## Objetivo

Calcular o desenvolvimento de peças dobradas.

## Entradas

* geometria;
* dimensões;
* espessura;
* material;
* raios;
* ângulos;
* quantidade de dobras;
* parâmetros de processo.

## Atividades

* bend allowance;
* bend deduction;
* fator K;
* desenvolvimento;
* validação dimensional;
* múltiplas dobras.

## Resultado esperado

Gerar as dimensões do blank necessário para fabricação.

---

# 14. FASE 11 — PLANEJAMENTO DIMENSIONAL

**Status:** EM DESENVOLVIMENTO

## Objetivo

Relacionar a peça desenvolvida às dimensões comerciais disponíveis.

## Atividades

* identificar dimensões;
* consultar padrões de chapa;
* verificar compatibilidade;
* determinar chapa-base;
* informar impossibilidade;
* indicar necessidade de interpretação.

## Resultado esperado

Exemplo:

```text
Peça:
672 x 163 mm

Material:
A36

Espessura:
6.35 mm

Chapa comercial compatível:
SIM
```

---

# 15. FASE 12 — CALCULADORA DE CORTE

**Status:** EM DESENVOLVIMENTO

## Objetivo

Determinar quantas peças podem ser obtidas de uma chapa.

## Atividades

* orientação;
* quantidade por chapa;
* quantidade necessária;
* sobra;
* aproveitamento;
* comparação entre orientações;
* futura otimização.

## Resultado esperado

Exemplo:

```text
Peças por chapa:
24

Chapas necessárias:
1

Peças produzidas:
24

Sobra:
4

Aproveitamento:
83.33%
```

---

# 16. FASE 13 — NESTING

**Status:** FUTURA

## Objetivo

Evoluir a calculadora de corte para otimização de aproveitamento.

## Recursos futuros

* múltiplas peças;
* diferentes quantidades;
* diferentes tamanhos;
* rotação;
* espaçamento;
* kerf;
* margens;
* agrupamento;
* otimização.

## Resultado esperado

Gerar uma disposição otimizada das peças na chapa.

---

# 17. FASE 14 — INTEGRAÇÃO DOS MOTORES

**Status:** FUTURA

## Objetivo

Conectar os motores em um fluxo completo.

Exemplo:

```text
TOTVS
 ↓
BOM
 ↓
PEÇA
 ↓
DESENHO
 ↓
EXTRAÇÃO
 ↓
DIAGNÓSTICO
 ↓
GEOMETRIA
 ↓
DESENVOLVIMENTO
 ↓
CHAPA
 ↓
CORTE
 ↓
RESULTADO
```

## Resultado esperado

Executar um processo completo sem necessidade de intervenção manual em cada etapa.

---

# 18. FASE 15 — PROCESSAMENTO EM LOTE

**Status:** FUTURA

## Objetivo

Processar grandes quantidades de peças automaticamente.

Exemplo:

```text
100 peças
 ↓
100 desenhos
 ↓
Extração
 ↓
Diagnóstico
 ↓
Geometria
 ↓
Desenvolvimento
 ↓
Corte
 ↓
Relatório
```

O processamento deverá identificar automaticamente erros e exceções.

---

# 19. FASE 16 — INTERFACE

**Status:** FUTURA**

## Objetivo

Criar uma interface para utilização dos motores.

Inicialmente:

```text
Desktop
```

Posteriormente:

```text
Web
API
Dashboard
```

## Princípio

A interface não conterá lógica de engenharia.

Ela apenas utilizará os serviços existentes.

---

# 20. FASE 17 — RELATÓRIOS

**Status:** FUTURA

## Objetivo

Transformar resultados técnicos em informações úteis para engenharia e produção.

Possíveis relatórios:

* diagnóstico de desenho;
* lista de peças;
* desenvolvimento;
* plano de corte;
* consumo de chapa;
* aproveitamento;
* inconsistências;
* peças pendentes de validação.

---

# 21. FASE 18 — INTELIGÊNCIA ARTIFICIAL

**Status:** FUTURA**

## Objetivo

Adicionar IA sobre a base estruturada criada pelos motores determinísticos.

Aplicações:

* interpretação de desenhos;
* classificação;
* identificação de padrões;
* análise de inconsistências;
* recomendação;
* explicação;
* auxílio à decisão.

## Princípio

A IA não deverá substituir automaticamente cálculos confiáveis.

Fluxo:

```text
Motor
 ↓
Resultado estruturado
 ↓
IA
 ↓
Interpretação
 ↓
Recomendação
```

---

# 22. FASE 19 — APRENDIZADO COM VALIDAÇÕES

**Status:** FUTURA

## Objetivo

Utilizar as correções realizadas pelos engenheiros para melhorar o sistema.

Exemplo:

```text
AIZI identifica peça
 ↓
Engenheiro corrige
 ↓
Correção registrada
 ↓
Base de conhecimento
 ↓
Futuras análises
```

A validação humana passa a ser fonte de conhecimento.

---

# 23. FASE 20 — INTEGRAÇÃO COM PRODUÇÃO

**Status:** FUTURA

## Objetivo

Expandir o AIZI da engenharia para processos de produção.

Possibilidades:

* tempos;
* processos;
* recursos;
* capacidade;
* planejamento;
* gargalos;
* consumo;
* custos;
* sequenciamento.

---

# 24. FASE 21 — MOTOR DE PROCESSOS

**Status:** FUTURA

O AIZI poderá evoluir para interpretar o processo completo de fabricação.

Exemplo:

```text
Peça
 ↓
Corte
 ↓
Dobra
 ↓
Solda
 ↓
Acabamento
 ↓
Montagem
```

Cada operação poderá possuir:

* tempo;
* recurso;
* máquina;
* pessoas;
* capacidade;
* sequência;
* restrições.

---

# 25. FASE 22 — PLANEJAMENTO INDUSTRIAL

**Status:** FUTURA

Após consolidar os motores de engenharia, o AIZI poderá evoluir para planejamento industrial.

Possibilidades:

* capacidade;
* cronograma;
* gargalos;
* sequenciamento;
* carga;
* recursos;
* lead time;
* previsão;
* cenários.

---

# 26. FASE 23 — INTEGRAÇÃO COM ERP

**Status:** FUTURA

O AIZI poderá evoluir de consumidor de dados para participante ativo do fluxo industrial.

Possibilidades:

```text
ERP
 ↕
AIZI
 ↕
Engenharia
 ↕
Produção
```

Qualquer escrita automática em sistemas externos deverá ser implementada somente após validação e controle apropriados.

---

# 27. FASE 24 — ECOSSISTEMA AIZI

**Status:** VISÃO FUTURA

A longo prazo, o AIZI poderá possuir diferentes módulos especializados.

```text
                    AIZI
                      │
      ┌───────────────┼────────────────┐
      │               │                │
 Engenharia       Produção           IA
      │               │                │
 ┌────┼────┐      ┌───┼────┐      ┌────┼────┐
 BOM Desenho       PCP Corte       Análise
 Geo Corte         Capacidade      Previsão
 Dobras Processos  Gargalos        Recomendação
```

---

# 28. PRIORIDADE DE DESENVOLVIMENTO

A prioridade inicial será:

```text
1. Fundação
2. Base técnica
3. Modelo de dados
4. Cadastro
5. BOM
6. Desenho
7. Diagnóstico
8. Geometria
9. Desenvolvimento
10. Corte
11. Integração
12. Interface
13. IA
```

Não antecipar funcionalidades complexas de IA antes da consolidação dos dados e motores.

---

# 29. CRITÉRIO DE PRONTO

Uma fase será considerada concluída quando:

1. a funcionalidade estiver implementada;
2. existir teste;
3. existir resultado verificável;
4. erros conhecidos estiverem documentados;
5. o módulo estiver integrado corretamente;
6. a documentação estiver atualizada.

"Funciona uma vez" não será considerado conclusão.

---

# 30. REGRA DE EVOLUÇÃO

Cada nova funcionalidade deverá responder:

```text
O que ela resolve?
Qual módulo é responsável?
Quais dados recebe?
Qual resultado produz?
Como será testada?
Quem utilizará o resultado?
```

Se essas perguntas não puderem ser respondidas, a funcionalidade ainda não está suficientemente definida.

---

# 31. CONTROLE DE ESCOPO

O projeto deverá evitar expansão descontrolada.

Novas ideias serão registradas e classificadas como:

```text
ESSENCIAL
IMPORTANTE
FUTURA
EXPERIMENTAL
```

Uma ideia interessante não deverá automaticamente entrar na próxima etapa.

---

# 32. PRINCÍPIO DE ENTREGA

O AIZI deverá evoluir através de pequenos incrementos funcionais.

Exemplo:

```text
Importar BOM
 ↓
Testar
 ↓
Corrigir
 ↓
Persistir
 ↓
Testar
 ↓
Integrar
```

E não:

```text
Construir tudo
 ↓
Testar no final
```

---

# 33. ESTADO ATUAL DO PROJETO

Neste momento existem componentes já desenvolvidos ou em desenvolvimento relacionados a:

* importação TOTVS;
* cadastro de produtos;
* explosão de BOM;
* banco de dados;
* modelos;
* extração de PDF;
* diagnóstico de desenho;
* geometria;
* ranking de candidatos;
* cálculo dimensional;
* desenvolvimento;
* planejamento dimensional;
* cálculo de corte.

O próximo trabalho deverá priorizar a consolidação desses componentes dentro da arquitetura definida.

---

# 34. PRÓXIMA ETAPA IMEDIATA

Após a conclusão deste documento, não será iniciado um novo grande módulo imediatamente.

Primeiro deverá ser executado:

```text
aizi_context.py
```

para consolidar:

```text
_CONTEXT.md
ARQUITETURA.md
DECISOES.md
ROADMAP.md
```

Depois será realizada uma análise do estado atual do código.

Somente então serão definidas as próximas alterações técnicas.

---

# 35. VISÃO FINAL

O roadmap do AIZI segue uma lógica deliberada:

```text
FUNDAMENTO
    ↓
DADOS
    ↓
ESTRUTURA
    ↓
ENGENHARIA
    ↓
AUTOMAÇÃO
    ↓
IA
    ↓
DECISÃO
```

O projeto não será construído começando pela inteligência artificial.

Será construída primeiro uma base de engenharia capaz de produzir dados confiáveis.

A inteligência será adicionada sobre essa base.

---

# 36. PRINCÍPIO FINAL

> **Construir primeiro a capacidade de entender e calcular. Depois construir a capacidade de interpretar. Finalmente construir a capacidade de decidir.**

Esse será o princípio de evolução do AIZI Engineering AI.