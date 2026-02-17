# 🏪 Guia: Problema de Disponibilidade Operacional

**Data:** 2026-02-08  
**Cenário:** Produtos com estoque mas não vendendo (problema operacional)

---

## 🎯 O Problema

### Situação Real:
1. ✅ Produto foi **comprado** do fornecedor
2. ✅ Pedido foi **recebido** (status: RECEIVED)
3. ✅ Produto **tem estoque** no sistema
4. ❌ Produto **NÃO está vendendo** (ou vendendo muito pouco)
5. ❌ Vendas **incompatíveis** com histórico

### Causa Provável:
- 🏢 Produto está **preso no depósito**
- 📦 Produto **não foi reposto** na prateleira
- 🌐 Produto **não está disponível** online
- 🎨 Problema de **exposição/merchandising**
- 📋 Erro no **sistema de disponibilidade**

---

## 📊 Diferença das Outras Tools

| Tool | O que detecta | Quando usar |
|------|---------------|-------------|
| `detect_stock_rupture` | Estoque = 0, JÁ zerou | Produtos sem estoque |
| `detect_imminent_stockout_risk` | Vai zerar em breve | Prevenção de ruptura |
| `detect_availability_issues` | Histórico de stockouts | Problemas crônicos |
| **`detect_operational_availability_issues`** 🆕 | **TEM estoque mas NÃO vende** | **Problema operacional** |

---

## 🔍 Como Funciona a Nova Tool

### Timeline Visual:

```
PROBLEMA DE DISPONIBILIDADE OPERACIONAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

60 dias atrás ━━━━━━━━━━━━━━━━━ 14 dias atrás ━━━━━━━━━━━━━━━ Hoje
    ▲                                 ▲                          ▲
    │                                 │                          │
    │                             Recebeu PO                     │
    │                             (150 un)                       │
    │                                 │                          │
    │◄──── Historical Period ────────►│◄─── Recent Period ──────►│
    │      (60 dias)                  │      (14 dias)           │
    │                                 │                          │

VENDAS HISTÓRICAS (60 dias atrás até 14 dias atrás):
┌─────────────────────────────────────────────────────────────────────┐
│ Semana 1 │ Semana 2 │ Semana 3 │ Semana 4 │ Semana 5 │ Semana 6    │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤
│  35 un   │  42 un   │  38 un   │  40 un   │  37 un   │  41 un      │
│  ✅      │  ✅      │  ✅      │  ✅      │  ✅      │  ✅         │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘
📊 Total: 233 unidades em 60 dias
📊 Média: 3.9 unidades/dia (BOM HISTÓRICO!)

PEDIDO RECEBIDO:
┌─────────────────────────────────────────────────────────────────────┐
│ 14 dias atrás:                                                      │
│ • Pedido PO-2024-089 RECEBIDO                                      │
│ • 150 unidades adicionadas ao estoque                              │
│ • Status: RECEIVED ✅                                               │
│ • Estoque após recebimento: 150 unidades                           │
└─────────────────────────────────────────────────────────────────────┘

VENDAS RECENTES (últimos 14 dias - APÓS RECEBIMENTO):
┌─────────────────────────────────────────────────────────────────────┐
│ Dia 1-7  │ Dia 8-14                                                 │
├──────────┼──────────────────────────────────────────────────────────┤
│  2 un    │  1 un                                                    │
│  ❌      │  ❌                                                      │
└──────────┴──────────────────────────────────────────────────────────┘
📊 Total: 3 unidades em 14 dias
📊 Média: 0.2 unidades/dia (QUEDA DE 95%!)

ANÁLISE:
┌─────────────────────────────────────────────────────────────────────┐
│ Esperado (últimos 14 dias): 3.9 × 14 = 55 unidades                │
│ Real (últimos 14 dias):     3 unidades                             │
│ PERDA:                      52 unidades                             │
│ Queda:                      95% ⚠️ CRÍTICO                          │
│                                                                     │
│ Estoque atual:              147 unidades (tem estoque!)            │
│ Receita perdida:            R$ 26.000 (52 × R$ 500)               │
│                                                                     │
│ 💡 DIAGNÓSTICO: Produto TEM estoque mas NÃO está disponível!       │
│                 Provável causa: preso no depósito                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🆕 Nova Tool Criada

### `detect_operational_availability_issues()`

**Localização:** `tools/operational_availability.py`

**Parâmetros:**
```python
detect_operational_availability_issues(
    recent_period_days=14,          # Período recente para comparar
    historical_period_days=60,      # Período histórico de referência
    drop_threshold_percentage=70.0  # % mínimo de queda para alertar
)
```

**Retorna:**
```python
{
    'product_id': 123,
    'name': 'Notebook Dell XPS',
    'current_stock': 147.0,
    'historical_daily_sales': 3.9,     # Média histórica
    'recent_daily_sales': 0.2,         # Média recente
    'sales_drop_percentage': 95.0,     # % de queda
    'expected_sales_recent': 55.0,     # Deveria vender
    'actual_sales_recent': 3.0,        # Vendeu de fato
    'lost_sales': 52.0,                # Diferença
    'last_received_date': '2026-01-17',
    'days_since_received': 14,
    'potential_lost_revenue': 26000.0,
    'issue_severity': 'CRITICAL',
    'recommendation': 'URGENT: Check if product is available on shelves/online...'
}
```

---

## 📦 Cenário Adicionado no Banco de Dados

### Scenario 5: Operational Availability Issues

**Arquivo:** `database/seed_data.py`

**O que cria:**
- **5 produtos** com problema operacional
- **Cada produto tem:**
  1. ✅ Histórico de vendas **BOM** (60 dias, 4-8 un/dia)
  2. ✅ Pedido recebido **14 dias atrás** (status: RECEIVED)
  3. ✅ Estoque **abundante** (100-150 unidades)
  4. ❌ Vendas **muito baixas** últimos 12 dias (1-2 vendas)
  5. ❌ Queda de **80-95%** nas vendas

**Dados gerados:**
```
Produto A:
  • Histórico: 5 un/dia × 45 dias = 225 vendas
  • Recebeu: 150 unidades (PO-RECEIVED-001)
  • Estoque atual: 145 unidades
  • Vendas recentes: 2 em 12 dias (esperava 60!)
  • Perda: 58 vendas = R$ 29.000
```

---

## 🧪 Como Testar

### Passo 1: Regenerar Banco de Dados

```bash
python reseed_with_risk_scenarios.py
```

### Passo 2: Testar a Tool Diretamente

```python
from tools.operational_availability import detect_operational_availability_issues

# Detectar problemas operacionais
issues = detect_operational_availability_issues()

print(f"Produtos com problema: {len(issues)}")

for issue in issues:
    print(f"\n🏪 {issue['name']}")
    print(f"   Queda nas vendas: {issue['sales_drop_percentage']:.0f}%")
    print(f"   Vendas perdidas: {issue['lost_sales']:.0f} unidades")
    print(f"   Receita perdida: R$ {issue['potential_lost_revenue']:,.2f}")
    print(f"   Recomendação: {issue['recommendation']}")
```

### Passo 3: Testar com o Agente

```bash
streamlit run app/streamlit_app.py
```

**Perguntas para testar:**
```
"Quais produtos têm estoque mas não estão vendendo?"
"Me mostre produtos com queda nas vendas apesar de ter estoque"
"Há produtos recebidos recentemente mas não vendendo?"
"Produtos presos no depósito ou não repostos?"
"Problemas operacionais de disponibilidade?"
```

---

## 🎯 Casos de Uso

### Pergunta 1: "Produtos com estoque mas sem vendas"
**Tool chamada:** `detect_operational_availability_issues`

**Resultado esperado:**
```
Encontrei 5 produtos com problema operacional:

🔴 Notebook Dell XPS
   • Estoque: 147 unidades
   • Histórico: 3.9 un/dia
   • Vendas recentes: 0.2 un/dia (queda de 95%)
   • Perdeu 52 vendas (R$ 26.000)
   • Ação: Verificar se está disponível nas prateleiras
```

### Pergunta 2: "Produtos que pararam de vender"
**Tool chamada:** `detect_operational_availability_issues`

**Filtro:** Produtos com queda > 80%

### Pergunta 3: "Produtos recebidos mas não vendendo"
**Tool chamada:** `detect_operational_availability_issues`

**Verifica:** `days_since_received < 30` e `sales_drop > 70%`

---

## 🔧 Integração com Sistema

### No Agente (Tool #13):

```python
Tool(
    name="detect_operational_availability_issues",
    func=_detect_operational_availability_wrapper,
    description="""Detecta produtos com estoque mas que pararam de vender.
    Use quando o usuário perguntar sobre:
    - Produtos com estoque mas sem vendas
    - Produtos no depósito não repostos
    - Queda súbita nas vendas com estoque disponível
    """
)
```

### Palavras-chave para o LLM:
- "estoque mas não vende"
- "parou de vender"
- "depósito"
- "não reposto"
- "problema operacional"
- "queda nas vendas"
- "recebido mas não vendendo"

---

## 📊 Resumo dos Dados Fake

| Cenário | Qtd | Descrição |
|---------|-----|-----------|
| 4A | 6 | Sem pedido de compra (CRITICAL) |
| 4B | 4 | Pedido insuficiente (HIGH) |
| 4C | 3 | Pedido atrasado (HIGH) |
| 4D | 2 | Pedido suficiente (LOW) |
| **5 (NOVO)** | **5** | **Problema operacional (CRITICAL)** |
| **Total** | **20** | **cenários diversos** |

---

## ✅ Checklist

- [x] Tool criada (`operational_availability.py`)
- [x] Tool exportada (`tools/__init__.py`)
- [x] Tool registrada no agente (`stock_agent.py`)
- [x] Cenário adicionado no seed (`seed_data.py`)
- [x] Documentação criada (este arquivo)
- [ ] Testar com banco regenerado
- [ ] Validar com agente
- [ ] Adicionar diagrama visual no RFC

---

## 🎉 Resultado Final

**Agora o sistema detecta 3 tipos de problemas:**

1. 🔴 **Ruptura** (estoque = 0) → `detect_stock_rupture`
2. ⚠️ **Risco de ruptura** (vai zerar) → `detect_imminent_stockout_risk`
3. 🏪 **Problema operacional** (tem estoque mas não vende) → `detect_operational_availability_issues` 🆕

**Sistema completo e robusto! 📦✨**
