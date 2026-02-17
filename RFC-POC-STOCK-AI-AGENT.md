# RFC: POC - AI Agent for Stock Management System

**Status:** Draft  
**Author:** Development Team  
**Created:** 2026-01-26  
**Last Updated:** 2026-01-26  

---

## 1. Executive Summary

Esta RFC define a implementação de uma Prova de Conceito (POC) de um sistema de gestão de estoque com agente de IA para análise inteligente e suporte à decisão operacional. O objetivo é demonstrar como IA pode auxiliar gestores na identificação de problemas, otimização de compras e redução de perdas.

## 2. Problem Statement

Sistemas de gestão tradicionais requerem que o usuário saiba exatamente qual relatório gerar ou query executar. Problemas comuns incluem:

- **Ruptura de estoque**: Produtos sem estoque por falta de reposição oportuna
- **Estoque parado**: Produtos comprados que não vendem há muito tempo (capital parado)
- **Fornecedores problemáticos**: Identificar fornecedores com produtos de baixo giro
- **Oportunidades perdidas**: Produtos com alto giro mas estoque insuficiente
- **Perdas não identificadas**: Divergências entre compra e venda não detectadas

A IA pode analisar esses padrões conversacionalmente e proativamente.

## 3. Goals & Non-Goals

### Goals
- ✅ Implementar agente de IA conversacional para análise de estoque
- ✅ Criar base de dados realista com histórico simulado
- ✅ Demonstrar casos de uso práticos de análise inteligente
- ✅ Interface simples e funcional para interação
- ✅ Arquitetura extensível para adicionar novos casos de uso

### Non-Goals
- ❌ Sistema pronto para produção (é uma POC)
- ❌ Integração com sistemas ERP reais
- ❌ Autenticação/autorização robusta
- ❌ Performance otimizada para milhões de registros
- ❌ Multi-tenancy

## 4. Solution Overview

### 4.1 Architecture Stack

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND                          │
│              Streamlit Web UI                       │
└─────────────────┬───────────────────────────────────┘
                  │ Direct Function Calls
┌─────────────────▼───────────────────────────────────┐
│                  AI AGENT LAYER                     │
│         LangChain + OpenAI GPT-4o-mini              │
│         (Agent Executor + Tools)                    │
└─────────────────┬───────────────────────────────────┘
                  │ Function Calls
┌─────────────────▼───────────────────────────────────┐
│              BUSINESS LOGIC LAYER                   │
│        Python Tools/Functions                       │
│        (Database Queries + Analytics)               │
└─────────────────┬───────────────────────────────────┘
                  │ SQL Queries (SQLAlchemy)
┌─────────────────▼───────────────────────────────────┐
│               DATABASE LAYER                        │
│         SQLite (stock.db file)                      │
│         (Schema + Fake Data Generator)              │
└─────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack Validation

| Component | Proposta Original | Validação | Recomendação Final |
|-----------|------------------|-----------|-------------------|
| **Database** | PostgreSQL + Docker | ✅ **BOM** - Robusto mas overhead para POC | ✅ **SQLite** (arquivo) - Zero setup, portátil |
| **Backend Language** | Python | ✅ **IDEAL** - Ecossistema IA maduro | ✅ **Python** |
| **API Framework** | FastAPI | ⚠️ **DESNECESSÁRIO** para POC | ❌ **REMOVER** - Integração direta |
| **AI Framework** | LangChain | ✅ **PERFEITO** - Padrão para agents | ✅ **LangChain** |
| **LLM** | OpenAI GPT-4 | ✅ **BOM** - Caro para POC | ✅ **GPT-4o-mini** (60% mais barato) |
| **Frontend** | Streamlit | ✅ **IDEAL PARA POC** - Rápido, simples | ✅ **Streamlit** |

**Stack Final Recomendada:** 
- ✅ **SQLite (arquivo)** - Built-in Python, zero configuração, arquivo único portátil
- ✅ **Python** - Linguagem base
- ✅ **LangChain** - Framework de agentes
- ✅ **GPT-4o-mini** - Custo-benefício ideal para POC
- ✅ **Streamlit** - UI rápida e funcional
- ❌ **Sem Docker** - Desnecessário com SQLite
- ❌ **Sem FastAPI** - Streamlit chama agente diretamente

**Nota sobre Migração Futura:**
- O código usa SQLAlchemy (ORM agnóstico)
- Migração para PostgreSQL = trocar 1 linha de conexão
- Recomendado PostgreSQL apenas se for para produção ou demo "enterprise"

### 4.3 Simplified Architecture (Recommended)

```python
# Streamlit App
streamlit_app.py
    ↓
# AI Agent (LangChain)
agent.py (create_agent, run_query)
    ↓
# Tools
tools/
    - stock_analysis.py
    - sales_analysis.py
    - purchase_analysis.py
    - inventory_alerts.py
    ↓
# Database
database/
    - connection.py
    - models.py
```

## 5. AI Agent Capabilities

### 5.1 Core Use Cases

#### UC1: Stock Rupture Detection (REACTIVE)
**Descrição:** Identificar produtos sem estoque que tiveram vendas recentes (detecta ruptura JÁ acontecida)

**Exemplo de pergunta:**
- "Quais produtos estão sem estoque mas venderam nas últimas 2 semanas?"
- "Me mostre produtos em ruptura de estoque"
- "Calcule a receita perdida por produtos que zeraram"

**Tool:** `detect_stock_rupture(days_lookback=14)`

**Como funciona - Timeline Visual:**

```
Dia 15/01 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Dia 29/01 (hoje)
         ▲                                            ▲
     cutoff_date                                   datetime.now()
     (lookback=14)
     
┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ Dia 15  │ Dia 18  │ Dia 21  │ Dia 24  │ Dia 26  │ Dia 29  │
│         │         │         │         │         │ (HOJE)  │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │
│ = 50    │ = 35    │ = 20    │ = 8     │ = 0     │ = 0     │
│         │         │         │         │         │         │
│ Vendeu  │ Vendeu  │ Vendeu  │ Vendeu  │ SEM     │ SEM     │
│ 15 unid │ 15 unid │ 12 unid │ 8 unid  │ ESTOQUE │ ESTOQUE │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
           ▲         ▲         ▲         ▲         
           │         │         │         │
        Vendas ACONTECERAM quando TINHA estoque
                                         │
                                    Zerou aqui!
                                    (26/01)

📊 Resultado da análise:
   • Estoque ATUAL: 0 (sem estoque AGORA)
   • Vendas nos últimos 14 dias: 50 unidades (prova de demanda)
   • Demanda diária média: 50 ÷ 14 = 3.57 unid/dia
   • Dias sem estoque: 3 dias (desde 26/01)
   • Receita perdida estimada: 3 dias × 3.57 un/dia × R$ preço

💡 Insight: Produto com alta demanda em RUPTURA = Oportunidade de venda perdida!
```

**Lógica:**
1. Produtos com `current_stock <= 0` (sem estoque AGORA)
2. Que tiveram vendas entre `cutoff_date` e hoje (quando TINHA estoque)
3. Calcula demanda média diária baseada nas vendas recentes
4. Estima receita perdida desde que o estoque zerou

**Query SQL:**
```sql
SELECT p.name, p.current_stock, 
       COUNT(DISTINCT so.id) as recent_sales,
       MAX(so.sale_date) as last_sale_date,
       SUM(soi.quantity) as total_quantity_sold
FROM product p
JOIN sale_order_item soi ON p.id = soi.product_id
JOIN sale_order so ON soi.sale_order_id = so.id
WHERE p.current_stock <= 0
  AND so.sale_date >= CURRENT_DATE - INTERVAL '14 days'
  AND so.status = 'PAID'
GROUP BY p.id, p.name, p.current_stock
ORDER BY total_quantity_sold DESC;
```

---

#### UC1.5: Imminent Stockout Risk Detection (PREVENTIVE) 🆕
**Descrição:** Identificar produtos que vão ficar sem estoque em breve e verificar se possuem pedidos de compra suficientes para reposição

**Exemplo de pergunta:**
- "Quais produtos vão ficar sem estoque e não têm pedido de compra?"
- "Me mostre produtos em risco de ruptura que precisam de reposição urgente"
- "Há produtos que vão zerar nos próximos 7 dias?"

**Tool:** `detect_imminent_stockout_risk(days_forecast=30, min_days_threshold=7)`

**Como funciona - Timeline Visual:**

```
CENÁRIO 1: SEM Pedido de Compra (CRÍTICO!) 🔴
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hoje (29/01) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ +30 dias (28/02)
    ▲                                                              ▲
    │                                                              │
    │                                                        Forecast period
    │
    │
┌───┴──────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ HOJE     │ +3 dias │ +6 dias │ +9 dias │ +12 dia │ +15 dia │ +18 dia │
│ 29/01    │ 01/02   │ 04/02   │ 07/02   │ 10/02   │ 13/02   │ 16/02   │
├──────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Estoque  │ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │
│ = 15 un  │ = 10 un │ = 5 un  │ = 0 un  │ = 0 un  │ = 0 un  │ = 0 un  │
│          │         │         │         │         │         │         │
│ Demanda  │ Demanda │ Demanda │ 💀 ZERA │ ❌ PERDA│ ❌ PERDA│ ❌ PERDA│
│ 5 un/dia │ 5 un/dia│ 5 un/dia│ ESTOQUE │ VENDA   │ VENDA   │ VENDA   │
│          │         │         │         │         │         │         │
│ PO? ❌   │ PO? ❌  │ PO? ❌  │ PO? ❌  │ PO? ❌  │ PO? ❌  │ PO? ❌  │
└──────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
                                    ▲
                                    │
                              🔴 CRÍTICO!
                            Vai zerar em 9 dias
                          SEM pedido de compra!

📊 Resultado da análise:
   • Estoque ATUAL: 15 unidades
   • Demanda diária média: 5 un/dia
   • Dias até ruptura: 3 dias (15 ÷ 5 = 3)
   • Pedidos pendentes: ❌ NENHUM
   • Demanda prevista (30 dias): 150 unidades
   • Gap de reposição: 135 unidades (150 - 15 atual)
   • Receita perdida potencial: R$ 675,00 (135 × R$ 5,00)
   • Risk Level: 🔴 CRITICAL

💡 Ação requerida: CRIAR PEDIDO DE COMPRA IMEDIATAMENTE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


CENÁRIO 2: COM Pedido Insuficiente (ALTO RISCO) 🟠
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hoje (29/01) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ +30 dias (28/02)
    ▲              ▲                                              ▲
    │              │                                              │
    │          Pedido de                                    Forecast period
    │          Compra                                       
    │          (50 un)
    │          
┌───┴──────┬───┴─────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ HOJE     │ +3 dias │ +6 dias │ +9 dias │ +12 dia │ +15 dia │ +18 dia │
│ 29/01    │ 01/02   │ 04/02   │ 07/02   │ 10/02   │ 13/02   │ 16/02   │
├──────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Estoque  │ 📦 CHEGA│ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │
│ = 15 un  │ 50 un   │ = 50 un │ = 35 un │ = 20 un │ = 5 un  │ = 0 un  │
│          │ PO-1234 │         │         │         │         │         │
│ Demanda  │ Demanda │ Demanda │ Demanda │ Demanda │ Demanda │ 💀 ZERA │
│ 5 un/dia │ 5 un/dia│ 5 un/dia│ 5 un/dia│ 5 un/dia│ 5 un/dia│ ESTOQUE │
│          │         │         │         │         │         │         │
│ PO       │ ✅ RECV │         │         │         │         │ PO? ❌  │
│ PENDING  │ 50 un   │         │         │         │         │         │
└──────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
              ▲                                                  ▲
              │                                                  │
         Pedido cobre                                      🟠 Vai zerar!
         apenas 13 dias                                  Precisa mais!
         (50 ÷ 5 = 10 dias)

📊 Resultado da análise:
   • Estoque ATUAL: 15 unidades
   • Demanda diária média: 5 un/dia
   • Dias até ruptura (sem PO): 3 dias
   • Pedidos pendentes: ✅ 1 pedido (50 unidades)
   • Estoque após PO: 65 unidades (15 atual + 50 PO)
   • Dias de cobertura com PO: 13 dias (65 ÷ 5)
   • Demanda prevista (30 dias): 150 unidades
   • Gap de reposição: 85 unidades (150 - 65 disponível)
   • Risk Level: 🟠 HIGH

💡 Ação requerida: PEDIDO INSUFICIENTE! Comprar mais 85 unidades.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


CENÁRIO 3: Pedido Atrasado (ALTO RISCO) ⏰
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

15/01 (Pedido feito) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 29/01 (Hoje, 14 dias)
    ▲                                                        ▲
    │                                                        │
    PO-5678                                            Ainda PENDING
    100 unidades                                       (Atrasado!)
    Status: PENDING
    
┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ Dia 15  │ Dia 18  │ Dia 21  │ Dia 24  │ Dia 26  │ Dia 29  │ +3 dias │
│ (pedido)│         │         │         │         │ (HOJE)  │         │
├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │
│ = 50 un │ = 35 un │ = 20 un │ = 10 un │ = 5 un  │ = 2 un  │ = 0 un  │
│         │         │         │         │         │         │         │
│ CRIOU PO│ Demanda │ Demanda │ Demanda │ Demanda │ Demanda │ 💀 ZERA │
│ 100 un  │ 5 un/dia│ 5 un/dia│ 5 un/dia│ 5 un/dia│ 5 un/dia│ ESTOQUE │
│         │         │         │         │         │         │         │
│ Espera  │ PO? ⏰  │ PO? ⏰  │ PO? ⏰  │ PO? ⏰  │ PO? ⏰  │ PO? ⏰  │
│ entrega │ ATRASO  │ ATRASO  │ ATRASO  │ ATRASO  │ ATRASO  │ ATRASO  │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
            ▲────────────────────────────────────────▲
            │              14 dias esperando!         │
            └─────────────────────────────────────────┘
                       ⏰ PEDIDO ATRASADO!

📊 Resultado da análise:
   • Estoque ATUAL: 2 unidades
   • Demanda diária média: 5 un/dia
   • Dias até ruptura: 0.4 dias (menos de 1 dia!)
   • Pedidos pendentes: ✅ 1 pedido (100 unidades)
   • Idade do pedido: 14 dias (threshold: 7 dias)
   • Status do pedido: ⏰ ATRASADO
   • Risk Level: 🔴 HIGH (atrasado + estoque crítico)

💡 Ação requerida: CONTATAR FORNECEDOR URGENTE! Pedido atrasado.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


CENÁRIO 4: Pedido Suficiente (BAIXO RISCO) ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hoje (29/01) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ +30 dias (28/02)
    ▲              ▲                                              ▲
    │              │                                              │
    │          Pedido de                                    Forecast period
    │          Compra                                       
    │          (150 un)
    │          
┌───┴──────┬───┴─────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ HOJE     │ +3 dias │ +6 dias │ +12 dia │ +18 dia │ +24 dia │ +30 dia │
│ 29/01    │ 01/02   │ 04/02   │ 10/02   │ 16/02   │ 22/02   │ 28/02   │
├──────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Estoque  │ 📦 CHEGA│ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │
│ = 15 un  │ 150 un  │ = 150 un│ = 120 un│ = 90 un │ = 60 un │ = 30 un │
│          │ PO-9999 │         │         │         │         │         │
│ Demanda  │ Demanda │ Demanda │ Demanda │ Demanda │ Demanda │ ✅ OK   │
│ 5 un/dia │ 5 un/dia│ 5 un/dia│ 5 un/dia│ 5 un/dia│ 5 un/dia│ Coberto │
│          │         │         │         │         │         │         │
│ PO       │ ✅ RECV │         │         │         │         │ ✅ SAFE │
│ PENDING  │ 150 un  │         │         │         │         │         │
└──────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
              ▲                                                  ▲
              │                                                  │
         Pedido cobre                                      ✅ Estoque OK!
         30 dias completos                                 (30 unidades)

📊 Resultado da análise:
   • Estoque ATUAL: 15 unidades
   • Demanda diária média: 5 un/dia
   • Pedidos pendentes: ✅ 1 pedido (150 unidades)
   • Estoque após PO: 165 unidades (15 + 150)
   • Dias de cobertura: 33 dias (165 ÷ 5)
   • Demanda prevista (30 dias): 150 unidades
   • Gap de reposição: 0 unidades ✅
   • Risk Level: 🟢 LOW

💡 Ação requerida: MONITORAR. Pedido pendente cobre demanda.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Diferenças entre UC1 (detect_stock_rupture) vs UC1.5 (detect_imminent_stockout_risk):**

| Aspecto | UC1: Stock Rupture | UC1.5: Imminent Stockout Risk |
|---------|-------------------|------------------------------|
| **Momento** | Já aconteceu (REATIVO) | Vai acontecer (PREVENTIVO) |
| **Estoque** | = 0 (zerado) | > 0 mas vai zerar em breve |
| **Objetivo** | Calcular prejuízo | Evitar prejuízo |
| **Pedidos** | Não verifica | ✅ Verifica se tem PO suficiente |
| **Ação** | Comprar URGENTE | Comprar ANTES de zerar |
| **Exemplo** | "Produto X zerou há 3 dias" | "Produto Y vai zerar em 5 dias" |

**Lógica da Ferramenta:**

```python
1. Produtos com estoque > 0 (ainda tem)
2. Calcular demanda diária (vendas / dias histórico)
3. Calcular dias_até_ruptura = estoque_atual / demanda_diária
4. Se dias_até_ruptura < threshold (ex: 7 dias) → RISCO!
5. Buscar pedidos PENDING para o produto
6. Calcular se pedidos cobrem demanda forecast
7. Calcular GAP = demanda_forecast - (estoque + pedidos_pending)
8. Classificar risco: CRITICAL / HIGH / MEDIUM / LOW
9. Gerar recomendação específica
```

**Query SQL (Simplificada):**

```sql
-- 1. Calcular demanda
WITH sales_velocity AS (
  SELECT 
    p.id,
    p.current_stock,
    AVG(daily_sales) as avg_daily_sales
  FROM product p
  JOIN sales_history sh ON p.id = sh.product_id
  WHERE sale_date >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY p.id
),

-- 2. Verificar pedidos pendentes
pending_orders AS (
  SELECT
    poi.product_id,
    SUM(poi.quantity) as pending_quantity,
    COUNT(*) as order_count
  FROM purchase_order_item poi
  JOIN purchase_order po ON poi.purchase_order_id = po.id
  WHERE po.status = 'PENDING'
  GROUP BY poi.product_id
)

-- 3. Identificar produtos em risco
SELECT 
  sv.*,
  po.pending_quantity,
  po.order_count,
  (sv.current_stock / sv.avg_daily_sales) as days_until_stockout,
  (sv.avg_daily_sales * 30) as forecasted_demand,
  CASE 
    WHEN (sv.current_stock / sv.avg_daily_sales) <= 3 
      AND COALESCE(po.pending_quantity, 0) < (sv.avg_daily_sales * 30)
      THEN 'CRITICAL'
    WHEN (sv.current_stock / sv.avg_daily_sales) <= 7 
      THEN 'HIGH'
    ELSE 'MEDIUM'
  END as risk_level
FROM sales_velocity sv
LEFT JOIN pending_orders po ON sv.id = po.product_id
WHERE (sv.current_stock / sv.avg_daily_sales) <= 7
ORDER BY risk_level, days_until_stockout;
```

---

#### UC2: Slow-Moving Stock Analysis
**Descrição:** Produtos parados em estoque há muito tempo (capital imobilizado)

**Exemplo de pergunta:**
- "Quais produtos não vendem há mais de 30 dias?"
- "Me mostre o capital parado em produtos sem giro"

**Tool:** `analyze_slow_moving_stock(days_threshold=30)`

**Como funciona - Timeline Visual:**

```
PRODUTO PARADO (Capital Imobilizado) 💰
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

90 dias atrás ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Hoje (29/01)
    ▲                                                              ▲
    │                                                              │
  Compra                                                   SEM VENDAS!
  200 un                                                   (90 dias)
  R$ 50/un
  = R$ 10.000
    
┌───┴──────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
│ 01/11/25 │ 15/11   │ 01/12   │ 15/12   │ 01/01   │ 15/01   │ 29/01   │
│ (COMPRA) │         │         │         │         │         │ (HOJE)  │
├──────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
│ Comprou  │         │         │         │         │         │         │
│ 200 un   │ Vendas? │ Vendas? │ Vendas? │ Vendas? │ Vendas? │ Vendas? │
│ R$ 10k   │ ❌ ZERO │ ❌ ZERO │ ❌ ZERO │ ❌ ZERO │ ❌ ZERO │ ❌ ZERO │
│          │         │         │         │         │         │         │
│ Estoque  │ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │ Estoque │
│ = 200 un │ = 200 un│ = 200 un│ = 200 un│ = 200 un│ = 200 un│ = 200 un│
└──────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
              ▲────────────────────────────────────────────────▲
              │         90 DIAS SEM VENDER!                    │
              └────────────────────────────────────────────────┘
                       💰 CAPITAL PARADO!

📊 Resultado da análise:
   • Estoque ATUAL: 200 unidades
   • Última venda: Nunca (ou há > 90 dias)
   • Dias sem venda: 90+ dias
   • Valor do estoque: R$ 10.000,00 (200 × R$ 50)
   • Capital imobilizado: R$ 10.000,00
   • Custo de oportunidade: Poderia investir em produtos A
   • Taxa de giro: 0% (produto MORTO)

💡 Recomendação: URGENT - Discount/promotion ou devolução ao fornecedor

Categorias de produtos parados:
┌──────────────────────┬──────────────┬─────────────────────────────┐
│ Dias sem venda       │ Severidade   │ Ação recomendada            │
├──────────────────────┼──────────────┼─────────────────────────────┤
│ > 90 dias            │ 🔴 CRÍTICO   │ Desconto forte/Devolver     │
│ 60-90 dias           │ 🟠 ALTO      │ Promoção urgente            │
│ 30-60 dias           │ 🟡 MÉDIO     │ Monitorar/Promoção leve     │
│ < 30 dias            │ 🟢 NORMAL    │ Dentro da normalidade       │
└──────────────────────┴──────────────┴─────────────────────────────┘
```

**Análise:**
- Produtos com estoque > 0
- Última venda há mais de X dias
- Valor total investido parado

---

#### UC3: Best & Worst Suppliers
**Descrição:** Análise de performance de fornecedores por giro de produtos

**Exemplo de pergunta:**
- "Quais fornecedores têm produtos com melhor giro?"
- "Me mostre fornecedores com produtos parados"

**Tool:** `analyze_supplier_performance(metric='turnover_rate')`

**Como funciona - Comparação Visual:**

```
COMPARAÇÃO DE FORNECEDORES (Performance de Giro)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 FORNECEDOR A (EXCELENTE)
┌─────────────────────────────────────────────────────────────────────┐
│ Produtos fornecidos: 15                                             │
│ Taxa de giro: 85% (Alto)                                           │
│ Tempo até 1ª venda: 3 dias (Rápido)                               │
│ Produtos parados: 1 (6.7%)                                         │
│                                                                     │
│ Timeline típica:                                                    │
│ Compra → 3 dias → 1ª Venda → Vendas frequentes → Reposição        │
│   ▲         ✅          ✅            ✅               ✅          │
│                                                                     │
│ 📊 Score: 95/100                                                   │
│ 💰 Receita gerada: R$ 150.000                                     │
│ ✅ Recomendação: PRIORIZAR compras deste fornecedor               │
└─────────────────────────────────────────────────────────────────────┘

⚠️ FORNECEDOR B (MÉDIO)
┌─────────────────────────────────────────────────────────────────────┐
│ Produtos fornecidos: 20                                             │
│ Taxa de giro: 45% (Médio)                                          │
│ Tempo até 1ª venda: 12 dias (Moderado)                            │
│ Produtos parados: 8 (40%)                                          │
│                                                                     │
│ Timeline típica:                                                    │
│ Compra → 12 dias → 1ª Venda → Vendas esporádicas → ?              │
│   ▲         ⏰          ⚠️             ❌                           │
│                                                                     │
│ 📊 Score: 52/100                                                   │
│ 💰 Receita gerada: R$ 80.000                                      │
│ ⚠️ Recomendação: REVISAR mix de produtos                          │
└─────────────────────────────────────────────────────────────────────┘

❌ FORNECEDOR C (RUIM)
┌─────────────────────────────────────────────────────────────────────┐
│ Produtos fornecidos: 10                                             │
│ Taxa de giro: 15% (Baixo)                                          │
│ Tempo até 1ª venda: 45 dias (Lento)                               │
│ Produtos parados: 7 (70%)                                          │
│                                                                     │
│ Timeline típica:                                                    │
│ Compra → 45 dias → 1ª Venda? → Pouquíssimas vendas → Parado       │
│   ▲         ❌          ❌              ❌               ❌          │
│                                                                     │
│ 📊 Score: 18/100                                                   │
│ 💰 Receita gerada: R$ 12.000                                      │
│ 🔴 Recomendação: REDUZIR ou ELIMINAR compras                      │
└─────────────────────────────────────────────────────────────────────┘

📊 Ranking de Fornecedores:
┌──────┬───────────────┬────────────┬──────────────┬────────────────┐
│ Rank │ Fornecedor    │ Taxa Giro  │ Produtos     │ Score          │
├──────┼───────────────┼────────────┼──────────────┼────────────────┤
│  1º  │ Fornecedor A  │ 85%  🏆    │ 15 produtos  │ 95/100  ✅     │
│  2º  │ Fornecedor D  │ 72%  ✅    │ 8 produtos   │ 88/100  ✅     │
│  3º  │ Fornecedor B  │ 45%  ⚠️    │ 20 produtos  │ 52/100  ⚠️     │
│  4º  │ Fornecedor C  │ 15%  ❌    │ 10 produtos  │ 18/100  ❌     │
└──────┴───────────────┴────────────┴──────────────┴────────────────┘

💡 Insight: Concentrar compras nos fornecedores top 2 (A e D)
           Revisar necessidade de manter fornecedor C
```

**Métricas:**
- Taxa de giro (vendas / estoque médio)
- Tempo médio até primeira venda
- % de produtos com baixo giro

---

#### UC4: Loss Inference
**Descrição:** Identificar possíveis perdas por divergência entre compra/venda

**Exemplo de pergunta:**
- "Tem algum produto com possível perda ou furto?"
- "Analise divergências no estoque"

**Tool:** `detect_stock_losses(tolerance_percentage=5)`

**Como funciona - Fluxo de Detecção:**

```
DETECÇÃO DE PERDAS (Análise de Divergência)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

01/01 (Início) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 31/01 (Hoje)

MOVIMENTAÇÕES DO PRODUTO X:
┌────────────────────────────────────────────────────────────────────┐
│ 01/01 - Estoque Inicial:           100 unidades                   │
│                                                                    │
│ 05/01 - Compra:                   +200 unidades                   │
│         Estoque esperado:          300 unidades                   │
│                                                                    │
│ 10/01 - Venda:                     -50 unidades                   │
│         Estoque esperado:          250 unidades                   │
│                                                                    │
│ 15/01 - Compra:                   +100 unidades                   │
│         Estoque esperado:          350 unidades                   │
│                                                                    │
│ 20/01 - Venda:                     -80 unidades                   │
│         Estoque esperado:          270 unidades                   │
│                                                                    │
│ 25/01 - Venda:                     -45 unidades                   │
│         Estoque esperado:          225 unidades                   │
└────────────────────────────────────────────────────────────────────┘

ANÁLISE DE DIVERGÊNCIA:
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│ 📊 Estoque ESPERADO (calculado):     225 unidades                 │
│                                                                    │
│ 📦 Estoque REAL (físico/sistema):    200 unidades                 │
│                                                                    │
│ ❌ DIVERGÊNCIA:                       -25 unidades (PERDA!)       │
│                                                                    │
│ 📈 Percentual de perda:               11.1% (25 ÷ 225)           │
│                                                                    │
│ 💰 Valor da perda:                    R$ 1.250 (25 × R$ 50)      │
│                                                                    │
│ ⚠️  STATUS: ACIMA DO THRESHOLD (5%)                               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

POSSÍVEIS CAUSAS:
┌────────────────────────────────────────────────────────────────────┐
│ 1. 🕵️ Furto/Roubo                                                 │
│    - Perda externa (clientes)                                     │
│    - Perda interna (funcionários)                                 │
│                                                                    │
│ 2. 📦 Erro de Contagem                                            │
│    - Inventário físico incorreto                                  │
│    - Erro no recebimento                                          │
│                                                                    │
│ 3. 🔨 Quebra/Avaria                                               │
│    - Produtos danificados não registrados                         │
│    - Validade vencida não baixada                                 │
│                                                                    │
│ 4. 📝 Erro de Registro                                            │
│    - Venda não lançada no sistema                                 │
│    - Ajuste manual incorreto                                      │
└────────────────────────────────────────────────────────────────────┘

FLUXO DE CÁLCULO:
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  Estoque        +  Total      -  Total     =  Estoque             │
│  Inicial           Compras       Vendas        Esperado           │
│                                                                    │
│    100      +    300      -    175     =    225                  │
│                                                                    │
│                    vs                                              │
│                                                                    │
│                 Estoque Real = 200                                │
│                                                                    │
│              PERDA = 225 - 200 = 25 unidades                     │
│                                                                    │
│         % Perda = (25 ÷ 225) × 100 = 11.1%                       │
│                                                                    │
│         Se % > Threshold (5%) → ⚠️ ALERTAR                        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

💡 Recomendação: Investigar causa da divergência, revisar segurança
```

**Lógica:**
```
Estoque Esperado = Estoque Inicial + Compras - Vendas
Perda = Estoque Esperado - Estoque Real
Se Perda > threshold → Alertar
```

---

#### UC5: Optimal Purchase Suggestions
**Descrição:** Sugerir compras baseadas em histórico de vendas

**Exemplo de pergunta:**
- "Quanto devo comprar de cada produto essa semana?"
- "Me sugira uma ordem de compra otimizada"

**Tool:** `suggest_purchase_order(days_forecast=30)`

**Como funciona - Cálculo de Reposição:**

```
SUGESTÃO DE COMPRA INTELIGENTE (Baseada em Demanda)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANÁLISE DE HISTÓRICO (Últimos 90 dias):
┌────────────────────────────────────────────────────────────────────┐
│ Produto: Notebook Dell XPS 15                                     │
│                                                                    │
│ Vendas dos últimos 90 dias:                                       │
│ ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐       │
│ │ Sem1 │ Sem2 │ Sem3 │ Sem4 │ Sem5 │ Sem6 │ Sem7 │ Sem8 │       │
│ ├──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤       │
│ │  45  │  52  │  48  │  50  │  47  │  53  │  49  │  51  │ un    │
│ └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘       │
│                                                                    │
│ 📊 Total vendido: 395 unidades em 90 dias                        │
│ 📊 Média diária: 395 ÷ 90 = 4.4 unidades/dia                     │
└────────────────────────────────────────────────────────────────────┘

PROJEÇÃO PARA OS PRÓXIMOS 30 DIAS:
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  Demanda Projetada = Taxa Venda Diária × Dias Forecast           │
│                    = 4.4 un/dia × 30 dias                         │
│                    = 132 unidades                                 │
│                                                                    │
│  + Safety Stock (20%) = 132 × 1.2 = 158 unidades                 │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

CÁLCULO DE REPOSIÇÃO:
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  Estoque Atual:                    35 unidades                    │
│  Demanda Projetada (30 dias):    132 unidades                    │
│  Com Safety Buffer (20%):        158 unidades                    │
│                                                                    │
│  ─────────────────────────────────────────────────────           │
│                                                                    │
│  Quantidade a Comprar = 158 - 35 = 123 unidades                  │
│                                                                    │
│  Arredondamento (lote):            ≈ 125 unidades                │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

TIMELINE DE CONSUMO (Próximos 30 dias):
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│ Hoje        Dia 10      Dia 20      Dia 30                       │
│  ▼           ▼           ▼           ▼                            │
│ 35 un   →   22 un   →   9 un    →  -5 un  ❌ (sem compra)      │
│                                                                    │
│             COM COMPRA DE 125 UNIDADES:                          │
│                                                                    │
│ Hoje        Dia 1 (após PO)  Dia 30                              │
│  ▼           ▼                ▼                                   │
│ 35 un   →  160 un         →  28 un  ✅ (com buffer)            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

PRIORIZAÇÃO:
┌────────────────────────────────────────────────────────────────────┐
│ Produto            │ Estoque │ Dias até │ Prioridade │ Qtd       │
│                    │ Atual   │ Ruptura  │            │ Sugerida  │
│────────────────────┼─────────┼──────────┼────────────┼───────────┤
│ Notebook Dell XPS  │  35 un  │  8 dias  │ 🔴 HIGH    │ 125 un    │
│ Mouse Logitech MX  │  12 un  │  3 dias  │ 🔴 HIGH    │  90 un    │
│ Teclado Mecânico   │  45 un  │ 15 dias  │ 🟡 MEDIUM  │  60 un    │
│ Monitor LG 27"     │  80 un  │ 35 dias  │ 🟢 LOW     │  40 un    │
└────────────────────────────────────────────────────────────────────┘

SUGESTÃO DE PEDIDO CONSOLIDADO:
┌────────────────────────────────────────────────────────────────────┐
│ Total de produtos: 4                                              │
│ Total de unidades: 315                                            │
│ Valor total: R$ 89.450,00                                         │
│                                                                    │
│ 📦 Criar pedido de compra imediatamente para produtos HIGH        │
│ ⏰ Agendar pedido em 7 dias para produtos MEDIUM                  │
│ 📅 Monitorar produtos LOW (sem urgência)                          │
└────────────────────────────────────────────────────────────────────┘
```

**Lógica:**
```
Taxa de Venda Diária = Total vendido / dias analisados
Estoque Necessário = Taxa Venda * Dias Forecast
Quantidade a Comprar = max(0, Necessário - Estoque Atual)
+ Safety Buffer (20%)
```

---

#### UC6: Top Selling Products
**Descrição:** Análise de produtos mais vendidos por período/valor/quantidade

**Exemplo de pergunta:**
- "Quais os 10 produtos mais vendidos esse mês?"
- "Me mostre os produtos que mais geraram receita"

**Tool:** `get_top_selling_products(period='month', limit=10, metric='revenue')`

**Como funciona - Ranking Visual:**

```
TOP 10 PRODUTOS MAIS VENDIDOS (Janeiro 2026 - Por Receita)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PODIUM - TOP 3:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│     🥇 1º LUGAR                  🥈 2º LUGAR        🥉 3º LUGAR     │
│  ═══════════════              ═══════════════    ═══════════════   │
│                                                                     │
│  Notebook Dell XPS           iPhone 15 Pro       Smart TV Samsung  │
│                                                                     │
│  📊 Vendas: 95 un            📊 Vendas: 78 un    📊 Vendas: 142 un │
│  💰 Receita:                 💰 Receita:         💰 Receita:       │
│     R$ 475.000              R$ 390.000          R$ 355.000        │
│                                                                     │
│  📈 % do total: 18.5%        📈 % do total: 15.2% 📈 % do total: 13.8% │
│                                                                     │
│  🏆 Campeão absoluto!        🏆 Vice-campeão     🏆 Bronze          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

RANKING COMPLETO:
┌──────┬────────────────────────┬──────────┬──────────────┬─────────┬──────┐
│ Rank │ Produto                │ Qtd Vend │ Receita      │ % Total │ Est. │
├──────┼────────────────────────┼──────────┼──────────────┼─────────┼──────┤
│  1º  │ Notebook Dell XPS      │   95 un  │ R$ 475.000   │  18.5%  │ 35   │
│  2º  │ iPhone 15 Pro          │   78 un  │ R$ 390.000   │  15.2%  │ 12   │
│  3º  │ Smart TV Samsung 55"   │  142 un  │ R$ 355.000   │  13.8%  │ 45   │
│  4º  │ PlayStation 5          │   65 un  │ R$ 292.500   │  11.4%  │ 20   │
│  5º  │ MacBook Air M2         │   42 un  │ R$ 252.000   │   9.8%  │  8   │
│  6º  │ AirPods Pro            │  180 un  │ R$ 234.000   │   9.1%  │ 89   │
│  7º  │ iPad Air               │   68 un  │ R$ 204.000   │   7.9%  │ 22   │
│  8º  │ Xbox Series X          │   48 un  │ R$ 192.000   │   7.5%  │ 15   │
│  9º  │ Cafeteira Nespresso    │  156 un  │ R$ 93.600    │   3.6%  │ 78   │
│ 10º  │ Ar Cond LG 12.000 BTU  │   35 un  │ R$ 84.000    │   3.3%  │  9   │
└──────┴────────────────────────┴──────────┴──────────────┴─────────┴──────┘

GRÁFICO DE RECEITA (TOP 10):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ Notebook   ████████████████████ R$ 475k (18.5%)                   │
│ iPhone     ████████████████ R$ 390k (15.2%)                        │
│ TV Samsung ██████████████ R$ 355k (13.8%)                          │
│ PS5        ████████████ R$ 293k (11.4%)                            │
│ MacBook    ██████████ R$ 252k (9.8%)                               │
│ AirPods    █████████ R$ 234k (9.1%)                                │
│ iPad       ████████ R$ 204k (7.9%)                                 │
│ Xbox       ████████ R$ 192k (7.5%)                                 │
│ Cafeteira  ████ R$ 94k (3.6%)                                      │
│ Ar Cond    ███ R$ 84k (3.3%)                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

ANÁLISE 80/20 (Regra de Pareto):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Top 3 produtos (30% do catálogo):                                │
│  └─→ Geram 47.5% da receita total! 🎯                             │
│                                                                     │
│  Top 10 produtos (10% do catálogo):                               │
│  └─→ Geram 81.8% da receita total! 📊                             │
│                                                                     │
│  💡 Insight: Focar atenção nos top 10 garante 82% da receita      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

STATUS DE ESTOQUE (Top 10):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ✅ Estoque OK:        6 produtos (bom nível)                      │
│  ⚠️  Estoque BAIXO:     3 produtos (iPhone, MacBook, Xbox)         │
│  🔴 Risco CRÍTICO:     1 produto (iPhone - apenas 12 unidades!)    │
│                                                                     │
│  💡 Ação: Priorizar reposição dos 3 produtos em destaque          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

MÉTRICAS ADICIONAIS:
┌─────────────────────────────────────────────────────────────────────┐
│ Receita total (Top 10):     R$ 2.572.100                          │
│ Receita total (geral):      R$ 3.145.000                          │
│ Ticket médio:               R$ 8.574                               │
│ Unidades vendidas (Top 10): 909 unidades                          │
│ Período analisado:          01/01/2026 a 31/01/2026 (31 dias)    │
└─────────────────────────────────────────────────────────────────────┘
```

**Outras métricas disponíveis:**
- Por QUANTIDADE: `metric='quantity'` - Ranking por unidades vendidas
- Por FREQUÊNCIA: `metric='frequency'` - Produtos mais vendidos (nº de vendas)

---

#### UC7: Purchase vs Sales Timeline
**Descrição:** Analisar timeline entre compra e primeira venda (velocidade de giro)

**Exemplo de pergunta:**
- "Quanto tempo os produtos ficam parados antes de vender?"
- "Identifique produtos com tempo de giro alto"

**Tool:** `analyze_purchase_to_sale_time()`

**Como funciona - Timeline de Giro:**

```
ANÁLISE DE TEMPO ENTRE COMPRA E VENDA (Velocidade de Giro)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 PRODUTO RÁPIDO (Giro Alto - 3 dias):
┌─────────────────────────────────────────────────────────────────────┐
│ Mouse Gamer Logitech G502                                          │
│                                                                     │
│ Compra          1ª Venda      2ª Venda       3ª Venda              │
│   ▼              ▼             ▼              ▼                    │
│ 01/01 ━━━━━━━━ 04/01 ━━━━━ 05/01 ━━━━━━ 06/01                    │
│         3 dias!     1 dia       1 dia                              │
│                                                                     │
│ Timeline:                                                           │
│ │◄── 3d ──►│◄1d►│◄1d►│                                           │
│ Compra ───→ 1ª Venda → Vendas frequentes                          │
│                                                                     │
│ 📊 Tempo até 1ª venda: 3 dias ✅                                   │
│ 🔄 Taxa de giro: ALTA (vende rápido!)                             │
│ 💡 Característica: Alta demanda, produto popular                   │
└─────────────────────────────────────────────────────────────────────┘

⚠️ PRODUTO MÉDIO (Giro Normal - 15 dias):
┌─────────────────────────────────────────────────────────────────────┐
│ Teclado Mecânico Razer                                             │
│                                                                     │
│ Compra          1ª Venda                2ª Venda                   │
│   ▼              ▼                       ▼                         │
│ 01/01 ━━━━━━━━━━━━━━━━━━━━━━━━━━ 16/01 ━━━━━━━━ 20/01           │
│              15 dias                  4 dias                       │
│                                                                     │
│ Timeline:                                                           │
│ │◄──────── 15d ────────►│◄─ 4d ─►│                               │
│ Compra ──────────────────→ 1ª Venda → Vendas esporádicas          │
│                                                                     │
│ 📊 Tempo até 1ª venda: 15 dias ⚠️                                  │
│ 🔄 Taxa de giro: MÉDIA (giro normal)                              │
│ 💡 Característica: Demanda moderada                               │
└─────────────────────────────────────────────────────────────────────┘

🐌 PRODUTO LENTO (Giro Baixo - 45 dias):
┌─────────────────────────────────────────────────────────────────────┐
│ Impressora 3D Creality                                             │
│                                                                     │
│ Compra                                          1ª Venda           │
│   ▼                                              ▼                 │
│ 01/01 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15/02               │
│                        45 dias!                                    │
│                                                                     │
│ Timeline:                                                           │
│ │◄──────────────── 45 dias ────────────────────►│                │
│ Compra ──────────────────────────────────────────→ 1ª Venda       │
│                                                                     │
│ 📊 Tempo até 1ª venda: 45 dias ❌                                  │
│ 🔄 Taxa de giro: BAIXA (muito lento!)                             │
│ 💡 Característica: Produto nicho, demanda específica               │
│ ⚠️  Atenção: Capital parado por muito tempo                       │
└─────────────────────────────────────────────────────────────────────┘

DISTRIBUIÇÃO DE PRODUTOS POR VELOCIDADE:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 🚀 RÁPIDOS (0-7 dias):        32 produtos (40%)                   │
│    ████████████████████████                                        │
│    Ex: Mouse, Fone, Cabo USB, Carregador                          │
│                                                                     │
│ ⚡ NORMAIS (8-21 dias):       38 produtos (48%)                    │
│    █████████████████████████████                                   │
│    Ex: Teclado, Webcam, SSD, Monitor                              │
│                                                                     │
│ 🐌 LENTOS (22-60 dias):        8 produtos (10%)                    │
│    ██████                                                          │
│    Ex: Impressora 3D, Drone, Projetor                             │
│                                                                     │
│ ❌ MUITO LENTOS (>60 dias):    2 produtos (2%)                     │
│    ██                                                              │
│    Ex: Equipamento profissional especializado                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

RANKING - TOP 5 MAIS RÁPIDOS vs MAIS LENTOS:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 🚀 MAIS RÁPIDOS:                    🐌 MAIS LENTOS:                │
│                                                                     │
│ 1. Mouse Gamer           3 dias    1. Scanner Pro      78 dias    │
│ 2. Fone Bluetooth        4 dias    2. Impressora 3D    45 dias    │
│ 3. Cabo USB-C            5 dias    3. Drone 4K         38 dias    │
│ 4. Carregador 65W        6 dias    4. Projetor 4K      32 dias    │
│ 5. Película iPhone       7 dias    5. Tablet Pro       28 dias    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

INSIGHTS E RECOMENDAÇÕES:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ ✅ Produtos Rápidos (40%):                                         │
│    └─→ Manter estoque alto, reabastecer frequentemente            │
│    └─→ São os "carros-chefe" do negócio                           │
│                                                                     │
│ ⚠️ Produtos Normais (48%):                                         │
│    └─→ Estoque moderado, monitorar demanda                        │
│    └─→ Padrão esperado para maioria dos produtos                  │
│                                                                     │
│ 🔴 Produtos Lentos (12%):                                          │
│    └─→ Estoque mínimo, comprar sob demanda                        │
│    └─→ Considerar descontinuar se não são estratégicos            │
│    └─→ Avaliar margens para compensar custo de oportunidade       │
│                                                                     │
│ 💡 Tempo médio geral: 14 dias                                     │
│ 💰 Capital médio parado: R$ 185.000                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Insights:**
- Tempo médio até primeira venda
- Produtos que ficam muito tempo parados
- Sazonalidade e padrões de demanda

---

#### UC8: Stock Alerts & Recommendations
**Descrição:** Alertas proativos sobre situações críticas (usa UC1 + UC1.5 + outras análises)

**Exemplo de pergunta:**
- "Me dê um resumo da situação do estoque"
- "Quais são os alertas críticos de hoje?"
- "Dashboard executivo de estoque"

**Tool:** `get_stock_alerts()`

**Como funciona - Dashboard Consolidado:**

```
DASHBOARD DE ALERTAS DE ESTOQUE (Visão Executiva)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SAÚDE GERAL DO ESTOQUE:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│              🏥 HEALTH SCORE: 67/100 (FAIR)                        │
│                                                                     │
│  ████████████████████████████████████░░░░░░░░░░░░░░░░░░░          │
│  └─ 67% ─┘                                                         │
│                                                                     │
│  Legenda:                                                           │
│  🟢 80-100: EXCELLENT    🟡 60-79: GOOD                            │
│  🟠 40-59: FAIR          🔴 0-39: POOR                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

RESUMO GERAL:
┌─────────────────────────────────────────────────────────────────────┐
│ Total de Produtos:         120 produtos                            │
│ Produtos com Estoque:      95 produtos (79%)                       │
│ Valor Total em Estoque:    R$ 2.850.000                           │
│ Total de Alertas:          12 alertas ativos                       │
│ Período Analisado:         01/01/2026 - 31/01/2026                │
└─────────────────────────────────────────────────────────────────────┘

🔴 ALERTAS CRÍTICOS (5):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 1. 🔴 Notebook Dell XPS - Vai zerar em 2.5 dias                   │
│    └─→ Estoque: 11 unidades                                       │
│    └─→ Demanda: 4.4 un/dia                                        │
│    └─→ Pedidos: NENHUM                                            │
│    └─→ AÇÃO: Criar pedido de compra IMEDIATAMENTE                 │
│                                                                     │
│ 2. 🔴 iPhone 15 Pro - JÁ sem estoque com demanda                  │
│    └─→ Estoque: 0 unidades                                        │
│    └─→ Vendas recentes: 15 vendas (últimos 14 dias)               │
│    └─→ Receita perdida: R$ 75.000                                 │
│    └─→ AÇÃO: Comprar URGENTE                                      │
│                                                                     │
│ 3. 🔴 Smart TV 55" - Pedido insuficiente                          │
│    └─→ Estoque: 8 unidades                                        │
│    └─→ Pedido pendente: 30 unidades                               │
│    └─→ Necessário: 90 unidades                                    │
│    └─→ Gap: 52 unidades                                           │
│    └─→ AÇÃO: Complementar pedido                                  │
│                                                                     │
│ 4. 🔴 MacBook Air M2 - Divergência de estoque (perda)            │
│    └─→ Estoque esperado: 45 unidades                              │
│    └─→ Estoque real: 35 unidades                                  │
│    └─→ Perda: 10 unidades (22%)                                   │
│    └─→ Valor: R$ 60.000                                           │
│    └─→ AÇÃO: Investigar causa da perda                            │
│                                                                     │
│ 5. ⏰ PlayStation 5 - Pedido atrasado (12 dias)                   │
│    └─→ Pedido: PO-2024-045                                        │
│    └─→ Quantidade: 50 unidades                                    │
│    └─→ Data pedido: 19/01/2026                                    │
│    └─→ Status: PENDING há 12 dias                                 │
│    └─→ AÇÃO: Contatar fornecedor URGENTE                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

🟠 AVISOS IMPORTANTES (4):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 1. 🟠 Mouse Gamer - Estoque baixo para alta demanda               │
│    └─→ Estoque: 18 unidades (apenas 4 dias)                       │
│    └─→ Reabastecer em breve                                       │
│                                                                     │
│ 2. 🟠 Impressora Canon - Sem vendas há 67 dias                    │
│    └─→ Capital parado: R$ 32.400                                  │
│    └─→ Considerar promoção                                        │
│                                                                     │
│ 3. 🟠 Teclado Mecânico - Abaixo do estoque mínimo                 │
│    └─→ Atual: 12 un | Mínimo: 20 un                              │
│    └─→ Repor 8 unidades                                           │
│                                                                     │
│ 4. 🟠 3 produtos de Fornecedor XYZ com baixo giro                 │
│    └─→ Revisar mix de produtos deste fornecedor                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

💡 RECOMENDAÇÕES ESTRATÉGICAS (3):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 1. 📦 15 produtos precisam reposição urgente                       │
│    └─→ Valor total do pedido: R$ 245.000                          │
│    └─→ Criar pedidos de compra hoje                               │
│                                                                     │
│ 2. 💰 R$ 85.000 em estoque parado (>60 dias sem venda)           │
│    └─→ Aplicar descontos progressivos                             │
│    └─→ Liberar capital para produtos A                            │
│                                                                     │
│ 3. 🔍 2 fornecedores com performance baixa (<30% giro)            │
│    └─→ Revisar contratos                                          │
│    └─→ Buscar alternativas                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

MÉTRICAS-CHAVE (Últimos 30 dias):
┌─────────────────────────────────────────────────────────────────────┐
│ Vendas:                    R$ 1.850.000  (↑ 12% vs mês anterior)  │
│ Taxa de ruptura:           2.3%          (↓ 0.8% vs mês anterior) │
│ Produtos abaixo mín:       8 produtos    (6.7% do total)          │
│ Giro médio:                32 dias       (meta: < 30 dias)        │
│ Disponibilidade média:     97.7%         (meta: > 95%)            │
└─────────────────────────────────────────────────────────────────────┘

AÇÕES PRIORITÁRIAS - HOJE:
┌─────────────────────────────────────────────────────────────────────┐
│ ⚡ URGENTE (fazer hoje):                                           │
│    1. Criar pedido para Notebook Dell XPS (2 dias até ruptura)    │
│    2. Contatar fornecedor sobre PlayStation 5 (pedido atrasado)   │
│    3. Investigar perda de MacBook Air M2 (R$ 60k)                 │
│                                                                     │
│ 📅 IMPORTANTE (fazer esta semana):                                 │
│    1. Complementar pedido Smart TV 55"                             │
│    2. Criar campanha promocional para produtos parados            │
│    3. Revisar contrato com Fornecedor XYZ                          │
└─────────────────────────────────────────────────────────────────────┘
```

**Alertas Consolidados:**
- 🔴 Produtos que vão zerar sem pedido de compra (PREVENTIVO - UC1.5)
- 🔴 Produtos em ruptura com demanda (REATIVO - UC1)
- 🟠 Pedidos de compra insuficientes ou atrasados
- 🟡 Estoque abaixo do mínimo
- 🟠 Produtos sem venda há muito tempo
- 🔵 Produtos com alta demanda e estoque baixo

---

#### UC9: Operational Availability Issues Detection 🆕
**Descrição:** Detectar produtos com estoque mas que pararam de vender (problema operacional)

**Exemplo de pergunta:**
- "Quais produtos têm estoque mas não estão vendendo?"
- "Me mostre produtos com queda nas vendas apesar de ter estoque"
- "Há produtos no depósito que não foram repostos?"
- "Produtos recebidos mas não vendendo?"

**Tool:** `detect_operational_availability_issues(recent_period_days=14, historical_period_days=60)`

**Como funciona - Detecção de Problema Operacional:**

```
PROBLEMA OPERACIONAL: Produto TEM Estoque mas NÃO Vende
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CASO: Mouse Gamer Logitech G502 (Produto Popular)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

75 dias atrás ━━━━━━━━━━━━━ 14 dias atrás ━━━━━━━━━━━━━ Hoje (31/01)
    ▲                             ▲                          ▲
    │                             │                          │
    │◄─── Historical Period ─────►│◄─── Recent Period ──────►│
    │       (60 dias)             │       (14 dias)          │
    │                             │                          │
    │                         Recebeu PO                     │
    │                         150 unidades                   │
    │                         Status: RECEIVED ✅            │

FASE 1: VENDAS HISTÓRICAS (BOM DESEMPENHO) ✅
┌─────────────────────────────────────────────────────────────────────┐
│ 75 dias atrás → 15 dias atrás (60 dias de histórico)              │
│                                                                     │
│ Semana  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │ 8  │ 9  │           │
│ Vendas  │ 35 │ 42 │ 38 │ 40 │ 37 │ 41 │ 39 │ 36 │ 40 │ un        │
│ Status  │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │           │
│                                                                     │
│ 📊 Total histórico: 348 unidades em 60 dias                       │
│ 📊 Média diária: 5.8 unidades/dia                                 │
│ 💰 Receita: R$ 17.400 (348 × R$ 50)                              │
│ ✅ Performance: EXCELENTE                                          │
└─────────────────────────────────────────────────────────────────────┘

FASE 2: PEDIDO RECEBIDO (14 dias atrás) 📦
┌─────────────────────────────────────────────────────────────────────┐
│ Data: 17/01/2026                                                   │
│ Pedido: PO-2024-0567                                               │
│ Fornecedor: Tech Imports Ltda                                      │
│ Quantidade: 150 unidades                                           │
│ Status: RECEIVED ✅                                                 │
│                                                                     │
│ Estoque ANTES:  45 unidades                                        │
│ Estoque DEPOIS: 195 unidades                                       │
│                                                                     │
│ ✅ Produto adicionado ao sistema                                   │
│ ✅ Movimentação registrada                                         │
│ ❓ Mas onde está o produto fisicamente?                            │
└─────────────────────────────────────────────────────────────────────┘

FASE 3: QUEDA SÚBITA NAS VENDAS (PROBLEMA!) ❌
┌─────────────────────────────────────────────────────────────────────┐
│ Últimos 14 dias (após recebimento):                               │
│                                                                     │
│ Dia    │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │11 │12 │13 │14 │ │
│ Vendas │ 0 │ 1 │ 0 │ 0 │ 0 │ 0 │ 0 │ 2 │ 0 │ 0 │ 0 │ 0 │ 0 │ 0 │ │
│ Status │ ❌│ ⚠️│ ❌│ ❌│ ❌│ ❌│ ❌│ ⚠️│ ❌│ ❌│ ❌│ ❌│ ❌│ ❌│ │
│                                                                     │
│ 📊 Total recente: 3 unidades em 14 dias                           │
│ 📊 Média diária: 0.2 unidades/dia                                 │
│ 💰 Receita: R$ 150 (3 × R$ 50)                                    │
│ 🔴 Performance: CRÍTICA (queda de 96%!)                            │
└─────────────────────────────────────────────────────────────────────┘

DIAGNÓSTICO:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ ✅ Produto TEM estoque:        195 unidades                        │
│ ✅ Produto TEM histórico bom:  5.8 un/dia                         │
│ ✅ Produto FOI recebido:       14 dias atrás                       │
│ ❌ Produto NÃO está vendendo:  0.2 un/dia (96% de queda!)         │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════   │
│                                                                     │
│ 💡 CONCLUSÃO: PROBLEMA OPERACIONAL!                                │
│                                                                     │
│    Produto existe no sistema MAS não está disponível para venda   │
│                                                                     │
│ ═══════════════════════════════════════════════════════════════   │
│                                                                     │
│ 🔍 POSSÍVEIS CAUSAS:                                               │
│    1. 📦 Produto preso no depósito/CD                             │
│    2. 🏪 Não foi reposto nas prateleiras                          │
│    3. 🌐 Não disponível no e-commerce                             │
│    4. 🎨 Problema de exposição/merchandising                      │
│    5. 📋 Erro no sistema de disponibilidade                       │
│    6. 🏷️ Preço errado bloqueando vendas                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

IMPACTO FINANCEIRO:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ Vendas esperadas (14 dias):    5.8 × 14 = 81 unidades            │
│ Vendas reais (14 dias):        3 unidades                         │
│                                ─────────────                       │
│ VENDAS PERDIDAS:               78 unidades                         │
│                                                                     │
│ Receita perdida:               R$ 3.900 (78 × R$ 50)              │
│ Período:                       14 dias                             │
│ Perda diária:                  R$ 279/dia                          │
│                                                                     │
│ 📊 Se continuar por 30 dias:   R$ 8.370 em perdas!               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

COMPARAÇÃO COM OUTRAS SITUAÇÕES:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ ❌ RUPTURA (UC1):                                                  │
│    Estoque = 0 → Cliente sabe que não tem                         │
│    └─→ Expectativa clara                                          │
│                                                                     │
│ ⚠️ RISCO (UC1.5):                                                  │
│    Estoque baixo → Sistema alerta para comprar                    │
│    └─→ Problema previsto                                          │
│                                                                     │
│ 🏪 OPERACIONAL (UC9 - NOVO):                                      │
│    Estoque alto → Sistema diz "tem"                               │
│    Cliente: "Cadê?" → Não encontra                                │
│    └─→ PIOR CENÁRIO: frustração + perda + não detectado          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

AÇÕES RECOMENDADAS (Por Severidade):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 🔴 CRITICAL (queda > 90%):                                         │
│    1. Verificar localização física IMEDIATAMENTE                   │
│    2. Confirmar se produto está nas prateleiras/online            │
│    3. Revisar processo de recebimento e reposição                 │
│    4. Ações em 24 horas!                                          │
│                                                                     │
│ 🟠 HIGH (queda 80-90%):                                            │
│    1. Auditoria de disponibilidade                                │
│    2. Verificar exposição e visibilidade                          │
│    3. Revisar preços e cadastro                                   │
│    4. Ações em 48 horas                                           │
│                                                                     │
│ 🟡 MEDIUM (queda 70-80%):                                          │
│    1. Monitorar nas próximas 48h                                  │
│    2. Verificar concorrência e sazonalidade                       │
│    3. Revisar estratégia de marketing                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

💡 INSIGHT: Ter estoque não garante vendas - produto precisa estar ACESSÍVEL!
```

---

#### UC10: Pending Purchase Orders Summary 🆕
**Descrição:** Listar e analisar pedidos de compra pendentes

**Exemplo de pergunta:**
- "Quais pedidos de compra estão pendentes?"
- "Me mostre pedidos de compra atrasados?"
- "Qual o status do pedido para o Produto X?"

**Tool:** `get_pending_order_summary(product_id=None)`

**Como funciona - Painel de Pedidos:**

```
PEDIDOS DE COMPRA PENDENTES (Status: PENDING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESUMO GERAL:
┌─────────────────────────────────────────────────────────────────────┐
│ Total de pedidos pendentes: 8                                      │
│ Valor total aguardando:     R$ 485.000                            │
│ Pedidos atrasados (>7 dias): 3 pedidos  ⚠️                        │
│ Pedidos recentes (<3 dias):  5 pedidos  ✅                         │
└─────────────────────────────────────────────────────────────────────┘

⏰ PEDIDOS ATRASADOS (3):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 🔴 PO-2024-0042 - ATRASADO 15 DIAS                                │
│ ├─ Fornecedor: Tech Suppliers Ltda                                │
│ ├─ Data do pedido: 16/01/2026                                     │
│ ├─ Dias pendente: 15 dias (threshold: 7 dias)                     │
│ ├─ Produtos:                                                        │
│ │  • PlayStation 5: 50 unidades @ R$ 4.500 = R$ 225.000          │
│ │  • Xbox Series X: 30 unidades @ R$ 4.000 = R$ 120.000          │
│ ├─ Valor total: R$ 345.000                                        │
│ └─ ⚠️ AÇÃO: CONTATAR FORNECEDOR URGENTE!                          │
│                                                                     │
│ Timeline do pedido:                                                 │
│ 16/01 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 31/01 (HOJE)  │
│  ▲                                                     ▲            │
│ Pedido                                          15 dias depois!    │
│ feito                                           AINDA PENDING      │
│                                                                     │
│────────────────────────────────────────────────────────────────────│
│                                                                     │
│ 🟠 PO-2024-0045 - ATRASADO 10 DIAS                                │
│ ├─ Fornecedor: Eletrônicos Brasil SA                              │
│ ├─ Data do pedido: 21/01/2026                                     │
│ ├─ Dias pendente: 10 dias                                         │
│ ├─ Produtos:                                                        │
│ │  • Smart TV 55": 40 unidades @ R$ 2.500 = R$ 100.000          │
│ ├─ Valor total: R$ 100.000                                        │
│ └─ ⚠️ AÇÃO: Verificar status da entrega                           │
│                                                                     │
│────────────────────────────────────────────────────────────────────│
│                                                                     │
│ 🟡 PO-2024-0048 - ATRASADO 8 DIAS                                 │
│ ├─ Fornecedor: Distribuidora XYZ                                  │
│ ├─ Data do pedido: 23/01/2026                                     │
│ ├─ Dias pendente: 8 dias                                          │
│ ├─ Produtos:                                                        │
│ │  • Notebook Dell: 15 unidades @ R$ 5.000 = R$ 75.000          │
│ ├─ Valor total: R$ 75.000                                         │
│ └─ ⚠️ AÇÃO: Acompanhar entrega próxima semana                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

✅ PEDIDOS RECENTES (5):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ PO-2024-0052 │ Apple Store BR    │ 2 dias │ R$ 120.000 │ ✅       │
│ PO-2024-0053 │ Samsung Oficial   │ 1 dia  │ R$ 85.000  │ ✅       │
│ PO-2024-0054 │ Tech Imports      │ 3 dias │ R$ 95.000  │ ✅       │
│ PO-2024-0055 │ Dell Corporation  │ 2 dias │ R$ 145.000 │ ✅       │
│ PO-2024-0056 │ LG Electronics    │ 1 dia  │ R$ 65.000  │ ✅       │
│                                                                     │
│ Status: Dentro do prazo normal (< 7 dias)                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

TIMELINE VISUAL DOS PEDIDOS:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ 15 dias atrás ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Hoje (31/01)│
│                                                                     │
│ PO-0042 ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● 🔴 15d   │
│                                                                     │
│         PO-0045 ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● 🟠 10d   │
│                                                                     │
│           PO-0048 ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● 🟡 8d    │
│                                                                     │
│                               PO-0054 ●━━━━━● ✅ 3d               │
│                                 PO-0052 ●━━● ✅ 2d                 │
│                                 PO-0055 ●━━● ✅ 2d                 │
│                                   PO-0053 ●● ✅ 1d                 │
│                                   PO-0056 ●● ✅ 1d                 │
│                                                                     │
│ Legenda:                                                            │
│ 🔴 Muito atrasado (>14d)  🟠 Atrasado (>10d)  🟡 Atenção (>7d)   │
│ ✅ Normal (<7d)                                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

ANÁLISE POR FORNECEDOR:
┌─────────────────────────────────────────────────────────────────────┐
│ Fornecedor            │ Pedidos │ Valor Total │ Status Médio       │
│───────────────────────┼─────────┼─────────────┼────────────────────┤
│ Tech Suppliers Ltda   │    1    │ R$ 345.000  │ 🔴 Atrasado (15d) │
│ Eletrônicos Brasil SA │    1    │ R$ 100.000  │ 🟠 Atrasado (10d) │
│ Dell Corporation      │    1    │ R$ 145.000  │ ✅ OK (2d)        │
│ Apple Store BR        │    1    │ R$ 120.000  │ ✅ OK (2d)        │
│ (outros 4)            │    4    │ R$ 245.000  │ ✅ OK (<3d)       │
└─────────────────────────────────────────────────────────────────────┘

PRODUTOS MAIS AGUARDADOS:
┌─────────────────────────────────────────────────────────────────────┐
│ Produto           │ Qtd Pendente │ Pedidos │ Maior Atraso         │
│───────────────────┼──────────────┼─────────┼──────────────────────┤
│ PlayStation 5     │    50 un     │    1    │ 15 dias (PO-0042)   │
│ Notebook Dell     │    45 un     │    3    │  8 dias (PO-0048)   │
│ Smart TV 55"      │    40 un     │    1    │ 10 dias (PO-0045)   │
│ iPhone 15 Pro     │    80 un     │    2    │  2 dias (PO-0052)   │
│ MacBook Air M2    │    35 un     │    1    │  1 dia (PO-0053)    │
└─────────────────────────────────────────────────────────────────────┘

AÇÕES RECOMENDADAS:
┌─────────────────────────────────────────────────────────────────────┐
│ 🔴 URGENTE:                                                        │
│    • Contatar Tech Suppliers sobre PO-0042 (15 dias de atraso)   │
│    • Considerar fornecedor alternativo se não houver resposta     │
│                                                                     │
│ 🟠 IMPORTANTE:                                                     │
│    • Follow-up com Eletrônicos Brasil sobre PO-0045 (10 dias)    │
│    • Verificar status de PO-0048 com Distribuidora XYZ (8 dias)  │
│                                                                     │
│ 📊 MONITORAMENTO:                                                  │
│    • Acompanhar chegada dos 5 pedidos recentes                    │
│    • Atualizar sistema assim que receberem                         │
└─────────────────────────────────────────────────────────────────────┘
```

**Informações:**
- Lista de pedidos com status PENDING
- Dias desde o pedido (detecta atrasos >7 dias)
- Produtos e quantidades de cada pedido
- Valor total dos pedidos
- Timeline visual de atrasos

---

### 5.2 Advanced Use Cases (Future)

- **Price Optimization:** Sugerir alterações de preço baseado em giro
- **Seasonality Detection:** Identificar padrões sazonais
- **Supplier Negotiation Insights:** Identificar melhores momentos para negociar
- **Category Performance:** Análise por categoria/departamento

## 6. Data Model

### 6.1 Final Schema (Simplified for POC)

```sql
-- Core tables (from previous discussion)
- product (id, sku, gtin, name, category, brand, sale_price, cost_price, current_stock)
- supplier (id, name, tax_id, email, phone)
- purchase_order (id, order_number, supplier_id, order_date, total_amount, status)
- purchase_order_item (id, purchase_order_id, product_id, quantity, unit_price)
- sale_order (id, order_number, sale_date, total_amount, status)
- sale_order_item (id, sale_order_id, product_id, quantity, unit_price)
- stock_movement (id, product_id, movement_type, quantity, stock_before, stock_after, movement_date)
```

### 6.2 Fake Data Generation Strategy

**Objetivo:** Gerar 6 meses de histórico operacional realista

**Volumes:**
- **Produtos:** 50-100 produtos (baseados no CSV fornecido)
- **Fornecedores:** 10-15 fornecedores
- **Compras:** 100-150 ordens de compra
- **Vendas:** 500-1000 vendas
- **Movimentos de Estoque:** ~3000 registros

**Padrões Realistas:**
- Produtos com sazonalidade (ex: bebidas vendem mais no verão)
- Alguns produtos com alta rotação (80/20 rule)
- Alguns produtos "mortos" (comprados mas não vendidos)
- Algumas rupturas de estoque simuladas
- Perdas ocasionais (divergências)

**Gerador:**
```python
# faker_data_generator.py
- generate_products(csv_file='stock.csv')
- generate_suppliers()
- generate_purchase_orders(months=6)
- generate_sales(months=6, pattern='realistic')
- generate_stock_movements()
```

## 7. Implementation Plan

### 7.1 Setup Instructions

**Inicialização do Projeto (< 5 minutos):**

```bash
# 1. Clone/Create repository
cd poc-stock

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Editar .env e adicionar OPENAI_API_KEY

# 5. Initialize database and seed data
python database/seed_data.py

# 6. Run application
streamlit run app/streamlit_app.py
```

**Arquivo `.gitignore`:**
```
# Python
__pycache__/
*.py[cod]
venv/
.env

# Database
stock.db
*.db-journal

# IDE
.vscode/
.idea/
```

### 7.2 Project Structure

```
poc-stock/
├── README.md
├── RFC-POC-STOCK-AI-AGENT.md
├── requirements.txt
├── .env.example
├── .gitignore
├── stock.db                    # ← SQLite database (auto-generated)
├── stock.csv                   # ← Sample data for seeding
│
├── database/
│   ├── __init__.py
│   ├── schema.py               # ← SQLAlchemy models
│   ├── connection.py           # ← Database connection
│   └── seed_data.py            # ← Fake data generator
│
├── tools/
│   ├── __init__.py
│   ├── stock_analysis.py
│   ├── sales_analysis.py
│   ├── purchase_analysis.py
│   └── inventory_alerts.py
│
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts.py
│
├── app/
│   └── streamlit_app.py
│
└── tests/
    └── test_tools.py
```

### 7.3 Implementation Phases

#### Phase 1: Database Setup (Dia 1)
- [ ] Create SQLAlchemy models (schema.py)
- [ ] Setup database connection (connection.py)
- [ ] Generate fake data script (seed_data.py)
- [ ] Run seed and validate data integrity
- [ ] Test basic queries

**Estimativa: 4-6 horas** (muito mais rápido sem Docker!)

#### Phase 2: Tools Implementation (Dia 2-3)
- [ ] Implement 8 core tools
- [x] **NEW:** Implement imminent stockout risk detection (UC1.5)
- [x] **NEW:** Implement pending orders summary tool (UC9)
- [x] **ENHANCED:** Update suggest_purchase_order with pending orders info
- [x] **ENHANCED:** Update get_stock_alerts with preventive alerts
- [ ] Unit tests for each tool
- [ ] Query optimization

**Estimativa: 12-16 horas** ✅ **Enhancements completed on 2026-02-08**

#### Phase 3: AI Agent Setup (Dia 4-5)
- [ ] Configure LangChain agent
- [ ] Register tools with proper descriptions
- [ ] Create system prompts
- [ ] Test conversation flows

**Estimativa: 8-12 horas**

#### Phase 4: Frontend (Dia 6-7)
- [ ] Streamlit interface
- [ ] Chat UI with history
- [ ] Visualization widgets (charts)
- [ ] Export reports (optional)

**Estimativa: 8-12 horas**

#### Phase 5: Testing & Refinement (Dia 8)
- [ ] End-to-end testing
- [ ] Prompt engineering optimization
- [ ] Performance tuning
- [ ] Documentation (README + comments)

**Estimativa: 6-8 horas**

**Total POC: 8 dias → 6-7 dias** (ganho de 1-2 dias sem Docker/PostgreSQL setup!)

## 8. Technical Specifications

### 8.1 Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///stock.db

# Optional: Para migrar para PostgreSQL no futuro
# DATABASE_URL=postgresql://user:password@localhost:5432/stock_db
```

### 8.2 Dependencies

```txt
# requirements.txt
# Database (SQLite is built-in Python, no driver needed)
sqlalchemy==2.0.25

# AI Framework
langchain==0.1.4
langchain-openai==0.0.5
langchain-community==0.0.16

# Frontend
streamlit==1.30.0

# Data Generation
faker==22.0.0
pandas==2.1.4

# Utils
python-dotenv==1.0.0
pydantic==2.5.3

# Optional: Only if migrating to PostgreSQL
# psycopg2-binary==2.9.9
```

### 8.3 Database Connection (SQLite + Migration Path)

```python
# database/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Get database URL from environment or use SQLite default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///stock.db')

# Create engine (works with SQLite and PostgreSQL)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL debugging
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base for models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database (create all tables)"""
    from database.schema import Product, Supplier, PurchaseOrder, SaleOrder, StockMovement
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DATABASE_URL}")
```

**Migração para PostgreSQL (Opcional):**

Se futuramente precisar migrar para PostgreSQL:

1. Instalar driver: `pip install psycopg2-binary`
2. Subir PostgreSQL: `docker-compose up -d` (criar arquivo docker-compose.yml)
3. Trocar `.env`: `DATABASE_URL=postgresql://user:pass@localhost:5432/stock_db`
4. Rodar seed novamente: `python database/seed_data.py`

**Sem mudanças de código necessárias!**

### 8.4 SQLite vs PostgreSQL: Decision Matrix

**Por que SQLite para POC?**

| Benefício | Descrição |
|-----------|-----------|
| ⚡ **Zero Setup** | Sem instalação, configuração ou Docker |
| 📦 **Portabilidade** | Arquivo único `stock.db` - fácil de compartilhar |
| 🚀 **Rapidez** | POC funcionando em minutos, não horas |
| 💰 **Custo Zero** | Sem infraestrutura ou recursos de servidor |
| 🎯 **Foco** | Mais tempo no agente, menos em devops |
| ✅ **Suficiente** | Performance idêntica para < 100k registros |

**Quando migrar para PostgreSQL?**

Considere PostgreSQL apenas se:
- [ ] Precisar de múltiplos usuários simultâneos (> 10 conexões)
- [ ] Volume de dados > 100k registros
- [ ] Precisar de features avançadas (JSON columns, full-text search)
- [ ] Demo precisa parecer "enterprise"
- [ ] Vai para staging/produção

**Para esta POC:** SQLite é mais que suficiente ✅

## 9. Agent System Prompt

```python
SYSTEM_PROMPT = """
Você é um assistente especializado em análise de estoque e gestão de inventário.

Você tem acesso a um banco de dados de um sistema de gestão com informações sobre:
- Produtos e estoque atual
- Histórico de compras e fornecedores
- Histórico de vendas
- Movimentações de estoque

Suas responsabilidades:
1. Analisar dados e identificar problemas proativamente
2. Responder perguntas sobre estoque, vendas e compras
3. Gerar insights e recomendações baseadas em dados
4. Alertar sobre situações críticas (rupturas, perdas, produtos parados)

Diretrizes:
- Sempre use as tools disponíveis para buscar dados reais
- Seja conciso mas completo nas análises
- Use números e métricas específicas
- Sugira ações práticas quando identificar problemas
- Formate respostas de forma clara (use tabelas quando apropriado)

Quando receber uma pergunta:
1. Identifique qual(is) tool(s) usar
2. Execute a análise
3. Interprete os resultados
4. Forneça insights e recomendações
"""
```

## 10. Success Metrics

### POC Success Criteria

✅ **Funcional:**
- Agente responde corretamente aos 8 casos de uso principais
- Database com dados realistas (6 meses de histórico)
- Interface funcional e responsiva

✅ **Qualidade:**
- Accuracy > 90% nas análises (validação manual)
- Tempo de resposta < 5 segundos para queries simples
- Zero erros de SQL nas tools

✅ **Experiência:**
- Usuário consegue ter conversação natural
- Respostas incluem insights acionáveis
- UI intuitiva

## 11. Risks & Mitigations

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| OpenAI API instável | Baixa | Alto | Implementar retry logic + cache |
| Dados fake não realistas | Média | Médio | Validar com especialista + ajustar gerador |
| Performance ruim em queries | Baixa | Médio | Indexar colunas + otimizar queries |
| Agent confuso com perguntas ambíguas | Média | Médio | Prompt engineering + exemplos |
| Custos de API elevados | Baixa | Baixo | Usar gpt-4o-mini + limitar histórico |

## 12. Cost Estimation

### OpenAI API Costs (GPT-4o-mini)

**Pricing:**
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens

**Estimativa POC (100 queries):**
- Avg input: 1000 tokens/query
- Avg output: 500 tokens/query
- Total: (100k * 0.15) + (50k * 0.60) = $0.015 + $0.03 = **~$0.05**

**Custo POC total:** < $1 USD

## 13. Future Enhancements

**Post-POC:**
- [ ] Multi-user support
- [ ] Export dashboards to PDF
- [ ] Scheduled alerts (email/Slack)
- [ ] Integration with real ERP APIs
- [ ] Mobile app
- [ ] RAG for historical insights
- [ ] Fine-tuned model for domain

## 14. References

- [LangChain Agents Documentation](https://python.langchain.com/docs/modules/agents/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

## 15. Approval

**Stakeholders:**
- [ ] Development Team
- [ ] Product Owner
- [ ] Technical Lead

**Next Steps:**
1. Aprovação da RFC
2. Setup inicial do ambiente (< 5 minutos com SQLite!)
3. Kick-off Phase 1

---

## 16. Summary of Changes (SQLite Adoption)

**Principais Mudanças na Stack:**

| Componente | Antes | Depois | Benefício |
|------------|-------|--------|-----------|
| Database | PostgreSQL + Docker | SQLite (arquivo) | -2h setup, zero config |
| API Layer | FastAPI | Removido | Arquitetura simplificada |
| LLM | GPT-4 | GPT-4o-mini | -60% custo |
| Setup Time | ~4-6 horas | ~5 minutos | ⚡ 48x mais rápido |
| Dependencies | 8 packages | 6 packages | Menos dependências |
| Infra Needed | Docker Desktop | Nenhuma | Zero overhead |
| Timeline | 10 dias | 6-7 dias | -30% tempo |

**Trade-offs Aceitáveis para POC:**
- ✅ SQLite suporta 100% dos casos de uso definidos
- ✅ Performance idêntica para volume da POC (< 1000 vendas)
- ✅ Migração para PostgreSQL é trivial (1 linha de código)
- ✅ Foco 100% no agente de IA, não em DevOps

**Resultado:** POC mais rápida, simples e barata, sem perder funcionalidade! 🚀

---

## 17. Recent Enhancements (2026-02-08)

### 17.1 Nova Ferramenta: Detecção de Risco Iminente de Ruptura

**Ferramenta:** `detect_imminent_stockout_risk()` (tools/stockout_risk.py)

**Motivação:**
A ferramenta `detect_stock_rupture()` existente detecta apenas produtos que **JÁ zeraram** o estoque (reativo). Precisávamos de uma abordagem **PREVENTIVA** que identifique produtos em risco **ANTES** de ficarem sem estoque, considerando também se existem pedidos de compra pendentes.

**Funcionalidades:**

1. **Análise Preventiva:**
   - Identifica produtos com estoque > 0 que vão zerar em breve
   - Calcula dias até ruptura baseado em demanda média
   - Alerta quando `days_until_stockout < threshold` (default: 7 dias)

2. **Verificação de Pedidos Pendentes:**
   - Busca todos os pedidos com status='PENDING' para cada produto
   - Calcula quantidade total pendente
   - Determina se pedidos são suficientes para cobrir demanda forecast
   - Detecta pedidos atrasados (> 7 dias esperando)

3. **Análise de Gap:**
   - Calcula: `gap = demanda_forecast - (estoque_atual + pedidos_pending)`
   - Indica exatamente quanto ainda precisa comprar

4. **Classificação de Risco:**
   - **CRITICAL:** Vai zerar em ≤ 3 dias E sem pedidos suficientes
   - **HIGH:** Vai zerar em ≤ 3 dias OU pedidos atrasados E insuficientes
   - **MEDIUM:** Pedidos insuficientes mas tempo > 3 dias
   - **LOW:** Pedidos pendentes cobrem demanda

5. **Recomendações Específicas:**
   - Sem pedidos: "URGENT: Create purchase order for X units"
   - Pedidos insuficientes: "ORDER MORE: Need X additional units"
   - Pedidos atrasados: "FOLLOW UP: Contact supplier (Y days pending)"
   - Pedidos suficientes: "MONITOR: Pending orders should cover demand"

**Exemplo de Uso:**

```python
# Encontrar produtos em risco nos próximos 7 dias
at_risk = detect_imminent_stockout_risk(
    days_forecast=30,      # Projetar demanda para 30 dias
    days_history=90,       # Usar 90 dias de histórico
    min_days_threshold=7   # Alertar se vai zerar em 7 dias
)

# Produtos críticos sem pedidos
for product in at_risk:
    if product['risk_level'] == 'CRITICAL':
        print(f"🔴 {product['name']}")
        print(f"   Estoque: {product['current_stock']} unidades")
        print(f"   Dias até ruptura: {product['days_until_stockout']:.1f}")
        print(f"   Pedidos pendentes: {product['pending_orders']['total_quantity']}")
        print(f"   Precisa comprar: {product['gap_quantity']} unidades")
        print(f"   Ação: {product['recommendation']}")
```

**Perguntas que podem ser respondidas:**
- "Quais produtos vão ficar sem estoque nos próximos 7 dias?"
- "Mostre produtos que precisam de reposição urgente"
- "Há produtos em risco de ruptura sem pedido de compra?"
- "Quais produtos têm pedidos pendentes insuficientes?"
- "Me alerte sobre pedidos de compra atrasados"

---

### 17.2 Melhoria: suggest_purchase_order()

**Arquivo:** tools/purchase_suggestions.py

**O que mudou:**

Adicionado campo `pending_orders` no retorno, contendo:

```python
'pending_orders': {
    'has_pending': bool,           # Tem pedido pendente?
    'total_quantity': float,        # Quantidade total pendente
    'order_count': int,             # Número de pedidos
    'is_sufficient': bool           # Pedidos cobrem demanda forecast?
}
```

**Benefícios:**

1. **Evita Duplicação:** Antes sugeria comprar produtos que já tinham pedidos pendentes
2. **Priorização Inteligente:** Ajusta prioridade considerando pedidos existentes
3. **Informação Completa:** Usuário vê situação completa (estoque + pedidos)

**Exemplo de Impacto:**

```python
# ANTES:
{
  'name': 'Produto X',
  'suggested_quantity': 100,
  'priority': 'HIGH'
}

# DEPOIS:
{
  'name': 'Produto X',
  'suggested_quantity': 100,
  'priority': 'LOW',  # Ajustado!
  'pending_orders': {
    'has_pending': True,
    'total_quantity': 150,
    'order_count': 1,
    'is_sufficient': True  # Já tem pedido suficiente!
  }
}
```

---

### 17.3 Melhoria: get_stock_alerts()

**Arquivo:** tools/alerts.py

**O que mudou:**

1. **Nova Seção de Alertas:** "Imminent Stockout" (preventivo)
   - Usa `detect_imminent_stockout_risk()` internamente
   - Prioriza os 5 produtos mais críticos
   - Aparece ANTES dos alertas de ruptura (já zerado)

2. **Reordenação de Alertas:**
   - 1️⃣ Imminent Stockout (PREVENTIVO) ← **NOVO**
   - 2️⃣ Stock Rupture (REATIVO)
   - 3️⃣ Slow Moving Stock
   - 4️⃣ Stock Losses
   - 5️⃣ Low Stock High Demand
   - 6️⃣ Purchase Recommendations
   - 7️⃣ Explicit Losses

3. **Alertas Mais Informativos:**

```python
# Exemplo de alerta gerado:
{
  'type': 'IMMINENT_STOCKOUT',
  'severity': 'CRITICAL',
  'product_name': 'Produto X',
  'message': '🔴 Produto X - Will run out in 2.5 days',
  'detail': 'Pending orders: Insufficient. Gap: 85 units',
  'action': 'URGENT: Create purchase order for 85 units immediately'
}
```

**Benefício Principal:**

Dashboard agora mostra problemas **ANTES** de acontecerem, não apenas depois!

---

### 17.4 Nova Ferramenta Auxiliar: get_pending_order_summary()

**Arquivo:** tools/stockout_risk.py

**Descrição:**
Ferramenta auxiliar para listar e analisar todos os pedidos de compra pendentes.

**Funcionalidades:**
- Lista todos os pedidos com status='PENDING'
- Identifica pedidos atrasados (> 7 dias)
- Pode filtrar por produto específico
- Mostra valor total e produtos de cada pedido

**Exemplo de Uso:**

```python
# Ver todos os pedidos pendentes
pending = get_pending_order_summary()

# Encontrar atrasados
delayed = [p for p in pending if p['is_delayed']]
print(f"⚠️ {len(delayed)} pedidos atrasados!")

# Filtrar por produto
product_orders = get_pending_order_summary(product_id=123)
```

---

### 17.5 Comparação: Ruptura vs Risco Iminente

| Aspecto | detect_stock_rupture() | detect_imminent_stockout_risk() |
|---------|------------------------|--------------------------------|
| **Tipo** | REATIVO | PREVENTIVO |
| **Estoque** | = 0 (zerado) | > 0 (ainda tem) |
| **Quando alerta** | Depois de zerar | Antes de zerar |
| **Verifica PO** | ❌ Não | ✅ Sim |
| **Calcula gap** | ❌ Não | ✅ Sim |
| **Detecta atrasos** | ❌ Não | ✅ Sim |
| **Use quando** | Calcular prejuízo | Evitar prejuízo |
| **Métrica chave** | Receita perdida | Dias até ruptura |
| **Ação** | Comprar URGENTE | Planejar compra |

**Ambas são necessárias:**
- `detect_stock_rupture()`: Para agir em crises (já zerou)
- `detect_imminent_stockout_risk()`: Para prevenir crises (vai zerar)

---

### 17.6 Impacto nos Casos de Uso

**Novos casos de uso habilitados:**

1. ✅ "Me mostre produtos que vão ficar sem estoque mas não têm pedido de compra"
2. ✅ "Quais produtos têm pedidos pendentes insuficientes?"
3. ✅ "Há algum pedido de compra atrasado?"
4. ✅ "Qual o risco de ruptura considerando os pedidos que já fiz?"
5. ✅ "Quanto ainda preciso comprar além dos pedidos pendentes?"

**Perguntas do agente melhoradas:**

- Dashboard proativo com alertas preventivos
- Sugestões de compra mais inteligentes (considera pedidos)
- Visibilidade completa da situação (estoque + pedidos + demanda)

---

### 17.7 Testes Recomendados

**Cenários para validar:**

1. **Produto sem pedido próximo de zerar:**
   - Estoque: 10 unidades
   - Demanda: 5 un/dia
   - Pedidos: NENHUM
   - ✅ Deve alertar: CRITICAL, 2 dias até ruptura

2. **Produto com pedido insuficiente:**
   - Estoque: 10 unidades
   - Demanda: 5 un/dia (150 em 30 dias)
   - Pedidos: 50 unidades
   - ✅ Deve alertar: Pedido insuficiente, gap de 90 unidades

3. **Produto com pedido atrasado:**
   - Estoque: 5 unidades
   - Pedidos: 100 unidades (10 dias atrás, ainda PENDING)
   - ✅ Deve alertar: Pedido atrasado, contatar fornecedor

4. **Produto com pedido suficiente:**
   - Estoque: 20 unidades
   - Demanda: 5 un/dia (150 em 30 dias)
   - Pedidos: 150 unidades
   - ✅ Deve mostrar: LOW risk, monitorar

---

### 17.8 Arquivos Modificados

```
📝 Arquivos NOVOS:
   - tools/stockout_risk.py (289 linhas)

📝 Arquivos MODIFICADOS:
   - tools/purchase_suggestions.py (+20 linhas)
   - tools/alerts.py (+15 linhas)
   - RFC-POC-STOCK-AI-AGENT.md (+400 linhas de documentação)

✅ Nenhuma quebra de compatibilidade
✅ Todas as ferramentas existentes continuam funcionando
✅ Apenas adições e melhorias
```

---

**Questions? Contact:** [your-email]
