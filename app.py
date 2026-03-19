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
    return render_template('index.html')

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
    lang = data.get('lang', 'pt')

    frases = [f.strip() for f in texto.split('.') if f.strip()]

    estruturas = []
    argumentos = []
    for frase in frases:
        estrutura = extrair_estrutura(frase, lang=lang)
        if estrutura:
            estruturas.append(f"{frase} → {estrutura}")
            argumentos.append(estrutura)
        else:
            estruturas.append(f"{frase} → (sem estrutura clara)")

    detector = DetectorFalacias()
    falacias = detector.analisar(texto, argumentos, frases=frases, lang=lang)

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
    lang = data.get('lang', 'pt')
    
    frases = [f.strip() for f in texto.split('.') if f.strip()]
    
    estruturas = []
    argumentos = []
    for frase in frases:
        estrutura = extrair_estrutura(frase, lang=lang)
        if estrutura:
            estruturas.append(f"{frase} → {estrutura}")
            argumentos.append(estrutura)
        else:
            estruturas.append(f"{frase} → (sem estrutura clara)")
    
    detector = DetectorFalacias()
    falacias = detector.analisar(texto, argumentos, frases=frases, lang=lang)
    
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