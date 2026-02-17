"""
Stock Management AI Agent using LangChain.

This module creates and configures the AI agent with all available tools.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imported lazily at runtime to reduce import-time issues in some environments.
    from langchain.agents import AgentExecutor  # pragma: no cover

from agent.prompts import SYSTEM_PROMPT
from tools.stock_analysis import detect_stock_rupture, analyze_slow_moving_stock
from tools.stockout_risk import detect_imminent_stockout_risk, get_pending_order_summary  # NEW - 2026-02-08
from tools.supplier_analysis import analyze_supplier_performance
from tools.loss_detection import detect_stock_losses, get_explicit_losses
from tools.purchase_suggestions import suggest_purchase_order, group_suggestions_by_supplier
from tools.sales_analysis import get_top_selling_products, get_sales_by_category
from tools.turnover_analysis import analyze_purchase_to_sale_time, get_inventory_age_distribution
from tools.alerts import get_stock_alerts
from tools.availability_analysis import detect_availability_issues
from tools.operational_availability import detect_operational_availability_issues  # NEW - 2026-02-08
from tools.profitability_analysis import calculate_profitability_analysis, get_profitability_summary
from tools.abc_analysis import get_abc_analysis


"""
LangChain Tool wrapper functions.

LangChain `Tool` (non-structured) calls the tool function with a single positional
argument (the tool input as a string). Our analytics functions often don't need
that input, but they must accept it to avoid errors like:
  get_stock_alerts() takes 0 positional arguments but 1 was given
"""


def _detect_stock_rupture_wrapper(tool_input: str = ""):
    _ = tool_input
    return detect_stock_rupture(days_lookback=30)


def _analyze_slow_moving_wrapper(tool_input: str = ""):
    _ = tool_input
    return analyze_slow_moving_stock(days_threshold=60)


def _analyze_supplier_performance_wrapper(tool_input: str = ""):
    _ = tool_input
    return analyze_supplier_performance(metric="turnover_rate", days_period=90)


def _detect_losses_wrapper(tool_input: str = ""):
    _ = tool_input
    return detect_stock_losses(tolerance_percentage=5.0)


def _suggest_purchase_wrapper(tool_input: str = ""):
    _ = tool_input
    return suggest_purchase_order(days_forecast=30, days_history=90)


def _get_top_selling_wrapper(tool_input: str = ""):
    _ = tool_input
    return get_top_selling_products(period="month", metric="revenue", limit=10)


def _analyze_purchase_to_sale_time_wrapper(tool_input: str = ""):
    _ = tool_input
    return analyze_purchase_to_sale_time(days_period=90, min_purchases=1)


def _get_stock_alerts_wrapper(tool_input: str = ""):
    _ = tool_input
    return get_stock_alerts()


def _detect_availability_wrapper(tool_input: str = ""):
    _ = tool_input
    return detect_availability_issues(days_period=90)


def _calculate_profitability_wrapper(tool_input: str = ""):
    _ = tool_input
    return calculate_profitability_analysis(period="month", min_sales=1)


def _get_abc_wrapper(tool_input: str = ""):
    _ = tool_input
    return get_abc_analysis(period="month", metric="revenue")


def _detect_imminent_stockout_wrapper(tool_input: str = ""):
    """NEW - 2026-02-08: Preventive stockout risk detection."""
    _ = tool_input
    return detect_imminent_stockout_risk(days_forecast=30, days_history=90, min_days_threshold=7)


def _get_pending_orders_wrapper(tool_input: str = ""):
    """NEW - 2026-02-08: List pending purchase orders."""
    _ = tool_input
    return get_pending_order_summary(product_id=None)


def _detect_operational_availability_wrapper(tool_input: str = ""):
    """NEW - 2026-02-08: Detect operational availability issues."""
    _ = tool_input
    return detect_operational_availability_issues(recent_period_days=14, historical_period_days=60)


def create_tools() -> List[Tool]:
    """
    Create and configure all tools for the AI agent.
    
    Returns:
        List of LangChain Tool objects
    """
    tools = [
        # Tool #1: Imminent Stockout Risk Detection (NEW - PREVENTIVE)
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
        ),
        
        # Tool #2: Stock Rupture Detection (REACTIVE)
        Tool(
            name="detect_stock_rupture",
            func=_detect_stock_rupture_wrapper,
            description="""FERRAMENTA REATIVA: Identifica produtos que JÁ estão com estoque zero mas tiveram vendas recentes.
            Use quando o usuário perguntar sobre:
            - Produtos que zeraram
            - Produtos sem estoque (já zerado)
            - Rupturas que já aconteceram
            - Receita perdida (já perdida)
            - Produtos em falta agora
            Retorna lista de produtos críticos que já zeraram com estimativa de perda."""
        ),
        
        # Tool #3: Slow Moving Stock
        Tool(
            name="analyze_slow_moving_stock",
            func=_analyze_slow_moving_wrapper,
            description="""Analisa produtos parados no estoque há muito tempo.
            Use quando o usuário perguntar sobre:
            - Produtos parados
            - Estoque encalhado
            - Capital parado
            - Produtos sem giro
            Retorna produtos com dias sem venda e capital imobilizado."""
        ),
        
        # Tool #4: Supplier Performance
        Tool(
            name="analyze_supplier_performance",
            func=_analyze_supplier_performance_wrapper,
            description="""Analisa performance dos fornecedores baseado em giro e vendas.
            Use quando o usuário perguntar sobre:
            - Melhores fornecedores
            - Performance de fornecedores
            - Qual fornecedor comprar
            Retorna ranking com score de performance."""
        ),
        
        # Tool #5: Stock Losses
        Tool(
            name="detect_stock_losses",
            func=_detect_losses_wrapper,
            description="""Detecta perdas e discrepâncias no estoque.
            Use quando o usuário perguntar sobre:
            - Perdas
            - Discrepâncias
            - Diferenças de inventário
            - Produtos com problema
            Retorna produtos com possíveis perdas não registradas."""
        ),
        
        # Tool #6: Purchase Suggestions
        Tool(
            name="suggest_purchase_order",
            func=_suggest_purchase_wrapper,
            description="""Sugere pedidos de compra baseado em histórico de vendas e estoque atual.
            Use quando o usuário perguntar sobre:
            - O que comprar
            - Sugestões de compra
            - Reposição de estoque
            - Pedidos necessários
            Retorna lista priorizada de compras com quantidades sugeridas."""
        ),
        
        # Tool #7: Top Selling Products
        Tool(
            name="get_top_selling_products",
            func=_get_top_selling_wrapper,
            description="""Lista produtos mais vendidos por diferentes métricas.
            Use quando o usuário perguntar sobre:
            - Produtos mais vendidos
            - Top vendas
            - Mais populares
            - Campeões de venda
            Retorna ranking de produtos com valores e quantidades."""
        ),
        
        # Tool #8: Purchase to Sale Time
        Tool(
            name="analyze_purchase_to_sale_time",
            func=_analyze_purchase_to_sale_time_wrapper,
            description="""Analisa tempo médio desde compra até primeira venda (giro de estoque).
            Use quando o usuário perguntar sobre:
            - Giro de estoque
            - Tempo no estoque
            - Rotatividade
            - Velocidade de venda
            Retorna produtos mais rápidos e mais lentos."""
        ),
        
        # Tool #9: Stock Alerts Dashboard
        Tool(
            name="get_stock_alerts",
            func=_get_stock_alerts_wrapper,
            description="""Dashboard completo com saúde geral do estoque e todos os alertas.
            Use quando o usuário perguntar sobre:
            - Como está o estoque
            - Visão geral
            - Status do estoque
            - Resumo
            - Dashboard
            Retorna análise completa com alertas críticos, avisos e recomendações."""
        ),
        
        # Tool #10: Availability Issues
        Tool(
            name="detect_availability_issues",
            func=_detect_availability_wrapper,
            description="""Detecta produtos com problemas recorrentes de disponibilidade.
            Use quando o usuário perguntar sobre:
            - Problemas de disponibilidade
            - Produtos que faltam frequentemente
            - Taxa de disponibilidade
            - Stockouts recorrentes
            Retorna produtos com baixa disponibilidade e frequência de rupturas."""
        ),
        
        # Tool #11: Profitability Analysis
        Tool(
            name="calculate_profitability_analysis",
            func=_calculate_profitability_wrapper,
            description="""Analisa lucratividade, margens e ROI dos produtos.
            Use quando o usuário perguntar sobre:
            - Lucratividade
            - Margem de lucro
            - Produtos mais lucrativos
            - ROI
            - Rentabilidade
            Retorna análise financeira detalhada por produto."""
        ),
        
        # Tool #11: ABC Analysis
        Tool(
            name="get_abc_analysis",
            func=_get_abc_wrapper,
            description="""Classificação ABC (Curva de Pareto 80/20) dos produtos.
            Use quando o usuário perguntar sobre:
            - Classificação ABC
            - Curva de Pareto
            - Produtos mais importantes
            - Priorização
            Retorna produtos classificados em A (80%), B (15%), C (5%) com estratégias."""
        ),
        
        # Tool #12: Pending Purchase Orders (NEW)
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
        ),
        
        # Tool #13: Operational Availability Issues (NEW)
        Tool(
            name="detect_operational_availability_issues",
            func=_detect_operational_availability_wrapper,
            description="""Detecta produtos com estoque mas que pararam de vender (problema operacional).
            Use quando o usuário perguntar sobre:
            - Produtos com estoque mas sem vendas
            - Produtos que pararam de vender
            - Produtos no depósito não repostos
            - Produtos não disponíveis para venda (apesar de ter estoque)
            - Queda súbita nas vendas com estoque disponível
            - Produtos recebidos mas não vendendo
            Identifica problemas como: produto preso no depósito, não reposto na prateleira,
            não disponível online, problema de exposição."""
        )
    ]
    
    return tools


def create_stock_agent() -> AgentExecutor:
    """
    Create and configure the Stock Management AI Agent.
    
    Returns:
        Configured AgentExecutor ready to use
    
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    # Lazy imports to avoid import-time crashes in some environments
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.memory import ConversationBufferMemory

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    
    # Get model from env or use default
    model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.1,  # Low temperature for consistent, factual responses
        api_key=api_key
    )
    
    # Create tools
    tools = create_tools()
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create agent
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create memory for conversation history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,  # Show reasoning steps
        max_iterations=5,  # Prevent infinite loops
        early_stopping_method="generate",
        handle_parsing_errors=True
    )
    
    return agent_executor


def query_agent(agent: AgentExecutor, question: str) -> str:
    """
    Query the agent with a question.
    
    Args:
        agent: The configured AgentExecutor
        question: User's question
    
    Returns:
        Agent's response as string
    """
    try:
        response = agent.invoke({"input": question})
        return response.get("output", "Desculpe, não consegui gerar uma resposta.")
    except Exception as e:
        error_msg = f"Erro ao processar pergunta: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
