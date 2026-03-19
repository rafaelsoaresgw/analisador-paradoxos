#!/usr/bin/env python3
# teste_completo.py - Testa todos os componentes do Analisador de Paradoxos

import subprocess
import sys
import os
import json
import urllib.request
import urllib.error
import time

# Cores para saída no terminal
VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
RESET = "\033[0m"

def print_ok(msg):
    print(f"{VERDE}✅ {msg}{RESET}")

def print_erro(msg):
    print(f"{VERMELHO}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{AZUL}ℹ️ {msg}{RESET}")

def print_aviso(msg):
    print(f"{AMARELO}⚠️ {msg}{RESET}")

def verificar_dependencias():
    """Verifica se os pacotes necessários estão instalados."""
    print_info("Verificando dependências...")
    pacotes = ["flask", "spacy", "flask_sqlalchemy"]
    for pacote in pacotes:
        try:
            __import__(pacote.replace('-', '_'))
            print_ok(f"Pacote {pacote} instalado.")
        except ImportError:
            print_erro(f"Pacote {pacote} NÃO instalado. Execute: pip install {pacote}")

def verificar_modelos_spacy():
    """Verifica se os modelos do spaCy estão instalados."""
    print_info("Verificando modelos do spaCy...")
    try:
        import spacy
        modelos = ["pt_core_news_sm", "en_core_web_sm"]
        for modelo in modelos:
            try:
                spacy.load(modelo)
                print_ok(f"Modelo {modelo} instalado.")
            except OSError:
                print_erro(f"Modelo {modelo} NÃO instalado. Execute: python -m spacy download {modelo}")
    except ImportError:
        print_erro("spacy não está instalado.")

def verificar_arquivos():
    """Verifica se os arquivos principais existem."""
    print_info("Verificando arquivos do projeto...")
    arquivos = ["app.py", "parser_logico.py", "detector_falacias.py", "motor_inferencia.py", "testes.py", "requirements.txt"]
    for arquivo in arquivos:
        if os.path.isfile(arquivo):
            print_ok(f"Arquivo {arquivo} encontrado.")
        else:
            print_erro(f"Arquivo {arquivo} NÃO encontrado!")

def verificar_banco():
    """Verifica se o banco de dados SQLite foi criado."""
    print_info("Verificando banco de dados...")
    if os.path.isfile("analises.db"):
        print_ok("Banco de dados analises.db encontrado.")
        tamanho = os.path.getsize("analises.db")
        print_info(f"Tamanho do banco: {tamanho} bytes")
    else:
        print_aviso("Banco de dados ainda não foi criado. Ele será gerado na primeira execução.")

def executar_testes_unitarios():
    """Executa os testes unitários (testes.py)."""
    print_info("Executando testes unitários...")
    try:
        resultado = subprocess.run([sys.executable, "testes.py"], capture_output=True, text=True, timeout=30)
        if resultado.returncode == 0:
            print_ok("Testes unitários passaram!")
            # Mostra um resumo
            linhas = resultado.stdout.split('\n')
            for linha in linhas:
                if "OK" in linha or "FAILED" in linha or "Ran" in linha:
                    print(f"   {linha}")
        else:
            print_erro("Testes unitários FALHARAM!")
            print("Saída:")
            print(resultado.stdout)
            print("Erros:")
            print(resultado.stderr)
    except subprocess.TimeoutExpired:
        print_erro("Testes unitários excederam o tempo limite.")
    except Exception as e:
        print_erro(f"Erro ao executar testes: {e}")

def testar_api(endpoint="http://localhost:5000/api/analisar"):
    """Testa a API com algumas requisições de exemplo."""
    print_info("Testando a API (requer servidor rodando em localhost:5000)...")
    
    # Teste 1: Silogismo em português
    payload_pt = {
        "texto": "Todo homem é mortal. Sócrates é homem. Sócrates é mortal.",
        "lang": "pt"
    }
    # Teste 2: Oração relativa em inglês
    payload_en = {
        "texto": "The man who killed the lion fled.",
        "lang": "en"
    }
    
    for i, payload in enumerate([payload_pt, payload_en], 1):
        try:
            dados = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(endpoint, data=dados, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    resposta = json.loads(response.read().decode('utf-8'))
                    print_ok(f"API teste {i} OK (código 200)")
                    print(f"   Estruturas: {len(resposta.get('estruturas', []))} encontradas")
                    print(f"   Falácias: {len(resposta.get('falacias', []))}")
                else:
                    print_erro(f"API teste {i} retornou código {response.getcode()}")
        except urllib.error.URLError as e:
            print_aviso(f"API teste {i} não pôde ser acessada. Certifique-se de que o servidor está rodando em {endpoint}")
            print(f"   Erro: {e}")
            break  # Se o servidor não está rodando, não adianta continuar
        except Exception as e:
            print_erro(f"Erro no teste {i}: {e}")

def main():
    print("="*60)
    print("🧠 TESTE COMPLETO DO ANALISADOR DE PARADOXOS 🧠")
    print("="*60)
    
    verificar_dependencias()
    verificar_modelos_spacy()
    verificar_arquivos()
    verificar_banco()
    executar_testes_unitarios()
    
    # Pergunta se quer testar a API (opcional)
    resp = input("\nDeseja testar a API? (Requer servidor rodando em http://localhost:5000) [s/N]: ").strip().lower()
    if resp == 's':
        testar_api()
    
    print("\n" + "="*60)
    print("✅ Teste concluído!")
    print("="*60)

if __name__ == "__main__":
    main()