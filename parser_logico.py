import spacy
import re

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

class QuantificadorExistencial:
    def __init__(self, variavel, propriedade):
        self.variavel = variavel
        self.propriedade = propriedade
    def __repr__(self):
        return f"∃{self.variavel} ({self.propriedade})"

class QuantificadorNegacao:
    def __init__(self, variavel, condicao, propriedade):
        self.variavel = variavel
        self.condicao = condicao
        self.propriedade = propriedade
    def __repr__(self):
        return f"∀{self.variavel} ({self.condicao} → ¬{self.propriedade})"

class Conjuncao:
    def __init__(self, esquerda, direita):
        self.esquerda = esquerda
        self.direita = direita
    def __repr__(self):
        return f"({self.esquerda} ∧ {self.direita})"

class Disjuncao:
    def __init__(self, esquerda, direita):
        self.esquerda = esquerda
        self.direita = direita
    def __repr__(self):
        return f"({self.esquerda} ∨ {self.direita})"

class Implicacao:
    def __init__(self, antecedente, consequente):
        self.antecedente = antecedente
        self.consequente = consequente
    def __repr__(self):
        return f"({self.antecedente} → {self.consequente})"

class Fato:
    def __init__(self, sujeito, predicado, negado=False):
        self.sujeito = sujeito
        self.predicado = predicado
        self.negado = negado
    def __repr__(self):
        if self.negado:
            return f"¬{self.predicado}"
        return f"{self.predicado}"

def extrair_predicado_completo(doc, sujeito_omitido=None):
    """
    Extrai um Fato de uma frase considerando verbos auxiliares e objetos.
    Se não encontrar sujeito, mas a frase for um único verbo, cria fato com sujeito "IMPESSOAL".
    Retorna um Fato ou None.
    """
    print(f"\n      [extrair_predicado_completo] frase: '{doc.text}', comprimento: {len(doc)}")
    for token in doc:
        print(f"         token: '{token.text}', pos: {token.pos_}, dep: {token.dep_}")

    negado = False
    for token in doc:
        if token.dep_ == "neg":
            negado = True
            break
    if not negado and "não" in doc.text.lower():
        negado = True

    # Lista de verbos impessoais comuns (pode ser expandida)
    verbos_impessoais = ["chover", "nevar", "ventar", "trovejar", "relampejar", "anoitecer", "amanhecer"]

    # --- NOVA VERIFICAÇÃO: palavras únicas que são verbos ou impessoais ---
    if len(doc) == 1:
        palavra = doc[0].text.lower()
        # Se a palavra está na lista de verbos impessoais ou se é um verbo (mesmo classificado como PROPN)
        if palavra in verbos_impessoais or doc[0].pos_ in ("VERB", "PROPN"):
            # Pega o lema se disponível, senão a própria palavra
            predicado = doc[0].lemma_ if doc[0].lemma_ else palavra
            sujeito = Termo("IMPESSOAL")
            print(f"      → Verbo impessoal detectado! Criando fato com sujeito IMPESSOAL, predicado: {predicado}")
            return Fato(sujeito, Predicado(predicado, sujeito), negado)

    # --- LÓGICA ORIGINAL (com pequenos ajustes) ---
    sujeito = None
    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass"):
            sujeito = Termo(token.text)
            print(f"      → Sujeito encontrado: {sujeito}")
            break
    if not sujeito and sujeito_omitido:
        sujeito = sujeito_omitido
        print(f"      → Sujeito omitido usado: {sujeito}")
    if not sujeito:
        for token in doc:
            if token.pos_ in ("PROPN", "NOUN", "PRON"):
                sujeito = Termo(token.text)
                print(f"      → Sujeito (PROPN/NOUN/PRON): {sujeito}")
                break

    # Se ainda não tem sujeito e a frase tem um único verbo, trata como impessoal (fallback)
    if not sujeito and len(doc) == 1 and doc[0].pos_ == "VERB":
        sujeito = Termo("IMPESSOAL")
        predicado = doc[0].lemma_
        print(f"      → Verbo único detectado (fallback)! Criando fato com sujeito IMPESSOAL, predicado: {predicado}")
        return Fato(sujeito, Predicado(predicado, sujeito), negado)

    if not sujeito:
        print("      → Nenhum sujeito encontrado, retornando None")
        return None

    verbo_principal = None
    objeto = None
    for token in doc:
        if token.pos_ == "VERB" and token.dep_ != "aux":
            verbo_principal = token
            print(f"      → Verbo principal: {verbo_principal}")
            break
    if not verbo_principal:
        for token in doc:
            if token.pos_ == "VERB":
                verbo_principal = token
                print(f"      → Verbo principal (fallback): {verbo_principal}")
                break
    if verbo_principal:
        for child in verbo_principal.children:
            if child.dep_ in ("obj", "iobj", "pobj"):
                objeto = child.text.lower()
                print(f"      → Objeto encontrado: {objeto}")
                break
        if objeto:
            predicado = f"{verbo_principal.lemma_}_{objeto}"
        else:
            predicado = verbo_principal.lemma_
    else:
        # Tenta encontrar predicado a partir de ser/estar
        for token in doc:
            if token.lemma_ in ("ser", "estar") and token.dep_ == "ROOT":
                for child in token.children:
                    if child.dep_ in ("attr", "acomp", "obj"):
                        predicado = child.lemma_ if child.pos_ == "VERB" else child.text.lower()
                        print(f"      → Predicado de ser/estar: {predicado}")
                        break
                break
        else:
            # Último recurso: pega o último substantivo/adjetivo
            predicado = None
            for token in reversed(doc):
                if token.pos_ in ("NOUN", "ADJ") and token != sujeito:
                    predicado = token.text.lower()
                    print(f"      → Predicado (último recurso): {predicado}")
                    break
    if not predicado:
        print("      → Nenhum predicado encontrado, retornando None")
        return None

    print(f"      → Fato criado: {Fato(sujeito, Predicado(predicado, sujeito), negado)}")
    return Fato(sujeito, Predicado(predicado, sujeito), negado)

def extrair_estrutura(frase, sujeito_contexto=None):
    """
    Versão definitiva com suporte a implicações, conectivos e quantificadores.
    Prioridade: implicações > conectivos > quantificadores > fatos.
    """
    if not frase or len(frase.strip()) == 0:
        return None

    frase = frase.strip()
    # Remove pontuação final
    if frase and frase[-1] in '.!?':
        frase = frase[:-1]

    doc = nlp(frase)
    frase_lower = frase.lower()

    # ----- PRIORIDADE 1: IMPLICAÇÃO COM "SE...ENTÃO" -----
    # Regex flexível: "se X, então Y" ou "se X então Y"
    match = re.search(r'\bse\s+(.+?)\s*,?\s+então\s+(.+)', frase_lower, re.IGNORECASE)
    if match:
        ant_texto = match.group(1).strip()
        cons_texto = match.group(2).strip()
        print(f"\n🔍 IMPLICAÇÃO DETECTADA: antecedente='{ant_texto}', consequente='{cons_texto}'")
        
        # Parseia antecedente e consequente
        ant = extrair_estrutura(ant_texto.capitalize())
        print(f"   ANT result (extrair_estrutura): {ant}")
        if not ant:
            doc_ant = nlp(ant_texto.capitalize())
            ant = extrair_predicado_completo(doc_ant)
            print(f"   ANT result (extrair_predicado_completo): {ant}")
        
        cons = extrair_estrutura(cons_texto.capitalize())
        print(f"   CONS result (extrair_estrutura): {cons}")
        if not cons:
            doc_cons = nlp(cons_texto.capitalize())
            cons = extrair_predicado_completo(doc_cons)
            print(f"   CONS result (extrair_predicado_completo): {cons}")
        
        if ant and cons:
            print(f"   ✅ IMPLICAÇÃO CRIADA: {ant} → {cons}")
            return Implicacao(ant, cons)
        else:
            print(f"   ❌ Falha ao criar implicação: ant={ant}, cons={cons}")

    # ----- PRIORIDADE 2: CONECTIVOS -----
    # Conjunção "e"
    if " e " in frase_lower and not any(q in frase_lower for q in ["todo", "todos", "toda", "nenhum"]):
        partes = re.split(r'\s+e\s+', frase_lower, maxsplit=1)
        if len(partes) == 2:
            esq = extrair_estrutura(partes[0].strip().capitalize())
            dire = extrair_estrutura(partes[1].strip().capitalize())
            if esq and dire:
                return Conjuncao(esq, dire)

    # Disjunção "ou"
    if " ou " in frase_lower:
        partes = re.split(r'\s+ou\s+', frase_lower, maxsplit=1)
        if len(partes) == 2:
            esq = extrair_estrutura(partes[0].strip().capitalize())
            dire = extrair_estrutura(partes[1].strip().capitalize())
            if esq and dire:
                return Disjuncao(esq, dire)

    # ----- PRIORIDADE 3: QUANTIFICADORES -----
    if any(p in frase_lower for p in ["todo ", "todos ", "toda ", "todas "]):
        match = re.search(r'todo\s+(\w+)\s+é\s+(\w+)', frase_lower)
        if match:
            sujeito = match.group(1)
            predicado = match.group(2)
            variavel = "x"
            condicao = Predicado(sujeito, Termo(variavel))
            propriedade = Predicado(predicado, Termo(variavel))
            return QuantificadorUniversal(variavel, condicao, propriedade)

    if any(p in frase_lower for p in ["nenhum ", "nenhuma "]):
        match = re.search(r'nenhum\s+(\w+)\s+é\s+(\w+)', frase_lower)
        if match:
            sujeito = match.group(1)
            predicado = match.group(2)
            variavel = "x"
            condicao = Predicado(sujeito, Termo(variavel))
            propriedade = Predicado(predicado, Termo(variavel))
            return QuantificadorNegacao(variavel, condicao, propriedade)

    if any(p in frase_lower for p in ["existe ", "existem ", "há "]):
        match = re.search(r'existe\s+(\w+)\s+que\s+é\s+(\w+)', frase_lower)
        if match:
            sujeito = match.group(1)
            predicado = match.group(2)
            variavel = "x"
            # Por enquanto retorna como string, mas pode ser melhorado
            return f"∃{variavel} ({sujeito}({variavel}) ∧ {predicado}({variavel}))"

    # ----- PRIORIDADE 4: FATOS SIMPLES -----
    # Regex para padrões simples "X é Y" ou "X não é Y"
    match = re.match(r'^(\w+)\s+(?:não\s+)?é\s+(?:um|uma)?\s*(\w+)$', frase_lower)
    if match:
        sujeito = match.group(1).capitalize()
        predicado = match.group(2)
        negado = 'não' in frase_lower
        return Fato(Termo(sujeito), Predicado(predicado, Termo(sujeito)), negado)

    # Caso geral: usar extração completa com dependências
    fato = extrair_predicado_completo(doc, sujeito_contexto)
    if fato:
        return fato

    # Último recurso: se a frase for uma única palavra e for verbo, trata como impessoal
    if len(doc) == 1 and doc[0].pos_ == "VERB":
        return Fato(Termo("IMPESSOAL"), Predicado(doc[0].lemma_, Termo("IMPESSOAL")), False)

    return None