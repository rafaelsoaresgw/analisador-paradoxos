import re

class DetectorFalacias:
    """Detector de falácias com análise semântica avançada"""

    def __init__(self):
        self.falacias_encontradas = []

    def analisar_contexto(self, texto):
        contexto = {
            'tem_religiao': any(p in texto.lower() for p in ["deus", "bíblia", "padre", "pastor", "igreja", "fé"]),
            'tem_politica': any(p in texto.lower() for p in ["política", "governo", "presidente", "partido", "eleição"]),
            'tem_ciencia': any(p in texto.lower() for p in ["ciência", "cientista", "pesquisa", "estudo", "dados"]),
            'tem_emocao': any(p in texto.lower() for p in ["sentimento", "emoção", "amor", "ódio", "medo"]),
        }
        return contexto

    def detectar_ad_hominem(self, texto):
        texto_lower = texto.lower()
        contexto = self.analisar_contexto(texto)

        # Padrão específico: "você não é um X"
        match = re.search(r'você não é (?:um|uma) (\w+)', texto_lower)
        if match:
            profissao = match.group(1)
            if contexto['tem_ciencia'] and profissao in ['cientista', 'pesquisador', 'especialista']:
                return f"⚠️ Ad hominem: ataque à credencial científica (você não é {profissao})"
            return f"⚠️ Ad hominem: ataque à credencial (você não é {profissao})"

        # Padrões gerais
        padroes = [
            (r"você (?:é|não é) (\w+)", "ataque direto"),
            (r"tu (?:és|não és) (\w+)", "ataque direto"),
            (r"você não (?:entende|sabe|compreende)", "ataque à capacidade"),
            (r"você não pode falar porque", "desqualificação"),
            (r"seu argumento não vale porque", "desqualificação"),
            (r"você está errado porque", "ataque pessoal"),
            (r"ignorante|burro|idiota", "xingamento"),
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

    def detectar_apelo_autoridade(self, texto):
        texto_lower = texto.lower()
        contexto = self.analisar_contexto(texto)

        autoridades_religiosas = ["padre", "pastor", "papa", "bispo", "apóstolo", "profeta"]
        autoridades_academicas = ["cientista", "professor", "doutor", "pesquisador", "especialista"]
        autoridades_midia = ["famoso", "celebridade", "jornalista", "apresentador"]

        padroes = [
            "segundo", "como disse", "de acordo com", "conforme",
            "é sabido por todos que", "especialistas dizem",
            "está escrito que", "a bíblia diz", "o papa disse",
            "o padre disse", "o pastor disse", "o professor disse",
        ]

        for padrao in padroes:
            if padrao in texto_lower:
                for autoridade in autoridades_religiosas:
                    if autoridade in texto_lower:
                        if not contexto['tem_religiao']:
                            return f"⚠️ Apelo à autoridade religiosa irrelevante: '{padrao} {autoridade}'"
                        return f"⚠️ Apelo à autoridade: '{padrao} {autoridade}'"

                for autoridade in autoridades_academicas:
                    if autoridade in texto_lower:
                        if not contexto['tem_ciencia']:
                            return f"⚠️ Apelo à autoridade acadêmica irrelevante: '{padrao} {autoridade}'"
                        return f"⚠️ Apelo à autoridade: '{padrao} {autoridade}'"

                for autoridade in autoridades_midia:
                    if autoridade in texto_lower:
                        return f"⚠️ Apelo à autoridade midiática: '{padrao} {autoridade}' (autoridade não qualificada)"

        return None

    def detectar_falsa_dicotomia(self, texto):
        texto_lower = texto.lower()

        # Lista expandida de padrões de falsa dicotomia
        padroes = [
            r'ou .* ou .*',
            r'(?:é|está) (?:uma coisa|assim):? .* ou .*',
            r'só (?:há|existem) duas opções',
            r'se não (?:for|é) (?:assim|desse jeito), (?:então|é porque)',
            r'a única alternativa é',
            r'não há outra saída (?:senão|a não ser)',
        ]

        for padrao in padroes:
            if re.search(padrao, texto_lower):
                return "⚠️ Falsa dicotomia: apresenta apenas duas opções ignorando outras possibilidades"

        # Verifica estrutura "ou X ou Y" com palavras curtas
        if " ou " in texto_lower:
            partes = texto_lower.split(" ou ")
            if len(partes) == 2 and len(partes[0].split()) < 5 and len(partes[1].split()) < 5:
                return f"⚠️ Possível falsa dicotomia: '{partes[0].strip()} ou {partes[1].strip()}'"

        return None

    def detectar_post_hoc(self, texto, frases=None):
        """
        Detecta a falácia post hoc ergo propter hoc.
        Se frases (lista de strings) for fornecida, analisa relações entre elas.
        """
        texto_lower = texto.lower()

        # Padrões de sequência temporal
        padroes_temporais = [
            r'depois (?:de|que)',
            r'desde que',
            r'após',
            r'logo após',
            r'assim que',
            r'no momento em que',
            r'quando',
        ]

        # Padrões de conclusão causal
        padroes_conclusao = [
            r'logo',
            r'portanto',
            r'então',
            r'por isso',
            r'consequentemente',
            r'assim',
            r'por causa disso',
        ]

        # Verifica se há sequência temporal + conclusão na mesma frase
        for padrao_tempo in padroes_temporais:
            if re.search(padrao_tempo, texto_lower):
                for padrao_conc in padroes_conclusao:
                    if re.search(padrao_conc, texto_lower):
                        return f"⚠️ Post hoc ergo propter hoc: correlação temporal ('{padrao_tempo}') seguida de conclusão causal ('{padrao_conc}') não implica causalidade"

        # Se temos múltiplas frases, verifica a primeira com tempo e a segunda com conclusão
        if frases and len(frases) >= 2:
            primeira = frases[0].lower()
            segunda = frases[1].lower()
            for padrao_tempo in padroes_temporais:
                if re.search(padrao_tempo, primeira):
                    for padrao_conc in padroes_conclusao:
                        if re.search(padrao_conc, segunda):
                            return f"⚠️ Post hoc ergo propter hoc: evento temporal na primeira frase, conclusão na segunda"

        return None

    def detectar_generalizacao_apressada(self, texto):
        texto_lower = texto.lower()

        # Palavras de generalização (usando regex com boundaries)
        generalizadores = [
            r'\btodo mundo\b', r'\btodos\b', r'\bninguém\b', r'\bsempre\b', r'\bnunca\b',
            r'\bem todos os casos\b', r'\bqualquer pessoa\b', r'\bqualquer um\b',
            r'\babsolutamente todos\b', r'\bem qualquer situação\b',
        ]

        # Indicadores de amostra pequena
        amostra_pequena = [r'\bum\b', r'\bexemplo\b', r'\bcaso\b', r'\bconheci\b', r'\bvi\b', r'\bouvi falar\b']

        tem_generalizacao = any(re.search(p, texto_lower) for p in generalizadores)
        tem_amostra_pequena = any(re.search(p, texto_lower) for p in amostra_pequena)

        if tem_generalizacao and tem_amostra_pequena:
            return "⚠️ Generalização apressada: conclusão universal baseada em evidência insuficiente"

        # Generalização temporal sozinha
        if re.search(r'\b(sempre|nunca|todo mundo|todos os dias|todas as semanas)\b', texto_lower):
            return "⚠️ Generalização temporal: uso de palavras absolutas sem evidência"

        return None

    def detectar_circular(self, argumentos):
        if len(argumentos) >= 2:
            args_str = [str(a) for a in argumentos]
            if args_str[0] == args_str[-1]:
                return "⚠️ Raciocínio circular: conclusão igual a premissa"
            for i in range(len(args_str)):
                for j in range(i+1, len(args_str)):
                    if args_str[i] in args_str[j] and args_str[j] in args_str[i]:
                        return "⚠️ Raciocínio circular: premissas se pressupõem mutuamente"
        return None

    def detectar_falso_consenso(self, texto):
        texto_lower = texto.lower()
        padroes = [
            "todo mundo sabe", "é óbvio que", "claramente",
            "como todos sabem", "é fato que", "não há dúvida"
        ]
        for padrao in padroes:
            if padrao in texto_lower:
                return f"⚠️ Falso consenso: assume que todos concordam sem evidência ('{padrao}')"
        return None

    def detectar_espantalho(self, texto):
        texto_lower = texto.lower()
        padroes = [
            "você está dizendo que", "então você acredita que",
            "o que você quer é", "sua ideia é que"
        ]
        for padrao in padroes:
            if padrao in texto_lower:
                return f"⚠️ Espantalho: distorce o argumento do oponente ('{padrao}')"
        return None

    def detectar_apelo_emocao(self, texto):
        texto_lower = texto.lower()
        palavras_emocao = ["sofrimento", "dor", "medo", "ódio", "amor", "esperança", "crianças", "família", "futuro"]
        for palavra in palavras_emocao:
            if palavra in texto_lower:
                return f"⚠️ Apelo à emoção: uso da palavra '{palavra}' para influenciar sentimento"
        return None

    def analisar(self, texto, argumentos=None, frases=None):
        """
        Analisa o texto em busca de falácias.
        :param texto: string com o texto completo.
        :param argumentos: lista de objetos lógicos (opcional, para detectar circularidade).
        :param frases: lista de frases separadas (opcional, para detectar post hoc entre frases).
        """
        self.falacias_encontradas = []
        detectors = [
            self.detectar_ad_hominem,
            self.detectar_apelo_autoridade,
            self.detectar_falsa_dicotomia,
            self.detectar_post_hoc,
            self.detectar_generalizacao_apressada,
            self.detectar_falso_consenso,
            self.detectar_espantalho,
            self.detectar_apelo_emocao,
        ]
        for detector in detectors:
            # Para detectores que aceitam parâmetros adicionais, tratamos separadamente
            if detector == self.detectar_post_hoc:
                resultado = detector(texto, frases)
            else:
                resultado = detector(texto)
            if resultado:
                self.falacias_encontradas.append(resultado)
        if argumentos:
            resultado = self.detectar_circular(argumentos)
            if resultado:
                self.falacias_encontradas.append(resultado)
        return self.falacias_encontradas