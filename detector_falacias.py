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

        # Padrão específico: "você não é um X" (deve vir primeiro)
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
        padroes = [
            (r"ou (?:você|isto) (?:está|é) (\w+) ou (?:está|é) (\w+)", "falso dilema"),
            (r"só há duas opções", "falso dilema"),
            (r"se não é (\w+), é (\w+)", "falso dilema"),
            (r"ou está comigo ou contra mim", "falso dilema"),
        ]
        for padrao, tipo in padroes:
            if re.search(padrao, texto_lower):
                return f"⚠️ Falsa dicotomia: apresenta apenas duas opções ignorando outras possibilidades"
        if " ou " in texto_lower:
            partes = texto_lower.split(" ou ")
            if len(partes) == 2 and len(partes[0].split()) < 5 and len(partes[1].split()) < 5:
                return f"⚠️ Possível falsa dicotomia: '{partes[0].strip()} ou {partes[1].strip()}'"
        return None

    def detectar_post_hoc(self, texto):
        texto_lower = texto.lower()
        padroes_causais = [
            (r"depois (?:disso|de) (?:então|logo)", "sequência temporal"),
            (r"desde que (?:aconteceu|ocorreu)", "causa presumida"),
            (r"por causa disso", "causa direta"),
            (r"portanto foi causado por", "causalidade afirmada"),
            (r"após (?:isso|o evento)", "sequência"),
        ]
        for padrao, tipo in padroes_causais:
            if re.search(padrao, texto_lower):
                return f"⚠️ Post hoc ergo propter hoc: correlação temporal não implica causalidade"
        return None

    def detectar_generalizacao_apressada(self, texto):
        texto_lower = texto.lower()
        generalizadores = ["todo mundo", "todos são", "ninguém", "sempre", "nunca", "em todos os casos"]
        amostra_pequena = ["um", "exemplo", "caso", "conheci", "vi", "ouvi falar"]

        tem_generalizacao = any(g in texto_lower for g in generalizadores)
        tem_amostra_pequena = any(a in texto_lower for a in amostra_pequena)

        if tem_generalizacao and tem_amostra_pequena:
            return f"⚠️ Generalização apressada: conclusão universal baseada em evidência insuficiente"
        if "todo" in texto_lower and "um" in texto_lower and not re.search(r'não é um', texto_lower):
            return f"⚠️ Possível generalização apressada"
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

    def analisar(self, texto, argumentos=None):
        self.falacias_encontradas = []
        detectors = [
            self.detectar_ad_hominem,
            self.detectar_apelo_autoridade,
            self.detectar_falsa_dicotomia,
            self.detectar_post_hoc,
            self.detectar_generalizacao_apressada,
            self.detectar_falso_consenso,
            self.detectar_espantalho,
        ]
        for detector in detectors:
            resultado = detector(texto)
            if resultado:
                self.falacias_encontradas.append(resultado)
        if argumentos:
            resultado = self.detectar_circular(argumentos)
            if resultado:
                self.falacias_encontradas.append(resultado)
        return self.falacias_encontradas
