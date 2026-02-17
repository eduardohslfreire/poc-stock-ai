"""
Streamlit UI for Stock Management AI Agent.

This is the main user interface for interacting with the AI agent.
"""

import streamlit as st
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.stock_agent import create_stock_agent, query_agent
from agent.prompts import WELCOME_MESSAGE, ERROR_MESSAGE

# Page configuration
st.set_page_config(
    page_title="Stock AI Assistant",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure environment variables
# Priority: Streamlit secrets > .env file > environment variables
if "openai" in st.secrets:
    # Running on Streamlit Cloud - use secrets
    os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]
    os.environ["OPENAI_MODEL"] = st.secrets["openai"].get("model", "gpt-4o-mini")
else:
    # Running locally - use .env file
    load_dotenv()

# Auto-seed database on first run (for deployment)
@st.cache_resource
def ensure_database_ready():
    """Ensure database is created and populated."""
    try:
        from database.auto_seed import auto_seed_if_needed
        auto_seed_if_needed(force=False, verbose=False)
        return True
    except Exception as e:
        st.error(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

# Initialize database
if not ensure_database_ready():
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .example-question {
        background-color: #fff9c4;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
        cursor: pointer;
        border: 1px solid #fbc02d;
    }
    .example-question:hover {
        background-color: #fff59d;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .status-ok {
        color: #4caf50;
    }
    .status-warning {
        color: #ff9800;
    }
    .status-error {
        color: #f44336;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False


def initialize_agent():
    """Initialize the AI agent with error handling."""
    try:
        with st.spinner("🤖 Inicializando agente de IA..."):
            st.session_state.agent = create_stock_agent()
            st.session_state.agent_initialized = True
            return True
    except ValueError as e:
        msg = str(e)
        st.error(f"❌ Erro de configuração: {msg}")
        # ValueError is also used by pydantic ValidationError; keep hints specific.
        if "OPENAI_API_KEY" in msg:
            st.info("💡 **Desenvolvimento local:** Configure a variável OPENAI_API_KEY no arquivo `.env`")
            st.info("💡 **Streamlit Cloud:** Configure em Settings → Secrets")
        elif "unexpected keyword argument 'proxies'" in msg:
            st.info("💡 Dica: pin de httpx para 0.27.x (ex: httpx==0.27.2) resolve esse erro.")
        return False
    except Exception as e:
        st.error(f"❌ Erro ao inicializar agente: {str(e)}")
        return False


def display_sidebar():
    """Display sidebar with info and example questions."""
    with st.sidebar:
        st.markdown("### 📊 Stock AI Assistant")
        st.markdown("---")
        
        # Status indicator
        if st.session_state.agent_initialized:
            st.success("✅ Agente inicializado")
        else:
            st.warning("⚠️ Agente não inicializado")
        
        # Model info
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        st.info(f"🤖 Modelo: {model}")
        
        st.markdown("---")
        st.markdown("### 💡 Exemplos de Perguntas")
        
        example_questions = [
            "Como está meu estoque hoje?",
            "Quais produtos devo comprar urgente?",
            "Mostre os 10 produtos mais vendidos",
            "Quais produtos estão parados?",
            "Analise a lucratividade",
            "Classifique meus produtos (ABC)",
            "Qual fornecedor é melhor?",
            "Identifique perdas no estoque",
            "Mostre produtos com ruptura",
            "Analise problemas de disponibilidade"
        ]
        
        for question in example_questions:
            if st.button(f"💬 {question}", key=f"ex_{question}", use_container_width=True):
                st.session_state.current_question = question
        
        st.markdown("---")
        st.markdown("### 🔧 Ferramentas Disponíveis")
        st.markdown("""
        - 📦 Análise de Estoque
        - 💰 Análise Financeira
        - 🛒 Sugestões de Compra
        - 👥 Performance Fornecedores
        - 📈 Dashboard Completo
        - 🏷️ Classificação ABC
        - 🔄 Análise de Giro
        - ⚠️ Alertas e Problemas
        """)
        
        st.markdown("---")
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.agent.memory.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ Informações")
        st.caption(f"Versão: 1.0.0")
        st.caption(f"Data: {datetime.now().strftime('%d/%m/%Y')}")


def display_chat_message(role: str, content: str):
    """Display a chat message with proper styling."""
    if role == "user":
        st.markdown(
            f'<div class="chat-message user-message">👤 <strong>Você:</strong><br>{content}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-message assistant-message">🤖 <strong>Assistente:</strong><br>{content}</div>',
            unsafe_allow_html=True
        )


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📦 Stock AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Seu assistente inteligente de gestão de estoque</p>", unsafe_allow_html=True)
    
    # Display sidebar
    display_sidebar()
    
    # Initialize agent if not done yet
    if not st.session_state.agent_initialized:
        if not initialize_agent():
            st.stop()
    
    # Display welcome message if no conversation yet
    if len(st.session_state.messages) == 0:
        st.info(WELCOME_MESSAGE)
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])
    
    # Handle example question from sidebar
    if 'current_question' in st.session_state:
        question = st.session_state.current_question
        del st.session_state.current_question
        
        # Add to messages
        st.session_state.messages.append({"role": "user", "content": question})
        display_chat_message("user", question)
        
        # Get response
        with st.spinner("🤔 Pensando..."):
            try:
                response = query_agent(st.session_state.agent, question)
                st.session_state.messages.append({"role": "assistant", "content": response})
                display_chat_message("assistant", response)
            except Exception as e:
                error_msg = f"❌ Erro: {str(e)}\n\n{ERROR_MESSAGE}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                display_chat_message("assistant", error_msg)
        
        st.rerun()
    
    # Chat input
    question = st.chat_input("Digite sua pergunta sobre o estoque...")
    
    if question:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        display_chat_message("user", question)
        
        # Get agent response
        with st.spinner("🤔 Analisando dados..."):
            try:
                response = query_agent(st.session_state.agent, question)
                st.session_state.messages.append({"role": "assistant", "content": response})
                display_chat_message("assistant", response)
            except Exception as e:
                error_msg = f"❌ Erro: {str(e)}\n\n{ERROR_MESSAGE}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                display_chat_message("assistant", error_msg)
        
        st.rerun()


if __name__ == "__main__":
    main()
