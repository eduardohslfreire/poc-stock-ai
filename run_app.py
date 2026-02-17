"""
Quick launcher script for the Stock AI Assistant.

This script makes it easy to run the Streamlit app with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is properly configured."""
    errors = []
    
    # Check if .env exists
    env_file = Path('.env')
    if not env_file.exists():
        errors.append(
            "⚠️  Arquivo .env não encontrado!\n"
            "   Copie env.example para .env e configure OPENAI_API_KEY:\n"
            "   $ cp env.example .env"
        )
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        errors.append(
            "⚠️  Ambiente virtual não ativado!\n"
            "   Ative o ambiente virtual:\n"
            "   $ source venv/bin/activate"
        )
    
    # Check if database exists
    db_file = Path('stock.db')
    if not db_file.exists():
        errors.append(
            "⚠️  Banco de dados não encontrado!\n"
            "   Execute os scripts de setup:\n"
            "   $ python setup_db.py\n"
            "   $ python database/seed_data.py"
        )
    
    # Check if OPENAI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        errors.append(
            "⚠️  OPENAI_API_KEY não configurada!\n"
            "   Configure no arquivo .env:\n"
            "   OPENAI_API_KEY=sk-your-key-here"
        )
    
    if errors:
        print("\n❌ Problemas de configuração detectados:\n")
        for error in errors:
            print(error)
            print()
        
        response = input("Deseja continuar mesmo assim? (s/N): ")
        if response.lower() != 's':
            print("\n👋 Configuração cancelada. Corrija os problemas acima e tente novamente.")
            sys.exit(1)
    else:
        print("✅ Ambiente configurado corretamente!")


def run_streamlit():
    """Run the Streamlit app."""
    print("\n🚀 Iniciando Stock AI Assistant...\n")
    
    try:
        # Run streamlit
        subprocess.run([
            "streamlit", "run",
            "app/streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Aplicação encerrada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro ao executar aplicação: {e}")
        sys.exit(1)


def main():
    """Main function."""
    print("=" * 70)
    print("📦 Stock AI Assistant - Launcher")
    print("=" * 70)
    
    # Check environment
    check_environment()
    
    # Run app
    run_streamlit()


if __name__ == "__main__":
    main()
