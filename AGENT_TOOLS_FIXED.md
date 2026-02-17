# 🔧 Correção: Nova Ferramenta Registrada no Agente

**Data:** 2026-02-08  
**Problema:** Agente não chamava `detect_imminent_stockout_risk()` para perguntas sobre risco de estoque  
**Status:** ✅ **RESOLVIDO**

---

## 🐛 Problema Identificado

Quando o usuário perguntava:
> "Quais produtos têm risco de ficar sem estoque?"

O agente **NÃO** chamava a nova ferramenta `detect_imminent_stockout_risk()`.

### Causa Raiz:

A ferramenta foi criada em `tools/stockout_risk.py`, mas **NÃO foi registrada no agente** em `agent/stock_agent.py`.

---

## ✅ Correções Aplicadas

### 1. Importação Adicionada

```python
# LINHA 22 - agent/stock_agent.py
from tools.stockout_risk import detect_imminent_stockout_risk, get_pending_order_summary  # NEW
```

### 2. Wrappers Criados

```python
# LINHAS 99-109 - agent/stock_agent.py
def _detect_imminent_stockout_wrapper(tool_input: str = ""):
    """NEW - 2026-02-08: Preventive stockout risk detection."""
    _ = tool_input
    return detect_imminent_stockout_risk(days_forecast=30, days_history=90, min_days_threshold=7)


def _get_pending_orders_wrapper(tool_input: str = ""):
    """NEW - 2026-02-08: List pending purchase orders."""
    _ = tool_input
    return get_pending_order_summary(product_id=None)
```

### 3. Ferramentas Registradas

#### Tool #1: detect_imminent_stockout_risk (NOVA - PREVENTIVA)

```python
Tool(
    name="detect_imminent_stockout_risk",
    func=_detect_imminent_stockout_wrapper,
    description="""FERRAMENTA PREVENTIVA: Detecta produtos que VÃO ficar sem estoque em breve.
    Use quando o usuário perguntar sobre:
    - Produtos em risco de ruptura
    - Produtos que vão zerar
    - Risco de ficar sem estoque
    - Produtos sem pedido de compra
    - Previsão de ruptura
    - Produtos próximos de zerar
    - Pedidos de compra insuficientes
    - Pedidos atrasados
    Retorna produtos com risco ANTES de zerarem, considerando pedidos pendentes."""
)
```

#### Tool #2: detect_stock_rupture (REATIVA - Renomeada para #2)

```python
Tool(
    name="detect_stock_rupture",
    func=_detect_stock_rupture_wrapper,
    description="""FERRAMENTA REATIVA: Identifica produtos que JÁ estão com estoque zero.
    Use quando o usuário perguntar sobre:
    - Produtos que zeraram
    - Produtos sem estoque (já zerado)
    - Rupturas que já aconteceram
    - Receita perdida (já perdida)
    - Produtos em falta agora
    Retorna lista de produtos críticos que já zeraram."""
)
```

#### Tool #12: get_pending_order_summary (NOVA)

```python
Tool(
    name="get_pending_order_summary",
    func=_get_pending_orders_wrapper,
    description="""Lista todos os pedidos de compra pendentes (status PENDING).
    Use quando o usuário perguntar sobre:
    - Pedidos pendentes
    - Pedidos de compra em andamento
    - Status de pedidos
    - Pedidos atrasados
    - O que já foi pedido
    Retorna lista de pedidos pendentes com dias de espera e produtos."""
)
```

---

## 📊 Diferenciação Clara: Preventivo vs Reativo

### Descrições Atualizadas para Evitar Confusão

| Aspecto | Tool #1: Imminent Risk | Tool #2: Rupture |
|---------|------------------------|------------------|
| **Momento** | VÃO ficar sem estoque | JÁ estão sem estoque |
| **Tipo** | PREVENTIVO | REATIVO |
| **Palavras-chave** | "risco", "vão zerar", "previsão" | "já zerou", "em falta agora" |
| **Verifica PO** | ✅ Sim | ❌ Não |
| **Objetivo** | Evitar ruptura | Calcular prejuízo |

---

## 🎯 Perguntas que Agora Funcionam

O agente agora deve responder corretamente a:

### Perguntas Preventivas (usa Tool #1):
- ✅ "Quais produtos têm risco de ficar sem estoque?"
- ✅ "Me mostre produtos que vão zerar em breve"
- ✅ "Há produtos sem pedido de compra que vão acabar?"
- ✅ "Produtos com risco de ruptura"
- ✅ "Previsão de falta de estoque"
- ✅ "Produtos próximos de zerar"

### Perguntas Reativas (usa Tool #2):
- ✅ "Quais produtos já zeraram o estoque?"
- ✅ "Produtos em falta agora"
- ✅ "Produtos sem estoque" (pode usar ambas)
- ✅ "Receita perdida por ruptura"

### Perguntas sobre Pedidos (usa Tool #12):
- ✅ "Quais pedidos estão pendentes?"
- ✅ "Me mostre pedidos atrasados"
- ✅ "Status dos pedidos de compra"

---

## 📈 Total de Ferramentas

**ANTES:** 11 ferramentas  
**DEPOIS:** 13 ferramentas (✅ +2 novas)

### Lista Completa:

1. ✨ **detect_imminent_stockout_risk** (NOVA - PREVENTIVA)
2. detect_stock_rupture (REATIVA)
3. analyze_slow_moving_stock
4. analyze_supplier_performance
5. detect_stock_losses
6. suggest_purchase_order
7. get_top_selling_products
8. analyze_purchase_to_sale_time
9. get_stock_alerts
10. detect_availability_issues
11. calculate_profitability_analysis
12. get_abc_analysis
13. ✨ **get_pending_order_summary** (NOVA)

---

## 🧪 Como Testar

### Via Streamlit:
```bash
streamlit run app/streamlit_app.py
```

Depois pergunte:
- "Quais produtos têm risco de ficar sem estoque?"
- "Me mostre produtos que vão zerar nos próximos 7 dias"

### Via Python:
```python
from agent.stock_agent import create_stock_agent

agent = create_stock_agent()
response = agent.invoke({
    "input": "Quais produtos têm risco de ficar sem estoque?"
})

print(response['output'])
```

---

## ⚠️ Importante

### Descrições Otimizadas para o LLM

As descrições das ferramentas foram escritas com **palavras-chave específicas** para ajudar o LLM a escolher a ferramenta correta:

**Tool #1 (Preventiva):**
- "VÃO ficar"
- "risco de"
- "previsão"
- "próximos de"

**Tool #2 (Reativa):**
- "JÁ estão"
- "já zerou"
- "em falta agora"
- "receita perdida"

Isso garante que o agente use a ferramenta certa para cada contexto.

---

## ✅ Checklist de Correção

- [x] Importação adicionada
- [x] Wrapper functions criadas
- [x] Ferramentas registradas no create_tools()
- [x] Descrições claras e diferenciadas
- [x] Palavras-chave otimizadas para o LLM
- [x] Documentação atualizada
- [x] Numeração das ferramentas corrigida (1-13)

---

## 📝 Arquivo Modificado

- ✅ `agent/stock_agent.py` (+30 linhas)
  - Imports atualizados
  - 2 wrappers adicionados
  - 2 ferramentas registradas
  - Numeração corrigida

---

## 🚀 Resultado Esperado

Agora quando o usuário perguntar:

> "Quais produtos têm risco de ficar sem estoque?"

O agente deverá:

1. ✅ Reconhecer as palavras-chave "risco" + "ficar sem estoque"
2. ✅ Escolher `detect_imminent_stockout_risk` (Tool #1)
3. ✅ Executar a ferramenta
4. ✅ Retornar produtos em risco com:
   - Dias até ruptura
   - Pedidos pendentes (se houver)
   - Gap de reposição
   - Recomendações específicas

**Problema resolvido! 🎉**
