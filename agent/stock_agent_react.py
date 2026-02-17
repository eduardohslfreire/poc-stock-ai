"""
Alternative Stock Agent using ReAct pattern.

This is an example showing how to use ReAct instead of Function Calling.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

if TYPE_CHECKING:
    from langchain.agents import AgentExecutor

from agent.prompts import SYSTEM_PROMPT
from agent.stock_agent import create_tools  # Reuse the same tools


def create_stock_agent_react() -> AgentExecutor:
    """
    Create Stock Agent using ReAct pattern instead of Function Calling.
    
    Returns:
        Configured AgentExecutor with ReAct agent
    """
    # Lazy imports
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain.memory import ConversationBufferMemory
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")
    
    model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.1,
        api_key=api_key
    )
    
    # Create tools
    tools = create_tools()
    
    # ReAct prompt template
    # Uses special format: Thought → Action → Action Input → Observation
    react_prompt = PromptTemplate.from_template("""
{system_prompt}

Você tem acesso às seguintes ferramentas:

{tools}

Use o seguinte formato:

Question: a pergunta que você deve responder
Thought: você deve sempre pensar sobre o que fazer
Action: a ação a tomar, deve ser uma das [{tool_names}]
Action Input: a entrada para a ação
Observation: o resultado da ação
... (esse Thought/Action/Action Input/Observation pode se repetir N vezes)
Thought: Agora sei a resposta final
Final Answer: a resposta final para a pergunta original

Comece!

Question: {input}
Thought: {agent_scratchpad}
""")
    
    # Inject system prompt
    react_prompt = react_prompt.partial(system_prompt=SYSTEM_PROMPT)
    
    # Create ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=react_prompt
    )
    
    # Create memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,  # Show ReAct steps
        max_iterations=5,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )
    
    return agent_executor
