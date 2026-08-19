# AIZI ENGINEERING AI

## CONTEXTO CENTRAL DO PROJETO

**Projeto:** AIZI Engineering AI
**Finalidade:** Plataforma de engenharia e inteligência aplicada à manufatura
**Data de consolidação:** 12/08/2026

---

# 1. VISÃO DO PROJETO

O AIZI Engineering AI é uma plataforma de engenharia voltada para aplicação prática de inteligência, automação e análise de dados nos processos industriais.

O objetivo não é criar simplesmente um "chat com IA".

O AIZI deve funcionar como uma plataforma de engenharia capaz de:

* interpretar informações técnicas;
* integrar dados de produtos e estruturas;
* analisar desenhos técnicos;
* realizar cálculos de engenharia;
* apoiar planejamento dimensional;
* apoiar processos de corte;
* analisar estruturas de produtos;
* integrar informações provenientes do ERP;
* apoiar PCP e planejamento de produção;
* organizar conhecimento técnico;
* criar rastreabilidade das decisões;
* evoluir progressivamente para automação de processos de engenharia.

---

# 2. PRINCÍPIO CENTRAL

O AIZI deve ser construído como uma plataforma modular.

A inteligência não deve ficar concentrada em um único programa ou script.

Cada domínio deve possuir responsabilidades próprias e interfaces claras.

A arquitetura deve permitir evolução gradual sem necessidade de reconstruir o sistema inteiro.

---

# 3. AMBIENTE ATUAL

Sistema operacional principal:

* Windows

Ambiente de desenvolvimento:

* Python
* ambiente virtual `.venv`
* PowerShell
* VS Code

Diretório principal:

```text
C:\Projetos\AIZI Engineering AI
```

---

# 4. ESTRUTURA ATUAL CONHECIDA

A estrutura atual do projeto já possui diversos módulos e diretórios.

Estrutura principal conhecida:

```text
AIZI Engineering AI
│
├── aizi_context.py
│
├── app
│   ├── database
│   ├── engineering
│   ├── ia
│   ├── importadores
│   ├── pcp
│   ├── scanner
│   ├── services
│   ├── teste
│   ├── ui
│   └── utils
│
├── arquivos
├── config
├── data
├── diagnostico
├── docs
└── ...
```

A arquitetura existente deve ser preservada.

Não deve ser criada uma estrutura paralela apenas para substituir a organização atual.

---

# 5. DOCUMENTAÇÃO CENTRAL DO AIZI

A documentação de contexto está sendo organizada em:

```text
docs
└── AIZI
    ├── AIZI_CONTEXT.md
    ├── ARQUITETURA.md
    ├── DECISOES.md
    ├── ROADMAP.md
    └── _CONTEXT
        └── _COMPLETO.md
```

O arquivo:

```text
_CONTEXT/_COMPLETO.md
```

é um documento consolidado gerado automaticamente a partir dos documentos de contexto.

Ele não deve ser tratado como documento principal para edição manual.

Os documentos principais são:

* `AIZI_CONTEXT.md`
* `ARQUITETURA.md`
* `DECISOES.md`
* `ROADMAP.md`

---

# 6. MÓDULOS DE ENGENHARIA

O projeto já possui ou já trabalhou com módulos relacionados a:

* importação de dados do TOTVS;
* explosão de BOM;
* motor de engenharia;
* cadastro de produtos;
* materiais;
* cálculo de corte;
* extração de desenhos;
* diagnóstico de desenhos;
* extração dimensional;
* planejamento dimensional;
* cálculo de desenvolvimento;
* análise geométrica;
* PCP;
* testes e validações.

---

# 7. INTEGRAÇÃO COM TOTVS

O AIZI utiliza informações provenientes do TOTVS Protheus.

Entre os dados trabalhados estão:

* código do produto;
* descrição;
* tipo do produto;
* unidade;
* componente;
* descrição do componente;
* quantidade;
* NCM;
* IPI;
* origem;
* preço;
* custo médio;
* estrutura de produto.

Foi desenvolvido um processo de importação de dados exportados do TOTVS.

Um dos formatos trabalhados utiliza:

* separador `;`;
* codificação `latin1`.

---

# 8. EXPLOSÃO DE BOM

O projeto possui conceito de explosão de estrutura de produto.

A explosão permite percorrer:

```text
Produto
    ↓
Componentes
    ↓
Subcomponentes
    ↓
Estrutura completa
```

O objetivo é transformar a estrutura do ERP em informação utilizável pelos módulos de engenharia.

Também foi criado o conceito de um motor de engenharia capaz de enriquecer a explosão da BOM com dados do cadastro de produtos.

---

# 9. BANCO DE DADOS

O projeto possui estrutura de banco de dados em:

```text
app/database
```

Já foram trabalhados conceitos de:

* conexão;
* repositórios;
* modelos;
* produtos;
* peças;
* materiais;
* projetos;
* arquivos técnicos;
* configurações.

SQLAlchemy faz parte do ambiente utilizado.

---

# 10. PROCESSAMENTO DE DESENHOS TÉCNICOS

Uma das áreas mais importantes do AIZI é a interpretação automática de desenhos técnicos.

O projeto utiliza PDF como uma das principais fontes de informação.

Foi utilizado:

```text
PyMuPDF / fitz
```

para análise de arquivos PDF.

O sistema já consegue analisar elementos como:

* textos;
* textos numéricos;
* linhas vetoriais;
* contornos;
* dimensões;
* geometria;
* coordenadas;
* elementos relacionados a dobras.

---

# 11. DIAGNÓSTICO DE DESENHO

Foi desenvolvido um processo de diagnóstico de desenho.

O diagnóstico trabalha com:

* identificação do arquivo;
* número de páginas;
* tamanho da página;
* textos encontrados;
* dimensões numéricas;
* linhas vetoriais;
* contornos;
* geometria;
* possíveis dobras;
* material;
* espessura.

Exemplo real já analisado:

```text
Componente: 046
Dimensão estimada: aproximadamente 672 x 163 mm
Material: CH AÇO ASTM A36
Espessura: 6,35 mm
```

Também foram identificadas informações de dobra, incluindo:

```text
Dobra: 90°
Raio: R10
```

---

# 12. ANÁLISE GEOMÉTRICA

O sistema já trabalha com elementos geométricos extraídos do desenho.

Entre os dados analisados estão:

* quantidade de segmentos;
* segmentos retos;
* vértices;
* área;
* perímetro;
* contornos;
* dimensões;
* escala geométrica;
* proporção.

Em um dos testes reais:

```text
Componente: 046
Segmentos: 48
Vértices: 49
Dimensão alvo: aproximadamente 672 x 163 mm
```

Essas informações foram utilizadas para criar um ranking de candidatos geométricos.

---

# 13. IDENTIFICAÇÃO DA PEÇA

Foi desenvolvido um conceito de ranking de candidatos.

O objetivo é relacionar:

```text
Informações do desenho
        ↓
Geometria encontrada
        ↓
Dimensões
        ↓
Cadastro de peças
        ↓
Candidato mais provável
```

O ranking já considera fatores como:

* número de segmentos;
* dimensões;
* proporção;
* escala;
* área;
* correspondência geométrica.

---

# 14. CÁLCULO DE DESENVOLVIMENTO

O projeto possui um módulo de cálculo de desenvolvimento de peças.

Uma das áreas críticas é determinar o blank/desenvolvimento de peças dobradas.

São consideradas informações como:

* comprimento;
* largura;
* espessura;
* raio;
* ângulo;
* quantidade de dobras;
* material;
* fator relacionado à dobra;
* bend allowance;
* geometria.

O projeto já passou por versões de:

```text
Calculadora de Desenvolvimento
V1
V2
```

A V2 trabalha com ranking dos candidatos geométricos.

---

# 15. PROBLEMA TÉCNICO JÁ ENCONTRADO

Em determinado estágio, o diagnóstico apresentou:

```text
PatternError: nothing to repeat at position 33
```

Esse problema estava relacionado à expressão regular utilizada no processamento.

A correção desse problema faz parte do histórico de evolução do diagnóstico.

---

# 16. CÁLCULO DE CORTE

O projeto possui uma calculadora de corte.

Ela considera:

* dimensão da peça;
* largura da chapa;
* comprimento da chapa;
* orientação;
* quantidade de peças por chapa;
* quantidade de chapas necessárias;
* aproveitamento;
* sobras.

Exemplo já validado:

```text
Material: G2005887
Descrição: CHAPA ACO A36
Espessura: 6,35 mm

Peça:
500 x 1000 mm

Chapa:
2000 x 6000 mm

Resultado:
24 peças por chapa
1 chapa necessária
24 peças produzidas
4 peças sobrando
```

---

# 17. PLANEJAMENTO DIMENSIONAL

O projeto possui conceito de planejador dimensional.

O planejador deve relacionar:

```text
Peça
↓
Dimensões
↓
Material
↓
Espessura
↓
Chapa comercial
↓
Orientação
↓
Aproveitamento
↓
Necessidade de material
```

Também foram definidas referências de tamanhos comerciais de chapas.

---

# 18. PCP E PRODUÇÃO

O AIZI também possui um domínio relacionado ao planejamento e controle da produção.

O contexto industrial considerado inclui fabricação de implementos rodoviários, especialmente rodotrem.

Foram discutidos processos como:

* pré-montagem;
* gabarito;
* solda;
* acessórios;
* montagem de viga;
* montagem de solda;
* união;
* montagem do Dolly;
* fluxo das caixas;
* capacidade produtiva;
* cronanálise;
* programação.

---

# 19. SIMULAÇÃO DE PRODUÇÃO

Foram estudados conceitos de simulação de produção.

Ferramentas consideradas:

* FlexSim;
* alternativas de simulação.

A finalidade é representar o fluxo produtivo, recursos, pessoas, tempos e restrições.

---

# 20. CONTROLE DE TEMPO DE PRODUÇÃO

Foi desenvolvido conhecimento relacionado ao cálculo de término de produção.

Parâmetros utilizados em determinados modelos:

```text
Início: 07:30
Fim: 17:18
Tempo diário: 9:48
```

Também foram consideradas:

* segunda a sexta;
* finais de semana;
* continuidade para o próximo dia útil;
* carga produtiva;
* duração em formato de tempo do Excel;
* duração em dias produtivos.

---

# 21. TECNOLOGIAS UTILIZADAS

Tecnologias e bibliotecas já utilizadas ou consideradas:

* Python
* PyMuPDF
* SQLAlchemy
* openpyxl
* customtkinter
* darkdetect
* greenlet
* packaging
* typing_extensions
* Excel
* VBA
* Power BI
* TOTVS Protheus
* FlexSim

---

# 22. INTERFACE

O projeto possui diretório:

```text
app/ui
```

A interface deve evoluir como parte da plataforma.

O objetivo não é transformar todos os processos em scripts isolados.

Os scripts e motores devem futuramente ser utilizados como serviços/módulos da plataforma.

---

# 23. PRINCÍPIO DE EVOLUÇÃO

O desenvolvimento do AIZI deve seguir uma evolução incremental.

Primeiro:

```text
Dados confiáveis
```

Depois:

```text
Motores confiáveis
```

Depois:

```text
Integração entre motores
```

Depois:

```text
Interface
```

Depois:

```text
Automação
```

E posteriormente:

```text
Inteligência avançada
```

---

# 24. IA NO AIZI

A inteligência artificial deve ser aplicada como componente da plataforma.

Ela não deve substituir os motores determinísticos quando estes forem mais adequados.

Exemplo:

```text
Cálculo matemático
        ↓
Motor determinístico
```

Enquanto:

```text
Interpretação
Classificação
Inferência
Explicação
        ↓
IA
```

O sistema deve combinar os dois.

---

# 25. PRINCÍPIO DE CONFIABILIDADE

Sempre que um resultado puder ser calculado deterministicamente, deve-se priorizar um motor determinístico.

A IA deve atuar principalmente onde existe:

* interpretação;
* classificação;
* associação;
* inferência;
* reconhecimento de padrões;
* decisão assistida.

---

# 26. ESTADO ATUAL

O projeto encontra-se em fase de construção e consolidação arquitetural.

Já existem diversos módulos experimentais e funcionais.

Neste momento está sendo criada uma camada documental central para registrar:

* contexto;
* arquitetura;
* decisões;
* roadmap.

O sistema `aizi_context.py` já foi criado e está funcionando como mecanismo de consolidação dos documentos de contexto.

---

# 27. SITUAÇÃO DOS DOCUMENTOS

Atualmente:

```text
AIZI_CONTEXT.md
→ em construção

ARQUITETURA.md
→ ainda será estruturado

DECISOES.md
→ ainda será estruturado

ROADMAP.md
→ ainda será estruturado

_CONTEXT/_COMPLETO.md
→ gerado automaticamente
```

---

# 28. REGRA IMPORTANTE PARA O DESENVOLVIMENTO

Não reconstruir o projeto do zero.

Não substituir a arquitetura atual sem necessidade.

Não criar estruturas paralelas sem justificativa.

Não apagar módulos existentes sem validação.

Toda evolução deve considerar o que já foi construído.

---

# 29. OBJETIVO FINAL

O AIZI deve evoluir para uma plataforma capaz de conectar:

```text
ERP
│
├── Produtos
├── Estruturas
├── Materiais
└── Custos
        │
        ▼
ENGENHARIA
│
├── Desenhos
├── Geometria
├── Dimensional
├── Desenvolvimento
├── Corte
└── Materiais
        │
        ▼
PLANEJAMENTO
│
├── PCP
├── Capacidade
├── Cronanálise
└── Simulação
        │
        ▼
INTELIGÊNCIA
│
├── Classificação
├── Inferência
├── Análise
└── Automação
        │
        ▼
DECISÃO INDUSTRIAL
```

---

# 30. DIRETRIZ CENTRAL

O AIZI Engineering AI deve ser tratado como uma **plataforma de engenharia industrial**, e não como um simples aplicativo de IA.

A construção deve priorizar:

1. confiabilidade;
2. rastreabilidade;
3. modularidade;
4. integração;
5. reutilização;
6. automação;
7. inteligência;
8. evolução contínua.

Este documento representa o contexto-base conhecido do projeto até 12/08/2026.