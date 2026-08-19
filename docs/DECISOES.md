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