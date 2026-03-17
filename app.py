from flask import Flask, render_template, request, jsonify
import spacy
from parser_logico import extrair_estrutura, QuantificadorUniversal, QuantificadorNegacao, Fato, Predicado, Termo
from detector_falacias import DetectorFalacias
from motor_inferencia import MotorInferencia

# Carrega o modelo de português
nlp = spacy.load("pt_core_news_sm")

app = Flask(__name__)

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
                gap: 30px;
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

            <!-- ===== NOVO: ÁREA DE ESTATÍSTICAS ===== -->
            <div class="stats-footer" style="text-align: center; margin-top: 20px; color: var(--text-secondary);">
                <span id="frasesAnalisadas">0 frases analisadas</span> |
                <span id="falaciasEncontradas">0 falácias encontradas</span>
            </div>
            
            <div class="footer">
                <div>🧠 Analisador de Paradoxos · IA Simbólica</div>
                <div class="footer-links">
                    <a onclick="carregarExemploEspecifico('ad')">Ad Hominem</a>
                    <a onclick="carregarExemploEspecifico('autoridade')">Apelo à Autoridade</a>
                    <a onclick="carregarExemploEspecifico('negacao')">Negação</a>
                    <a onclick="carregarExemploEspecifico('silogismo')">Silogismo</a>
                    <a onclick="carregarExemploEspecifico('seu_exemplo')">Seu Exemplo</a>
                    <a onclick="carregarExemploEspecifico('conjuncao')">Conjunção</a>
                    <a onclick="carregarExemploEspecifico('disjuncao')">Disjunção</a>
                    <a onclick="carregarExemploEspecifico('implicacao')">Implicação</a>
                    <a onclick="carregarExemploEspecifico('existencial')">Existencial</a>
                    <a onclick="carregarExemploEspecifico('falso_consenso')">Falso Consenso</a>
                    <a onclick="carregarExemploEspecifico('espantalho')">Espantalho</a>
                </div>
            </div>
        </div>
        
        <script>
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
                    
                    // Mostra falácias
                    const falaciasDiv = document.getElementById('falacias');
                    if (data.falacias && data.falacias.length > 0) {
                        let html = '';
                        for (let i = 0; i < data.falacias.length; i++) {
                            html += '<div class="fallacy-item">' + data.falacias[i] + '</div>';
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

                    // ===== ATUALIZA AS ESTATÍSTICAS =====
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
                // Zera também as estatísticas
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
                    'autoridade': 'Segundo um famoso pastor, a terra é plana. Portanto, a terra é plana.',
                    'negacao': 'Nenhum homem é pássaro. Sócrates é homem. Sócrates não é pássaro.',
                    'silogismo': 'Todo mamífero é animal. Todo gato é mamífero. Totó é gato. Totó é animal.',
                    'seu_exemplo': 'Você não pode falar sobre mudanças climáticas porque você não é um cientista.',
                    'conjuncao': 'Deus existe e é bom.',
                    'disjuncao': 'O time vence ou empata.',
                    'implicacao': 'Se chover, então a rua fica molhada.',
                    'existencial': 'Existe um homem que é mortal.',
                    'falso_consenso': 'Todo mundo sabe que a terra é plana.',
                    'espantalho': 'Você está dizendo que Deus não existe, então você é ateu.'
                };
                document.getElementById('texto').value = exemplos[tipo] || exemplos['silogismo'];
                updateCharCount();
                analisar();
            }
            
            window.onload = function() {
                carregarExemplo();
            };
        </script>
    </body>
    </html>
    '''

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
    
    return jsonify({
        'estruturas': estruturas,
        'falacias': falacias,
        'conclusoes': conclusoes
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)