# AIZI ENGINEERING AI

# CONTEXTO COMPLETO

Gerado em: 2026-08-13 10:56:24


================================================================================
# _CONTEXT.md
================================================================================

ARQUIVO NAO ENCONTRADO
Caminho esperado: C:\Projetos\AIZI Engineering AI\docs\AIZI\_CONTEXT.md


================================================================================
# ARQUITETURA.md
================================================================================

# AIZI ENGINEERING AI

# ARQUITETURA DO SISTEMA

**Versão:** 1.0
**Data:** 13/08/2026
**Status:** Arquitetura base do projeto

---

# 1. OBJETIVO

O AIZI Engineering AI é uma plataforma de engenharia orientada à indústria, projetada para transformar dados técnicos, cadastros, estruturas de produtos, desenhos, informações de fabricação e regras de engenharia em decisões estruturadas para apoio à engenharia e à produção.

O sistema não deve ser concebido como um chatbot.

A arquitetura deve priorizar:

* processamento estruturado;
* rastreabilidade;
* regras de engenharia;
* cálculos determinísticos;
* integração com dados industriais;
* reutilização de módulos;
* separação entre dados, regras e interface;
* possibilidade de evolução para modelos de inteligência artificial;
* geração de resultados técnicos verificáveis.

A IA será um componente da plataforma, e não a própria plataforma.

---

# 2. PRINCÍPIO FUNDAMENTAL

O AIZI deve funcionar como uma plataforma de engenharia composta por motores especializados.

A arquitetura geral segue o princípio:

```text
DADOS
  ↓
IMPORTAÇÃO
  ↓
NORMALIZAÇÃO
  ↓
MODELO DE DADOS
  ↓
MOTORES DE ENGENHARIA
  ↓
VALIDAÇÃO
  ↓
RESULTADO TÉCNICO
  ↓
DECISÃO / PLANEJAMENTO
```

Quando necessário, componentes de IA poderão atuar sobre os resultados estruturados:

```text
DADOS → ENGENHARIA → RESULTADO ESTRUTURADO → IA → INTERPRETAÇÃO / RECOMENDAÇÃO
```

A IA não deve substituir cálculos determinísticos quando estes puderem ser realizados por regras matemáticas ou algoritmos verificáveis.

---

# 3. ARQUITETURA EM CAMADAS

O sistema será organizado em camadas.

```text
┌─────────────────────────────────────────────┐
│                 INTERFACE                   │
│        Desktop / Web / Relatórios          │
├─────────────────────────────────────────────┤
│              ORQUESTRAÇÃO                   │
│     Fluxos / Projetos / Processamentos     │
├─────────────────────────────────────────────┤
│          MOTORES DE ENGENHARIA              │
│ BOM | Desenho | Dimensional | Corte | etc. │
├─────────────────────────────────────────────┤
│             REGRAS DE NEGÓCIO               │
│ Materiais | Processos | Fabricação | etc.  │
├─────────────────────────────────────────────┤
│              MODELO DE DADOS                │
│ Peça | Produto | Material | Projeto | etc. │
├─────────────────────────────────────────────┤
│              PERSISTÊNCIA                   │
│             Banco de Dados                  │
├─────────────────────────────────────────────┤
│             INTEGRAÇÕES                     │
│       TOTVS | Arquivos | PDF | Excel       │
└─────────────────────────────────────────────┘
```

---

# 4. CAMADA DE DADOS DE ENTRADA

O AIZI receberá informações provenientes de diferentes fontes industriais.

Principais fontes:

* TOTVS Protheus;
* arquivos CSV;
* arquivos Excel;
* desenhos técnicos em PDF;
* documentos técnicos;
* bancos de dados;
* arquivos internos da empresa;
* informações de projetos;
* dados de produção;
* parâmetros definidos pela engenharia.

A origem dos dados deve ser preservada sempre que possível.

Cada informação importante deverá possuir rastreabilidade para sua origem.

---

# 5. IMPORTADORES

Os importadores são responsáveis por transformar dados externos em estruturas internas compreendidas pelo AIZI.

Exemplos:

```text
app/
└── importadores/
    ├── importador_totvs.py
    ├── importador_excel.py
    ├── importador_csv.py
    └── ...
```

Os importadores não devem conter regras complexas de engenharia.

Sua responsabilidade principal é:

1. localizar os dados;
2. ler os dados;
3. validar a estrutura;
4. normalizar campos;
5. converter tipos;
6. registrar erros;
7. entregar dados ao sistema.

---

# 6. INTEGRAÇÃO COM TOTVS

O TOTVS Protheus é considerado uma fonte externa de dados industriais.

Entre os dados relevantes estão:

* código do produto;
* descrição;
* unidade;
* tipo de produto;
* estrutura de produto;
* componentes;
* quantidade;
* custo;
* NCM;
* origem;
* demais informações cadastrais.

A integração deve permitir a utilização desses dados pelos motores de engenharia sem acoplar diretamente os motores ao formato original do TOTVS.

Fluxo:

```text
TOTVS
  ↓
CSV / Integração
  ↓
Importador
  ↓
Normalização
  ↓
Modelo AIZI
  ↓
Motores de Engenharia
```

---

# 7. ESTRUTURA DE PRODUTO / BOM

O sistema deverá possuir um motor específico para interpretação e explosão de estruturas de produtos.

Responsabilidades:

* carregar estruturas;
* identificar níveis;
* identificar produto pai;
* identificar componentes;
* calcular quantidades;
* realizar explosão recursiva;
* montar árvore de componentes;
* relacionar cadastro;
* identificar peças e conjuntos;
* fornecer estrutura aos demais motores.

Exemplo:

```text
PRODUTO
│
├── CONJUNTO A
│   ├── PEÇA 01
│   ├── PEÇA 02
│   └── PEÇA 03
│
├── CONJUNTO B
│   ├── PEÇA 04
│   └── PEÇA 05
│
└── COMPONENTE C
```

O motor de BOM deve ser independente da interface.

---

# 8. MODELO DE DOMÍNIO

O AIZI utilizará objetos de domínio para representar entidades industriais.

Entidades principais:

```text
Projeto
ArquivoTecnico
Produto
Peca
Material
Configuracao
EstruturaBOM
Desenho
Dimensao
Operacao
Processo
```

Os modelos devem representar conceitos de engenharia e não simplesmente copiar tabelas externas.

---

# 9. BANCO DE DADOS

O banco de dados será responsável pela persistência das informações estruturadas do AIZI.

Estrutura inicial:

```text
app/
└── database/
    ├── database.py
    ├── repository.py
    └── models/
        ├── arquivo_tecnico.py
        ├── projeto.py
        ├── peca.py
        ├── material.py
        └── configuracao.py
```

A camada de persistência deve ser separada dos motores de engenharia.

Os motores não devem depender diretamente de comandos SQL espalhados pelo código.

O acesso deverá ocorrer preferencialmente através de:

```text
Engine
  ↓
Repository
  ↓
Database
```

---

# 10. REPOSITORIES

Os repositories serão responsáveis por encapsular o acesso aos dados.

Exemplos:

```text
ProdutoRepository
PecaRepository
MaterialRepository
ProjetoRepository
ArquivoTecnicoRepository
```

Responsabilidades:

* salvar;
* consultar;
* atualizar;
* excluir;
* pesquisar;
* recuperar estruturas relacionadas.

Isso permitirá trocar ou evoluir a tecnologia do banco sem reescrever os motores de engenharia.

---

# 11. MOTOR DE ENGENHARIA

O núcleo do AIZI será composto por motores especializados.

Exemplo:

```text
app/
└── engineering/
    ├── motor_engenharia.py
    ├── explosao_bom.py
    ├── extrator_desenho.py
    ├── extrator_dimensional.py
    ├── planejador_dimensional.py
    ├── calculadora_corte.py
    └── ...
```

Cada motor deve possuir uma responsabilidade clara.

Evitar a criação de um único arquivo contendo toda a lógica da plataforma.

---

# 12. MOTOR DE ENGENHARIA GERAL

O `motor_engenharia.py` funcionará como camada de coordenação entre diferentes processos de engenharia.

Ele poderá:

* receber uma peça;
* identificar dados disponíveis;
* consultar cadastro;
* consultar material;
* consultar desenho;
* executar análise dimensional;
* executar cálculos;
* consolidar resultados;
* gerar diagnóstico.

Ele não deve concentrar todas as regras específicas.

As regras devem permanecer nos respectivos motores especializados.

---

# 13. EXTRAÇÃO DE DESENHOS

O AIZI deverá possuir capacidade de analisar desenhos técnicos, inicialmente em PDF.

A tecnologia utilizada atualmente inclui PyMuPDF.

O extrator deve ser capaz de identificar, quando disponível:

* textos;
* números;
* dimensões;
* linhas;
* segmentos;
* contornos;
* coordenadas;
* informações de material;
* espessura;
* indicações de dobra;
* raios;
* ângulos;
* códigos de peças;
* informações técnicas.

Fluxo:

```text
PDF
 ↓
Extração de conteúdo
 ↓
Objetos vetoriais
 ↓
Textos
 ↓
Dimensões
 ↓
Geometria
 ↓
Interpretação
```

---

# 14. DIAGNÓSTICO DE DESENHO

O diagnóstico de desenho deverá ser separado da extração.

Extração responde:

> "O que existe no arquivo?"

Diagnóstico responde:

> "O que os dados encontrados significam para a engenharia?"

Exemplo:

```text
PDF
 ↓
Extrator
 ↓
Dados brutos
 ↓
Diagnóstico
 ↓
Dimensões
 ↓
Geometria
 ↓
Dobras
 ↓
Material
 ↓
Espessura
 ↓
Confiança
```

O diagnóstico deverá informar quando uma interpretação não puder ser realizada com segurança.

O sistema não deve inventar dimensões ou características inexistentes.

---

# 15. INTERPRETAÇÃO GEOMÉTRICA

A interpretação geométrica será responsável por transformar entidades vetoriais em uma representação geométrica da peça.

Possíveis informações:

* largura;
* comprimento;
* área;
* perímetro;
* número de vértices;
* segmentos retos;
* arcos;
* furos;
* recortes;
* contornos;
* dobras.

Exemplo de resultado:

```text
Componente: 046

Dimensão estimada:
672.00 x 163.00 mm

Área:
107539.40 mm²

Perímetro:
1686.76 mm

Vértices:
49

Segmentos retos:
48

Dobras:
2

Dobra 1:
90°
R10

Dobra 2:
90°
R10
```

Esses dados devem permanecer estruturados.

---

# 16. RANKING DE CANDIDATOS GEOMÉTRICOS

Quando existirem múltiplos contornos ou candidatos dentro de um desenho, o sistema deverá realizar classificação e ranking.

Critérios possíveis:

* número de segmentos;
* proporção;
* dimensões;
* área;
* perímetro;
* escala;
* quantidade de vértices;
* correspondência com dimensões declaradas;
* relação com código da peça;
* coerência com o desenho.

O sistema deve apresentar:

```text
Candidato
Score
Dimensões
Área
Escala
Erro
Confiança
```

A escolha do candidato não deve depender exclusivamente de um único critério.

---

# 17. ESCALA GEOMÉTRICA

Desenhos técnicos podem conter diferentes escalas.

A arquitetura deverá separar:

```text
Dimensão do desenho
        ↓
Dimensão real
        ↓
Fator de escala
```

O sistema deverá registrar o fator utilizado.

Exemplo:

```text
Dimensão detectada:
634.90 mm

Dimensão alvo:
672.00 mm

Escala:
1.058438
```

A escala deve ser validada contra múltiplas dimensões sempre que possível.

---

# 18. PLANEJAMENTO DIMENSIONAL

O `planejador_dimensional.py` deverá transformar informações do desenho em dados úteis para fabricação.

Responsabilidades:

* interpretar dimensões;
* identificar dimensões relevantes;
* relacionar material;
* relacionar espessura;
* avaliar necessidade de desenvolvimento;
* identificar dimensões comerciais;
* determinar possíveis chapas-base;
* informar quando os dados são insuficientes.

O planejador não deve assumir informações que não estejam disponíveis.

---

# 19. DESENVOLVIMENTO DE CHAPAS DOBRADAS

Para peças dobradas, o AIZI deverá possuir uma camada específica para cálculo do desenvolvimento.

Informações relevantes:

* espessura;
* raio interno;
* ângulo;
* quantidade de dobras;
* comprimento dos trechos;
* método de cálculo;
* fator K;
* bend allowance;
* bend deduction;
* tolerância de dobra.

Fluxo:

```text
Geometria final
 ↓
Dobras
 ↓
Parâmetros do material
 ↓
Parâmetros da máquina/processo
 ↓
Cálculo do desenvolvimento
 ↓
Blank
```

Os parâmetros utilizados devem ser registrados para permitir auditoria.

---

# 20. CALCULADORA DE CORTE

O `calculadora_corte.py` será responsável por determinar como peças podem ser obtidas a partir de chapas comerciais.

Dados de entrada:

```text
Peça:
largura
comprimento

Chapa:
largura
comprimento

Parâmetros:
kerf
espaçamento
margem
orientação
```

Resultados possíveis:

```text
Peças por chapa
Chapas necessárias
Peças produzidas
Peças sobrando
Aproveitamento da necessidade
Aproveitamento da chapa
Orientação utilizada
```

O algoritmo deverá avaliar diferentes orientações quando aplicável.

---

# 21. OTIMIZAÇÃO DE CORTE

A calculadora de corte poderá evoluir para um módulo de otimização.

Objetivos:

* reduzir desperdício;
* maximizar aproveitamento;
* reduzir quantidade de chapas;
* agrupar peças;
* considerar diferentes tamanhos;
* considerar rota de corte;
* considerar restrições de fabricação.

A arquitetura deve permitir evolução futura para algoritmos de nesting.

---

# 22. MATERIAIS

O cadastro de materiais deverá ser tratado como uma entidade própria.

Informações possíveis:

* código;
* descrição;
* norma;
* composição;
* espessura;
* densidade;
* peso;
* propriedades mecânicas;
* parâmetros de corte;
* parâmetros de dobra;
* parâmetros de fabricação.

Exemplo:

```text
Material:
CH AÇO ASTM A36

Espessura:
6.35 mm
```

Os parâmetros de engenharia não devem ficar hardcoded em múltiplos arquivos.

---

# 23. CONFIGURAÇÕES DE ENGENHARIA

Parâmetros que variam conforme empresa, máquina, processo ou material deverão ser configuráveis.

Exemplos:

* fator K;
* tolerância;
* kerf;
* folga;
* margem;
* dimensões comerciais;
* parâmetros de dobra;
* parâmetros de corte;
* regras de fabricação.

Essas informações devem ser armazenadas em configuração ou banco de dados quando apropriado.

---

# 24. RASTREABILIDADE

Todo resultado técnico importante deve permitir responder:

```text
De onde veio este dado?
Qual arquivo foi utilizado?
Qual versão?
Qual algoritmo?
Quais parâmetros?
Qual regra?
Qual cálculo?
Qual resultado intermediário?
```

Exemplo:

```text
Resultado
 ↓
Peça 046
 ↓
Desenho I1044988.pdf
 ↓
Página 1
 ↓
Geometria detectada
 ↓
Dimensões
 ↓
Escala
 ↓
Cálculo
 ↓
Resultado final
```

A rastreabilidade será um requisito fundamental da plataforma.

---

# 25. CONFIANÇA E VALIDAÇÃO

Resultados de engenharia deverão possuir indicação de confiança quando houver interpretação automática.

Exemplo:

```text
CONFIDENÇA: ALTA
```

ou:

```text
CONFIANÇA: MÉDIA
Necessita validação dimensional.
```

ou:

```text
CONFIANÇA: BAIXA
Dados insuficientes para determinar o blank.
```

O sistema deve diferenciar:

```text
DADO EXTRAÍDO
```

de:

```text
DADO INTERPRETADO
```

e de:

```text
DADO CALCULADO
```

---

# 26. PRINCÍPIO DE NÃO INVENÇÃO

O AIZI não deverá fabricar informações técnicas ausentes.

Quando os dados forem insuficientes, o resultado deverá indicar explicitamente:

```text
NECESSITA INTERPRETAÇÃO
```

ou:

```text
DADOS INSUFICIENTES
```

ou:

```text
NECESSITA VALIDAÇÃO HUMANA
```

É preferível não concluir uma informação a produzir um resultado tecnicamente incorreto.

---

# 27. INTELIGÊNCIA ARTIFICIAL

A inteligência artificial deverá ser utilizada principalmente onde exista necessidade de:

* interpretação;
* classificação;
* reconhecimento de padrões;
* correlação de informações;
* análise de documentos;
* recomendação;
* auxílio à decisão;
* explicação de resultados.

A IA não deverá substituir automaticamente cálculos determinísticos.

Exemplo:

```text
Cálculo matemático
        ↓
Motor determinístico
        ↓
Resultado
        ↓
IA
        ↓
Explicação / recomendação
```

---

# 28. CAMADA DE IA

A arquitetura deverá permitir substituir ou adicionar modelos de IA sem modificar os motores principais.

Exemplo:

```text
AIProvider
│
├── Modelo local
├── API externa
├── Modelo especializado
└── Futuro modelo interno
```

Os motores devem receber uma interface abstrata.

Assim, a plataforma não ficará presa a um único fornecedor ou modelo.

---

# 29. ORQUESTRAÇÃO

Processos maiores deverão ser coordenados por uma camada de orquestração.

Exemplo:

```text
Projeto
 ↓
Carregar produto
 ↓
Explodir BOM
 ↓
Identificar peças
 ↓
Localizar desenhos
 ↓
Extrair dados
 ↓
Diagnosticar
 ↓
Calcular desenvolvimento
 ↓
Planejar corte
 ↓
Consolidar resultado
```

A orquestração não deve conter os cálculos específicos.

Ela apenas coordena os motores.

---

# 30. PROJETOS

O conceito de Projeto será utilizado para agrupar:

* produtos;
* peças;
* desenhos;
* versões;
* análises;
* resultados;
* configurações;
* documentos;
* processos.

Estrutura conceitual:

```text
Projeto
│
├── Produto
│
├── BOM
│
├── Peças
│
├── Desenhos
│
├── Materiais
│
├── Análises
│
├── Resultados
│
└── Histórico
```

---

# 31. ARQUIVOS TÉCNICOS

Arquivos externos deverão possuir registro próprio.

Exemplos:

```text
ArquivoTecnico
├── caminho
├── nome
├── extensão
├── tamanho
├── hash
├── data
├── versão
└── origem
```

Isso permitirá rastrear exatamente qual arquivo foi utilizado em uma análise.

---

# 32. VERSIONAMENTO

O AIZI deverá considerar versionamento de:

* desenhos;
* produtos;
* estruturas;
* regras;
* configurações;
* resultados;
* algoritmos;
* parâmetros.

Uma alteração de regra não deve apagar a possibilidade de compreender um resultado produzido anteriormente.

---

# 33. TESTES

Cada motor deverá possuir testes independentes.

Estrutura conceitual:

```text
app/
└── teste/
    ├── teste_bom.py
    ├── teste_cadastro.py
    ├── teste_planejador.py
    ├── teste_diagnostico_desenho.py
    └── ...
```

Os testes deverão validar:

* entradas;
* resultados;
* casos normais;
* casos extremos;
* dados inválidos;
* ausência de informações;
* regressões.

---

# 34. DIAGNÓSTICOS

Os diagnósticos técnicos deverão ser produzidos em formato estruturado sempre que possível.

Exemplo:

```text
{
    "componente": "046",
    "dimensao": {
        "largura_mm": 672.0,
        "altura_mm": 163.0
    },
    "material": "A36",
    "espessura_mm": 6.35,
    "dobras": 2,
    "confianca": "ALTA"
}
```

Arquivos TXT poderão continuar existindo para inspeção humana, mas o JSON deverá ser preferencial para comunicação entre módulos.

---

# 35. FORMATO DOS DADOS ENTRE MÓDULOS

Os módulos devem trocar informações através de estruturas claras.

Evitar:

```text
print()
```

como mecanismo de comunicação entre módulos.

Preferir:

```text
Objeto
Dicionário estruturado
Dataclass
Modelo de domínio
JSON
```

O `print()` deverá ser utilizado principalmente para diagnóstico e interface de execução.

---

# 36. SEPARAÇÃO ENTRE CÓDIGO E DADOS

Regras e parâmetros de engenharia não devem ficar espalhados no código.

Evitar:

```python
if material == "A36":
    fator = 0.38
```

quando o valor puder ser configurável.

Preferir:

```text
Material
 ↓
Parâmetros
 ↓
Motor
 ↓
Cálculo
```

Isso permitirá evolução sem necessidade de alterar o código principal.

---

# 37. ESTRUTURA BASE DO PROJETO

A estrutura deverá evoluir aproximadamente para:

```text
AIZI Engineering AI/
│
├── aizi_context.py
│
├── docs/
│   └── AIZI/
│       ├── _CONTEXT.md
│       ├── ARQUITETURA.md
│       ├── DECISOES.md
│       ├── ROADMAP.md
│       └── _COMPLETO.md
│
├── app/
│   │
│   ├── importadores/
│   │   ├── importador_totvs.py
│   │   ├── importador_excel.py
│   │   └── importador_csv.py
│   │
│   ├── engineering/
│   │   ├── motor_engenharia.py
│   │   ├── explosao_bom.py
│   │   ├── extrator_desenho.py
│   │   ├── extrator_dimensional.py
│   │   ├── planejador_dimensional.py
│   │   ├── calculadora_corte.py
│   │   └── ...
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── repository.py
│   │   └── models/
│   │
│   ├── teste/
│   │   └── ...
│   │
│   └── data/
│
├── diagnostico/
│
├── dados/
│
└── .venv/
```

A estrutura poderá mudar conforme a evolução do projeto.

A arquitetura lógica, entretanto, deve permanecer organizada por responsabilidade.

---

# 38. FLUXO COMPLETO DE ENGENHARIA

O fluxo conceitual principal será:

```text
                ┌───────────────┐
                │     TOTVS     │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │  IMPORTADOR   │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │ NORMALIZAÇÃO  │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │ MODELO AIZI   │
                └───────┬───────┘
                        │
             ┌──────────▼──────────┐
             │      MOTOR BOM      │
             └──────────┬──────────┘
                        │
                ┌───────▼───────┐
                │ IDENTIFICAÇÃO │
                │    DE PEÇAS   │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │    DESENHO    │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │   EXTRAÇÃO    │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │  DIAGNÓSTICO  │
                └───────┬───────┘
                        │
              ┌─────────▼─────────┐
              │  GEO / DIMENSIONAL│
              └─────────┬─────────┘
                        │
                ┌───────▼───────┐
                │ DESENVOLVIMENTO│
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │  PLANEJAMENTO │
                │     DE CORTE  │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │    RESULTADO  │
                └───────────────┘
```

---

# 39. INTERFACE

A interface será uma camada separada dos motores.

Inicialmente poderá existir uma interface desktop.

Posteriormente poderá existir:

```text
Desktop
Web
API
Relatórios
Dashboard
```

Nenhuma dessas interfaces deverá conter a lógica principal de engenharia.

A interface apenas solicita operações e apresenta resultados.

---

# 40. API FUTURA

A arquitetura deve permitir a criação futura de uma API.

Exemplo:

```text
POST /projetos
GET  /projetos
GET  /pecas
POST /diagnostico
POST /desenvolvimento
POST /corte
GET  /resultados
```

A criação da API não é obrigatória na primeira fase, mas a arquitetura deve permitir sua implementação sem reconstruir os motores.

---

# 41. LOGS

O sistema deverá possuir registro de execução.

Informações relevantes:

* início;
* fim;
* módulo;
* arquivo;
* operação;
* erro;
* aviso;
* resultado;
* tempo de processamento.

Exemplo:

```text
[INFO] Iniciando diagnóstico
[INFO] Arquivo: I1044988.pdf
[INFO] Página: 1
[INFO] Vetores: 624
[INFO] Textos: 79
[INFO] Contornos: 7
[INFO] Diagnóstico concluído
```

---

# 42. TRATAMENTO DE ERROS

Erros deverão ser classificados.

Exemplos:

```text
Erro de arquivo
Erro de formato
Erro de importação
Erro de dados
Erro de geometria
Erro de cálculo
Erro de configuração
Erro de banco
Erro de integração
```

O sistema deve evitar mensagens genéricas quando for possível identificar a causa.

---

# 43. PRINCÍPIO DE MODULARIDADE

Cada módulo deve poder ser testado isoladamente.

Exemplo:

```text
Calculadora de corte
```

não deve depender do:

```text
Diagnóstico de desenho
```

para realizar um teste simples.

A dependência deve ocorrer somente quando o fluxo de negócio realmente exigir.

---

# 44. PRINCÍPIO DE REUTILIZAÇÃO

Resultados produzidos por um motor devem poder ser utilizados por outros motores.

Exemplo:

```text
Diagnóstico
      ↓
Geometria
      ↓
Desenvolvimento
      ↓
Corte
```

Não deve ser necessário executar novamente a extração do PDF para cada etapa.

---

# 45. PRINCÍPIO DE DETERMINISMO

Sempre que possível, o mesmo conjunto de entradas e parâmetros deverá produzir o mesmo resultado.

Isso é especialmente importante para:

* cálculos;
* desenvolvimento;
* corte;
* áreas;
* perímetros;
* escalas;
* quantidades;
* custos.

Quando IA for utilizada, o sistema deverá registrar o modelo e os parâmetros relevantes.

---

# 46. PRINCÍPIO DE AUDITORIA

Todo resultado importante deve ser auditável.

Deve ser possível verificar:

```text
Entrada
 ↓
Processamento
 ↓
Regra
 ↓
Parâmetro
 ↓
Resultado
```

A plataforma deve permitir que um engenheiro questione o resultado e consiga identificar como ele foi produzido.

---

# 47. PRINCÍPIO DE EVOLUÇÃO

O AIZI será desenvolvido de forma incremental.

A primeira versão não precisa resolver todos os problemas.

A arquitetura deve permitir adicionar novos motores posteriormente.

Exemplos futuros:

```text
Motor de custos
Motor de soldagem
Motor de usinagem
Motor de pintura
Motor de montagem
Motor de tempos
Motor de capacidade
Motor de planejamento
Motor de qualidade
Motor de manutenção
Motor de compras
Motor de otimização
```

Esses módulos deverão consumir os mesmos modelos e princípios de arquitetura.

---

# 48. VISÃO DE LONGO PRAZO

A arquitetura final poderá evoluir para:

```text
                         AIZI
                          │
          ┌───────────────┼────────────────┐
          │               │                │
       DADOS          ENGENHARIA          IA
          │               │                │
      ┌───┴───┐      ┌────┴────┐      ┌────┴────┐
     TOTVS   PDF    BOM       CAD    Análise   Recomendação
      │       │      │          │       │          │
      └───────┴──────┴──────────┴───────┴──────────┘
                          │
                   MODELO AIZI
                          │
                   DECISÃO TÉCNICA
```

O objetivo é transformar o AIZI em uma camada inteligente entre os dados industriais e a tomada de decisão de engenharia.

---

# 49. REGRA FUNDAMENTAL DA ARQUITETURA

O AIZI deve seguir a seguinte regra:

> **Dados primeiro. Engenharia depois. Inteligência por último.**

Ou seja:

```text
1. Capturar corretamente
2. Estruturar corretamente
3. Validar corretamente
4. Calcular corretamente
5. Interpretar
6. Recomendar
```

A inteligência somente será confiável se os dados e os motores de engenharia forem confiáveis.

---

# 50. ESTADO ATUAL

A arquitetura inicial já possui conceitos implementados ou em desenvolvimento para:

* importação de dados TOTVS;
* explosão de BOM;
* cadastro de produtos;
* banco de dados;
* modelos de domínio;
* extração de desenhos PDF;
* extração dimensional;
* diagnóstico de desenhos;
* identificação geométrica;
* ranking de candidatos;
* cálculo de desenvolvimento;
* planejamento dimensional;
* cálculo de corte;
* geração de diagnósticos estruturados.

Esses componentes deverão ser progressivamente reorganizados dentro da arquitetura definida neste documento.

---

# 51. PRÓXIMA EVOLUÇÃO

Após a definição desta arquitetura, os próximos documentos deverão registrar:

```text
ARQUITETURA.md
        ↓
DECISOES.md
        ↓
ROADMAP.md
```

`ARQUITETURA.md` define **como o sistema é estruturado**.

`DECISOES.md` registrará **por que determinadas escolhas foram feitas**.

`ROADMAP.md` definirá **o que será construído e em qual ordem**.

---

# 52. CONCLUSÃO

O AIZI Engineering AI será construído como uma plataforma modular de engenharia industrial.

Sua arquitetura deverá preservar:

* separação de responsabilidades;
* rastreabilidade;
* determinismo;
* validação;
* modularidade;
* integração com sistemas existentes;
* independência dos motores;
* possibilidade de utilização de IA;
* evolução incremental.

A IA será utilizada para ampliar a capacidade de interpretação e decisão, mas os fundamentos técnicos permanecerão apoiados em dados estruturados, regras de engenharia e cálculos verificáveis.

**AIZI não é um chatbot de engenharia.**

**AIZI é uma plataforma de engenharia com inteligência artificial.**


================================================================================
# DECISOES.md
================================================================================

# AIZI ENGINEERING AI

# DECISÕES DO PROJETO

**Versão:** 1.0
**Data:** 13/08/2026
**Status:** Decisões fundamentais do projeto

---

# 1. OBJETIVO

Este documento registra as decisões arquiteturais, técnicas e conceituais tomadas durante o desenvolvimento do AIZI Engineering AI.

O objetivo é preservar a direção do projeto e evitar que decisões importantes sejam perdidas, alteradas ou contraditas durante futuras implementações.

Uma decisão registrada neste documento deve ser considerada parte da memória técnica oficial do projeto.

---

# 2. DECISÃO 001 — O AIZI NÃO SERÁ UM CHATBOT

**Status:** DEFINIDA

O AIZI Engineering AI não será desenvolvido como um chatbot cuja principal função seja conversar com o usuário.

O produto será uma **plataforma de engenharia industrial**.

A interface conversacional poderá existir no futuro, porém será apenas uma forma de interação com os motores da plataforma.

Princípio:

```text
AIZI = PLATAFORMA DE ENGENHARIA
       +
     IA
```

E não:

```text
AIZI = CHATBOT
```

---

# 3. DECISÃO 002 — A ENGENHARIA É O NÚCLEO

**Status:** DEFINIDA

Os cálculos e regras de engenharia são o núcleo do sistema.

A inteligência artificial deverá complementar os motores de engenharia, e não substituí-los quando existir uma solução determinística.

Exemplo:

```text
Geometria
   ↓
Cálculo
   ↓
Resultado
   ↓
IA interpreta
```

E não:

```text
IA
 ↓
"acho que o resultado é..."
```

---

# 4. DECISÃO 003 — SEPARAÇÃO ENTRE IA E CÁLCULO

**Status:** DEFINIDA

Cálculos matemáticos, geométricos, dimensionais e de fabricação deverão ser executados por algoritmos determinísticos sempre que possível.

A IA será utilizada principalmente para:

* interpretação;
* classificação;
* reconhecimento de padrões;
* análise;
* recomendação;
* correlação;
* explicação.

Isso aumenta a confiabilidade dos resultados.

---

# 5. DECISÃO 004 — NÃO INVENTAR DADOS TÉCNICOS

**Status:** DEFINIDA

O sistema não deverá inventar informações técnicas que não estejam presentes nos dados de entrada ou que não possam ser calculadas de forma justificável.

Quando os dados forem insuficientes, o sistema deverá informar explicitamente a situação.

Exemplos:

```text
DADOS INSUFICIENTES
```

```text
NECESSITA INTERPRETAÇÃO
```

```text
NECESSITA VALIDAÇÃO HUMANA
```

É preferível retornar uma incerteza explícita a gerar um resultado tecnicamente falso.

---

# 6. DECISÃO 005 — RASTREABILIDADE É OBRIGATÓRIA

**Status:** DEFINIDA

Resultados de engenharia deverão possuir rastreabilidade.

Sempre que possível deverá ser possível identificar:

* arquivo de origem;
* página;
* peça;
* versão;
* dados utilizados;
* parâmetros;
* algoritmo;
* cálculo;
* resultado.

O sistema deverá permitir reconstruir como um resultado foi obtido.

---

# 7. DECISÃO 006 — DADOS BRUTOS E DADOS INTERPRETADOS DEVEM SER DIFERENCIADOS

**Status:** DEFINIDA

O AIZI deverá diferenciar claramente:

```text
DADO EXTRAÍDO
```

```text
DADO INTERPRETADO
```

```text
DADO CALCULADO
```

Isso é especialmente importante para análise de desenhos.

Exemplo:

```text
PDF
 ↓
Linha encontrada
 ↓
Geometria interpretada
 ↓
Dimensão calculada
```

Cada etapa possui natureza diferente e não deve ser confundida.

---

# 8. DECISÃO 007 — OS MOTORES DEVEM SER MODULARES

**Status:** DEFINIDA

Cada problema de engenharia deverá possuir um motor especializado quando houver complexidade suficiente para justificar sua separação.

Exemplos:

```text
Motor BOM
Motor de desenho
Motor dimensional
Motor geométrico
Motor de desenvolvimento
Motor de corte
Motor de materiais
```

Não será criado um único motor monolítico contendo toda a lógica do AIZI.

---

# 9. DECISÃO 008 — A INTERFACE NÃO TERÁ A LÓGICA DE ENGENHARIA

**Status:** DEFINIDA

A interface será responsável por:

* receber comandos;
* apresentar informações;
* exibir resultados;
* solicitar operações.

A interface não deverá conter os cálculos principais.

Fluxo:

```text
INTERFACE
   ↓
ORQUESTRAÇÃO
   ↓
MOTOR
   ↓
RESULTADO
   ↓
INTERFACE
```

Isso permitirá trocar a interface sem reconstruir os motores.

---

# 10. DECISÃO 009 — O BANCO DE DADOS SERÁ SEPARADO DOS MOTORES

**Status:** DEFINIDA

Os motores não deverão acessar diretamente o banco de dados através de comandos SQL espalhados pelo código.

Será utilizada uma camada de persistência/repository.

Fluxo:

```text
MOTOR
 ↓
REPOSITORY
 ↓
DATABASE
```

Essa separação facilita manutenção e evolução futura.

---

# 11. DECISÃO 010 — TOTVS É FONTE DE DADOS, NÃO O MODELO INTERNO

**Status:** DEFINIDA

O TOTVS Protheus será tratado como uma fonte externa.

Os formatos de dados do TOTVS não deverão contaminar a arquitetura interna do AIZI.

Fluxo:

```text
TOTVS
 ↓
IMPORTADOR
 ↓
NORMALIZAÇÃO
 ↓
MODELO AIZI
```

Isso permite que futuramente outras fontes sejam utilizadas sem modificar os motores.

---

# 12. DECISÃO 011 — O MODELO INTERNO REPRESENTA O DOMÍNIO

**Status:** DEFINIDA

Os modelos internos devem representar conceitos da engenharia.

Exemplos:

```text
Produto
Peça
Material
Projeto
Arquivo Técnico
Desenho
Dimensão
Operação
Processo
```

O sistema não deverá simplesmente reproduzir estruturas de tabelas externas.

---

# 13. DECISÃO 012 — JSON SERÁ UTILIZADO NA COMUNICAÇÃO ENTRE MÓDULOS QUANDO APROPRIADO

**Status:** DEFINIDA

Resultados estruturados deverão ser preferencialmente transmitidos entre módulos utilizando estruturas formais.

Exemplos:

* objetos;
* dataclasses;
* modelos;
* dicionários;
* JSON.

O `print()` não deverá ser utilizado como mecanismo principal de comunicação entre módulos.

---

# 14. DECISÃO 013 — DIAGNÓSTICOS DEVEM SER ESTRUTURADOS

**Status:** DEFINIDA

O sistema poderá gerar arquivos TXT para inspeção humana, porém os dados de diagnóstico deverão possuir representação estruturada.

O JSON será utilizado quando apropriado.

Exemplo:

```text
diagnostico/
├── _I1044988.txt
└── _I1044988_geometria_dimensional.json
```

Isso permitirá que outros motores consumam os resultados sem precisar interpretar texto humano.

---

# 15. DECISÃO 014 — PDF É UMA FONTE TÉCNICA, NÃO APENAS UM DOCUMENTO

**Status:** DEFINIDA

Desenhos técnicos em PDF deverão ser tratados como fontes de dados de engenharia.

O AIZI poderá analisar:

* texto;
* vetores;
* linhas;
* contornos;
* dimensões;
* coordenadas;
* geometria;
* informações técnicas.

O objetivo não é apenas extrair texto do PDF.

---

# 16. DECISÃO 015 — EXTRAÇÃO E INTERPRETAÇÃO SERÃO SEPARADAS

**Status:** DEFINIDA

O extrator deverá identificar os elementos existentes.

O interpretador/diagnóstico deverá determinar o significado desses elementos.

Exemplo:

```text
EXTRAÇÃO
"90"
"R10"
linha
linha
linha

        ↓

INTERPRETAÇÃO

Dobra:
90°
Raio:
10 mm
```

Essa separação será fundamental para evolução do sistema.

---

# 17. DECISÃO 016 — GEOMETRIA SERÁ TRATADA COMO DADO ESTRUTURADO

**Status:** DEFINIDA

A geometria de uma peça não deverá existir apenas como informação textual.

Quando possível deverá ser representada por:

* segmentos;
* vértices;
* arcos;
* contornos;
* coordenadas;
* áreas;
* perímetros;
* relações geométricas.

Isso permitirá reutilização por diferentes motores.

---

# 18. DECISÃO 017 — RANKING DE CANDIDATOS SERÁ UTILIZADO

**Status:** DEFINIDA

Quando um desenho possuir múltiplos elementos candidatos à identificação da peça, o sistema não deverá depender de uma única regra.

Será utilizado um sistema de ranking.

Critérios poderão incluir:

* dimensões;
* proporção;
* área;
* perímetro;
* segmentos;
* vértices;
* escala;
* correspondência com informações do desenho.

O resultado deverá apresentar o candidato e sua pontuação.

---

# 19. DECISÃO 018 — ESCALA DEVE SER CALCULADA E VALIDADA

**Status:** DEFINIDA

A escala geométrica não deverá ser assumida automaticamente a partir de uma única dimensão quando houver outras informações disponíveis.

Sempre que possível, o sistema deverá validar a escala usando múltiplas dimensões.

Exemplo:

```text
Dimensão detectada
        ↓
Dimensão conhecida
        ↓
Fator de escala
        ↓
Validação com outras dimensões
```

---

# 20. DECISÃO 019 — DESENVOLVIMENTO DE CHAPA SERÁ UM MOTOR PRÓPRIO

**Status:** DEFINIDA

O desenvolvimento de peças dobradas não ficará incorporado ao extrator de desenho.

O extrator identifica informações.

O motor de desenvolvimento executa os cálculos.

Fluxo:

```text
DESENHO
 ↓
GEOMETRIA
 ↓
DOBRAS
 ↓
PARÂMETROS
 ↓
MOTOR DE DESENVOLVIMENTO
 ↓
BLANK
```

---

# 21. DECISÃO 020 — CALCULADORA DE CORTE SERÁ INDEPENDENTE

**Status:** DEFINIDA

A calculadora de corte deverá funcionar independentemente do diagnóstico de desenho.

Ela poderá receber uma peça já dimensionada e calcular sua distribuição na chapa.

Isso permite reutilização em outros fluxos.

---

# 22. DECISÃO 021 — PARÂMETROS DE ENGENHARIA NÃO DEVEM FICAR ESPALHADOS NO CÓDIGO

**Status:** DEFINIDA

Parâmetros como:

* fator K;
* kerf;
* folga;
* tolerância;
* dimensões comerciais;
* parâmetros de material;
* parâmetros de dobra;

deverão ser centralizados e configuráveis quando apropriado.

Evitar valores mágicos espalhados pelo código.

---

# 23. DECISÃO 022 — O SISTEMA DEVE SER DETERMINÍSTICO QUANDO POSSÍVEL

**Status:** DEFINIDA

Para uma mesma entrada e os mesmos parâmetros, o resultado deverá ser reproduzível.

Isso é especialmente importante para:

* cálculos;
* dimensões;
* áreas;
* perímetros;
* desenvolvimento;
* corte;
* quantidades.

---

# 24. DECISÃO 023 — TESTES DEVEM ACOMPANHAR OS MOTORES

**Status:** DEFINIDA

Cada motor importante deverá possuir testes.

Os testes deverão incluir:

* casos normais;
* casos extremos;
* dados incompletos;
* dados inválidos;
* regressões;
* resultados conhecidos.

Uma correção em um motor não deverá quebrar silenciosamente funcionalidades existentes.

---

# 25. DECISÃO 024 — RESULTADOS DEVEM POSSUIR CONFIANÇA

**STATUS:** DEFINIDA

Quando um resultado envolver interpretação, deverá existir uma indicação de confiança.

Exemplo:

```text
ALTA
MÉDIA
BAIXA
```

Quando necessário, o resultado deverá incluir a justificativa.

Exemplo:

```text
CONFIANÇA: MÉDIA

Motivo:
duas geometrias apresentam proporções semelhantes.
```

---

# 26. DECISÃO 025 — O SISTEMA DEVE ACEITAR INTERVENÇÃO HUMANA

**STATUS:** DEFINIDA

O AIZI não deverá tentar automatizar absolutamente todas as decisões.

Quando uma interpretação for ambígua, o sistema deverá permitir que o usuário valide ou corrija o resultado.

Fluxo:

```text
AIZI
 ↓
Análise
 ↓
Resultado
 ↓
Confiança baixa
 ↓
Validação humana
 ↓
Resultado confirmado
```

A validação humana deverá poder se tornar dado útil para futuras melhorias do sistema.

---

# 27. DECISÃO 026 — O PROJETO SERÁ EVOLUTIVO

**STATUS:** DEFINIDA

Não será necessário construir toda a plataforma antes de obter resultados.

O desenvolvimento seguirá uma evolução incremental:

```text
Fundação
 ↓
Motor
 ↓
Teste
 ↓
Validação
 ↓
Integração
 ↓
Novo motor
```

Cada etapa deverá gerar uma base funcional para a próxima.

---

# 28. DECISÃO 027 — DOCUMENTAÇÃO É PARTE DA ARQUITETURA

**STATUS:** DEFINIDA

Os documentos técnicos do projeto não serão considerados acessórios.

A estrutura documental deverá preservar o conhecimento do projeto.

Documentos principais:

```text
_CONTEXT.md
ARQUITETURA.md
DECISOES.md
ROADMAP.md
_COMPLETO.md
```

O `_COMPLETO.md` será uma consolidação automática desses documentos quando o mecanismo de contexto for executado.

---

# 29. DECISÃO 028 — `_COMPLETO.md` NÃO SERÁ EDITADO MANUALMENTE

**STATUS:** DEFINIDA

O arquivo `_COMPLETO.md` será considerado um arquivo gerado.

O arquivo deverá ser recriado automaticamente pelo:

```text
aizi_context.py
```

As informações oficiais deverão ser mantidas nos documentos de origem.

Não será necessário editar manualmente `_COMPLETO.md`.

---

# 30. DECISÃO 029 — `ARQUITETURA.md` DEFINE A ESTRUTURA

**STATUS:** DEFINIDA

O documento `ARQUITETURA.md` será utilizado para registrar:

* camadas;
* módulos;
* responsabilidades;
* fluxos;
* entidades;
* integração;
* princípios técnicos.

Ele responde:

> **Como o AIZI é estruturado?**

---

# 31. DECISÃO 030 — `DECISOES.md` REGISTRA O PORQUÊ

**STATUS:** DEFINIDA

Este documento registra as decisões que explicam por que determinada arquitetura ou abordagem foi escolhida.

Ele responde:

> **Por que construímos dessa maneira?**

---

# 32. DECISÃO 031 — `ROADMAP.md` DEFINIRÁ A ORDEM DE CONSTRUÇÃO

**STATUS:** DEFINIDA

O roadmap não deverá substituir a arquitetura.

Ele deverá organizar a evolução do projeto em etapas.

Ele responde:

> **O que será construído primeiro, depois e posteriormente?**

---

# 33. DECISÃO 032 — O CONTEXTO DO PROJETO DEVE SER RECONSTRUÍVEL

**STATUS:** DEFINIDA

O projeto deverá possuir mecanismo para reconstruir o contexto central a partir dos documentos oficiais.

O arquivo:

```text
aizi_context.py
```

será responsável por consolidar as informações.

Isso reduz o risco de perda de contexto durante a evolução do projeto.

---

# 34. DECISÃO 033 — PRIMEIRO CONSOLIDAR, DEPOIS REESTRUTURAR

**STATUS:** DEFINIDA

Antes de grandes refatorações, o sistema deverá consolidar:

* arquitetura;
* decisões;
* roadmap;
* contexto;
* estado atual dos módulos.

Isso evita modificar o código sem uma visão clara da arquitetura desejada.

---

# 35. DECISÃO 034 — CÓDIGO EXISTENTE NÃO SERÁ DESCARTADO SEM ANÁLISE

**STATUS:** DEFINIDA

Os módulos já desenvolvidos representam conhecimento e trabalho acumulado.

Antes de substituir um módulo, deverá ser avaliado:

* o que já funciona;
* quais regras foram implementadas;
* quais testes existem;
* quais problemas foram encontrados;
* o que pode ser reutilizado.

A evolução deverá ocorrer preferencialmente por refatoração e consolidação.

---

# 36. DECISÃO 035 — CORREÇÕES DEVEM PRESERVAR O QUE JÁ FUNCIONA

**STATUS:** DEFINIDA

Ao corrigir um problema, o objetivo não será apenas eliminar o erro atual.

A correção deverá preservar as funcionalidades válidas existentes.

Sempre que possível:

```text
Erro identificado
 ↓
Teste reproduz o erro
 ↓
Correção
 ↓
Teste anterior continua passando
 ↓
Novo teste confirma correção
```

---

# 37. DECISÃO 036 — O AIZI DEVE SER INDEPENDENTE DA INTERFACE

**STATUS:** DEFINIDA

Os motores deverão poder ser executados sem uma interface gráfica.

Isso permite:

* testes;
* automações;
* scripts;
* processamento em lote;
* integração futura;
* API.

A interface não será requisito para funcionamento do núcleo.

---

# 38. DECISÃO 037 — PROCESSAMENTO EM LOTE DEVE SER POSSÍVEL

**STATUS:** DEFINIDA

A arquitetura deverá permitir processar múltiplas peças ou desenhos sem intervenção manual em cada etapa.

Exemplo:

```text
Pasta de desenhos
 ↓
Identificação
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

Essa capacidade será importante para aplicações industriais.

---

# 39. DECISÃO 038 — RESULTADO TÉCNICO DEVE SER REUTILIZÁVEL

**STATUS:** DEFINIDA

Um resultado produzido pelo AIZI deverá poder ser consumido por outros módulos.

Exemplo:

```text
Geometria
 ↓
Desenvolvimento
 ↓
Corte
 ↓
Custo
 ↓
Planejamento
```

O sistema não deve recalcular informações que já estejam disponíveis e válidas.

---

# 40. DECISÃO 039 — O AIZI DEVE PRIORIZAR CONFIABILIDADE SOBRE AUTOMAÇÃO

**STATUS:** DEFINIDA

Uma automação parcial e confiável é preferível a uma automação completa e incorreta.

O sistema deverá priorizar:

```text
CONFIABILIDADE
>
RASTREABILIDADE
>
VALIDAÇÃO
>
AUTOMAÇÃO
```

A automação deverá crescer conforme a confiança nos motores aumentar.

---

# 41. DECISÃO 040 — PRINCÍPIO CENTRAL DO PROJETO

**STATUS:** DEFINIDA

O princípio central do AIZI Engineering AI será:

> **Transformar dados industriais em conhecimento técnico estruturado e, posteriormente, em decisões de engenharia.**

Fluxo:

```text
DADOS
 ↓
INFORMAÇÃO
 ↓
ENGENHARIA
 ↓
CONHECIMENTO
 ↓
DECISÃO
```

A inteligência artificial será utilizada para ampliar essa capacidade.

---

# 42. RESUMO DAS DECISÕES

As decisões fundamentais do AIZI podem ser resumidas em:

```text
01. AIZI é uma plataforma, não um chatbot.
02. Engenharia é o núcleo.
03. IA complementa cálculos determinísticos.
04. Dados técnicos não devem ser inventados.
05. Resultados devem ser rastreáveis.
06. Dados extraídos e interpretados devem ser separados.
07. Motores devem ser modulares.
08. Interface não contém lógica de engenharia.
09. Banco é separado dos motores.
10. TOTVS é fonte externa.
11. Modelo interno representa o domínio.
12. Comunicação entre módulos deve ser estruturada.
13. Diagnósticos devem possuir estrutura formal.
14. PDF é fonte de dados técnicos.
15. Extração é diferente de interpretação.
16. Geometria é dado estruturado.
17. Candidatos podem ser classificados por ranking.
18. Escala deve ser validada.
19. Desenvolvimento é motor independente.
20. Corte é motor independente.
21. Parâmetros devem ser configuráveis.
22. Resultados devem ser determinísticos quando possível.
23. Motores devem possuir testes.
24. Resultados interpretados devem possuir confiança.
25. Usuário pode validar resultados.
26. Projeto será incremental.
27. Documentação faz parte do sistema.
28. `_COMPLETO.md` é gerado automaticamente.
29. ARQUITETURA.md define como.
30. DECISOES.md define por quê.
31. ROADMAP.md define quando.
32. Contexto deve ser reconstruível.
33. Primeiro consolidar, depois reestruturar.
34. Código existente deve ser analisado antes de substituir.
35. Correções devem preservar funcionalidades.
36. Núcleo deve ser independente da interface.
37. Processamento em lote deve ser possível.
38. Resultados devem ser reutilizáveis.
39. Confiabilidade vem antes da automação.
40. Dados → Informação → Engenharia → Conhecimento → Decisão.
```

---

# 43. REGRA DE ALTERAÇÃO DAS DECISÕES

Uma decisão registrada poderá ser alterada futuramente.

Porém, a alteração deverá:

1. identificar a decisão original;
2. explicar o motivo da mudança;
3. registrar a nova decisão;
4. preservar o histórico;
5. avaliar impactos na arquitetura;
6. avaliar impactos no código.

Não apagar silenciosamente uma decisão antiga.

---

# 44. ESTADO DO DOCUMENTO

Este documento representa as decisões fundamentais conhecidas até o momento.

Novas decisões deverão ser adicionadas conforme o projeto evoluir.

As decisões futuras devem manter a mesma lógica:

```text
DECISÃO
STATUS
MOTIVO
IMPACTO
```

O objetivo não é burocratizar o desenvolvimento.

O objetivo é evitar perda de conhecimento arquitetural.

---

# 45. PRINCÍPIO FINAL

O AIZI Engineering AI deverá evoluir sem perder sua identidade arquitetural.

A plataforma deve permanecer:

**modular, rastreável, determinística quando possível, orientada à engenharia, integrada aos dados industriais e ampliada por inteligência artificial.**


================================================================================
# ROADMAP.md
================================================================================

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
