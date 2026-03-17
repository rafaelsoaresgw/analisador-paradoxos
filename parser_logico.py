# parser_logico.py - Versão definitiva com orações relativas e predicados nominais corrigidos

import spacy
import re

# Carrega o modelo de português
nlp = spacy.load("pt_core_news_sm")

# Variável global para resolução simples de pronomes
ultimo_sujeito = None

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

def extrair_predicado_completo(doc, sujeito_omitido=None, ignorar_que=False):
    """
    Extrai um Fato de uma frase considerando verbos auxiliares e objetos.
    Agora com suporte a predicados nominais (ser/estar + adjetivo/substantivo).
    Retorna um Fato ou None.
    """
    global ultimo_sujeito

    # Se for para ignorar orações com "que" (para evitar recursão infinita)
    if ignorar_que and any(token.text.lower() == "que" for token in doc):
        return None

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

    # Lista expandida de verbos impessoais
    verbos_impessoais = ["chover", "nevar", "ventar", "trovejar", "relampejar", "anoitecer", "amanhecer", "choviscar", "garoar", "escurecer", "entardecer"]

    # --- VERIFICAÇÃO: palavras únicas que são verbos ou impessoais ---
    if len(doc) == 1:
        palavra = doc[0].text.lower()
        if palavra in verbos_impessoais or doc[0].pos_ in ("VERB", "PROPN"):
            predicado = doc[0].lemma_ if doc[0].lemma_ else palavra
            sujeito = Termo("IMPESSOAL")
            print(f"      → Verbo impessoal detectado! Criando fato com sujeito IMPESSOAL, predicado: {predicado}")
            return Fato(sujeito, Predicado(predicado, sujeito), negado)

    # --- LÓGICA ORIGINAL ---
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

    # --- CORREÇÃO PARA PRONOME RELATIVO "QUE" ---
    if sujeito and sujeito.nome.lower() == "que" and sujeito_omitido:
        print(f"      → Substituindo pronome relativo 'que' por antecedente: {sujeito_omitido}")
        sujeito = sujeito_omitido

    # --- DETECÇÃO DE VOZ PASSIVA ---
    verbo_aux = None
    verbo_participio = None
    agente = None
    for token in doc:
        if token.pos_ == "AUX" and token.lemma_ in ("ser", "estar"):
            verbo_aux = token
        if token.pos_ == "VERB" and ("Part" in token.morph.get("VerbForm", []) or token.tag_ == "VBN"):
            verbo_participio = token
        if token.dep_ == "agent" and token.head == verbo_participio:
            for child in token.children:
                if child.dep_ == "pobj":
                    agente = child.text
                    break
    if verbo_aux and verbo_participio:
        if agente:
            sujeito = Termo(agente)
            print(f"      → Voz passiva com agente: {sujeito}")
        else:
            print(f"      → Voz passiva sem agente, paciente: {sujeito}")
        predicado = verbo_participio.lemma_
        fato = Fato(sujeito, Predicado(predicado, sujeito), negado)
        ultimo_sujeito = sujeito
        print(f"      → Fato criado (voz passiva): {fato}")
        return fato

    # --- PRONOMES: resolução ---
    if not sujeito:
        for token in doc:
            if token.pos_ == "PRON" and token.text.lower() in ["ele", "ela", "eles", "elas", "isso", "isto", "aquilo"]:
                if token.text.lower() in ["ele", "ela", "eles", "elas"] and ultimo_sujeito:
                    sujeito = ultimo_sujeito
                    print(f"      → Pronome resolvido para: {sujeito}")
                else:
                    sujeito = Termo(token.text)
                    print(f"      → Pronome detectado: {sujeito}")
                break

    # --- FALLBACK: verbo único impessoal ---
    if not sujeito and len(doc) == 1 and doc[0].pos_ == "VERB":
        sujeito = Termo("IMPESSOAL")
        predicado = doc[0].lemma_
        print(f"      → Verbo único detectado (fallback)! Criando fato com sujeito IMPESSOAL, predicado: {predicado}")
        return Fato(sujeito, Predicado(predicado, sujeito), negado)

    if not sujeito:
        print("      → Nenhum sujeito encontrado, retornando None")
        return None

    # --- EXTRAÇÃO DO PREDICADO ---
    verbo_principal = None
    objeto = None
    predicado_nominal = None

    # Primeiro, tenta encontrar um verbo principal (não auxiliar)
    for token in doc:
        if token.pos_ == "VERB" and token.dep_ != "aux":
            verbo_principal = token
            print(f"      → Verbo principal: {verbo_principal}")
            break

    if verbo_principal:
        # Verifica objetos
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
        # Se não há verbo principal, tenta predicado nominal
        # Verifica se há um verbo de ligação (copula) e um predicativo (ROOT)
        tem_copula = any(token.lemma_ in ("ser", "estar") and token.dep_ == "cop" for token in doc)
        if tem_copula:
            # O ROOT é o predicativo
            for token in doc:
                if token.dep_ == "ROOT" and token.pos_ in ("ADJ", "NOUN"):
                    predicado_nominal = token.text.lower()
                    print(f"      → Predicado nominal (ROOT): {predicado_nominal}")
                    break
        if predicado_nominal:
            predicado = predicado_nominal
        else:
            # Último recurso: pega o último substantivo/adjetivo
            for token in reversed(doc):
                if token.pos_ in ("NOUN", "ADJ") and token != sujeito:
                    predicado = token.text.lower()
                    print(f"      → Predicado (último recurso): {predicado}")
                    break
            else:
                predicado = None

    if not predicado:
        print("      → Nenhum predicado encontrado, retornando None")
        return None

    # Armazena o sujeito para pronomes futuros
    ultimo_sujeito = sujeito

    print(f"      → Fato criado: {Fato(sujeito, Predicado(predicado, sujeito), negado)}")
    return Fato(sujeito, Predicado(predicado, sujeito), negado)

def processar_oracao_relativa(doc, sujeito_contexto=None):
    """
    Processa especificamente orações relativas.
    Retorna uma Conjuncao se encontrar uma oração relativa, None caso contrário.
    Agora com construção manual do fato da relativa usando o lema do verbo.
    """
    print(f"\n      [processar_oracao_relativa] processando: '{doc.text}'")
    
    # Encontra o token principal (root) da oração principal (pode ser VERB, ADJ, NOUN...)
    token_principal = None
    for token in doc:
        if token.dep_ == "ROOT":
            token_principal = token
            print(f"      → Token principal encontrado: {token_principal} (pos: {token_principal.pos_})")
            break
    
    if not token_principal:
        print("      → Nenhum token principal encontrado")
        return None
    
    # Encontra orações relativas (acl:relcl)
    oracoes_relativas = []
    for token in doc:
        if token.dep_ == "acl:relcl":
            oracoes_relativas.append(token)
            print(f"      → Oração relativa encontrada: '{token.text}' (head: {token.head.text})")
    
    if not oracoes_relativas:
        print("      → Nenhuma oração relativa encontrada")
        return None
    
    # O antecedente é o head da primeira oração relativa
    primeira_rel = oracoes_relativas[0]
    antecedente = Termo(primeira_rel.head.text)
    print(f"      → Antecedente identificado: {antecedente}")
    
    # Extrai o fato da oração principal (ignorando a relativa)
    tokens_principais = []
    for token in doc:
        if token not in oracoes_relativas and not any(token in rel.subtree for rel in oracoes_relativas):
            tokens_principais.append(token)
    
    if tokens_principais:
        texto_principal = " ".join([t.text for t in sorted(tokens_principais, key=lambda x: x.i)])
        print(f"      → Texto principal: '{texto_principal}'")
        doc_principal = nlp(texto_principal)
        fato_principal = extrair_predicado_completo(doc_principal, sujeito_contexto, ignorar_que=True)
        print(f"      → Fato principal extraído: {fato_principal}")
    else:
        print("      → Não foi possível extrair texto principal")
        return None
    
    if not fato_principal:
        print("      → Falha ao extrair fato principal")
        return None
    
    # --- CONSTRUÇÃO MANUAL DO FATO DA RELATIVA ---
    rel_tokens = []
    for rel in oracoes_relativas:
        for token in rel.subtree:
            if token not in rel_tokens:
                rel_tokens.append(token)
    
    if rel_tokens:
        verbo_rel = None
        objeto_rel = None
        for token in rel_tokens:
            if token.pos_ == "VERB":
                verbo_rel = token
                for child in token.children:
                    if child.dep_ in ("obj", "iobj", "pobj"):
                        objeto_rel = child.text.lower()
                        break
                break
        
        if verbo_rel:
            # Usa o lema do verbo para formar o predicado
            if objeto_rel:
                nome_predicado = f"{verbo_rel.lemma_}_{objeto_rel}"
            else:
                nome_predicado = verbo_rel.lemma_
            
            fato_rel = Fato(antecedente, Predicado(nome_predicado, antecedente), negado=False)
            print(f"      → Fato da relativa construído manualmente: {fato_rel}")
            
            resultado = Conjuncao(fato_principal, fato_rel)
            print(f"      ✅ Conjunção criada: {resultado}")
            return resultado
        else:
            print("      → Nenhum verbo encontrado na oração relativa")
    else:
        print("      → Nenhum token na oração relativa")
    
    return None

def extrair_estrutura(frase, sujeito_contexto=None):
    """
    Versão definitiva com suporte a implicações, conectivos e quantificadores.
    Agora com suporte robusto a orações relativas (com "que").
    """
    if not frase or len(frase.strip()) == 0:
        return None

    frase = frase.strip()
    if frase and frase[-1] in '.!?':
        frase = frase[:-1]

    doc = nlp(frase)
    frase_lower = frase.lower()

    # ----- PRIORIDADE 0: ORAÇÕES RELATIVAS -----
    if any(token.dep_ == "acl:relcl" for token in doc):
        resultado_rel = processar_oracao_relativa(doc, sujeito_contexto)
        if resultado_rel:
            return resultado_rel

    # ----- PRIORIDADE 1: IMPLICAÇÃO "se...então" -----
    match = re.search(r'\bse\s+(.+?)\s*,?\s+então\s+(.+)', frase_lower, re.IGNORECASE)
    if match:
        ant_texto = match.group(1).strip()
        cons_texto = match.group(2).strip()
        print(f"\n🔍 IMPLICAÇÃO DETECTADA: antecedente='{ant_texto}', consequente='{cons_texto}'")
        
        ant = extrair_estrutura(ant_texto.capitalize())
        if not ant:
            ant = extrair_predicado_completo(nlp(ant_texto.capitalize()))
        cons = extrair_estrutura(cons_texto.capitalize())
        if not cons:
            cons = extrair_predicado_completo(nlp(cons_texto.capitalize()))
        
        if ant and cons:
            return Implicacao(ant, cons)

    # ----- PRIORIDADE 2: CONECTIVOS -----
    if " e " in frase_lower and not any(q in frase_lower for q in ["todo", "todos", "toda", "nenhum"]):
        partes = re.split(r'\s+e\s+', frase_lower, maxsplit=1)
        if len(partes) == 2:
            esq = extrair_estrutura(partes[0].strip().capitalize())
            dire = extrair_estrutura(partes[1].strip().capitalize())
            if esq and dire:
                return Conjuncao(esq, dire)

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
            return QuantificadorExistencial(variavel, Predicado(predicado, Termo(variavel)))

    # ----- PRIORIDADE 4: FATOS SIMPLES -----
    match = re.match(r'^(\w+)\s+(?:não\s+)?é\s+(?:um|uma)?\s*(\w+)$', frase_lower)
    if match:
        sujeito = match.group(1).capitalize()
        predicado = match.group(2)
        negado = 'não' in frase_lower
        return Fato(Termo(sujeito), Predicado(predicado, Termo(sujeito)), negado)

    # Caso geral
    fato = extrair_predicado_completo(doc, sujeito_contexto)
    if fato:
        return fato

    # Último recurso
    if len(doc) == 1 and doc[0].pos_ == "VERB":
        return Fato(Termo("IMPESSOAL"), Predicado(doc[0].lemma_, Termo("IMPESSOAL")), False)

    return None