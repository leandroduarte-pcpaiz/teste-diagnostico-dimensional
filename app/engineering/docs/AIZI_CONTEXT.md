# AIZI ENGINEERING AI
## CONTEXTO CENTRAL DO PROJETO

Versão do contexto: 1.0
Data: 2026-08-12

---

# 1. OBJETIVO

AIZI Engineering AI é uma plataforma de engenharia voltada para
manufatura, engenharia, planejamento e produção.

A AIZI NÃO deve ser construída como um simples chatbot.

A IA deve atuar como motor de engenharia dentro da plataforma.

---

# 2. AMBIENTE

Sistema operacional:
Windows

Projeto:
C:\Projetos\AIZI Engineering AI

Python:
Virtual environment (.venv)

Principais bibliotecas:
- PyMuPDF / fitz
- SQLAlchemy
- openpyxl
- customtkinter

ERP:
TOTVS Protheus

---

# 3. ARQUITETURA

Fluxo geral:

TOTVS
 ↓
Importadores
 ↓
Banco de dados
 ↓
Engenharia
 ↓
Diagnóstico
 ↓
Planejamento
 ↓
Corte
 ↓
Produção

---

# 4. MÓDULO DE DESENHO

Arquivo principal:

app/teste/diagnostico_desenho.py

Responsabilidade:

- ler PDF técnico;
- extrair textos;
- extrair dimensões;
- identificar geometria;
- identificar contornos;
- identificar dobras;
- determinar material;
- determinar espessura;
- calcular desenvolvimento.

O diagnóstico NÃO deve calcular aproveitamento de chapa.

---

# 5. DESENVOLVIMENTO

O desenvolvimento deve ser calculado antes da calculadora de corte.

Fluxo:

PDF
 ↓
Diagnóstico geométrico
 ↓
Desenvolvimento
 ↓
Blank
 ↓
JSON
 ↓
Calculadora de corte

A calculadora de corte NÃO deve recalcular o blank.

---

# 6. COMPONENTE ATUAL

Componente:
046

Arquivo:
I1044988.pdf

Dimensão externa estimada:

672,0023 × 162,9995 mm

Espessura:

6,35 mm

Material:

CH AÇO ASTM A36

Dobras:

2 × 90°

Raio:

R10

Desenvolvimento atualmente calculado:

645,5988 mm

Diferença:

672,0023 - 645,5988 = 26,4035 mm

STATUS:

O desenvolvimento ainda precisa ser validado matematicamente
antes de ser considerado definitivo.

---

# 7. CALCULADORA DE CORTE

Arquivo:

calculadora_corte.py

Responsabilidade:

Receber a geometria já calculada e determinar:

- peças por chapa;
- orientação;
- chapas necessárias;
- peças produzidas;
- peças sobrando;
- aproveitamento;
- sobra.

A calculadora NÃO deve recalcular desenvolvimento.

---

# 8. JSON DE INTEGRAÇÃO

Arquivo planejado:

_calculadora_corte.json

Ele será a ponte entre:

diagnostico_desenho.py

e

calculadora_corte.py

Estrutura prevista:

{
    "componente": "046",
    "dimensoes_externas_mm": {},
    "blank_mm": {},
    "espessura_mm": 6.35,
    "material": "",
    "dobras": [],
    "status_geometrico": "",
    "metodo": ""
}

---

# 9. ESTADO ATUAL

ETAPA 1:
Diagnóstico do PDF
[EM DESENVOLVIMENTO]

ETAPA 2:
Validação do desenvolvimento
[PENDENTE]

ETAPA 3:
JSON de integração
[PENDENTE]

ETAPA 4:
Calculadora de corte integrada ao JSON
[PENDENTE]

ETAPA 5:
Catálogo de chapas comerciais
[PENDENTE]

ETAPA 6:
Escolha automática da melhor chapa
[PENDENTE]

ETAPA 7:
Plano de corte
[PENDENTE]

---

# 10. REGRA FUNDAMENTAL

Não avançar para otimização de chapa enquanto o desenvolvimento
da peça não estiver matematicamente validado.

---

# 11. PRINCÍPIO DO PROJETO

Cada módulo deve ter uma responsabilidade clara.

Diagnóstico:
"Qual é a geometria?"

Desenvolvimento:
"Qual é o blank?"

Calculadora de corte:
"Como colocar o blank na matéria-prima?"

Otimização:
"Qual matéria-prima gera o melhor resultado?"

Produção:
"Como fabricar?"
