# 🧠 Analisador de Paradoxos

**IA Simbólica · Lógica de Primeira Ordem · Detecção de Falácias em Português**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Flask](https://img.shields.io/badge/Flask-2.3.x-green.svg)](https://flask.palletsprojects.com/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7.x-yellow.svg)](https://spacy.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/demo-online-brightgreen.svg)](https://analisador-paradoxos.onrender.com)

O **Analisador de Paradoxos** é uma ferramenta de IA simbólica que analisa argumentos em português, convertendo‑os em estruturas de lógica de primeira ordem, detectando falácias comuns e deduzindo conclusões por meio de regras de inferência. O sistema é composto por um parser linguístico, um motor de inferência, uma interface web interativa e uma API REST.

---

## ✨ Funcionalidades

### 📚 Parser Lógico (NLP + Lógica)
- ✅ **Fatos simples:** "Sócrates é homem" → `homem(Sócrates)`
- ✅ **Quantificador Universal:** "Todo homem é mortal" → `∀x (homem(x) → mortal(x))`
- ✅ **Quantificador de Negação:** "Nenhum homem é pássaro" → `∀x (homem(x) → ¬pássaro(x))`
- ✅ **Quantificador Existencial:** "Existe um homem" → `∃x (homem(x))`
- ✅ **Conjunções:** "Deus existe e é bom" → `(existe(Deus) ∧ bom(Deus))`
- ✅ **Disjunções:** "O time vence ou empata" → `(vence(time) ∨ empata(time))`
- ✅ **Implicações:** "Se chover, a rua fica molhada" → `(chover → molhada(rua))`
- ✅ **Causalidade:** "X porque Y" → `(Y → X)`
- ✅ **Orações relativas:** "O homem que matou o leão fugiu" → `(fugir(homem) ∧ matar_leão(homem))`
- ✅ **Voz passiva e verbos impessoais** (chover, nevar, etc.)

### ⚠️ Detector de Falácias (23+ tipos)
O sistema atualmente reconhece as seguintes falácias:

| Falácia | Descrição |
|--------|-----------|
| **Ad Hominem** | Ataca a pessoa em vez do argumento. |
| **Ad Hominem Circunstancial** | Ataca por suposto interesse pessoal. |
| **Apelo à Autoridade** | Usa a opinião de uma autoridade como prova, sem considerar seu real conhecimento. |
| **Apelo à Força** | Usa ameaça em vez de argumento. |
| **Apelo à Popularidade** | Algo é verdade porque muitos acreditam. |
| **Apelo à Natureza** | Assume que algo é bom apenas por ser natural. |
| **Apelo à Tradição** | Algo é certo porque sempre foi feito assim. |
| **Apelo à Novidade** | Assume que algo é melhor apenas por ser novo. |
| **Apelo à Emoção** | Manipula emoções em vez de usar argumentos lógicos. |
| **Apelo à Ignorância** | Afirma que algo é verdadeiro porque não foi provado falso (ou vice-versa). |
| **Falsa Dicotomia** | Apresenta apenas duas opções quando existem mais possibilidades. |
| **Post Hoc ergo Propter Hoc** | Correlação temporal não implica causalidade. |
| **Generalização Apressada** | Conclusão universal baseada em poucos exemplos. |
| **Generalização Temporal** | Uso de palavras absolutas (sempre, nunca) sem evidência. |
| **Falso Consenso** | Assume que todos concordam com uma ideia, sem evidências. |
| **Espantalho** | Distorce o argumento do oponente para facilitar o ataque. |
| **Raciocínio Circular** | A conclusão está implícita nas premissas. |
| **Composição** | Assume que o todo tem as mesmas propriedades das partes. |
| **Divisão** | Assume que as partes têm as mesmas propriedades do todo. |
| **Questão Complexa** | Pergunta que pressupõe algo não provado. |
| **Falácia do Apostador** | Achar que eventos independentes se influenciam. |
| **Apelo à Piedade** | Usar compaixão em vez de lógica. |
| **Falso Equilíbrio** | Dar peso igual a lados com evidências desiguais. |

### 💡 Motor de Inferência
- ✅ **Modus Ponens:** P → Q, P  ⊢  Q
- ✅ **Modus Tollens:** P → Q, ¬Q ⊢ ¬P
- ✅ **Silogismo Hipotético:** P → Q, Q → R  ⊢  P → R
- ✅ **Silogismo Categórico:** Nenhum A é B, x é A  ⊢  x não é B
- ✅ **Simplificação:** (P ∧ Q)  ⊢  P, Q
- ✅ **Silogismo Disjuntivo:** (P ∨ Q), ¬P  ⊢  Q
- ✅ **Contraposição:** P → Q  ⊢  ¬Q → ¬P

### 🌐 Interface Web
- Design moderno (dark mode, fonte JetBrains Mono)
- Totalmente responsiva (funciona em dispositivos móveis)
- Exemplos pré‑definidos para testar rapidamente
- Contador de caracteres e estatísticas (frases/falácias analisadas)
- Resultados organizados em três colunas: **estruturas lógicas**, **falácias detectadas** e **conclusões deduzidas**
- Página **"Sobre"** com explicação detalhada de cada falácia

### 📡 API REST
- Endpoint: `POST /api/analisar`
- Recebe JSON com o campo `"texto"` e retorna a análise completa em formato JSON
- Documentação interativa disponível em `/api/docs`

### 🧪 Testes Automatizados
- **Mais de 20 testes** cobrindo todas as falácias e funcionalidades principais
- Garantia de robustez e confiabilidade do sistema

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.12**
- **Flask** – framework web
- **spaCy** – processamento de linguagem natural (modelo `pt_core_news_sm`)
- **Gunicorn** – servidor WSGI para produção
- **Unittest** – testes automatizados
- **Render** – plataforma de deploy

---

## 🚀 Como Executar Localmente

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/analisador-paradoxos.git
   cd analisador-paradoxos