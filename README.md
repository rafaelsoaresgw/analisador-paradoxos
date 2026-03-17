# 🧠 Analisador de Paradoxos

**IA Simbólica · Lógica de Primeira Ordem · Detecção de Falácias em Português**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Flask](https://img.shields.io/badge/Flask-2.3.x-green.svg)](https://flask.palletsprojects.com/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7.x-yellow.svg)](https://spacy.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/demo-online-brightgreen.svg)](https://analisador-paradoxos.onrender.com)

O **Analisador de Paradoxos** é uma ferramenta de IA simbólica que analisa argumentos em português, convertendo‑os em estruturas de lógica de primeira ordem, detectando falácias comuns e deduzindo conclusões por meio de regras de inferência. O sistema é composto por um parser linguístico, um motor de inferência e uma interface web interativa.

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

### ⚠️ Detector de Falácias
1. **Ad Hominem** – ataque à pessoa em vez do argumento
2. **Apelo à Autoridade** – com análise de contexto (religioso, científico, midiático)
3. **Falsa Dicotomia** – “ou A ou B” ignorando outras opções
4. **Post Hoc ergo Propter Hoc** – correlação não implica causalidade
5. **Generalização Apressada** – conclusão universal com pouca evidência (inclui temporal)
6. **Falso Consenso** – “todo mundo sabe que...”
7. **Espantalho** – distorcer o argumento do oponente
8. **Apelo à Emoção** – uso de palavras como “sofrimento”, “medo”
9. **Raciocínio Circular** – premissas que se pressupõem mutuamente

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

### 🧪 Testes Automatizados
- **9 testes funcionando** (incluindo orações relativas e voz passiva)
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
   git clone https://github.com/rafaelsoaresgw/analisador-paradoxos.git
   cd analisador-paradoxos
