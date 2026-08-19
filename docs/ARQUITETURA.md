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