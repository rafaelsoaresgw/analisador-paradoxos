import re

class DetectorFalacias:
    """Detector de falácias com análise semântica avançada (multilíngue)"""

    def __init__(self):
        self.falacias_encontradas = []

    def analisar_contexto(self, texto, lang='pt'):
        """
        Analisa o contexto do texto para palavras‑chave de religião, política, ciência e emoção.
        Agora com suporte a inglês.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            contexto = {
                'tem_religiao': any(p in texto_lower for p in ["deus", "bíblia", "padre", "pastor", "igreja", "fé"]),
                'tem_politica': any(p in texto_lower for p in ["política", "governo", "presidente", "partido", "eleição"]),
                'tem_ciencia': any(p in texto_lower for p in ["ciência", "cientista", "pesquisa", "estudo", "dados"]),
                'tem_emocao': any(p in texto_lower for p in ["sentimento", "emoção", "amor", "ódio", "medo"]),
            }
        else:  # inglês
            contexto = {
                'tem_religiao': any(p in texto_lower for p in ["god", "bible", "priest", "pastor", "church", "faith"]),
                'tem_politica': any(p in texto_lower for p in ["politics", "government", "president", "party", "election"]),
                'tem_ciencia': any(p in texto_lower for p in ["science", "scientist", "research", "study", "data"]),
                'tem_emocao': any(p in texto_lower for p in ["feeling", "emotion", "love", "hate", "fear"]),
            }
        return contexto

    def detectar_ad_hominem(self, texto, lang='pt'):
        texto_lower = texto.lower()
        contexto = self.analisar_contexto(texto, lang)

        # Padrão específico: "você não é um X" / "you are not a X"
        if lang == 'pt':
            match = re.search(r'você não é (?:um|uma) (\w+)', texto_lower)
            if match:
                profissao = match.group(1)
                if contexto['tem_ciencia'] and profissao in ['cientista', 'pesquisador', 'especialista']:
                    return f"⚠️ Ad hominem: ataque à credencial científica (você não é {profissao})"
                return f"⚠️ Ad hominem: ataque à credencial (você não é {profissao})"
        else:
            match = re.search(r'you are not (?:a|an) (\w+)', texto_lower)
            if match:
                profession = match.group(1)
                if contexto['tem_ciencia'] and profession in ['scientist', 'researcher', 'specialist']:
                    return f"⚠️ Ad hominem: attack on scientific credential (you are not a {profession})"
                return f"⚠️ Ad hominem: attack on credential (you are not a {profession})"

        # Padrões gerais
        if lang == 'pt':
            padroes = [
                (r"você (?:é|não é) (\w+)", "ataque direto"),
                (r"tu (?:és|não és) (\w+)", "ataque direto"),
                (r"você não (?:entende|sabe|compreende)", "ataque à capacidade"),
                (r"você não pode falar porque", "desqualificação"),
                (r"seu argumento não vale porque", "desqualificação"),
                (r"você está errado porque", "ataque pessoal"),
                (r"ignorante|burro|idiota", "xingamento"),
            ]
        else:
            padroes = [
                (r"you (?:are|are not) (\w+)", "direct attack"),
                (r"you don't (?:understand|know|comprehend)", "attack on ability"),
                (r"you can't speak because", "disqualification"),
                (r"your argument is worthless because", "disqualification"),
                (r"you are wrong because", "personal attack"),
                (r"ignorant|stupid|idiot", "insult"),
            ]

        for padrao, tipo in padroes:
            match = re.search(padrao, texto_lower)
            if match:
                if len(match.groups()) > 0:
                    alvo = match.group(1)
                    return f"⚠️ Ad hominem: {tipo} ('{alvo}')"
                else:
                    return f"⚠️ Ad hominem: {tipo}"
        return None

    def detectar_ad_hominem_circunstancial(self, texto, lang='pt'):
        """Ataca a pessoa por suposto interesse pessoal."""
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'você só (?:diz|defende) isso porque (?:ganha dinheiro|tem interesse|é (?:funcionário|contratado))',
                r'você está falando isso porque (?:te convém|te beneficia)',
            ]
        else:
            padroes = [
                r'you only (?:say|defend) that because (?:you earn money|you have an interest|you are (?:an employee|hired))',
                r'you are saying that because (?:it suits you|it benefits you)',
            ]
        for padrao in padroes:
            if re.search(padrao, texto_lower):
                msg = "⚠️ Ad hominem circumstantial: attacks based on supposed personal interest"
                return msg if lang != 'pt' else "⚠️ Ad hominem circunstancial: ataca por suposto interesse pessoal"
        return None

    def detectar_apelo_autoridade(self, texto, lang='pt'):
        texto_lower = texto.lower()
        contexto = self.analisar_contexto(texto, lang)

        if lang == 'pt':
            autoridades_religiosas = ["padre", "pastor", "papa", "bispo", "apóstolo", "profeta"]
            autoridades_academicas = ["cientista", "professor", "doutor", "pesquisador", "especialista"]
            autoridades_midia = ["famoso", "celebridade", "jornalista", "apresentador"]
            padroes = [
                "segundo", "como disse", "de acordo com", "conforme",
                "é sabido por todos que", "especialistas dizem",
                "está escrito que", "a bíblia diz", "o papa disse",
                "o padre disse", "o pastor disse", "o professor disse",
            ]
        else:
            autoridades_religiosas = ["priest", "pastor", "pope", "bishop", "apostle", "prophet"]
            autoridades_academicas = ["scientist", "professor", "doctor", "researcher", "specialist"]
            autoridades_midia = ["celebrity", "famous", "journalist", "tv host"]
            padroes = [
                "according to", "as said by", "in accordance with",
                "it is known by everyone that", "experts say",
                "it is written that", "the bible says", "the pope said",
                "the priest said", "the pastor said", "the professor said",
            ]

        for padrao in padroes:
            if padrao in texto_lower:
                for autoridade in autoridades_religiosas:
                    if autoridade in texto_lower:
                        if not contexto['tem_religiao']:
                            return f"⚠️ Apelo à autoridade religiosa irrelevante: '{padrao} {autoridade}'" if lang == 'pt' else f"⚠️ Irrelevant religious authority: '{padrao} {autoridade}'"
                        return f"⚠️ Apelo à autoridade: '{padrao} {autoridade}'" if lang == 'pt' else f"⚠️ Appeal to authority: '{padrao} {autoridade}'"
                for autoridade in autoridades_academicas:
                    if autoridade in texto_lower:
                        if not contexto['tem_ciencia']:
                            return f"⚠️ Apelo à autoridade acadêmica irrelevante: '{padrao} {autoridade}'" if lang == 'pt' else f"⚠️ Irrelevant academic authority: '{padrao} {autoridade}'"
                        return f"⚠️ Apelo à autoridade: '{padrao} {autoridade}'" if lang == 'pt' else f"⚠️ Appeal to authority: '{padrao} {autoridade}'"
                for autoridade in autoridades_midia:
                    if autoridade in texto_lower:
                        return f"⚠️ Apelo à autoridade midiática: '{padrao} {autoridade}' (autoridade não qualificada)" if lang == 'pt' else f"⚠️ Appeal to media authority: '{padrao} {autoridade}' (unqualified authority)"
        return None

    def detectar_apelo_forca(self, texto, lang='pt'):
        """Apelo à força: usar ameaça em vez de argumento."""
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'se não (?:concordar|aceitar|fizer),? (?:vai sofrer|terá problemas|pior para você)',
                r'é melhor (?:aceitar|concordar) (?:ou então|senão)',
                r'você será (?:punido|demitido) se não',
            ]
        else:
            padroes = [
                r'if you don\'?t (?:agree|accept|do it),? (?:you will suffer|you will have problems|it will be worse for you)',
                r'you\'?d better (?:accept|agree) (?:or else|otherwise)',
                r'you will be (?:punished|fired) if you don\'?t',
            ]
        for padrao in padroes:
            if re.search(padrao, texto_lower):
                msg = "⚠️ Appeal to force: using threat instead of argument"
                return msg if lang != 'pt' else "⚠️ Apelo à força: usar ameaça em vez de argumento"
        return None

    def detectar_apelo_popularidade(self, texto, lang='pt'):
        """Apelo à popularidade: algo é verdade porque muitos acreditam."""
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'a maioria (?:acredita|pensa) que,? (?:portanto|logo)',
                r'todo mundo (?:está fazendo|acha) isso,? (?:então|logo)',
                r'é (?:moda|tendência),? (?:por isso|logo)',
            ]
        else:
            padroes = [
                r'the majority (?:believes|thinks) that,? (?:therefore|so)',
                r'everyone (?:is doing|thinks) that,? (?:so|then)',
                r'it is (?:fashionable|a trend),? (?:so|therefore)',
            ]
        for padrao in padroes:
            if re.search(padrao, texto_lower):
                msg = "⚠️ Appeal to popularity: something is true because many believe it"
                return msg if lang != 'pt' else "⚠️ Apelo à popularidade: algo é verdade porque muitos acreditam"
        return None

    def detectar_falsa_dicotomia(self, texto, lang='pt'):
        texto_lower = texto.lower()

        if lang == 'pt':
            padroes = [
                r'ou .* ou .*',
                r'(?:é|está) (?:uma coisa|assim):? .* ou .*',
                r'só (?:há|existem) duas opções',
                r'se não (?:for|é) (?:assim|desse jeito), (?:então|é porque)',
                r'a única alternativa é',
                r'não há outra saída (?:senão|a não ser)',
            ]
            # Verifica estrutura "ou X ou Y"
            if " ou " in texto_lower:
                partes = texto_lower.split(" ou ")
                if len(partes) == 2 and len(partes[0].split()) < 5 and len(partes[1].split()) < 5:
                    # CORREÇÃO: "Falsa" com maiúsculo para corresponder ao teste
                    return f"⚠️ Possível Falsa dicotomia: '{partes[0].strip()} ou {partes[1].strip()}'"
        else:
            padroes = [
                r'either .* or .*',
                r'(?:it is|it\'s) (?:one thing|like this):? .* or .*',
                r'there (?:is|are) only two options',
                r'if it is not (?:like that|that way), (?:then|it is because)',
                r'the only alternative is',
                r'there is no other way (?:but|other than)',
            ]
            if " or " in texto_lower:
                partes = texto_lower.split(" or ")
                if len(partes) == 2 and len(partes[0].split()) < 5 and len(partes[1].split()) < 5:
                    return f"⚠️ Possible false dichotomy: '{partes[0].strip()} or {partes[1].strip()}'"

        for padrao in padroes:
            if re.search(padrao, texto_lower):
                msg = "⚠️ False dichotomy: presents only two options ignoring other possibilities"
                return msg if lang != 'pt' else "⚠️ Falsa dicotomia: apresenta apenas duas opções ignorando outras possibilidades"
        return None

    def detectar_post_hoc(self, texto, frases=None, lang='pt'):
        """
        Detecta a falácia post hoc ergo propter hoc.
        Se frases (lista de strings) for fornecida, analisa relações entre elas.
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
            ]
            padroes_conclusao = [
                r'logo',
                r'portanto',
                r'então',
                r'por isso',
                r'consequentemente',
                r'assim',
                r'por causa disso',
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
            ]
            padroes_conclusao = [
                r'therefore',
                r'so',
                r'hence',
                r'consequently',
                r'thus',
                r'because of that',
            ]

        # Verifica se há sequência temporal + conclusão na mesma frase
        for padrao_tempo in padroes_temporais:
            if re.search(padrao_tempo, texto_lower):
                for padrao_conc in padroes_conclusao:
                    if re.search(padrao_conc, texto_lower):
                        msg = f"⚠️ Post hoc ergo propter hoc: temporal sequence ('{padrao_tempo}') followed by causal conclusion ('{padrao_conc}') does not imply causality"
                        return msg if lang != 'pt' else f"⚠️ Post hoc ergo propter hoc: correlação temporal ('{padrao_tempo}') seguida de conclusão causal ('{padrao_conc}') não implica causalidade"

        # Se temos múltiplas frases, verifica a primeira com tempo e a segunda com conclusão
        if frases and len(frases) >= 2:
            primeira = frases[0].lower()
            segunda = frases[1].lower()
            for padrao_tempo in padroes_temporais:
                if re.search(padrao_tempo, primeira):
                    for padrao_conc in padroes_conclusao:
                        if re.search(padrao_conc, segunda):
                            msg = "⚠️ Post hoc ergo propter hoc: temporal event in first sentence, conclusion in second"
                            return msg if lang != 'pt' else "⚠️ Post hoc ergo propter hoc: evento temporal na primeira frase, conclusão na segunda"
        return None

    def detectar_generalizacao_apressada(self, texto, lang='pt'):
        texto_lower = texto.lower()

        if lang == 'pt':
            generalizadores = [
                r'\btodo mundo\b', r'\btodos\b', r'\bninguém\b', r'\bsempre\b', r'\bnunca\b',
                r'\bem todos os casos\b', r'\bqualquer pessoa\b', r'\bqualquer um\b',
                r'\babsolutamente todos\b', r'\bem qualquer situação\b',
            ]
            amostra_pequena = [r'\bum\b', r'\bexemplo\b', r'\bcaso\b', r'\bconheci\b', r'\bvi\b', r'\bouvi falar\b']
        else:
            generalizadores = [
                r'\beveryone\b', r'\beverybody\b', r'\bno one\b', r'\balways\b', r'\bnever\b',
                r'\bin all cases\b', r'\banyone\b', r'\banybody\b',
                r'\babsolutely everyone\b', r'\bin any situation\b',
            ]
            amostra_pequena = [r'\ba\b', r'\ban\b', r'\ban example\b', r'\ba case\b', r'\bI met\b', r'\bI saw\b', r'\bI heard\b']

        tem_generalizacao = any(re.search(p, texto_lower) for p in generalizadores)
        tem_amostra_pequena = any(re.search(p, texto_lower) for p in amostra_pequena)

        if tem_generalizacao and tem_amostra_pequena:
            msg = "⚠️ Hasty generalization: universal conclusion based on insufficient evidence"
            return msg if lang != 'pt' else "⚠️ Generalização apressada: conclusão universal baseada em evidência insuficiente"

        # Generalização temporal sozinha (pode ser considerada)
        if lang == 'pt':
            if re.search(r'\b(sempre|nunca|todo mundo|todos os dias|todas as semanas)\b', texto_lower):
                return "⚠️ Generalização temporal: uso de palavras absolutas sem evidência"
        else:
            if re.search(r'\b(always|never|everyone|every day|every week)\b', texto_lower):
                return "⚠️ Temporal generalization: use of absolute words without evidence"
        return None

    def detectar_circular(self, argumentos, lang='pt'):
        if len(argumentos) >= 2:
            args_str = [str(a) for a in argumentos]
            if args_str[0] == args_str[-1]:
                msg = "⚠️ Circular reasoning: conclusion equals premise"
                return msg if lang != 'pt' else "⚠️ Raciocínio circular: conclusão igual a premissa"
            for i in range(len(args_str)):
                for j in range(i+1, len(args_str)):
                    if args_str[i] in args_str[j] and args_str[j] in args_str[i]:
                        msg = "⚠️ Circular reasoning: premises presuppose each other"
                        return msg if lang != 'pt' else "⚠️ Raciocínio circular: premissas se pressupõem mutuamente"
        return None

    def detectar_falso_consenso(self, texto, lang='pt'):
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                "todo mundo sabe", "é óbvio que", "claramente",
                "como todos sabem", "é fato que", "não há dúvida"
            ]
        else:
            padroes = [
                "everyone knows", "it is obvious that", "clearly",
                "as everyone knows", "it is a fact that", "there is no doubt"
            ]
        for padrao in padroes:
            if padrao in texto_lower:
                msg = f"⚠️ False consensus: assumes everyone agrees without evidence ('{padrao}')"
                return msg if lang != 'pt' else f"⚠️ Falso consenso: assume que todos concordam sem evidência ('{padrao}')"
        return None

    def detectar_espantalho(self, texto, lang='pt'):
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                "você está dizendo que", "então você acredita que",
                "o que você quer é", "sua ideia é que"
            ]
        else:
            padroes = [
                "you are saying that", "so you believe that",
                "what you want is", "your idea is that"
            ]
        for padrao in padroes:
            if padrao in texto_lower:
                msg = f"⚠️ Straw man: distorts opponent's argument ('{padrao}')"
                return msg if lang != 'pt' else f"⚠️ Espantalho: distorce o argumento do oponente ('{padrao}')"
        return None

    def detectar_apelo_emocao(self, texto, lang='pt'):
        texto_lower = texto.lower()
        if lang == 'pt':
            palavras_emocao = ["sofrimento", "dor", "medo", "ódio", "amor", "esperança", "crianças", "família", "futuro"]
        else:
            palavras_emocao = ["suffering", "pain", "fear", "hate", "love", "hope", "children", "family", "future"]
        for palavra in palavras_emocao:
            if palavra in texto_lower:
                msg = f"⚠️ Appeal to emotion: use of the word '{palavra}' to influence sentiment"
                return msg if lang != 'pt' else f"⚠️ Apelo à emoção: uso da palavra '{palavra}' para influenciar sentimento"
        return None

    # ===== NOVAS FALÁCIAS =====

    def detectar_composicao(self, texto, lang='pt'):
        """
        Falácia de composição: assumir que o todo tem as mesmas propriedades das partes.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'as partes? (são|têm) (.+?),? (portanto|logo|então) o todo',
                r'cada (parte|membro|jogador) é (.+?),? (portanto|logo|então) o (time|conjunto|todo)',
                r'todos os (componentes|elementos) são (.+?),? (portanto|logo|então)',
                r'se cada (um|parte) é (.+?),? então o (todo|conjunto) é',
            ]
        else:
            padroes = [
                r'the parts? (are|have) (.+?),? (therefore|so|then) the whole',
                r'each (part|member|player) is (.+?),? (therefore|so|then) the (team|whole)',
                r'all (components|elements) are (.+?),? (therefore|so|then)',
                r'if each (one|part) is (.+?),? then the (whole|set) is',
            ]
        for padrao in padroes:
            if re.search(padrao, texto_lower):
                msg = "⚠️ Composition fallacy: assuming the whole has the same properties as its parts"
                return msg if lang != 'pt' else "⚠️ Falácia de composição: assumir que o todo tem as mesmas propriedades das partes"
        return None

    def detectar_divisao(self, texto, lang='pt'):
        """
        Falácia de divisão: assumir que as partes têm as mesmas propriedades do todo.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'o (todo|time|conjunto) (é|tem) (.+?),? (portanto|logo|então) (as partes|cada (parte|membro|jogador))',
                r'se o (todo|time|conjunto) é (.+?),? então cada (parte|membro|jogador) é',
            ]
        else:
            padroes = [
                r'the (whole|team|set) (is|has) (.+?),? (therefore|so|then) (the parts|each (part|member|player))',
                r'if the (whole|team|set) is (.+?),? then each (part|member|player) is',
            ]
        for padrao in padroes:
            if re.search(padrao, texto_lower):
                msg = "⚠️ Division fallacy: assuming the parts have the same properties as the whole"
                return msg if lang != 'pt' else "⚠️ Falácia de divisão: assumir que as partes têm as mesmas propriedades do todo"
        return None

    def detectar_apelo_ignorancia(self, texto, lang='pt'):
        """
        Apelo à ignorância: "Não provaram que é falso, logo é verdadeiro" (ou vice-versa).
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'não (?:prov[oa]r?am|demonstr[oa]r?am) que é falso,? (?:portanto|logo|então) é verdadeiro',
                r'não (?:prov[oa]r?am|demonstr[oa]r?am) que é verdadeiro,? (?:portanto|logo|então) é falso',
                r'ninguém (?:conseguiu )?provou? que (.+?) (?:é falso|não existe),? (?:portanto|logo|então) (.+?) (?:é verdadeiro|existe)',
                r'ninguém (?:conseguiu )?provou? que (.+?) não existe,? (?:portanto|logo|então) \1 existe',
            ]
        else:
            padroes = [
                r'nobody has (?:proven|shown) that it is false,? (?:therefore|so|then) it is true',
                r'nobody has (?:proven|shown) that it is true,? (?:therefore|so|then) it is false',
                r'no one has (?:proven|shown) that (.+?) (?:is false|does not exist),? (?:therefore|so|then) (.+?) (?:is true|exists)',
                r'no one has (?:proven|shown) that (.+?) does not exist,? (?:therefore|so|then) \1 exists',
            ]
        for padrao in padroes:
            if re.search(padrao, texto_lower):
                msg = "⚠️ Appeal to ignorance: absence of proof is used as proof"
                return msg if lang != 'pt' else "⚠️ Apelo à ignorância: a ausência de prova é usada como prova"
        return None

    def detectar_apelo_natureza(self, texto, lang='pt'):
        """
        Apelo à natureza: algo é bom porque é natural.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'é natural,? (?:portanto|logo|então) é (?:melhor|bom|seguro)',
                r'por ser natural,? (?:é|deve ser) (?:melhor|mais seguro|mais saudável)',
                r'natureza (?:não|jamais) (?:erra|falha)',
                r'produto (?:natural|da natureza) (?:é|são) (?:superiores|melhores)',
            ]
        else:
            padroes = [
                r'it is natural,? (?:therefore|so|then) it is (?:better|good|safe)',
                r'because it is natural,? (?:it is|must be) (?:better|safer|healthier)',
                r'nature (?:never|does not) (?:makes mistakes|fails)',
                r'(?:natural|from nature) products? (?:are|is) (?:superior|better)',
            ]
        if any(re.search(p, texto_lower) for p in padroes):
            msg = "⚠️ Appeal to nature: assuming something is good just because it is natural"
            return msg if lang != 'pt' else "⚠️ Apelo à natureza: assumir que algo é bom apenas por ser natural"
        return None

    def detectar_apelo_tradicao(self, texto, lang='pt'):
        """
        Apelo à tradição: algo é certo porque sempre foi feito assim.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'sempre foi (?:assim|feito)\s*,?\s+(?:portanto|logo|então)\s+(?:deve continuar|está certo)',
                r'tradição (?:manda|diz) que',
                r'desde (?:sempre|antigamente)\s+(?:é|se faz) assim',
                r'é (?:tradicional|cultural)\s*,?\s+(?:por isso|logo)\s+(?:é certo|deve ser mantido)',
            ]
        else:
            padroes = [
                r'it has always been (?:like that|done that way)\s*,?\s+(?:therefore|so|then)\s+(?:it must continue|it is right)',
                r'tradition (?:says|dictates) that',
                r'since (?:always|ancient times)\s+(?:it is|it has been) done that way',
                r'it is (?:traditional|cultural)\s*,?\s+(?:so|therefore)\s+(?:it is right|it must be kept)',
            ]
        if any(re.search(p, texto_lower) for p in padroes):
            msg = "⚠️ Appeal to tradition: something is right just because it has always been done that way"
            return msg if lang != 'pt' else "⚠️ Apelo à tradição: algo é certo apenas porque sempre foi feito assim"
        return None

    def detectar_apelo_novidade(self, texto, lang='pt'):
        """
        Apelo à novidade: algo é melhor porque é novo.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'é (?:o|a)?\s*(?:tecnologia|produto)?\s*mais (?:nov[oa]|modern[oa]|recente)\s*,?\s+(?:portanto|logo|então)\s+é\s+(?:melhor|superior)',
                r'é (?:nov[oa]|modern[oa]|recente)\s*,?\s+(?:portanto|logo|então)\s+é\s+(?:melhor|superior)',
                r'última (?:tecnologia|versão|geração)\s*,?\s+(?:por isso|logo)\s+é\s+(?:a melhor|superior)',
                r'mais recente\s*,?\s+(?:então|logo)\s+é\s+(?:mais avançado|melhor)',
            ]
        else:
            padroes = [
                r'it is (?:the)?\s*(?:technology|product)?\s*more (?:new|modern|recent)\s*,?\s+(?:therefore|so|then)\s+it is (?:better|superior)',
                r'it is (?:new|modern|recent)\s*,?\s+(?:therefore|so|then)\s+it is (?:better|superior)',
                r'latest (?:technology|version|generation)\s*,?\s+(?:so|therefore)\s+it is (?:the best|superior)',
                r'more recent\s*,?\s+(?:so|then)\s+it is (?:more advanced|better)',
            ]
        if any(re.search(p, texto_lower) for p in padroes):
            msg = "⚠️ Appeal to novelty: assuming something is better just because it is new"
            return msg if lang != 'pt' else "⚠️ Apelo à novidade: assumir que algo é melhor apenas por ser novo"
        return None

    def detectar_questao_complexa(self, texto, lang='pt'):
        """
        Questão complexa: pergunta que pressupõe algo não provado.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes_pergunta = [
                r'você (?:ainda|continua) (?:batendo|mentindo|roubando|bebendo|fumando)',
                r'quando você (?:parou de|começou a) (?:bater|mentir|roubar|beber|fumar)',
                r'por que você (?:continua|ainda) (?:batendo|mentindo|roubando)',
                r'você ainda bate (?:na|no|em) (?:sua|seu) \w+',
            ]
        else:
            padroes_pergunta = [
                r'(?:do|did) you (?:still|continue to) (?:beat|lie|steal|drink|smoke)',
                r'when did you (?:stop|start) (?:beating|lying|stealing|drinking|smoking)',
                r'why do you (?:still|continue to) (?:beat|lie|steal)',
                r'do you still beat your \w+',
            ]
        if any(re.search(p, texto_lower) for p in padroes_pergunta):
            msg = "⚠️ Complex question: question that presupposes something unproven"
            return msg if lang != 'pt' else "⚠️ Questão complexa: pergunta que pressupõe algo não provado"
        return None

    def detectar_falacia_apostador(self, texto, lang='pt'):
        """
        Falácia do apostador: achar que eventos independentes se influenciam.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'já perdi (?:várias|muitas|\d+) vezes\s*,?\s+(?:agora|dessa vez)\s+(?:a chance|a sorte)(?:\s+de\s+\w+)?\s+(?:é maior|vai mudar)',
                r'depois de (?:tantas|várias) perdas\s*,?\s+(?:a probabilidade|a chance)(?:\s+de\s+\w+)?\s+(?:aumenta|é maior)',
                r'faz tempo que não (?:ganho|acerto)\s*,?\s+(?:agora|dessa vez)\s+(?:é a vez|vai sair)',
            ]
        else:
            padroes = [
                r'I\'?ve lost (?:several|many|\d+) times\s*,?\s+(?:now|this time)\s+(?:the chance|the luck)(?:\s+to\s+\w+)?\s+(?:is greater|will change)',
                r'after (?:so many|several) losses\s*,?\s+(?:the probability|the chance)(?:\s+to\s+\w+)?\s+(?:increases|is greater)',
                r'it\'?s been a while since I (?:won|hit)\s*,?\s+(?:now|this time)\s+(?:it\'s my turn|it will come out)',
            ]
        if any(re.search(p, texto_lower) for p in padroes):
            msg = "⚠️ Gambler's fallacy: independent events influence each other"
            return msg if lang != 'pt' else "⚠️ Falácia do apostador: eventos independentes não influenciam uns aos outros"
        return None

    def detectar_apelo_piedade(self, texto, lang='pt'):
        """
        Apelo à piedade: usar compaixão em vez de lógica.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            palavras_piedade = ['crianças', 'sofrendo', 'piedade', 'compaixão', 'lágrimas', 'coitado', 'inocentes']
            palavras_pedido = ['por favor', 'ajude', 'apoie', 'apoiar', 'pense em', 'considere', 'precisa']
        else:
            palavras_piedade = ['children', 'suffering', 'pity', 'compassion', 'tears', 'poor', 'innocent']
            palavras_pedido = ['please', 'help', 'support', 'think of', 'consider', 'need']
        if any(p in texto_lower for p in palavras_piedade) and any(w in texto_lower for w in palavras_pedido):
            msg = "⚠️ Appeal to pity: using emotion instead of rational arguments"
            return msg if lang != 'pt' else "⚠️ Apelo à piedade: usar emoção em vez de argumentos racionais"
        return None

    def detectar_falso_equilibrio(self, texto, lang='pt'):
        """
        Falso equilíbrio: dar peso igual a lados com evidências desiguais.
        """
        texto_lower = texto.lower()
        if lang == 'pt':
            padroes = [
                r'alguns\s+\w+\s+(?:dizem|concordam|defendem).*?,?\s+outros\s+(?:não|discordam|dizem o contrário)',
                r'há (?:quem|os que) (?:dizem|defendem).+? e (?:quem|os que) (?:dizem|defendem) o contrário',
                r'de um lado .+? do outro lado',
                r'(?:alguns|muitos) \w+ concordam,? outros não',
            ]
        else:
            padroes = [
                r'some\s+\w+\s+(?:say|agree|defend).*?,?\s+others\s+(?:don\'t|disagree|say the opposite)',
                r'there are (?:those who|people who) (?:say|defend).+? and (?:those who|people who) (?:say|defend) the opposite',
                r'on one hand .+? on the other hand',
                r'(?:some|many) \w+ agree,? others don\'t',
            ]
        if any(re.search(p, texto_lower, re.IGNORECASE) for p in padroes):
            msg = "⚠️ False balance: giving equal weight to sides with unequal evidence"
            return msg if lang != 'pt' else "⚠️ Falso equilíbrio: dar peso igual a lados com evidências desiguais"
        return None

    def analisar(self, texto, argumentos=None, frases=None, lang='pt'):
        """
        Analisa o texto em busca de falácias.
        :param texto: string com o texto completo.
        :param argumentos: lista de objetos lógicos (opcional, para detectar circularidade).
        :param frases: lista de frases separadas (opcional, para detectar post hoc entre frases).
        :param lang: idioma ('pt' ou 'en').
        """
        self.falacias_encontradas = []
        detectors = [
            (self.detectar_ad_hominem, False),
            (self.detectar_ad_hominem_circunstancial, False),
            (self.detectar_apelo_autoridade, False),
            (self.detectar_apelo_forca, False),
            (self.detectar_apelo_popularidade, False),
            (self.detectar_falsa_dicotomia, False),
            (self.detectar_post_hoc, True),   # precisa de frases
            (self.detectar_generalizacao_apressada, False),
            (self.detectar_falso_consenso, False),
            (self.detectar_espantalho, False),
            (self.detectar_apelo_emocao, False),
            (self.detectar_composicao, False),
            (self.detectar_divisao, False),
            (self.detectar_apelo_ignorancia, False),
            (self.detectar_apelo_natureza, False),
            (self.detectar_apelo_tradicao, False),
            (self.detectar_apelo_novidade, False),
            (self.detectar_questao_complexa, False),
            (self.detectar_falacia_apostador, False),
            (self.detectar_apelo_piedade, False),
            (self.detectar_falso_equilibrio, False),
        ]
        for detector, precisa_frases in detectors:
            if precisa_frases:
                resultado = detector(texto, frases, lang=lang)
            else:
                resultado = detector(texto, lang=lang)
            if resultado:
                self.falacias_encontradas.append(resultado)
        if argumentos:
            resultado = self.detectar_circular(argumentos, lang=lang)
            if resultado:
                self.falacias_encontradas.append(resultado)
        return self.falacias_encontradas