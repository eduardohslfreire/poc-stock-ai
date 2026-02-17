#!/usr/bin/env python3
"""
Check if deployment configuration is ready for Streamlit Cloud.

Usage:
    python check_deploy_ready.py
"""

import os
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> tuple[str, bool]:
    """Check if a file exists."""
    return description, Path(file_path).exists()


def check_file_content(file_path: str, search_text: str, description: str) -> tuple[str, bool]:
    """Check if file contains specific text."""
    path = Path(file_path)
    if not path.exists():
        return description, False
    
    content = path.read_text()
    return description, search_text in content


def main():
    """Run all deployment readiness checks."""
    print("\n" + "=" * 70)
    print("🔍 VERIFICANDO CONFIGURAÇÃO DE DEPLOY PARA STREAMLIT CLOUD")
    print("=" * 70 + "\n")
    
    checks = []
    
    # === Core Files ===
    print("📁 Arquivos Principais")
    checks.append(check_file_exists("requirements.txt", "requirements.txt existe"))
    checks.append(check_file_exists("app/streamlit_app.py", "app/streamlit_app.py existe"))
    checks.append(check_file_exists("README.md", "README.md existe"))
    print()
    
    # === Streamlit Configuration ===
    print("⚙️ Configuração Streamlit")
    checks.append(check_file_exists(".streamlit/config.toml", ".streamlit/config.toml existe"))
    checks.append(check_file_exists(".streamlit/secrets.toml.example", ".streamlit/secrets.toml.example existe"))
    checks.append(check_file_exists(".streamlit/secrets.toml", ".streamlit/secrets.toml configurado (local)"))
    print()
    
    # === Database Files ===
    print("🗄️ Arquivos de Banco de Dados")
    checks.append(check_file_exists("database/auto_seed.py", "database/auto_seed.py existe"))
    checks.append(check_file_exists("database/schema.py", "database/schema.py existe"))
    checks.append(check_file_exists("database/seed_data.py", "database/seed_data.py existe"))
    print()
    
    # === Security Checks ===
    print("🔒 Segurança")
    checks.append(check_file_exists(".gitignore", ".gitignore existe"))
    checks.append(check_file_content(".gitignore", "secrets.toml", ".gitignore ignora secrets.toml"))
    checks.append(check_file_content(".gitignore", ".env", ".gitignore ignora .env"))
    checks.append(check_file_content(".gitignore", "*.db", ".gitignore ignora *.db"))
    print()
    
    # === Documentation ===
    print("📚 Documentação")
    checks.append(check_file_exists("DEPLOY_STREAMLIT.md", "DEPLOY_STREAMLIT.md existe"))
    checks.append(check_file_exists("QUICK_DEPLOY_GUIDE.md", "QUICK_DEPLOY_GUIDE.md existe"))
    checks.append(check_file_exists("DEPLOYMENT_CHANGES.md", "DEPLOYMENT_CHANGES.md existe"))
    print()
    
    # === App Configuration Checks ===
    print("🎯 Verificações no Código")
    checks.append(check_file_content(
        "app/streamlit_app.py",
        "st.secrets",
        "app/streamlit_app.py usa st.secrets"
    ))
    checks.append(check_file_content(
        "app/streamlit_app.py",
        "auto_seed",
        "app/streamlit_app.py chama auto_seed"
    ))
    print()
    
    # === Requirements Check ===
    print("📦 Dependências")
    required_packages = [
        ("streamlit", "streamlit está em requirements.txt"),
        ("langchain", "langchain está em requirements.txt"),
        ("openai", "openai está em requirements.txt"),
        ("sqlalchemy", "sqlalchemy está em requirements.txt"),
        ("faker", "faker está em requirements.txt"),
    ]
    
    for package, description in required_packages:
        checks.append(check_file_content("requirements.txt", package, description))
    print()
    
    # === Print Results ===
    print("=" * 70)
    print("RESULTADOS")
    print("=" * 70 + "\n")
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    # === Summary ===
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    percentage = (passed / total) * 100
    
    print("\n" + "=" * 70)
    print(f"📊 RESUMO: {passed}/{total} checks passaram ({percentage:.1f}%)")
    print("=" * 70 + "\n")
    
    if passed == total:
        print("🎉 PROJETO PRONTO PARA DEPLOY!")
        print("\n📋 Próximos passos:")
        print("   1. Commit e push para GitHub")
        print("   2. Crie app no Streamlit Cloud")
        print("   3. Configure secrets (OpenAI API Key)")
        print("   4. Deploy!")
        print("\n📖 Consulte: QUICK_DEPLOY_GUIDE.md")
    elif percentage >= 80:
        print("⚠️ QUASE PRONTO - Alguns itens precisam de atenção.")
        print("\n💡 Dicas:")
        failed_checks = [name for name, result in checks if not result]
        for check in failed_checks[:5]:  # Show first 5 failed checks
            print(f"   - {check}")
        if len(failed_checks) > 5:
            print(f"   ... e mais {len(failed_checks) - 5} itens")
        print("\n📖 Consulte: DEPLOY_STREAMLIT.md")
    else:
        print("❌ VÁRIOS ITENS PRECISAM DE ATENÇÃO")
        print("\n📖 Por favor, consulte: DEPLOY_STREAMLIT.md")
    
    print()
    
    # Return exit code
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
