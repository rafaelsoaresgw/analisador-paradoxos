import spacy

# Carrega o modelo de português
nlp = spacy.load("pt_core_news_sm")

# Frase para testar
frase = "Todo homem é mortal. Sócrates é homem. Portanto, Sócrates é mortal."

# Processa a frase
doc = nlp(frase)

# Mostra cada palavra e sua função na frase
print("Análise sintática:\n")
for token in doc:
    print(f"Palavra: {token.text.ljust(12)} | Tipo: {token.pos_.ljust(10)} | Depende de: {token.head.text.ljust(12)} | Função: {token.dep_}")

# Mostra as entidades reconhecidas
print("\nEntidades encontradas:\n")
for ent in doc.ents:
    print(f"Entidade: {ent.text} | Tipo: {ent.label_}")
