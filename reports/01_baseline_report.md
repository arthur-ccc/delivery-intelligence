# Relatório — Primeiro Modelo de Classificação

## 1. Objetivo

Desenvolver um primeiro modelo de Machine Learning para prever se um pedido será entregue com atraso, utilizando as features construídas nas etapas anteriores do projeto.

## 2. Implementação

Foi utilizada uma **Regressão Logística (Logistic Regression)** como modelo baseline, com 15 features e 96.470 pedidos divididos cronologicamente em treino (70%), validação (15%) e teste (15%).

O pré-processamento consistiu na imputação de valores ausentes pela mediana e na padronização das variáveis. O modelo foi treinado exclusivamente com os dados de treino.

O threshold de classificação foi ajustado na validação, buscando maximizar o F1-score, e posteriormente aplicado ao conjunto de teste.

## 3. Resultados

| Métrica | Validação | Teste |
|---|---:|---:|
| Average Precision | 0,0597 | 0,0409 |
| ROC-AUC | 0,6060 | 0,4620 |
| Precision | 7,98% | 3,17% |
| Recall | 22,44% | 34,68% |
| F1-score | 0,1177 | 0,0582 |

O modelo apresentou desempenho insatisfatório, principalmente no conjunto de teste.

Dos 620 pedidos atrasados, apenas 215 foram identificados corretamente. Além disso, foram gerados 6.559 falsos positivos, indicando uma baixa confiabilidade das previsões de atraso.

Outro ponto observado foi a influência das variáveis temporais (`purchase_year` e `purchase_month`), que apresentaram os maiores coeficientes positivos do modelo.

## 4. Achados e possíveis melhorias

A diferença de desempenho entre validação e teste indica uma dificuldade de generalização para períodos posteriores. Uma possível causa é a mudança na distribuição dos dados ao longo do tempo (*data drift*).

Para investigar e melhorar os resultados, podem ser realizados os seguintes experimentos:

- **Análise de drift:** verificar como as distribuições das features e dos atrasos mudaram entre os conjuntos.
- **Remoção de features temporais:** avaliar se o modelo está dependendo excessivamente do ano e do mês da compra.
- **Novos algoritmos:** experimentar Random Forest e Gradient Boosting, capazes de representar relações não lineares.
- **Tratamento do desbalanceamento:** comparar estratégias de ponderação das classes e avaliar diferentes thresholds.

## 5. Conclusão

O primeiro modelo permitiu estabelecer um pipeline completo de treinamento, avaliação e persistência dos resultados.

Apesar de funcionar corretamente do ponto de vista técnico, **a Regressão Logística não apresentou desempenho suficiente para prever atrasos de forma confiável**.

Os resultados sugerem que as features atuais e as mudanças temporais dos dados precisam ser investigadas antes de avançar para modelos mais complexos.

O próximo passo será analisar o drift e realizar experimentos controlados para identificar os fatores que estão limitando o desempenho do modelo.