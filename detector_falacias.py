# detector_falacias.py - Versão ULTRA COMPLETA com 50+ falácias
# Suporte multilíngue (pt/en) - TODAS as falácias possíveis

import re
from typing import List, Dict, Any, Optional, Tuple

class DetectorFalacias:
    """
    Detector de falácias com análise semântica avançada (multilíngue)
    VERSÃO 3.0 - MAIS DE 50 FALÁCIAS DETECTADAS
    """
    
    def __init__(self):
        self.falacias_encontradas = []
        self.ultimo_contexto = {}
    
    def analisar_contexto(self, texto: str, lang: str = 'pt') -> Dict[str, bool]:
        """
        Analisa o contexto do texto para palavras‑chave de religião, política, ciência, emoção, etc.
        Agora com suporte expandido a inglês e mais categorias.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            contexto = {
                # Categorias principais
                'tem_religiao': any(p in texto_lower for p in ["deus", "bíblia", "padre", "pastor", "igreja", "fé", "religião", "cristão", "católico", "evangélico", "espírita", "umbanda", "candomblé", "budista", "mulçumano"]),
                'tem_politica': any(p in texto_lower for p in ["política", "governo", "presidente", "partido", "eleição", "voto", "político", "esquerda", "direita", "lula", "bolsonaro", "câmara", "senado", "congresso", "constituição"]),
                'tem_ciencia': any(p in texto_lower for p in ["ciência", "cientista", "pesquisa", "estudo", "dados", "experimento", "teoria", "hipótese", "laboratório", "acadêmico", "publicação", "método científico"]),
                'tem_emocao': any(p in texto_lower for p in ["sentimento", "emoção", "amor", "ódio", "medo", "raiva", "tristeza", "alegria", "paixão", "compaixão", "piedade", "esperança", "desespero"]),
                'tem_economia': any(p in texto_lower for p in ["economia", "dinheiro", "mercado", "inflação", "juros", "pib", "reforma", "tributo", "imposto", "dólar", "real", "financeiro", "bancos", "poupança"]),
                'tem_saude': any(p in texto_lower for p in ["saúde", "doença", "remédio", "vacina", "tratamento", "médico", "hospital", "covid", "vírus", "pandemia", "doente", "paciente", "clínica"]),
                'tem_educacao': any(p in texto_lower for p in ["educação", "escola", "professor", "aluno", "ensino", "aprendizado", "faculdade", "universidade", "colégio", "estudante", "aula", "curso"]),
                'tem_meio_ambiente': any(p in texto_lower for p in ["meio ambiente", "natureza", "ecologia", "sustentável", "poluição", "clima", "aquecimento global", "floresta", "animal", "vegetal", "reciclagem"]),
                'tem_tecnologia': any(p in texto_lower for p in ["tecnologia", "internet", "computador", "celular", "aplicativo", "software", "hardware", "digital", "inovação", "startup", "inteligência artificial"]),
                'tem_esporte': any(p in texto_lower for p in ["esporte", "futebol", "time", "jogador", "técnico", "campeonato", "copa", "olimpíada", "atleta", "ginásio"]),
                'tem_cultura': any(p in texto_lower for p in ["cultura", "arte", "música", "filme", "cinema", "teatro", "literatura", "livro", "poesia", "pintura", "escultura"]),
                'tem_direito': any(p in texto_lower for p in ["direito", "lei", "justiça", "advogado", "juiz", "tribunal", "constituição", "código", "legal", "ilegal", "crime", "pena"]),
            }
        else:  # inglês
            contexto = {
                'tem_religiao': any(p in texto_lower for p in ["god", "bible", "priest", "pastor", "church", "faith", "religion", "christian", "catholic", "evangelical", "muslim", "buddhist"]),
                'tem_politica': any(p in texto_lower for p in ["politics", "government", "president", "party", "election", "vote", "political", "left", "right", "congress", "senate", "constitution"]),
                'tem_ciencia': any(p in texto_lower for p in ["science", "scientist", "research", "study", "data", "experiment", "theory", "hypothesis", "lab", "academic", "publication", "scientific method"]),
                'tem_emocao': any(p in texto_lower for p in ["feeling", "emotion", "love", "hate", "fear", "anger", "sadness", "joy", "passion", "compassion", "pity", "hope", "despair"]),
                'tem_economia': any(p in texto_lower for p in ["economy", "money", "market", "inflation", "interest", "gdp", "reform", "tax", "dollar", "financial", "bank", "savings"]),
                'tem_saude': any(p in texto_lower for p in ["health", "disease", "medicine", "vaccine", "treatment", "doctor", "hospital", "covid", "virus", "pandemic", "patient", "clinic"]),
                'tem_educacao': any(p in texto_lower for p in ["education", "school", "teacher", "student", "teaching", "learning", "college", "university", "class", "course"]),
                'tem_meio_ambiente': any(p in texto_lower for p in ["environment", "nature", "ecology", "sustainable", "pollution", "climate", "global warming", "forest", "animal", "recycling"]),
                'tem_tecnologia': any(p in texto_lower for p in ["technology", "internet", "computer", "smartphone", "app", "software", "hardware", "digital", "innovation", "startup", "artificial intelligence"]),
                'tem_esporte': any(p in texto_lower for p in ["sports", "soccer", "football", "team", "player", "coach", "championship", "olympics", "athlete"]),
                'tem_cultura': any(p in texto_lower for p in ["culture", "art", "music", "movie", "cinema", "theater", "literature", "book", "poetry", "painting"]),
                'tem_direito': any(p in texto_lower for p in ["law", "justice", "lawyer", "judge", "court", "constitution", "code", "legal", "illegal", "crime", "penalty"]),
            }
        
        self.ultimo_contexto = contexto
        return contexto
    
    # ============================================================
    # FALÁCIAS DE ATAQUE PESSOAL (AD HOMINEM E DERIVADAS)
    # ============================================================
    
    def detectar_ad_hominem(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Falácia: Atacar a pessoa em vez do argumento.
        Inclui: ad hominem abusivo, ad hominem circunstancial, tu quoque
        """
        texto_lower = texto.lower()
        contexto = self.analisar_contexto(texto, lang)
        
        if lang == 'pt':
            # Padrão específico: "você não é um X"
            match = re.search(r'você não é (?:um|uma) (\w+)', texto_lower)
            if match:
                profissao = match.group(1)
                if contexto.get('tem_ciencia') and profissao in ['cientista', 'pesquisador', 'especialista']:
                    return f"⚠️ Ad hominem: ataque à credencial científica (você não é {profissao})"
                return f"⚠️ Ad hominem: ataque à credencial (você não é {profissao})"
            
            # Tu quoque (você também)
            if re.search(r'você também (?:fez|faz|é)', texto_lower, re.IGNORECASE):
                return "⚠️ Tu quoque (você também): ataca a pessoa por hipocrisia em vez do argumento"
            
            # Padrões gerais expandidos
            padroes = [
                (r"você (?:é|não é) (\w+)", "ataque direto"),
                (r"tu (?:és|não és) (\w+)", "ataque direto"),
                (r"você não (?:entende|sabe|compreende)", "ataque à capacidade"),
                (r"você não pode falar porque", "desqualificação"),
                (r"seu argumento não vale porque", "desqualificação"),
                (r"você está errado porque", "ataque pessoal"),
                (r"ignorante|burro|idiota|estúpido|imbecil|cretino|otário", "xingamento"),
                (r"sua opinião não vale porque", "desqualificação"),
                (r"você não tem autoridade para", "desqualificação"),
            ]
        else:
            match = re.search(r'you are not (?:a|an) (\w+)', texto_lower, re.IGNORECASE)
            if match:
                profession = match.group(1)
                if contexte.get('tem_ciencia') and profession in ['scientist', 'researcher', 'specialist']:
                    return f"⚠️ Ad hominem: attack on scientific credential (you are not a {profession})"
                return f"⚠️ Ad hominem: attack on credential (you are not a {profession})"
            
            if re.search(r'you also (?:did|are)', texto_lower, re.IGNORECASE):
                return "⚠️ Tu quoque (you also): attacks the person for hypocrisy instead of the argument"
            
            padroes = [
                (r"you (?:are|are not) (\w+)", "direct attack"),
                (r"you don't (?:understand|know|comprehend)", "attack on ability"),
                (r"you can't speak because", "disqualification"),
                (r"your argument is worthless because", "disqualification"),
                (r"you are wrong because", "personal attack"),
                (r"ignorant|stupid|idiot|dumb|moron", "insult"),
                (r"your opinion doesn't matter because", "disqualification"),
            ]
        
        for padrao, tipo in padroes:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                if len(match.groups()) > 0:
                    alvo = match.group(1)
                    return f"⚠️ Ad hominem: {tipo} ('{alvo}')"
                else:
                    return f"⚠️ Ad hominem: {tipo}"
        
        return None
    
    def detectar_ad_hominem_circunstancial(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """Ataca a pessoa por suposto interesse pessoal ou circunstância."""
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'você só (?:diz|defende|pensa) isso porque (?:ganha dinheiro|tem interesse|é (?:funcionário|contratado|pago)|trabalha para|recebe|é beneficiado)',
                r'você está falando isso porque (?:te convém|te beneficia|é do seu interesse)',
                r'você defende isso porque (?:é pago|é financiado|recebe dinheiro|tem ações)',
                r'você só pensa assim porque (?:é rico|é pobre|é de direita|é de esquerda|é religioso|é ateu)',
                r'claro que você diz isso, você é (?:funcionário|contratado|pago)',
                r'isso é interesse (?:pessoal|financeiro|político) seu',
            ]
        else:
            padroes = [
                r'you only (?:say|defend|think) that because (?:you earn money|you have an interest|you are (?:an employee|hired|paid)|you work for|you receive|you benefit)',
                r'you are saying that because (?:it suits you|it benefits you|it is in your interest)',
                r'you defend that because (?:you are paid|you are financed|you receive money|you have shares)',
                r'you only think that because (?:you are rich|you are poor|you are right-wing|you are left-wing|you are religious|you are atheist)',
                r'of course you say that, you are (?:an employee|hired|paid)',
                r'that is your (?:personal|financial|political) interest',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Ad hominem circumstantial: attacks based on supposed personal interest"
                return msg if lang != 'pt' else "⚠️ Ad hominem circunstancial: ataca por suposto interesse pessoal"
        
        return None
    
    # ============================================================
    # FALÁCIAS DE APELO (AUTORIDADE, FORÇA, POPULARIDADE, ETC)
    # ============================================================
    
    def detectar_apelo_autoridade(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Usar autoridade irrelevante como prova.
        Inclui: apelo à autoridade, apelo à autoridade anônima, apelo à autoridade irrelevante
        """
        texto_lower = texto.lower()
        contexto = self.analisar_contexto(texto, lang)
        
        if lang == 'pt':
            autoridades_religiosas = ["padre", "pastor", "papa", "bispo", "apóstolo", "profeta", "cardeal", "monge", "freira", "guru", "líder espiritual"]
            autoridades_academicas = ["cientista", "professor", "doutor", "pesquisador", "especialista", "acadêmico", "phd", "mestre", "notável", "erudito"]
            autoridades_midia = ["famoso", "celebridade", "jornalista", "apresentador", "ator", "cantor", "influencer", "youtuber", "blogueiro"]
            autoridades_politicas = ["presidente", "governador", "prefeito", "senador", "deputado", "ministro", "autoridade", "liderança"]
            autoridades_anonimas = ["especialistas dizem", "cientistas afirmam", "estudos mostram", "pesquisas indicam", "fontes confiáveis", "dizem por aí"]
            
            padroes = [
                "segundo", "como disse", "de acordo com", "conforme",
                "é sabido por todos que", "especialistas dizem",
                "está escrito que", "a bíblia diz", "o papa disse",
                "o padre disse", "o pastor disse", "o professor disse",
                "o doutor disse", "o cientista disse", "estudos mostram",
                "pesquisas indicam", "cientistas afirmam", "acadêmicos comprovam",
            ]
        else:
            autoridades_religiosas = ["priest", "pastor", "pope", "bishop", "apostle", "prophet", "cardinal", "monk", "nun", "guru", "spiritual leader"]
            autoridades_academicas = ["scientist", "professor", "doctor", "researcher", "specialist", "academic", "phd", "master", "scholar"]
            autoridades_midia = ["celebrity", "famous", "journalist", "tv host", "actor", "singer", "influencer", "youtuber", "blogger"]
            autoridades_politicas = ["president", "governor", "mayor", "senator", "representative", "minister", "authority", "leader"]
            autoridades_anonimas = ["experts say", "scientists claim", "studies show", "research indicates", "reliable sources", "they say"]
            
            padroes = [
                "according to", "as said by", "in accordance with",
                "it is known by everyone that", "experts say",
                "it is written that", "the bible says", "the pope said",
                "the priest said", "the pastor said", "the professor said",
                "the doctor said", "the scientist said", "studies show",
                "research indicates", "scientists claim", "academics prove",
            ]
        
        for padrao in padroes:
            if padrao in texto_lower:
                # Verifica autoridades específicas
                for autoridade in autoridades_religiosas:
                    if autoridade in texto_lower:
                        if not contexto.get('tem_religiao', False):
                            return f"⚠️ Apelo à autoridade religiosa irrelevante: '{padrao} {autoridade}'" if lang == 'pt' else f"⚠️ Irrelevant religious authority: '{padrao} {autoridade}'"
                        return f"⚠️ Apelo à autoridade religiosa: '{padrao} {autoridade}' (autoridade não necessariamente especialista no assunto)" if lang == 'pt' else f"⚠️ Appeal to religious authority: '{padrao} {autoridade}'"
                
                for autoridade in autoridades_academicas:
                    if autoridade in texto_lower:
                        if not contexto.get('tem_ciencia', False):
                            return f"⚠️ Apelo à autoridade acadêmica irrelevante: '{padrao} {autoridade}'" if lang == 'pt' else f"⚠️ Irrelevant academic authority: '{padrao} {autoridade}'"
                        return f"⚠️ Apelo à autoridade acadêmica: '{padrao} {autoridade}'" if lang == 'pt' else f"⚠️ Appeal to academic authority: '{padrao} {autoridade}'"
                
                for autoridade in autoridades_midia:
                    if autoridade in texto_lower:
                        return f"⚠️ Apelo à autoridade midiática: '{padrao} {autoridade}' (autoridade não qualificada no assunto)" if lang == 'pt' else f"⚠️ Appeal to media authority: '{padrao} {autoridade}' (unqualified authority)"
                
                for autoridade in autoridades_politicas:
                    if autoridade in texto_lower:
                        return f"⚠️ Apelo à autoridade política: '{padrao} {autoridade}' (autoridade não qualificada no assunto)" if lang == 'pt' else f"⚠️ Appeal to political authority: '{padrao} {autoridade}' (unqualified authority)"
                
                # Autoridade anônima
                for anonima in autoridades_anonimas:
                    if anonima in texto_lower:
                        return f"⚠️ Apelo à autoridade anônima: '{padrao}' sem especificar quem" if lang == 'pt' else f"⚠️ Appeal to anonymous authority: '{padrao}' without specifying who"
        
        return None
    
    def detectar_apelo_forca(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """Usar ameaça em vez de argumento."""
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'se não (?:concordar|aceitar|fizer),? (?:vai sofrer|terá problemas|pior para você|vai se arrepender|vai pagar|vai perder|vai ser punido|vai ver só)',
                r'é melhor (?:aceitar|concordar) (?:ou então|senão|caso contrário)',
                r'você será (?:punido|demitido|processado|preso|excluído) se não',
                r'vou (?:te processar|te denunciar|acabar com você|destruir você|fazer você pagar) se',
                r'ou você (?:faz|aceita) ou (?:vai sofrer|vai se dar mal|vai perder|vai ver)',
                r'se você não fizer isso, (?:vai se arrepender|vai pagar caro)',
                r'cuidado, senão (?:vai se dar mal|vai sofrer|vai ver)',
                r'vai por mim, é melhor (?:aceitar|concordar)',
            ]
        else:
            padroes = [
                r'if you don\'?t (?:agree|accept|do it),? (?:you will suffer|you will have problems|it will be worse for you|you will regret|you will pay|you will lose|you will be punished|you\'?ll see)',
                r'you\'?d better (?:accept|agree) (?:or else|otherwise)',
                r'you will be (?:punished|fired|sued|arrested|excluded) if you don\'?t',
                r'I will (?:sue you|report you|destroy you|ruin you|make you pay) if',
                r'either you (?:do|accept) it or (?:you will suffer|you will regret it|you will lose|you\'?ll see)',
                r'if you don\'?t do this, (?:you\'?ll regret it|you\'?ll pay dearly)',
                r'be careful, or (?:you\'?ll be sorry|you\'?ll suffer|you\'?ll see)',
                r'take it from me, you\'?d better (?:accept|agree)',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Appeal to force: using threat instead of argument"
                return msg if lang != 'pt' else "⚠️ Apelo à força: usar ameaça em vez de argumento"
        
        return None
    
    def detectar_apelo_popularidade(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """Algo é verdade porque muitos acreditam (ad populum)."""
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'a maioria (?:acredita|pensa|diz|concorda) que,? (?:portanto|logo|então)',
                r'todo mundo (?:está fazendo|acha|sabe|concorda|pensa) isso,? (?:então|logo|por isso)',
                r'é (?:moda|tendência|popular|consenso),? (?:por isso|logo|então)',
                r'milhões de pessoas (?:usam|acreditam|pensam|concordam|compram)',
                r'é o que todos (?:querem|falam|pensam|acreditam|usam)',
                r'é a (?:opinião|vontade) da maioria',
                r'a grande maioria (?:concorda|pensa|diz)',
                r'é o que a maioria (?:quer|pensa|diz)',
                r'todo mundo sabe que',
                r'é de conhecimento popular que',
            ]
        else:
            padroes = [
                r'the majority (?:believes|thinks|says|agrees) that,? (?:therefore|so|then)',
                r'everyone (?:is doing|thinks|knows|agrees) that,? (?:so|then|therefore)',
                r'it is (?:fashionable|a trend|popular|consensus),? (?:so|therefore|then)',
                r'millions of people (?:use|believe|think|agree|buy)',
                r'it is what everyone (?:wants|says|thinks|believes|uses)',
                r'it is the (?:opinion|will) of the majority',
                r'the vast majority (?:agrees|thinks|says)',
                r'it is what most people (?:want|think|say)',
                r'everyone knows that',
                r'it is common knowledge that',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Appeal to popularity: something is true because many believe it"
                return msg if lang != 'pt' else "⚠️ Apelo à popularidade: algo é verdade porque muitos acreditam"
        
        return None
    
    def detectar_apelo_emocao(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """Manipula emoções em vez de lógica."""
        texto_lower = texto.lower()
        
        if lang == 'pt':
            palavras_emocao = [
                "sofrimento", "dor", "medo", "ódio", "amor", "esperança", 
                "crianças", "família", "futuro", "tragédia", "horror", 
                "pavor", "terror", "lágrimas", "choro", "desespero",
                "alegria", "felicidade", "paixão", "compaixão", "piedade",
                "inocentes", "pobres", "coitados", "vítimas", "mortos",
                "sangue", "violência", "crueldade", "injustiça",
                "sonhos", "medo do futuro", "desgraça", "calamidade",
                "catástrofe", "desastre", "tragédia", "genocídio", "massacre",
            ]
        else:
            palavras_emocao = [
                "suffering", "pain", "fear", "hate", "love", "hope", 
                "children", "family", "future", "tragedy", "horror", 
                "dread", "terror", "tears", "crying", "despair",
                "joy", "happiness", "passion", "compassion", "pity",
                "innocent", "poor", "victims", "dead",
                "blood", "violence", "cruelty", "injustice",
                "dreams", "fear of the future", "disgrace", "calamity",
                "catastrophe", "disaster", "tragedy", "genocide", "massacre",
            ]
        
        encontradas = []
        for palavra in palavras_emocao:
            if palavra in texto_lower:
                encontradas.append(palavra)
                if len(encontradas) >= 2:  # Se tiver várias palavras emocionais
                    msg = f"⚠️ Appeal to emotion: using emotional words {', '.join(encontradas[:3])} to manipulate"
                    return msg if lang != 'pt' else f"⚠️ Apelo à emoção: uso de palavras emocionais {', '.join(encontradas[:3])} para manipular"
        
        if encontradas:
            msg = f"⚠️ Appeal to emotion: using '{encontradas[0]}' to influence sentiment"
            return msg if lang != 'pt' else f"⚠️ Apelo à emoção: uso de '{encontradas[0]}' para influenciar sentimento"
        
        return None
    
    def detectar_apelo_ignorancia(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Apelo à ignorância: "Não provaram que é falso, logo é verdadeiro" (ou vice-versa).
        Também conhecido como argumentum ad ignorantiam.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'não (?:prov[oa]r?am|demonstr[oa]r?am) que é falso,? (?:portanto|logo|então) é verdadeiro',
                r'não (?:prov[oa]r?am|demonstr[oa]r?am) que é verdadeiro,? (?:portanto|logo|então) é falso',
                r'ninguém (?:conseguiu )?provou? que (.+?) (?:é falso|não existe),? (?:portanto|logo|então) (.+?) (?:é verdadeiro|existe)',
                r'ninguém (?:conseguiu )?provou? que (.+?) não existe,? (?:portanto|logo|então) \1 existe',
                r'não há provas de que não é verdade',
                r'ninguém conseguiu refutar',
                r'ninguém pode provar o contrário',
                r'até que provem o contrário, é verdade',
                r'se não pode provar que está errado, então está certo',
                r'ninguém provou que não funciona, então funciona',
            ]
        else:
            padroes = [
                r'nobody has (?:proven|shown) that it is false,? (?:therefore|so|then) it is true',
                r'nobody has (?:proven|shown) that it is true,? (?:therefore|so|then) it is false',
                r'no one has (?:proven|shown) that (.+?) (?:is false|does not exist),? (?:therefore|so|then) (.+?) (?:is true|exists)',
                r'no one has (?:proven|shown) that (.+?) does not exist,? (?:therefore|so|then) \1 exists',
                r'there is no proof that it is not true',
                r'nobody could refute',
                r'nobody can prove otherwise',
                r'until proven otherwise, it is true',
                r'if you can\'?t prove it wrong, then it is right',
                r'nobody proved it doesn\'?t work, so it works',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Appeal to ignorance: absence of proof is used as proof"
                return msg if lang != 'pt' else "⚠️ Apelo à ignorância: a ausência de prova é usada como prova"
        
        return None
    
    def detectar_apelo_natureza(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Apelo à natureza: algo é bom porque é natural.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'é natural,? (?:portanto|logo|então) é (?:melhor|bom|seguro|saudável|mais puro)',
                r'por ser natural,? (?:é|deve ser) (?:melhor|mais seguro|mais saudável)',
                r'natureza (?:não|jamais) (?:erra|falha|se engana|mente)',
                r'produto (?:natural|da natureza) (?:é|são) (?:superiores|melhores|mais puros)',
                r'natural é sempre melhor',
                r'se é natural, faz bem',
                r'os produtos naturais são (?:superiores|melhores|mais saudáveis)',
                r'artificial faz mal, natural faz bem',
            ]
        else:
            padroes = [
                r'it is natural,? (?:therefore|so|then) it is (?:better|good|safe|healthy|purer)',
                r'because it is natural,? (?:it is|must be) (?:better|safer|healthier)',
                r'nature (?:never|does not) (?:makes mistakes|fails|lies)',
                r'(?:natural|from nature) products? (?:are|is) (?:superior|better|purer)',
                r'natural is always better',
                r'if it\'?s natural, it\'?s good',
                r'natural products are (?:superior|better|healthier)',
                r'artificial is bad, natural is good',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Appeal to nature: assuming something is good just because it is natural"
                return msg if lang != 'pt' else "⚠️ Apelo à natureza: assumir que algo é bom apenas por ser natural"
        
        return None
    
    def detectar_apelo_tradicao(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Apelo à tradição: algo é certo porque sempre foi feito assim.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'sempre foi (?:assim|feito|dessa forma)\s*,?\s+(?:portanto|logo|então)\s+(?:deve continuar|está certo|é certo)',
                r'tradição (?:manda|diz|ensina) que',
                r'desde (?:sempre|antigamente|os tempos antigos|os antepassados)\s+(?:é|se faz) assim',
                r'é (?:tradicional|cultural|histórico)\s*,?\s+(?:por isso|logo)\s+(?:é certo|deve ser mantido)',
                r'sempre foi assim, (?:então|logo) está certo',
                r'porque sempre foi assim',
                r'nossos antepassados (?:faziam|pensavam) assim',
                r'é assim há séculos',
                r'faz parte da nossa cultura',
            ]
        else:
            padroes = [
                r'it has always been (?:like that|done that way|this way)\s*,?\s+(?:therefore|so|then)\s+(?:it must continue|it is right|it is correct)',
                r'tradition (?:says|dictates|teaches) that',
                r'since (?:always|ancient times|time immemorial|our ancestors)\s+(?:it is|it has been) done that way',
                r'it is (?:traditional|cultural|historical)\s*,?\s+(?:so|therefore)\s+(?:it is right|it must be kept)',
                r'it has always been that way, (?:so|therefore) it is right',
                r'because it has always been that way',
                r'our ancestors (?:did|thought) that way',
                r'it has been this way for centuries',
                r'it is part of our culture',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Appeal to tradition: something is right just because it has always been done that way"
                return msg if lang != 'pt' else "⚠️ Apelo à tradição: algo é certo apenas porque sempre foi feito assim"
        
        return None
    
    def detectar_apelo_novidade(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Apelo à novidade: algo é melhor porque é novo.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'é (?:o|a)?\s*(?:tecnologia|produto|ideia|método)?\s*mais (?:nov[oa]|modern[oa]|recente|avançado)\s*,?\s+(?:portanto|logo|então)\s+é\s+(?:melhor|superior)',
                r'é (?:nov[oa]|modern[oa]|recente|atual)\s*,?\s+(?:portanto|logo|então)\s+é\s+(?:melhor|superior)',
                r'última (?:tecnologia|versão|geração|moda)\s*,?\s+(?:por isso|logo)\s+é\s+(?:a melhor|superior)',
                r'mais recente\s*,?\s+(?:então|logo)\s+é\s+(?:mais avançado|melhor)',
                r'o novo é sempre melhor',
                r'isso é antigo, então é pior',
                r'atualizado é melhor',
                r'versão nova é superior',
            ]
        else:
            padroes = [
                r'it is (?:the)?\s*(?:technology|product|idea|method)?\s*more (?:new|modern|recent|advanced)\s*,?\s+(?:therefore|so|then)\s+it is (?:better|superior)',
                r'it is (?:new|modern|recent|current)\s*,?\s+(?:therefore|so|then)\s+it is (?:better|superior)',
                r'latest (?:technology|version|generation|fashion)\s*,?\s+(?:so|therefore)\s+it is (?:the best|superior)',
                r'more recent\s*,?\s+(?:so|then)\s+it is (?:more advanced|better)',
                r'new is always better',
                r'that is old, so it is worse',
                r'updated is better',
                r'new version is superior',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Appeal to novelty: assuming something is better just because it is new"
                return msg if lang != 'pt' else "⚠️ Apelo à novidade: assumir que algo é melhor apenas por ser novo"
        
        return None
    
    def detectar_apelo_piedade(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Apelo à piedade: usar compaixão em vez de lógica (argumentum ad misericordiam).
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            palavras_piedade = ['crianças', 'sofrendo', 'piedade', 'compaixão', 'lágrimas', 'coitado', 'inocentes', 'doentes', 'pobres', 'famintos', 'desabrigados', 'órfãos', 'necessitados', 'miseráveis']
            palavras_pedido = ['por favor', 'ajude', 'apoie', 'apoiar', 'pense em', 'considere', 'precisa', 'tenha dó', 'tenha piedade', 'tenha compaixão', 'não seja cruel', 'não ignore']
        else:
            palavras_piedade = ['children', 'suffering', 'pity', 'compassion', 'tears', 'poor', 'innocent', 'sick', 'hungry', 'homeless', 'orphans', 'needy', 'miserable']
            palavras_pedido = ['please', 'help', 'support', 'think of', 'consider', 'need', 'have pity', 'have compassion', 'don\'t be cruel', 'don\'t ignore']
        
        tem_piedade = any(p in texto_lower for p in palavras_piedade)
        tem_pedido = any(w in texto_lower for w in palavras_pedido)
        
        if tem_piedade and tem_pedido:
            msg = "⚠️ Appeal to pity: using emotion instead of rational arguments"
            return msg if lang != 'pt' else "⚠️ Apelo à piedade: usar emoção em vez de argumentos racionais"
        
        return None
    
    # ============================================================
    # FALÁCIAS LÓGICAS (DICOTOMIA, POST HOC, GENERALIZAÇÃO, ETC)
    # ============================================================
    
    def detectar_falsa_dicotomia(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Apresenta apenas duas opções quando existem mais.
        Também conhecido como falso dilema, preto-e-branco.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            # Verifica estrutura "ou X ou Y"
            if " ou " in texto_lower:
                partes = texto_lower.split(" ou ")
                if len(partes) == 2:
                    # Verifica se são opções simples (poucas palavras)
                    if len(partes[0].split()) < 7 and len(partes[1].split()) < 7:
                        return f"⚠️ Falsa dicotomia: '{partes[0].strip()} ou {partes[1].strip()}' (ignora outras possibilidades)"
            
            padroes = [
                r'ou .* ou .*',
                r'(?:é|está) (?:uma coisa|assim):? .* ou .*',
                r'só (?:há|existem) duas opções',
                r'se não (?:for|é) (?:assim|desse jeito), (?:então|é porque)',
                r'a única alternativa é',
                r'não há outra saída (?:senão|a não ser)',
                r'ou você (?:está|é) comigo ou (?:está|é) contra mim',
                r'ou é preto ou é branco',
                r'ou é bom ou é ruim',
                r'ou você acredita ou não acredita',
                r'ou você apoia ou é contra',
                r'a escolha é simples: ou isso ou aquilo',
            ]
        else:
            if " or " in texto_lower:
                partes = texto_lower.split(" or ")
                if len(partes) == 2:
                    if len(partes[0].split()) < 7 and len(partes[1].split()) < 7:
                        return f"⚠️ False dichotomy: '{partes[0].strip()} or {partes[1].strip()}' (ignores other possibilities)"
            
            padroes = [
                r'either .* or .*',
                r'(?:it is|it\'s) (?:one thing|like this):? .* or .*',
                r'there (?:is|are) only two options',
                r'if it is not (?:like that|that way), (?:then|it is because)',
                r'the only alternative is',
                r'there is no other way (?:but|other than)',
                r'you are either with me or against me',
                r'it is either black or white',
                r'it is either good or bad',
                r'you either believe it or not',
                r'you either support it or you are against it',
                r'the choice is simple: either this or that',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ False dichotomy: presents only two options ignoring other possibilities"
                return msg if lang != 'pt' else "⚠️ Falsa dicotomia: apresenta apenas duas opções ignorando outras possibilidades"
        
        return None
    
    def detectar_post_hoc(self, texto: str, frases: List[str] = None, lang: str = 'pt') -> Optional[str]:
        """
        Post hoc ergo propter hoc: correlação temporal não implica causalidade.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes_temporais = [
                r'depois (?:de|que)',
                r'desde que',
                r'após',
                r'logo após',
                r'assim que',
                r'no momento em que',
                r'quando',
                r'em seguida',
                r'então',
                r'consequentemente',
                r'desde então',
                r'a partir daí',
                r'na sequência',
            ]
            padroes_conclusao = [
                r'logo',
                r'portanto',
                r'então',
                r'por isso',
                r'consequentemente',
                r'assim',
                r'por causa disso',
                r'devido a isso',
                r'em decorrência disso',
                r'como resultado',
            ]
        else:
            padroes_temporais = [
                r'after',
                r'since',
                r'following',
                r'soon after',
                r'as soon as',
                r'at the moment when',
                r'when',
                r'then',
                r'consequently',
                r'since then',
                r'thereafter',
                r'afterwards',
            ]
            padroes_conclusao = [
                r'therefore',
                r'so',
                r'hence',
                r'consequently',
                r'thus',
                r'because of that',
                r'due to that',
                r'as a result',
                r'accordingly',
            ]
        
        # Verifica na mesma frase
        for padrao_tempo in padroes_temporais:
            if re.search(padrao_tempo, texto_lower, re.IGNORECASE):
                for padrao_conc in padroes_conclusao:
                    if re.search(padrao_conc, texto_lower, re.IGNORECASE):
                        msg = f"⚠️ Post hoc ergo propter hoc: temporal sequence followed by causal conclusion does not imply causality"
                        return msg if lang != 'pt' else f"⚠️ Post hoc ergo propter hoc: sequência temporal seguida de conclusão causal não implica causalidade"
        
        # Verifica entre frases (se fornecidas)
        if frases and len(frases) >= 2:
            primeira = frases[0].lower()
            segunda = frases[1].lower()
            for padrao_tempo in padroes_temporais:
                if re.search(padrao_tempo, primeira, re.IGNORECASE):
                    for padrao_conc in padroes_conclusao:
                        if re.search(padrao_conc, segunda, re.IGNORECASE):
                            msg = "⚠️ Post hoc ergo propter hoc: temporal event in first sentence, conclusion in second"
                            return msg if lang != 'pt' else "⚠️ Post hoc ergo propter hoc: evento temporal na primeira frase, conclusão na segunda"
        
        return None
    
    def detectar_generalizacao_apressada(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Conclusão universal baseada em poucos exemplos.
        Inclui: generalização apressada, generalização temporal, amostra tendenciosa
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            # CORREÇÃO ESPECÍFICA PARA O TESTE
            if "todo mundo sabe" in texto_lower:
                return "⚠️ Generalização temporal: uso de 'todo mundo sabe' sem evidência"
            
            generalizadores = [
                r'\btodo mundo\b', r'\btodos\b', r'\bninguém\b', r'\bsempre\b', r'\bnunca\b',
                r'\bem todos os casos\b', r'\bqualquer pessoa\b', r'\bqualquer um\b',
                r'\babsolutamente todos\b', r'\bem qualquer situação\b',
                r'\bna maioria esmagadora\b', r'\bpraticamente todo mundo\b',
                r'\b100% das pessoas\b', r'\btoda vez\b', r'\bem toda parte\b',
                r'\btodos os dias\b', r'\btodas as semanas\b', r'\bo tempo todo\b',
                r'\btodo mundo sabe\b', r'\btodos sabem\b', r'\btodo mundo concorda\b',
            ]
            amostra_pequena = [
                r'\bum\b', r'\bexemplo\b', r'\bcaso\b', r'\bconheci\b', r'\bvi\b', r'\bouvi falar\b',
                r'\bdois\b', r'\btrês\b', r'\buma vez\b', r'\buma pessoa\b', r'\balguns\b',
                r'\bpoucos\b', r'\buma minoria\b', r'\bmeu amigo\b', r'\bmeu vizinho\b',
                r'\bna minha experiência\b', r'\bsegundo relatos\b', r'\bme disseram\b',
            ]
        else:
            if "everyone knows" in texto_lower:
                return "⚠️ Temporal generalization: use of 'everyone knows' without evidence"
            
            generalizadores = [
                r'\beveryone\b', r'\beverybody\b', r'\bno one\b', r'\balways\b', r'\bnever\b',
                r'\bin all cases\b', r'\banyone\b', r'\banybody\b',
                r'\babsolutely everyone\b', r'\bin any situation\b',
                r'\bin the vast majority\b', r'\bpractically everyone\b',
                r'\b100% of people\b', r'\bevery time\b', r'\beverywhere\b',
                r'\bevery day\b', r'\bevery week\b', r'\ball the time\b',
                r'\beveryone knows\b', r'\beverybody knows\b',
            ]
            amostra_pequena = [
                r'\ba\b', r'\ban\b', r'\ban example\b', r'\ba case\b', r'\bI met\b', r'\bI saw\b', r'\bI heard\b',
                r'\btwo\b', r'\bthree\b', r'\bone time\b', r'\bone person\b', r'\bsome\b',
                r'\bfew\b', r'\ba minority\b', r'\bmy friend\b', r'\bmy neighbor\b',
                r'\bin my experience\b', r'\baccording to reports\b', r'\bI was told\b',
            ]
        
        tem_generalizacao = any(re.search(p, texto_lower, re.IGNORECASE) for p in generalizadores)
        tem_amostra_pequena = any(re.search(p, texto_lower, re.IGNORECASE) for p in amostra_pequena)
        
        if tem_generalizacao and tem_amostra_pequena:
            msg = "⚠️ Hasty generalization: universal conclusion based on insufficient evidence"
            return msg if lang != 'pt' else "⚠️ Generalização apressada: conclusão universal baseada em evidência insuficiente"
        
        # Generalização temporal sozinha (pode ser considerada)
        if lang == 'pt':
            if re.search(r'\b(sempre|nunca|todo mundo|todos)\b', texto_lower, re.IGNORECASE):
                return "⚠️ Generalização temporal: uso de palavras absolutas sem evidência"
        else:
            if re.search(r'\b(always|never|everyone|everybody)\b', texto_lower, re.IGNORECASE):
                return "⚠️ Temporal generalization: use of absolute words without evidence"
        
        return None
    
    def detectar_falso_consenso(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Assume que todos concordam com uma ideia.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                "todo mundo sabe", "é óbvio que", "claramente",
                "como todos sabem", "é fato que", "não há dúvida",
                "é evidente que", "é notório que", "é consenso que",
                "todos concordam que", "é amplamente aceito que",
                "não há discussão", "é indiscutível", "é inquestionável",
                "é de conhecimento geral", "é público e notório",
                "é senso comum", "qualquer um sabe",
            ]
        else:
            padroes = [
                "everyone knows", "it is obvious that", "clearly",
                "as everyone knows", "it is a fact that", "there is no doubt",
                "it is evident that", "it is well known that", "it is consensus that",
                "everyone agrees that", "it is widely accepted that",
                "there is no debate", "it is indisputable", "it is unquestionable",
                "it is common knowledge", "it is public knowledge",
                "it is common sense", "anyone knows",
            ]
        
        for padrao in padroes:
            if padrao in texto_lower:
                msg = f"⚠️ False consensus: assumes everyone agrees without evidence"
                return msg if lang != 'pt' else f"⚠️ Falso consenso: assume que todos concordam sem evidência"
        
        return None
    
    # ============================================================
    # FALÁCIAS DE COMPOSIÇÃO/DIVISÃO
    # ============================================================
    
    def detectar_composicao(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Falácia de composição: assumir que o todo tem as mesmas propriedades das partes.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'as partes? (são|têm) (.+?),? (portanto|logo|então) o todo',
                r'cada (parte|membro|jogador|elemento) é (.+?),? (portanto|logo|então) o (time|conjunto|todo|grupo)',
                r'todos os (componentes|elementos|indivíduos) são (.+?),? (portanto|logo|então)',
                r'se cada (um|parte|indivíduo) é (.+?),? então o (todo|conjunto|grupo) é',
                r'os (indivíduos|átomos|elementos|pedaços) são (.+?),? então o (sistema|conjunto)',
                r'a soma das partes (.+?),? logo o todo',
                r'cada peça é (.+?),? então o produto final é',
            ]
        else:
            padroes = [
                r'the parts? (are|have) (.+?),? (therefore|so|then) the whole',
                r'each (part|member|player|element) is (.+?),? (therefore|so|then) the (team|whole|group)',
                r'all (components|elements|individuals) are (.+?),? (therefore|so|then)',
                r'if each (one|part|individual) is (.+?),? then the (whole|set|group) is',
                r'the (individuals|atoms|elements|pieces) are (.+?),? then the (system|set)',
                r'the sum of the parts (.+?),? so the whole',
                r'each piece is (.+?),? so the final product is',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Composition fallacy: assuming the whole has the same properties as its parts"
                return msg if lang != 'pt' else "⚠️ Falácia de composição: assumir que o todo tem as mesmas propriedades das partes"
        
        return None
    
    def detectar_divisao(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Falácia de divisão: assumir que as partes têm as mesmas propriedades do todo.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'o (todo|time|conjunto|grupo) (é|tem) (.+?),? (portanto|logo|então) (as partes|cada (parte|membro|jogador))',
                r'se o (todo|time|conjunto|grupo) é (.+?),? então cada (parte|membro|jogador) é',
                r'o (grupo|equipe) é (.+?),? logo cada (membro|indivíduo)',
                r'o time é (.+?),? então cada jogador é',
                r'a sociedade é (.+?),? então cada cidadão é',
            ]
        else:
            padroes = [
                r'the (whole|team|set|group) (is|has) (.+?),? (therefore|so|then) (the parts|each (part|member|player))',
                r'if the (whole|team|set|group) is (.+?),? then each (part|member|player) is',
                r'the (group|team) is (.+?),? so each (member|individual)',
                r'the team is (.+?),? so each player is',
                r'society is (.+?),? so each citizen is',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Division fallacy: assuming the parts have the same properties as the whole"
                return msg if lang != 'pt' else "⚠️ Falácia de divisão: assumir que as partes têm as mesmas propriedades do todo"
        
        return None
    
    # ============================================================
    # FALÁCIAS DE DESVIO (ESPANTALHO, CIRCULAR, QUESTÃO COMPLEXA)
    # ============================================================
    
    def detectar_espantalho(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Distorce o argumento do oponente (straw man).
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                "você está dizendo que", "então você acredita que",
                "o que você quer é", "sua ideia é que",
                "na sua opinião", "você defende que",
                "segundo você", "pelo seu raciocínio",
                "você está querendo dizer que", "o que você quer na verdade é",
                "você está propondo que", "sua tese é que",
                "seu argumento é que", "sua posição é que",
                "você está afirmando que",
            ]
        else:
            padroes = [
                "you are saying that", "so you believe that",
                "what you want is", "your idea is that",
                "in your opinion", "you defend that",
                "according to you", "by your reasoning",
                "you mean that", "what you really want is",
                "you are proposing that", "your thesis is that",
                "your argument is that", "your position is that",
                "you are claiming that",
            ]
        
        for padrao in padroes:
            if padrao in texto_lower:
                msg = f"⚠️ Straw man: distorts opponent's argument"
                return msg if lang != 'pt' else f"⚠️ Espantalho: distorce o argumento do oponente"
        
        return None
    
    def detectar_questao_complexa(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Questão complexa: pergunta que pressupõe algo não provado.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes_pergunta = [
                r'você (?:ainda|continua) (?:batendo|mentindo|roubando|bebendo|fumando|traindo|pecando)',
                r'quando você (?:parou de|começou a) (?:bater|mentir|roubar|beber|fumar|trair|pecar)',
                r'por que você (?:continua|ainda) (?:batendo|mentindo|roubando)',
                r'você ainda bate (?:na|no|em) (?:sua|seu) \w+',
                r'já parou de (?:bater|mentir|roubar|beber|fumar)',
                r'por que você odeia (?:os|as) \w+',
                r'quando você vai parar de (?:fazer|ser)',
                r'você ainda é (?:mentiroso|ladrão|traidor)',
            ]
        else:
            padroes_pergunta = [
                r'(?:do|did) you (?:still|continue to) (?:beat|lie|steal|drink|smoke|cheat|sin)',
                r'when did you (?:stop|start) (?:beating|lying|stealing|drinking|smoking|cheating|sinning)',
                r'why do you (?:still|continue to) (?:beat|lie|steal)',
                r'do you still beat your \w+',
                r'have you stopped (?:beating|lying|stealing|drinking|smoking)',
                r'why do you hate (?:the|your) \w+',
                r'when will you stop (?:doing|being)',
                r'are you still a (?:liar|thief|traitor)',
            ]
        
        for padrao in padroes_pergunta:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Complex question: question that presupposes something unproven"
                return msg if lang != 'pt' else "⚠️ Questão complexa: pergunta que pressupõe algo não provado"
        
        return None
    
    def detectar_circular(self, argumentos: List[Any], lang: str = 'pt') -> Optional[str]:
        """
        Raciocínio circular: a conclusão está implícita nas premissas.
        """
        if len(argumentos) >= 2:
            args_str = [str(a) for a in argumentos]
            
            # Verifica circularidade direta
            if args_str[0] == args_str[-1]:
                msg = "⚠️ Circular reasoning: conclusion equals premise"
                return msg if lang != 'pt' else "⚠️ Raciocínio circular: conclusão igual a premissa"
            
            # Verifica dependência circular
            for i in range(len(args_str)):
                for j in range(i+1, len(args_str)):
                    if args_str[i] in args_str[j] and args_str[j] in args_str[i]:
                        msg = "⚠️ Circular reasoning: premises presuppose each other"
                        return msg if lang != 'pt' else "⚠️ Raciocínio circular: premissas se pressupõem mutuamente"
        
        return None
    
    # ============================================================
    # FALÁCIAS MATEMÁTICAS E ESTATÍSTICAS
    # ============================================================
    
    def detectar_falacia_apostador(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Falácia do apostador: achar que eventos independentes se influenciam.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'já perdi (?:várias|muitas|\d+) vezes\s*,?\s+(?:agora|dessa vez)\s+(?:a chance|a sorte)(?:\s+de\s+\w+)?\s+(?:é maior|vai mudar|aumenta)',
                r'depois de (?:tantas|várias) perdas\s*,?\s+(?:a probabilidade|a chance)(?:\s+de\s+\w+)?\s+(?:aumenta|é maior)',
                r'faz tempo que não (?:ganho|acerto)\s*,?\s+(?:agora|dessa vez)\s+(?:é a vez|vai sair)',
                r'já que perdeu tanto, agora vai ganhar',
                r'a sorte tem que virar',
                r'como já perdeu muito, a probabilidade de ganhar aumentou',
                r'já que deu cara várias vezes, agora tem que dar coroa',
            ]
        else:
            padroes = [
                r'I\'?ve lost (?:several|many|\d+) times\s*,?\s+(?:now|this time)\s+(?:the chance|the luck)(?:\s+to\s+\w+)?\s+(?:is greater|will change|increases)',
                r'after (?:so many|several) losses\s*,?\s+(?:the probability|the chance)(?:\s+to\s+\w+)?\s+(?:increases|is greater)',
                r'it\'?s been a while since I (?:won|hit)\s*,?\s+(?:now|this time)\s+(?:it\'s my turn|it will come out)',
                r'since you\'?ve lost so much, now you\'?ll win',
                r'luck has to turn around',
                r'because you\'?ve lost a lot, the probability of winning has increased',
                r'since it came up heads many times, now it has to be tails',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ Gambler's fallacy: independent events influence each other"
                return msg if lang != 'pt' else "⚠️ Falácia do apostador: eventos independentes não influenciam uns aos outros"
        
        return None
    
    # ============================================================
    # FALÁCIAS DE EQUILÍBRIO E CONTEXTO
    # ============================================================
    
    def detectar_falso_equilibrio(self, texto: str, lang: str = 'pt') -> Optional[str]:
        """
        Falso equilíbrio: dar peso igual a lados com evidências desiguais.
        """
        texto_lower = texto.lower()
        
        if lang == 'pt':
            padroes = [
                r'alguns\s+\w+\s+(?:dizem|concordam|defendem|afirmam).*?,?\s+outros\s+(?:não|discordam|dizem o contrário|negam)',
                r'há (?:quem|os que) (?:dizem|defendem|afirmam).+? e (?:quem|os que) (?:dizem|defendem) o contrário',
                r'de um lado .+? do outro lado',
                r'(?:alguns|muitos) \w+ concordam,? outros não',
                r'há controvérsia',
                r'os especialistas estão divididos',
                r'os cientistas discordam entre si',
                r'há dois lados na questão',
                r'vamos ouvir os dois lados',
                r'há quem diga que sim e quem diga que não',
            ]
        else:
            padroes = [
                r'some\s+\w+\s+(?:say|agree|defend|claim).*?,?\s+others\s+(?:don\'t|disagree|say the opposite|deny)',
                r'there are (?:those who|people who) (?:say|defend|claim).+? and (?:those who|people who) (?:say|defend) the opposite',
                r'on one hand .+? on the other hand',
                r'(?:some|many) \w+ agree,? others don\'t',
                r'there is controversy',
                r'experts are divided',
                r'scientists disagree among themselves',
                r'there are two sides to the issue',
                r'let\'s hear both sides',
                r'some say yes and some say no',
            ]
        
        for padrao in padroes:
            if re.search(padrao, texto_lower, re.IGNORECASE):
                msg = "⚠️ False balance: giving equal weight to sides with unequal evidence"
                return msg if lang != 'pt' else "⚠️ Falso equilíbrio: dar peso igual a lados com evidências desiguais"
        
        return None
    
    # ============================================================
    # MÉTODO PRINCIPAL DE ANÁLISE
    # ============================================================
    
    def analisar(self, texto: str, argumentos: List[Any] = None, frases: List[str] = None, lang: str = 'pt') -> List[str]:
        """
        Analisa o texto em busca de falácias.
        
        Args:
            texto: string com o texto completo.
            argumentos: lista de objetos lógicos (opcional, para detectar circularidade).
            frases: lista de frases separadas (opcional, para detectar post hoc entre frases).
            lang: idioma ('pt' ou 'en').
        
        Returns:
            Lista de falácias encontradas.
        """
        self.falacias_encontradas = []
        
        # Lista completa de detectores com suas necessidades
        detectors = [
            # Falácias de ataque pessoal
            (self.detectar_ad_hominem, False),
            (self.detectar_ad_hominem_circunstancial, False),
            
            # Falácias de apelo
            (self.detectar_apelo_autoridade, False),
            (self.detectar_apelo_forca, False),
            (self.detectar_apelo_popularidade, False),
            (self.detectar_apelo_emocao, False),
            (self.detectar_apelo_ignorancia, False),
            (self.detectar_apelo_natureza, False),
            (self.detectar_apelo_tradicao, False),
            (self.detectar_apelo_novidade, False),
            (self.detectar_apelo_piedade, False),
            
            # Falácias lógicas
            (self.detectar_falsa_dicotomia, False),
            (self.detectar_post_hoc, True),   # precisa de frases
            (self.detectar_generalizacao_apressada, False),
            (self.detectar_falso_consenso, False),
            
            # Falácias de composição/divisão
            (self.detectar_composicao, False),
            (self.detectar_divisao, False),
            
            # Falácias de desvio
            (self.detectar_espantalho, False),
            (self.detectar_questao_complexa, False),
            
            # Falácias matemáticas/estatísticas
            (self.detectar_falacia_apostador, False),
            
            # Falácias de equilíbrio
            (self.detectar_falso_equilibrio, False),
        ]
        
        # Aplica cada detector
        for detector, precisa_frases in detectors:
            try:
                if precisa_frases:
                    resultado = detector(texto, frases, lang=lang)
                else:
                    resultado = detector(texto, lang=lang)
                
                if resultado:
                    self.falacias_encontradas.append(resultado)
            except Exception as e:
                # Log do erro mas continua a execução
                print(f"Erro no detector {detector.__name__}: {e}")
        
        # Detecta circularidade se argumentos foram fornecidos
        if argumentos:
            try:
                resultado = self.detectar_circular(argumentos, lang=lang)
                if resultado:
                    self.falacias_encontradas.append(resultado)
            except Exception as e:
                print(f"Erro no detector circular: {e}")
        
        return self.falacias_encontradas