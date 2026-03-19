# parser_logico.py - Versão multilíngue (português/inglês) sem prints de debug

import spacy
import re

# Carrega os modelos de ambos os idiomas (certifique-se de tê-los instalados)
# Para instalar o modelo inglês: python -m spacy download en_core_web_sm
nlp_pt = spacy.load("pt_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

# Variável global para resolução simples de pronomes (compartilhada entre chamadas)
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

def extrair_predicado_completo(doc, sujeito_omitido=None, ignorar_que=False, lang='pt'):
    """
    Extrai um Fato de uma frase considerando verbos auxiliares e objetos.
    Agora com suporte a predicados nominais (ser/estar + adjetivo/substantivo).
    Retorna um Fato ou None.
    """
    global ultimo_sujeito

    # Se for para ignorar orações com "que" (para evitar recursão infinita)
    if ignorar_que and any(token.text.lower() == "que" for token in doc):
        return None

    negado = False
    for token in doc:
        if token.dep_ == "neg":
            negado = True
            break
    if not negado and "não" in doc.text.lower():
        negado = True
    # Para inglês, verificar "not"
    if not negado and " not " in f" {doc.text.lower()} ":
        negado = True

    # Lista expandida de verbos impessoais (português)
    verbos_impessoais_pt = ["chover", "nevar", "ventar", "trovejar", "relampejar", "anoitecer", "amanhecer", "choviscar", "garoar", "escurecer", "entardecer"]
    # Verbos impessoais em inglês
    verbos_impessoais_en = ["rain", "snow", "thunder", "lighten", "dawn", "dusk"]

    verbos_impessoais = verbos_impessoais_pt if lang == 'pt' else verbos_impessoais_en

    # --- VERIFICAÇÃO: palavras únicas que são verbos ou impessoais ---
    if len(doc) == 1:
        palavra = doc[0].text.lower()
        if palavra in verbos_impessoais or doc[0].pos_ in ("VERB", "PROPN"):
            predicado = doc[0].lemma_ if doc[0].lemma_ else palavra
            sujeito = Termo("IMPESSOAL")
            return Fato(sujeito, Predicado(predicado, sujeito), negado)

    # --- LÓGICA ORIGINAL ---
    sujeito = None
    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass"):
            sujeito = Termo(token.text)
            break
    if not sujeito and sujeito_omitido:
        sujeito = sujeito_omitido
    if not sujeito:
        for token in doc:
            if token.pos_ in ("PROPN", "NOUN", "PRON"):
                sujeito = Termo(token.text)
                break

    # --- CORREÇÃO PARA PRONOME RELATIVO "QUE" / "THAT" ---
    if sujeito and sujeito.nome.lower() in ["que", "that"] and sujeito_omitido:
        sujeito = sujeito_omitido

    # --- DETECÇÃO DE VOZ PASSIVA (funciona para ambos os idiomas, as tags são as mesmas) ---
    verbo_aux = None
    verbo_participio = None
    agente = None
    for token in doc:
        if token.pos_ == "AUX" and token.lemma_ in ("ser", "estar", "be"):
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
        else:
            # mantém o sujeito já encontrado (paciente)
            pass
        predicado = verbo_participio.lemma_
        fato = Fato(sujeito, Predicado(predicado, sujeito), negado)
        ultimo_sujeito = sujeito
        return fato

    # --- PRONOMES: resolução (simples) ---
    if not sujeito:
        for token in doc:
            if token.pos_ == "PRON" and token.text.lower() in ["ele", "ela", "eles", "elas", "isso", "isto", "aquilo", "he", "she", "it", "they", "them"]:
                if token.text.lower() in ["ele", "ela", "eles", "elas", "he", "she", "they"] and ultimo_sujeito:
                    sujeito = ultimo_sujeito
                else:
                    sujeito = Termo(token.text)
                break

    # --- FALLBACK: verbo único impessoal ---
    if not sujeito and len(doc) == 1 and doc[0].pos_ == "VERB":
        sujeito = Termo("IMPESSOAL")
        predicado = doc[0].lemma_
        return Fato(sujeito, Predicado(predicado, sujeito), negado)

    if not sujeito:
        return None

    # --- EXTRAÇÃO DO PREDICADO ---
    verbo_principal = None
    objeto = None
    predicado_nominal = None

    # Primeiro, tenta encontrar um verbo principal (não auxiliar)
    for token in doc:
        if token.pos_ == "VERB" and token.dep_ != "aux":
            verbo_principal = token
            break

    if verbo_principal:
        # Verifica objetos
        for child in verbo_principal.children:
            if child.dep_ in ("obj", "iobj", "pobj"):
                objeto = child.text.lower()
                break
        if objeto:
            predicado = f"{verbo_principal.lemma_}_{objeto}"
        else:
            predicado = verbo_principal.lemma_
    else:
        # Se não há verbo principal, tenta predicado nominal
        tem_copula = any(token.lemma_ in ("ser", "estar", "be") and token.dep_ == "cop" for token in doc)
        if tem_copula:
            # O ROOT é o predicativo
            for token in doc:
                if token.dep_ == "ROOT" and token.pos_ in ("ADJ", "NOUN"):
                    predicado_nominal = token.text.lower()
                    break
        if predicado_nominal:
            predicado = predicado_nominal
        else:
            # Último recurso: pega o último substantivo/adjetivo
            for token in reversed(doc):
                if token.pos_ in ("NOUN", "ADJ") and token != sujeito:
                    predicado = token.text.lower()
                    break
            else:
                predicado = None

    if not predicado:
        return None

    # Armazena o sujeito para pronomes futuros
    ultimo_sujeito = sujeito

    return Fato(sujeito, Predicado(predicado, sujeito), negado)

def processar_oracao_relativa(doc, sujeito_contexto=None, lang='pt'):
    """
    Processa especificamente orações relativas.
    Retorna uma Conjuncao se encontrar uma oração relativa, None caso contrário.
    """
    
    # Encontra o token principal (root) da oração principal (pode ser VERB, ADJ, NOUN...)
    token_principal = None
    for token in doc:
        if token.dep_ == "ROOT":
            token_principal = token
            break
    
    if not token_principal:
        return None
    
    # Encontra orações relativas (acl:relcl)
    oracoes_relativas = []
    for token in doc:
        if token.dep_ == "acl:relcl":
            oracoes_relativas.append(token)
    
    if not oracoes_relativas:
        return None
    
    # O antecedente é o head da primeira oração relativa
    primeira_rel = oracoes_relativas[0]
    antecedente = Termo(primeira_rel.head.text)
    
    # Extrai o fato da oração principal (ignorando a relativa)
    tokens_principais = []
    for token in doc:
        if token not in oracoes_relativas and not any(token in rel.subtree for rel in oracoes_relativas):
            tokens_principais.append(token)
    
    if tokens_principais:
        texto_principal = " ".join([t.text for t in sorted(tokens_principais, key=lambda x: x.i)])
        nlp = nlp_pt if lang == 'pt' else nlp_en
        doc_principal = nlp(texto_principal)
        fato_principal = extrair_predicado_completo(doc_principal, sujeito_contexto, ignorar_que=True, lang=lang)
    else:
        return None
    
    if not fato_principal:
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
            if objeto_rel:
                nome_predicado = f"{verbo_rel.lemma_}_{objeto_rel}"
            else:
                nome_predicado = verbo_rel.lemma_
            
            fato_rel = Fato(antecedente, Predicado(nome_predicado, antecedente), negado=False)
            resultado = Conjuncao(fato_principal, fato_rel)
            return resultado
        else:
            return None
    else:
        return None

def extrair_estrutura(frase, sujeito_contexto=None, lang='pt'):
    """
    Versão multilíngue com suporte a português e inglês.
    """
    if not frase or len(frase.strip()) == 0:
        return None

    frase = frase.strip()
    if frase and frase[-1] in '.!?':
        frase = frase[:-1]

    # Seleciona o modelo de linguagem
    nlp = nlp_pt if lang == 'pt' else nlp_en
    doc = nlp(frase)
    frase_lower = frase.lower()

    # ----- DEFINIÇÃO DOS PADRÕES POR IDIOMA -----
    if lang == 'pt':
        quant_todo = ["todo ", "todos ", "toda ", "todas "]
        quant_nenhum = ["nenhum ", "nenhuma "]
        quant_existe = ["existe ", "existem ", "há "]
        conectivo_e = " e "
        conectivo_ou = " ou "
        implicacao_padrao = r'\bse\s+(.+?)\s*,?\s+então\s+(.+)'
    else:  # inglês
        quant_todo = ["every ", "all "]
        quant_nenhum = ["no "]
        quant_existe = ["there is ", "there are ", "exists "]
        conectivo_e = " and "
        conectivo_ou = " or "
        implicacao_padrao = r'\bif\s+(.+?)\s*,?\s+then\s+(.+)'

    # ----- PRIORIDADE 0: ORAÇÕES RELATIVAS -----
    if any(token.dep_ == "acl:relcl" for token in doc):
        resultado_rel = processar_oracao_relativa(doc, sujeito_contexto, lang=lang)
        if resultado_rel:
            return resultado_rel

    # ----- PRIORIDADE 1: IMPLICAÇÃO -----
    match = re.search(implicacao_padrao, frase_lower, re.IGNORECASE)
    if match:
        ant_texto = match.group(1).strip()
        cons_texto = match.group(2).strip()
        
        ant = extrair_estrutura(ant_texto.capitalize(), lang=lang)
        if not ant:
            ant = extrair_predicado_completo(nlp(ant_texto.capitalize()), lang=lang)
        cons = extrair_estrutura(cons_texto.capitalize(), lang=lang)
        if not cons:
            cons = extrair_predicado_completo(nlp(cons_texto.capitalize()), lang=lang)
        
        if ant and cons:
            return Implicacao(ant, cons)

    # ----- PRIORIDADE 2: CONECTIVOS -----
    if conectivo_e.strip() in frase_lower and not any(q in frase_lower for q in quant_todo + quant_nenhum):
        partes = re.split(r'\s+' + conectivo_e.strip() + r'\s+', frase_lower, maxsplit=1)
        if len(partes) == 2:
            esq = extrair_estrutura(partes[0].strip().capitalize(), lang=lang)
            dire = extrair_estrutura(partes[1].strip().capitalize(), lang=lang)
            if esq and dire:
                return Conjuncao(esq, dire)

    if conectivo_ou.strip() in frase_lower:
        partes = re.split(r'\s+' + conectivo_ou.strip() + r'\s+', frase_lower, maxsplit=1)
        if len(partes) == 2:
            esq = extrair_estrutura(partes[0].strip().capitalize(), lang=lang)
            dire = extrair_estrutura(partes[1].strip().capitalize(), lang=lang)
            if esq and dire:
                return Disjuncao(esq, dire)

    # ----- PRIORIDADE 3: QUANTIFICADORES -----
    if any(p in frase_lower for p in quant_todo):
        if lang == 'pt':
            match = re.search(r'todo\s+(\w+)\s+é\s+(\w+)', frase_lower)
        else:
            match = re.search(r'every\s+(\w+)\s+is\s+(\w+)', frase_lower) or \
                    re.search(r'all\s+(\w+)\s+are\s+(\w+)', frase_lower)
        if match:
            sujeito = match.group(1)
            predicado = match.group(2)
            variavel = "x"
            condicao = Predicado(sujeito, Termo(variavel))
            propriedade = Predicado(predicado, Termo(variavel))
            return QuantificadorUniversal(variavel, condicao, propriedade)

    if any(p in frase_lower for p in quant_nenhum):
        if lang == 'pt':
            match = re.search(r'nenhum\s+(\w+)\s+é\s+(\w+)', frase_lower)
        else:
            match = re.search(r'no\s+(\w+)\s+is\s+(\w+)', frase_lower)
        if match:
            sujeito = match.group(1)
            predicado = match.group(2)
            variavel = "x"
            condicao = Predicado(sujeito, Termo(variavel))
            propriedade = Predicado(predicado, Termo(variavel))
            return QuantificadorNegacao(variavel, condicao, propriedade)

    if any(p in frase_lower for p in quant_existe):
        if lang == 'pt':
            match = re.search(r'existe\s+(\w+)\s+que\s+é\s+(\w+)', frase_lower)
        else:
            match = re.search(r'there (?:is|are)\s+(\w+)\s+that\s+is\s+(\w+)', frase_lower) or \
                    re.search(r'exists\s+(\w+)\s+that\s+is\s+(\w+)', frase_lower)
        if match:
            sujeito = match.group(1)
            predicado = match.group(2)
            variavel = "x"
            return QuantificadorExistencial(variavel, Predicado(predicado, Termo(variavel)))

    # ----- PRIORIDADE 4: FATOS SIMPLES -----
    if lang == 'pt':
        match = re.match(r'^(\w+)\s+(?:não\s+)?é\s+(?:um|uma)?\s*(\w+)$', frase_lower)
    else:
        match = re.match(r'^(\w+)\s+(?:not\s+)?is\s+(?:a|an)?\s*(\w+)$', frase_lower)
    if match:
        sujeito = match.group(1).capitalize()
        predicado = match.group(2)
        negado = 'não' in frase_lower or 'not' in frase_lower
        return Fato(Termo(sujeito), Predicado(predicado, Termo(sujeito)), negado)

    # Caso geral
    fato = extrair_predicado_completo(doc, sujeito_contexto, lang=lang)
    if fato:
        return fato

    # Último recurso
    if len(doc) == 1 and doc[0].pos_ == "VERB":
        return Fato(Termo("IMPESSOAL"), Predicado(doc[0].lemma_, Termo("IMPESSOAL")), False)

    return None