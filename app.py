from flask import Flask, render_template, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import spacy
from parser_logico import extrair_estrutura, QuantificadorUniversal, QuantificadorNegacao, Fato, Predicado, Termo
from detector_falacias import DetectorFalacias
from motor_inferencia import MotorInferencia

# Carrega o modelo de português
nlp = spacy.load("pt_core_news_sm")

app = Flask(__name__)

# === CONFIGURAÇÃO DO BANCO DE DADOS ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///analises.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Analise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    num_frases = db.Column(db.Integer)
    num_falacias = db.Column(db.Integer)
    falacias = db.Column(db.Text)   # JSON string
    estruturas = db.Column(db.Text) # JSON string

    def __repr__(self):
        return f'<Analise {self.id} - {self.data}>'

# Cria as tabelas (executar uma vez)
with app.app_context():
    db.create_all()
# =======================================

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analisador de Paradoxos · IA Simbólica</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
            
            :root {
                --bg-primary: #0a0c0f;
                --bg-secondary: #14171c;
                --bg-card: #1e2228;
                --accent: #00ff9d;
                --accent-glow: rgba(0, 255, 157, 0.2);
                --text-primary: #eaeef2;
                --text-secondary: #8b949e;
                --error: #ff5e5e;
                --success: #00ff9d;
                --warning: #ffaa5e;
                --border: #2d3138;
                --gradient: linear-gradient(135deg, #00ff9d 0%, #00b8ff 100%);
            }

            [data-theme="light"] {
                --bg-primary: #f5f5f5;
                --bg-secondary: #ffffff;
                --bg-card: #eeeeee;
                --accent: #00b8ff;
                --accent-glow: rgba(0, 184, 255, 0.2);
                --text-primary: #222222;
                --text-secondary: #555555;
                --error: #d32f2f;
                --success: #388e3c;
                --warning: #f57c00;
                --border: #cccccc;
                --gradient: linear-gradient(135deg, #00b8ff 0%, #00ff9d 100%);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'JetBrains Mono', monospace;
                background: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .header {
                display: flex;
                align-items: center;
                gap: 20px;
                margin-bottom: 40px;
                padding: 20px 0;
                border-bottom: 1px solid var(--border);
            }
            
            .logo {
                font-size: 2.5rem;
                filter: drop-shadow(0 0 20px var(--accent-glow));
            }
            
            .title {
                flex: 1;
            }
            
            .title h1 {
                font-size: 2rem;
                background: var(--gradient);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
                letter-spacing: -0.02em;
            }
            
            .title p {
                color: var(--text-secondary);
                font-size: 0.9rem;
                margin-top: 5px;
            }
            
            .badge {
                background: var(--bg-card);
                border: 1px solid var(--border);
                padding: 8px 16px;
                border-radius: 100px;
                font-size: 0.8rem;
                color: var(--text-secondary);
            }
            
            .badge span {
                color: var(--accent);
                font-weight: 600;
            }
            
            .theme-toggle {
                background: var(--bg-card);
                border: 1px solid var(--border);
                color: var(--text-primary);
                padding: 8px 12px;
                border-radius: 100px;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.2s;
                margin-left: 10px;
            }
            
            .theme-toggle:hover {
                border-color: var(--accent);
                transform: scale(1.05);
            }
            
            .input-section {
                background: var(--bg-secondary);
                border-radius: 24px;
                padding: 30px;
                margin-bottom: 30px;
                border: 1px solid var(--border);
                box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            }
            
            .input-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .input-header label {
                color: var(--text-secondary);
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .input-header .stats {
                display: flex;
                gap: 20px;
            }
            
            .stat-item {
                display: flex;
                align-items: center;
                gap: 8px;
                color: var(--text-secondary);
                font-size: 0.8rem;
            }
            
            .stat-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--accent);
                box-shadow: 0 0 10px var(--accent);
            }
            
            textarea {
                width: 100%;
                height: 150px;
                background: var(--bg-primary);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 20px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 1rem;
                color: var(--text-primary);
                resize: vertical;
                margin-bottom: 20px;
                transition: all 0.2s;
            }
            
            textarea:focus {
                outline: none;
                border-color: var(--accent);
                box-shadow: 0 0 30px var(--accent-glow);
            }
            
            .button-group {
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            button {
                padding: 12px 24px;
                border: none;
                border-radius: 12px;
                font-family: 'JetBrains Mono', monospace;
                font-weight: 600;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
                background: var(--bg-primary);
                color: var(--text-primary);
                border: 1px solid var(--border);
            }
            
            button:hover {
                transform: translateY(-2px);
                border-color: var(--accent);
                box-shadow: 0 10px 20px rgba(0,255,157,0.1);
            }
            
            .btn-primary {
                background: var(--gradient);
                border: none;
                color: var(--bg-primary);
                font-weight: 700;
            }
            
            .btn-primary:hover {
                filter: brightness(1.1);
                box-shadow: 0 0 30px var(--accent);
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 40px;
            }
            
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 3px solid var(--border);
                border-top-color: var(--accent);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .results-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-top: 30px;
            }
            
            .card {
                background: var(--bg-secondary);
                border: 1px solid var(--border);
                border-radius: 20px;
                overflow: hidden;
                transition: all 0.2s;
            }
            
            .card:hover {
                border-color: var(--accent);
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0,255,157,0.1);
            }
            
            .card-header {
                padding: 20px;
                background: var(--bg-card);
                border-bottom: 1px solid var(--border);
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .card-header h3 {
                font-size: 1rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: var(--text-secondary);
            }
            
            .card-header .icon {
                font-size: 1.2rem;
            }
            
            .card-content {
                padding: 20px;
                max-height: 400px;
                overflow-y: auto;
            }
            
            .logic-item {
                background: var(--bg-primary);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.9rem;
                border-left: 4px solid var(--accent);
                transition: all 0.2s;
            }
            
            .logic-item:hover {
                border-color: var(--accent);
                transform: translateX(5px);
            }
            
            .fallacy-item {
                background: rgba(255, 94, 94, 0.1);
                border: 1px solid var(--error);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                color: var(--error);
                font-size: 0.9rem;
                border-left: 4px solid var(--error);
                cursor: help;
                transition: all 0.2s;
            }
            
            .fallacy-item:hover {
                background: rgba(255, 94, 94, 0.15);
                transform: translateX(5px);
            }
            
            .conclusion-item {
                background: rgba(0, 255, 157, 0.1);
                border: 1px solid var(--success);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
                color: var(--success);
                font-size: 0.9rem;
                border-left: 4px solid var(--success);
            }
            
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: var(--text-secondary);
                font-size: 0.9rem;
                opacity: 0.6;
            }
            
            .empty-state .emoji {
                font-size: 2rem;
                margin-bottom: 10px;
                opacity: 0.5;
            }
            
            .footer {
                margin-top: 60px;
                padding: 30px 0;
                border-top: 1px solid var(--border);
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: var(--text-secondary);
                font-size: 0.8rem;
            }
            
            .footer-links {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            
            .footer-links a {
                color: var(--text-secondary);
                text-decoration: none;
                transition: color 0.2s;
                cursor: pointer;
            }
            
            .footer-links a:hover {
                color: var(--accent);
            }
            
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--bg-primary);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--border);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--accent);
            }
            
            @media (max-width: 900px) {
                .results-grid {
                    grid-template-columns: 1fr;
                }
                
                .header {
                    flex-direction: column;
                    align-items: flex-start;
                }
                
                .button-group {
                    flex-direction: column;
                }
                
                button {
                    width: 100%;
                    justify-content: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🧠</div>
                <div class="title">
                    <h1>Analisador de Paradoxos</h1>
                    <p>IA Simbólica · Lógica de Primeira Ordem · Detecção de Falácias</p>
                </div>
                <div class="badge">
                    <span>v3.0</span> · Python + Flask + spaCy
                </div>
                <!-- Botão de alternância de tema -->
                <button class="theme-toggle" id="theme-toggle" title="Alternar tema claro/escuro">🌓</button>
            </div>
            
            <div class="input-section">
                <div class="input-header">
                    <label>Entrada</label>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-dot"></div>
                            <span id="charCount">0 caracteres</span>
                        </div>
                    </div>
                </div>
                
                <textarea id="texto" placeholder="Digite um argumento em português...&#10;&#10;Ex: Todo homem é mortal. Sócrates é homem. Sócrates é mortal." oninput="updateCharCount()"></textarea>
                
                <div class="button-group">
                    <button onclick="limpar()">
                        <span>🧹</span> Limpar
                    </button>
                    <button onclick="carregarExemplo()">
                        <span>📋</span> Carregar Exemplo Padrão
                    </button>
                    <button class="btn-primary" onclick="analisar()">
                        <span>⚡</span> Analisar
                    </button>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
                <div style="color: var(--text-secondary)">Processando argumento...</div>
            </div>
            
            <div class="results-grid" id="resultsGrid">
                <div class="card">
                    <div class="card-header">
                        <span class="icon">📚</span>
                        <h3>Estruturas Lógicas</h3>
                    </div>
                    <div class="card-content" id="logicas">
                        <div class="empty-state">
                            <div class="emoji">🔍</div>
                            <div>Nenhum texto analisado</div>
                            <div style="font-size:0.8rem; margin-top:10px">Digite um argumento e clique em Analisar</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="icon">⚠️</span>
                        <h3>Falácias Detectadas</h3>
                    </div>
                    <div class="card-content" id="falacias">
                        <div class="empty-state">
                            <div class="emoji">✨</div>
                            <div>Nenhuma falácia detectada</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="icon">💡</span>
                        <h3>Conclusões Deduzidas</h3>
                    </div>
                    <div class="card-content" id="conclusoes">
                        <div class="empty-state">
                            <div class="emoji">⚙️</div>
                            <div>Nenhuma conclusão deduzida</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ===== ÁREA DE ESTATÍSTICAS ===== -->
            <div class="stats-footer" style="text-align: center; margin-top: 20px; color: var(--text-secondary);">
                <span id="frasesAnalisadas">0 frases analisadas</span> |
                <span id="falaciasEncontradas">0 falácias encontradas</span>
            </div>
            
            <div class="footer">
                <div>🧠 Analisador de Paradoxos · IA Simbólica</div>
                <div class="footer-links">
                    <a onclick="carregarExemploEspecifico('ad')">Ad Hominem</a>
                    <a onclick="carregarExemploEspecifico('ad_circunstancial')">Ad Hominem Circunstancial</a>
                    <a onclick="carregarExemploEspecifico('autoridade')">Apelo à Autoridade</a>
                    <a onclick="carregarExemploEspecifico('forca')">Apelo à Força</a>
                    <a onclick="carregarExemploEspecifico('popularidade')">Apelo à Popularidade</a>
                    <a onclick="carregarExemploEspecifico('natureza')">Apelo à Natureza</a>
                    <a onclick="carregarExemploEspecifico('tradicao')">Apelo à Tradição</a>
                    <a onclick="carregarExemploEspecifico('novidade')">Apelo à Novidade</a>
                    <a onclick="carregarExemploEspecifico('emocao')">Apelo à Emoção</a>
                    <a onclick="carregarExemploEspecifico('ignorancia')">Apelo à Ignorância</a>
                    <a onclick="carregarExemploEspecifico('composicao')">Composição</a>
                    <a onclick="carregarExemploEspecifico('divisao')">Divisão</a>
                    <a onclick="carregarExemploEspecifico('falsa_dicotomia')">Falsa Dicotomia</a>
                    <a onclick="carregarExemploEspecifico('post_hoc')">Post Hoc</a>
                    <a onclick="carregarExemploEspecifico('generalizacao_apressada')">Generalização Apressada</a>
                    <a onclick="carregarExemploEspecifico('generalizacao_temporal')">Generalização Temporal</a>
                    <a onclick="carregarExemploEspecifico('falso_consenso')">Falso Consenso</a>
                    <a onclick="carregarExemploEspecifico('espantalho')">Espantalho</a>
                    <a onclick="carregarExemploEspecifico('circular')">Raciocínio Circular</a>
                    <a onclick="carregarExemploEspecifico('questao_complexa')">Questão Complexa</a>
                    <a onclick="carregarExemploEspecifico('apostador')">Falácia do Apostador</a>
                    <a onclick="carregarExemploEspecifico('piedade')">Apelo à Piedade</a>
                    <a onclick="carregarExemploEspecifico('falso_equilibrio')">Falso Equilíbrio</a>
                    <!-- NOVO LINK PARA ESTATÍSTICAS -->
                    <a href="/stats">📊 Estatísticas</a>
                    <a href="/sobre" style="color: var(--accent);">📘 Sobre</a>
                </div>
            </div>
        </div>
        
        <script>
            // Dicionário com explicações das falácias
            const explicacoes = {
                'Ad hominem': 'Ataca a pessoa em vez do argumento.',
                'Ad hominem circunstancial': 'Ataca por suposto interesse pessoal.',
                'Apelo à autoridade': 'Usa a opinião de uma autoridade como prova, sem considerar seu real conhecimento no assunto.',
                'Apelo à força': 'Usa ameaça em vez de argumento.',
                'Apelo à popularidade': 'Algo é verdade porque muitos acreditam.',
                'Apelo à natureza': 'Assume que algo é bom apenas por ser natural.',
                'Apelo à tradição': 'Algo é certo porque sempre foi feito assim.',
                'Apelo à novidade': 'Assume que algo é melhor apenas por ser novo.',
                'Apelo à emoção': 'Manipula emoções em vez de usar argumentos lógicos.',
                'Apelo à ignorância': 'Afirma que algo é verdadeiro porque não foi provado falso (ou vice-versa).',
                'Falsa dicotomia': 'Apresenta apenas duas opções quando existem mais possibilidades.',
                'Post hoc': 'Assume que, porque um evento aconteceu depois de outro, o primeiro causou o segundo.',
                'Generalização apressada': 'Tira uma conclusão geral a partir de poucos exemplos.',
                'Generalização temporal': 'Usa palavras absolutas (sempre, nunca) sem evidência suficiente.',
                'Falso consenso': 'Assume que todos concordam com uma ideia, sem evidências.',
                'Espantalho': 'Distorce o argumento do oponente para facilitar o ataque.',
                'Raciocínio circular': 'A conclusão está implícita nas premissas.',
                'Composição': 'Assume que o todo tem as mesmas propriedades das partes.',
                'Divisão': 'Assume que as partes têm as mesmas propriedades do todo.',
                'Questão complexa': 'Pergunta que pressupõe algo não provado.',
                'Falácia do apostador': 'Achar que eventos independentes se influenciam.',
                'Apelo à piedade': 'Usar compaixão em vez de lógica.',
                'Falso equilíbrio': 'Dar peso igual a lados com evidências desiguais.'
            };

            function updateCharCount() {
                const text = document.getElementById('texto').value;
                document.getElementById('charCount').innerText = text.length + ' caracteres';
            }
            
            function analisar() {
                const texto = document.getElementById('texto').value;
                if (!texto.trim()) {
                    alert('Digite um texto para analisar!');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                
                fetch('/analisar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ texto: texto })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    // Mostra estruturas lógicas
                    const logicasDiv = document.getElementById('logicas');
                    if (data.estruturas && data.estruturas.length > 0) {
                        let html = '';
                        for (let i = 0; i < data.estruturas.length; i++) {
                            html += '<div class="logic-item">' + data.estruturas[i] + '</div>';
                        }
                        logicasDiv.innerHTML = html;
                    } else {
                        logicasDiv.innerHTML = '<div class="empty-state"><div class="emoji">🔍</div><div>Nenhuma estrutura encontrada</div></div>';
                    }
                    
                    // Mostra falácias com tooltips
                    const falaciasDiv = document.getElementById('falacias');
                    if (data.falacias && data.falacias.length > 0) {
                        let html = '';
                        for (let i = 0; i < data.falacias.length; i++) {
                            const falacia = data.falacias[i];
                            // Tenta extrair o nome da falácia (removendo ícone e pontuação)
                            let nome = falacia.replace(/[⚠️*]/g, '').trim().split(' ')[0];
                            // Ajustes para nomes compostos
                            if (nome === 'Apelo') {
                                if (falacia.includes('força')) nome = 'Apelo à força';
                                else if (falacia.includes('popularidade')) nome = 'Apelo à popularidade';
                                else if (falacia.includes('natureza')) nome = 'Apelo à natureza';
                                else if (falacia.includes('tradição')) nome = 'Apelo à tradição';
                                else if (falacia.includes('novidade')) nome = 'Apelo à novidade';
                                else if (falacia.includes('emoção')) nome = 'Apelo à emoção';
                                else if (falacia.includes('ignorância')) nome = 'Apelo à ignorância';
                                else nome = 'Apelo à autoridade';
                            }
                            else if (nome === 'Ad' && falacia.includes('circunstancial')) nome = 'Ad hominem circunstancial';
                            else if (nome === 'Falsa') nome = 'Falsa dicotomia';
                            else if (nome === 'Post') nome = 'Post hoc';
                            else if (nome === 'Generalização') {
                                if (falacia.includes('temporal')) nome = 'Generalização temporal';
                                else nome = 'Generalização apressada';
                            }
                            else if (nome === 'Falso') nome = 'Falso consenso';
                            else if (nome === 'Raciocínio') nome = 'Raciocínio circular';
                            else if (nome === 'Questão') nome = 'Questão complexa';
                            else if (nome === 'Falácia') nome = 'Falácia do apostador';
                            else if (nome === 'Apelo' && falacia.includes('piedade')) nome = 'Apelo à piedade';
                            else if (nome === 'Falso' && falacia.includes('equilíbrio')) nome = 'Falso equilíbrio';
                            
                            const explicacao = explicacoes[nome] || '';
                            html += `<div class="fallacy-item" title="${explicacao}">${falacia}</div>`;
                        }
                        falaciasDiv.innerHTML = html;
                    } else {
                        falaciasDiv.innerHTML = '<div class="empty-state"><div class="emoji">✨</div><div>Nenhuma falácia detectada</div></div>';
                    }
                    
                    // Mostra conclusões
                    const conclusoesDiv = document.getElementById('conclusoes');
                    if (data.conclusoes && data.conclusoes.length > 0) {
                        let html = '';
                        for (let i = 0; i < data.conclusoes.length; i++) {
                            html += '<div class="conclusion-item">' + data.conclusoes[i] + '</div>';
                        }
                        conclusoesDiv.innerHTML = html;
                    } else {
                        conclusoesDiv.innerHTML = '<div class="empty-state"><div class="emoji">⚙️</div><div>Nenhuma conclusão deduzida</div></div>';
                    }

                    // Atualiza estatísticas
                    document.getElementById('frasesAnalisadas').innerText = data.estruturas.length + ' frases analisadas';
                    document.getElementById('falaciasEncontradas').innerText = data.falacias.length + ' falácias encontradas';
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    alert('Erro: ' + error);
                });
            }
            
            function limpar() {
                document.getElementById('texto').value = '';
                document.getElementById('charCount').innerText = '0 caracteres';
                document.getElementById('logicas').innerHTML = '<div class="empty-state"><div class="emoji">🔍</div><div>Nenhum texto analisado</div><div style="font-size:0.8rem; margin-top:10px">Digite um argumento e clique em Analisar</div></div>';
                document.getElementById('falacias').innerHTML = '<div class="empty-state"><div class="emoji">✨</div><div>Nenhuma falácia detectada</div></div>';
                document.getElementById('conclusoes').innerHTML = '<div class="empty-state"><div class="emoji">⚙️</div><div>Nenhuma conclusão deduzida</div></div>';
                document.getElementById('frasesAnalisadas').innerText = '0 frases analisadas';
                document.getElementById('falaciasEncontradas').innerText = '0 falácias encontradas';
            }
            
            function carregarExemplo() {
                const texto = 'Todo homem é mortal. Sócrates é homem. Sócrates é mortal.';
                document.getElementById('texto').value = texto;
                updateCharCount();
                analisar();
            }
            
            function carregarExemploEspecifico(tipo) {
                const exemplos = {
                    'ad': 'Você é ignorante. Portanto, seu argumento está errado.',
                    'ad_circunstancial': 'Você só defende isso porque ganha dinheiro com isso.',
                    'autoridade': 'Segundo um famoso cientista, isso é verdade.',
                    'forca': 'Se não concordar, vai sofrer as consequências.',
                    'popularidade': 'Todo mundo está fazendo isso, então é certo.',
                    'natureza': 'Este remédio é natural, portanto é melhor.',
                    'tradicao': 'Sempre foi assim, então está certo.',
                    'novidade': 'É a tecnologia mais nova, logo é superior.',
                    'emocao': 'Isso vai causar sofrimento às crianças.',
                    'ignorancia': 'Ninguém provou que Deus não existe, portanto Deus existe.',
                    'composicao': 'As partes são excelentes, portanto o todo é excelente.',
                    'divisao': 'O time é excelente, logo cada jogador é excelente.',
                    'falsa_dicotomia': 'Ou você está comigo, ou contra mim.',
                    'post_hoc': 'Desde que comecei a tomar esse remédio, melhorei. Logo, o remédio funcionou.',
                    'generalizacao_apressada': 'Conheci dois cariocas simpáticos, portanto todos os cariocas são simpáticos.',
                    'generalizacao_temporal': 'Todo mundo sabe que isso é verdade.',
                    'falso_consenso': 'É óbvio que isso é verdade.',
                    'espantalho': 'Você está dizendo que Deus não existe, então você é ateu e não tem moral.',
                    'circular': 'Deus existe porque a Bíblia diz, e a Bíblia é a palavra de Deus.',
                    'questao_complexa': 'Você ainda bate na sua esposa?',
                    'apostador': 'Já perdi 5 vezes, agora a chance de ganhar é maior.',
                    'piedade': 'Pense nas crianças sofrendo, você precisa apoiar esta causa.',
                    'falso_equilibrio': 'Alguns cientistas concordam, outros não – é polêmico.'
                };
                document.getElementById('texto').value = exemplos[tipo] || exemplos['silogismo'];
                updateCharCount();
                analisar();
            }

            // ===== MODO CLARO/ESCURO =====
            const themeToggle = document.getElementById('theme-toggle');
            const currentTheme = localStorage.getItem('theme') || 'dark';
            document.documentElement.setAttribute('data-theme', currentTheme);

            themeToggle.addEventListener('click', () => {
                let theme = document.documentElement.getAttribute('data-theme');
                if (theme === 'dark') {
                    document.documentElement.setAttribute('data-theme', 'light');
                    localStorage.setItem('theme', 'light');
                } else {
                    document.documentElement.setAttribute('data-theme', 'dark');
                    localStorage.setItem('theme', 'dark');
                }
            });
            
            window.onload = function() {
                carregarExemplo();
            };
        </script>
    </body>
    </html>
    '''

@app.route('/sobre')
def sobre():
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analisador de Paradoxos · Sobre</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
            
            :root {
                --bg-primary: #0a0c0f;
                --bg-secondary: #14171c;
                --bg-card: #1e2228;
                --accent: #00ff9d;
                --accent-glow: rgba(0, 255, 157, 0.2);
                --text-primary: #eaeef2;
                --text-secondary: #8b949e;
                --error: #ff5e5e;
                --success: #00ff9d;
                --border: #2d3138;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'JetBrains Mono', monospace;
                background: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            
            .header {
                display: flex;
                align-items: center;
                gap: 20px;
                margin-bottom: 40px;
                padding: 20px 0;
                border-bottom: 1px solid var(--border);
            }
            
            .logo {
                font-size: 2.5rem;
                filter: drop-shadow(0 0 20px var(--accent-glow));
            }
            
            .title h1 {
                font-size: 2rem;
                background: linear-gradient(135deg, #00ff9d 0%, #00b8ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
            }
            
            .back-link {
                margin-bottom: 30px;
            }
            
            .back-link a {
                color: var(--accent);
                text-decoration: none;
                font-size: 1rem;
            }
            
            .back-link a:hover {
                text-decoration: underline;
            }
            
            .fallacy-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .fallacy-card {
                background: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 20px;
                transition: all 0.2s;
            }
            
            .fallacy-card:hover {
                border-color: var(--accent);
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,255,157,0.1);
            }
            
            .fallacy-name {
                color: var(--error);
                font-weight: 700;
                font-size: 1.2rem;
                margin-bottom: 10px;
            }
            
            .fallacy-desc {
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            
            .footer {
                margin-top: 60px;
                padding: 30px 0;
                border-top: 1px solid var(--border);
                text-align: center;
                color: var(--text-secondary);
            }
            
            .footer a {
                color: var(--accent);
                text-decoration: none;
            }
            
            .footer a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🧠</div>
                <div class="title">
                    <h1>Sobre as Falácias</h1>
                </div>
            </div>
            
            <div class="back-link">
                <a href="/">← Voltar ao analisador</a>
            </div>
            
            <p style="margin-bottom: 30px; color: var(--text-secondary);">
                O Analisador de Paradoxos detecta atualmente <strong>mais de 20 tipos de falácias</strong>. 
                Abaixo você encontra uma breve explicação de cada uma.
            </p>
            
            <div class="fallacy-grid">
                <div class="fallacy-card">
                    <div class="fallacy-name">Ad Hominem</div>
                    <div class="fallacy-desc">Ataca a pessoa em vez do argumento. Ex: "Você é ignorante, logo sua opinião não vale."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Ad Hominem Circunstancial</div>
                    <div class="fallacy-desc">Ataca por suposto interesse pessoal. Ex: "Você só defende isso porque ganha dinheiro."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Autoridade</div>
                    <div class="fallacy-desc">Usa a opinião de uma autoridade como prova, sem considerar seu real conhecimento no assunto. Ex: "O padre disse, então é verdade."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Força</div>
                    <div class="fallacy-desc">Usa ameaça em vez de argumento. Ex: "Se não concordar, vai sofrer."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Popularidade</div>
                    <div class="fallacy-desc">Algo é verdade porque muitos acreditam. Ex: "Todo mundo está fazendo, então é certo."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Natureza</div>
                    <div class="fallacy-desc">Assume que algo é bom apenas por ser natural. Ex: "Este remédio é natural, portanto é melhor."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Tradição</div>
                    <div class="fallacy-desc">Algo é certo porque sempre foi feito assim. Ex: "Sempre foi assim, então está certo."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Novidade</div>
                    <div class="fallacy-desc">Assume que algo é melhor apenas por ser novo. Ex: "É a tecnologia mais nova, logo é superior."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Emoção</div>
                    <div class="fallacy-desc">Manipula emoções em vez de usar argumentos lógicos. Ex: "Pense nas crianças sofrendo."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Ignorância</div>
                    <div class="fallacy-desc">Afirma que algo é verdadeiro porque não foi provado falso (ou vice-versa). Ex: "Ninguém provou que Deus não existe, portanto Deus existe."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Falsa Dicotomia</div>
                    <div class="fallacy-desc">Apresenta apenas duas opções quando existem mais possibilidades. Ex: "Ou você está comigo, ou contra mim."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Post Hoc</div>
                    <div class="fallacy-desc">Assume que, porque um evento aconteceu depois de outro, o primeiro causou o segundo. Ex: "Depois que tomei esse remédio, melhorei; logo, o remédio funcionou."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Generalização Apressada</div>
                    <div class="fallacy-desc">Tira uma conclusão geral a partir de poucos exemplos. Ex: "Conheci dois cariocas simpáticos, portanto todos os cariocas são simpáticos."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Generalização Temporal</div>
                    <div class="fallacy-desc">Usa palavras absolutas (sempre, nunca) sem evidência suficiente. Ex: "Todo mundo sabe que isso é verdade."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Falso Consenso</div>
                    <div class="fallacy-desc">Assume que todos concordam com uma ideia, sem evidências. Ex: "É óbvio que isso é certo."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Espantalho</div>
                    <div class="fallacy-desc">Distorce o argumento do oponente para facilitar o ataque. Ex: "Você diz que Deus não existe, então você é ateu e não tem moral."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Raciocínio Circular</div>
                    <div class="fallacy-desc">A conclusão está implícita nas premissas. Ex: "Deus existe porque a Bíblia diz, e a Bíblia é a palavra de Deus."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Composição</div>
                    <div class="fallacy-desc">Assume que o todo tem as mesmas propriedades das partes. Ex: "As partes são excelentes, portanto o todo é excelente."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Divisão</div>
                    <div class="fallacy-desc">Assume que as partes têm as mesmas propriedades do todo. Ex: "O time é excelente, logo cada jogador é excelente."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Questão Complexa</div>
                    <div class="fallacy-desc">Pergunta que pressupõe algo não provado. Ex: "Você ainda bate na sua esposa?"</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Falácia do Apostador</div>
                    <div class="fallacy-desc">Achar que eventos independentes se influenciam. Ex: "Já perdi 5 vezes, agora a chance de ganhar é maior."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Apelo à Piedade</div>
                    <div class="fallacy-desc">Usar compaixão em vez de lógica. Ex: "Pense nas crianças sofrendo, você precisa apoiar."</div>
                </div>
                <div class="fallacy-card">
                    <div class="fallacy-name">Falso Equilíbrio</div>
                    <div class="fallacy-desc">Dar peso igual a lados com evidências desiguais. Ex: "Alguns cientistas concordam, outros não – é polêmico."</div>
                </div>
            </div>
            
            <div class="footer">
                <p>🧠 Analisador de Paradoxos · IA Simbólica · <a href="/">Voltar ao início</a></p>
            </div>
        </div>
    </body>
    </html>
    '''

# ===== ROTA DA API =====
@app.route('/api/analisar', methods=['POST'])
def api_analisar():
    data = request.get_json()
    if not data or 'texto' not in data:
        return jsonify({'erro': 'Campo "texto" é obrigatório'}), 400

    texto = data['texto']

    frases = [f.strip() for f in texto.split('.') if f.strip()]

    estruturas = []
    argumentos = []
    for frase in frases:
        estrutura = extrair_estrutura(frase)
        if estrutura:
            estruturas.append(f"{frase} → {estrutura}")
            argumentos.append(estrutura)
        else:
            estruturas.append(f"{frase} → (sem estrutura clara)")

    detector = DetectorFalacias()
    falacias = detector.analisar(texto, argumentos, frases=frases)

    conclusoes = []
    if argumentos:
        motor = MotorInferencia()
        for arg in argumentos:
            motor.adicionar_premissa(arg)
        novas = motor.resolver()
        for n in novas:
            if str(n) not in [str(c) for c in argumentos]:
                conclusoes.append(str(n))

    return jsonify({
        'estruturas': estruturas,
        'falacias': falacias,
        'conclusoes': conclusoes
    })

# ===== DOCUMENTAÇÃO DA API =====
@app.route('/api/docs')
def api_docs():
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API do Analisador de Paradoxos</title>
        <style>
            body { font-family: 'JetBrains Mono', monospace; background: #0a0c0f; color: #eaeef2; padding: 20px; }
            h1 { color: #00ff9d; }
            pre { background: #1e2228; padding: 10px; border-radius: 5px; }
            code { color: #00ff9d; }
            a { color: #00ff9d; }
        </style>
    </head>
    <body>
        <h1>📡 API do Analisador de Paradoxos</h1>
        <p>Endpoint: <code>POST /api/analisar</code></p>
        <h2>Exemplo de requisição:</h2>
        <pre>
{
    "texto": "O homem que matou o leão fugiu."
}
        </pre>
        <h2>Exemplo de resposta:</h2>
        <pre>
{
    "estruturas": ["O homem que matou o leão fugiu. → (fugir(homem) ∧ matar_leão(homem))"],
    "falacias": [],
    "conclusoes": ["fugir(homem)", "matar_leão(homem)"]
}
        </pre>
        <p>Os campos <code>falacias</code> e <code>conclusoes</code> podem ser arrays vazios.</p>
        <p><a href="/">← Voltar ao analisador</a></p>
    </body>
    </html>
    '''

# ===== ROTA PRINCIPAL DE ANÁLISE =====
@app.route('/analisar', methods=['POST'])
def analisar():
    data = request.get_json()
    texto = data.get('texto', '')
    
    frases = [f.strip() for f in texto.split('.') if f.strip()]
    
    estruturas = []
    argumentos = []
    for frase in frases:
        estrutura = extrair_estrutura(frase)
        if estrutura:
            estruturas.append(f"{frase} → {estrutura}")
            argumentos.append(estrutura)
        else:
            estruturas.append(f"{frase} → (sem estrutura clara)")
    
    detector = DetectorFalacias()
    falacias = detector.analisar(texto, argumentos, frases=frases)
    
    conclusoes = []
    if argumentos:
        motor = MotorInferencia()
        for arg in argumentos:
            motor.adicionar_premissa(arg)
        novas = motor.resolver()
        for n in novas:
            if str(n) not in [str(c) for c in argumentos]:
                conclusoes.append(str(n))
    
    nova_analise = Analise(
        texto=texto,
        data=datetime.utcnow(),
        num_frases=len(frases),
        num_falacias=len(falacias),
        falacias=json.dumps(falacias, ensure_ascii=False),
        estruturas=json.dumps(estruturas, ensure_ascii=False)
    )
    db.session.add(nova_analise)
    db.session.commit()
    
    return jsonify({
        'estruturas': estruturas,
        'falacias': falacias,
        'conclusoes': conclusoes
    })

# ===== ROTA DE ESTATÍSTICAS =====
@app.route('/stats')
def stats():
    analises = Analise.query.order_by(Analise.data.desc()).all()

    if not analises:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Estatísticas · Analisador de Paradoxos</title>
            <style>
                body { font-family: 'JetBrains Mono', monospace; background: #0a0c0f; color: #eaeef2; padding: 20px; }
                a { color: #00ff9d; }
            </style>
        </head>
        <body>
            <h1>📊 Estatísticas</h1>
            <p>Nenhuma análise realizada ainda.</p>
            <a href="/">← Voltar ao analisador</a>
        </body>
        </html>
        '''

    labels = [a.data.strftime('%d/%m %H:%M') for a in analises[:10]]
    num_frases = [a.num_frases for a in analises[:10]]
    num_falacias = [a.num_falacias for a in analises[:10]]

    from collections import Counter
    todas_falacias = []
    for a in analises:
        if a.falacias:
            try:
                fal_list = json.loads(a.falacias)
                for f in fal_list:
                    nome = f.split(':')[0].replace('⚠️', '').strip()
                    if nome:
                        todas_falacias.append(nome)
            except:
                pass
    contagem = Counter(todas_falacias).most_common(10)
    tipos = [c[0] for c in contagem]
    quantidades = [c[1] for c in contagem]

    total_analises = len(analises)
    total_frases = sum(a.num_frases for a in analises)
    total_falacias = sum(a.num_falacias for a in analises)
    media_falacias_por_analise = total_falacias / total_analises if total_analises else 0

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Estatísticas · Analisador de Paradoxos</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
            :root {
                --bg-primary: #0a0c0f;
                --bg-secondary: #14171c;
                --bg-card: #1e2228;
                --accent: #00ff9d;
                --text-primary: #eaeef2;
                --text-secondary: #8b949e;
                --border: #2d3138;
            }
            body {
                font-family: 'JetBrains Mono', monospace;
                background: var(--bg-primary);
                color: var(--text-primary);
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1, h2 {
                color: var(--accent);
            }
            .stats-summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .stat-card {
                background: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            }
            .stat-card .number {
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--accent);
            }
            .stat-card .label {
                color: var(--text-secondary);
                font-size: 0.9rem;
                text-transform: uppercase;
            }
            .chart-container {
                background: var(--bg-secondary);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 20px;
                margin: 30px 0;
            }
            canvas {
                max-height: 400px;
            }
            .back-link {
                margin-bottom: 20px;
            }
            .back-link a {
                color: var(--accent);
                text-decoration: none;
            }
            .back-link a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="back-link">
                <a href="/">← Voltar ao analisador</a>
            </div>
            <h1>📊 Estatísticas do Analisador</h1>

            <div class="stats-summary">
                <div class="stat-card">
                    <div class="number">{{ total_analises }}</div>
                    <div class="label">análises realizadas</div>
                </div>
                <div class="stat-card">
                    <div class="number">{{ total_frases }}</div>
                    <div class="label">frases analisadas</div>
                </div>
                <div class="stat-card">
                    <div class="number">{{ total_falacias }}</div>
                    <div class="label">falácias detectadas</div>
                </div>
                <div class="stat-card">
                    <div class="number">{{ "%.1f"|format(media_falacias_por_analise) }}</div>
                    <div class="label">média de falácias por análise</div>
                </div>
            </div>

            <div class="chart-container">
                <h2>Últimas 10 análises</h2>
                <canvas id="chart1"></canvas>
            </div>

            <div class="chart-container">
                <h2>Falácias mais frequentes</h2>
                <canvas id="chart2"></canvas>
            </div>
        </div>

        <script>
            const ctx1 = document.getElementById('chart1').getContext('2d');
            new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: {{ labels | tojson }},
                    datasets: [
                        { 
                            label: 'Frases', 
                            data: {{ num_frases | tojson }}, 
                            borderColor: '#00ff9d',
                            backgroundColor: 'rgba(0, 255, 157, 0.1)',
                            tension: 0.2
                        },
                        { 
                            label: 'Falácias', 
                            data: {{ num_falacias | tojson }}, 
                            borderColor: '#ff5e5e',
                            backgroundColor: 'rgba(255, 94, 94, 0.1)',
                            tension: 0.2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#eaeef2' } }
                    },
                    scales: {
                        x: { ticks: { color: '#8b949e' } },
                        y: { ticks: { color: '#8b949e' } }
                    }
                }
            });

            const ctx2 = document.getElementById('chart2').getContext('2d');
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: {{ tipos | tojson }},
                    datasets: [{ 
                        label: 'Ocorrências', 
                        data: {{ quantidades | tojson }}, 
                        backgroundColor: '#00ff9d',
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { ticks: { color: '#8b949e' } },
                        y: { ticks: { color: '#8b949e' } }
                    }
                }
            });
        </script>
    </body>
    </html>
    ''', 
    total_analises=total_analises,
    total_frases=total_frases,
    total_falacias=total_falacias,
    media_falacias_por_analise=media_falacias_por_analise,
    labels=labels,
    num_frases=num_frases,
    num_falacias=num_falacias,
    tipos=tipos,
    quantidades=quantidades
    )

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)