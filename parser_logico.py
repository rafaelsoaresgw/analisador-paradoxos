import spacy

# Carrega o modelo de português
nlp = spacy.load("pt_core_news_sm")

class Termo:
    def __init__(self, nome):
        self.nome = nome
    def __repr__(self):
        return self.nome

class Predicado:
    def __init__(self, nome, argumento):
        self.nome = nome
        self.argumento = argumento
    def __repr__(self):
        return f"{self.nome}({self.argumento})"

class QuantificadorUniversal:
    def __init__(self, variavel, condicao, propriedade):
        self.variavel = variavel
        self.condicao = condicao
        self.propriedade = propriedade
    def __repr__(self):
        return f"∀{self.variavel} ({self.condicao} → {self.propriedade})"

class QuantificadorNegacao:
    def __init__(self, variavel, condicao, propriedade):
        self.variavel = variavel
        self.condicao = condicao
        self.propriedade = propriedade
    def __repr__(self):
        return f"∀{self.variavel} ({self.condicao} → ¬{self.propriedade})"

class Fato:
    def __init__(self, sujeito, predicado, negado=False):
        self.sujeito = sujeito
        self.predicado = predicado
        self.negado = negado
    def __repr__(self):
        if self.negado:
            return f"¬{self.predicado}"
        return f"{self.predicado}"

def extrair_estrutura(frase):
    doc = nlp(frase)
    frase_lower = frase.lower()
    
    palavras_ignorar = ["é", "são", "era", "ser", "este", "esse", "meu", "seu", "o", "a", "os", "as", "um", "uma", "de", "da", "do"]
    
    tem_todo = "todo" in frase_lower or "todos" in frase_lower or "toda" in frase_lower
    tem_nenhum = "nenhum" in frase_lower or "nenhuma" in frase_lower
    tem_negacao = " não " in f" {frase_lower} " or "não é" in frase_lower
    
    correcoes_lemma = {
        "flutua": "flutuar",
        "voa": "voar",
        "corre": "correr",
        "come": "comer",
        "bebe": "beber"
    }
    
    # Caso 1: "Nenhum X é Y"
    if tem_nenhum:
        for token in doc:
            if token.pos_ == "NOUN" and token.text.lower() not in ["nenhum", "nenhuma"]:
                sujeito = token.lemma_
                predicado = None
                predicado_original = None
                
                for token2 in doc:
                    if token2.pos_ == "VERB":
                        predicado_original = token2.text.lower()
                        predicado = token2.lemma_
                        break
                
                if not predicado:
                    for token2 in doc:
                        if token2.pos_ == "ADJ":
                            predicado_original = token2.text.lower()
                            predicado = token2.lemma_
                            break
                
                if predicado_original and predicado_original in correcoes_lemma:
                    predicado = correcoes_lemma[predicado_original]
                
                if predicado:
                    variavel = "x"
                    condicao = Predicado(sujeito, Termo(variavel))
                    propriedade = Predicado(predicado, Termo(variavel))
                    return QuantificadorNegacao(variavel, condicao, propriedade)
    
    # Caso 2: "Todo X é Y"
    elif tem_todo:
        for token in doc:
            if token.pos_ == "NOUN" and token.text.lower() not in ["todo", "todos", "toda"]:
                sujeito = token.lemma_
                predicado = None
                predicado_original = None
                
                for token2 in doc:
                    if token2.pos_ == "VERB" and token2 != token:
                        predicado_original = token2.text.lower()
                        predicado = token2.lemma_
                        break
                
                if not predicado:
                    for token2 in doc:
                        if token2.pos_ == "ADJ":
                            predicado_original = token2.text.lower()
                            predicado = token2.lemma_
                            break
                
                if predicado_original and predicado_original in correcoes_lemma:
                    predicado = correcoes_lemma[predicado_original]
                
                if predicado:
                    variavel = "x"
                    condicao = Predicado(sujeito, Termo(variavel))
                    propriedade = Predicado(predicado, Termo(variavel))
                    return QuantificadorUniversal(variavel, condicao, propriedade)
    
    # Caso 3: Fato simples (com ou sem negação)
    else:
        sujeito = None
        predicado = None
        predicado_original = None
        negado = tem_negacao
        
        for token in doc:
            if token.pos_ in ["PROPN", "NOUN"] and token.dep_ != "ROOT" and token.text.lower() not in palavras_ignorar:
                sujeito = Termo(token.text)
            
            if token.pos_ in ["ADJ", "VERB", "NOUN"] and token.text.lower() not in palavras_ignorar and token != doc[0]:
                if token.pos_ == "VERB":
                    predicado_original = token.text.lower()
                    predicado = token.lemma_
                else:
                    predicado_original = token.text.lower()
                    predicado = token.lemma_
        
        if not sujeito or not predicado:
            for token in reversed(doc):
                if token.pos_ in ["PROPN", "NOUN"] and not sujeito:
                    sujeito = Termo(token.text)
                elif token.pos_ in ["ADJ", "VERB"] and not predicado and token != sujeito:
                    predicado_original = token.text.lower()
                    predicado = token.lemma_
        
        if predicado_original and predicado_original in correcoes_lemma:
            predicado = correcoes_lemma[predicado_original]
        
        if sujeito and predicado:
            if sujeito.nome.lower() not in ["esse", "este", "isto", "isso"]:
                return Fato(sujeito, Predicado(predicado, sujeito), negado)
    
    return None

# Testes
print("="*60)
print(" 🧠 ANALISADOR DE PARADOXOS - VERSÃO COM NEGAÇÃO ")
print("="*60)

testes = [
    "Todo homem é mortal",
    "Sócrates é homem",
    "Sócrates é mortal",
    "Nenhum homem é pássaro",
    "Sócrates não é pássaro",
    "O céu é azul",
    "Nenhuma pedra flutua"
]

for i, frase in enumerate(testes, 1):
    print(f"\n📝 Teste {i}: '{frase}'")
    resultado = extrair_estrutura(frase)
    if resultado:
        print(f"✅ Estrutura: {resultado}")
    else:
        print(f"⚠️  Ignorado")

print("\n" + "="*60)
print("✅ Parser atualizado!")
print("="*60)
