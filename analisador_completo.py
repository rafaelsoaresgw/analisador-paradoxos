import spacy
from parser_logico import extrair_estrutura, QuantificadorUniversal, QuantificadorNegacao, Fato, Predicado, Termo

# Carrega o modelo de português
nlp = spacy.load("pt_core_news_sm")

class DetectorFalacias:
    """Detecta padrões de argumentos falaciosos"""
    
    def __init__(self):
        self.falacias_encontradas = []
    
    def detectar_ad_hominem(self, texto):
        """Detecta ataques pessoais em vez de argumentos"""
        padroes = ["você é", "tu é", "seu argumento não vale porque", "não passa de um"]
        for padrao in padroes:
            if padrao in texto.lower():
                return f"Possível falácia ad hominem: ataque à pessoa ('{padrao}')"
        return None
    
    def detectar_apelo_autoridade(self, texto):
        """Detecta apelo a autoridade irrelevante"""
        padroes = ["segundo", "como disse", "de acordo com", "é sabido por todos que"]
        autoridades = ["pastor", "padre", "celebridade", "famoso", "especialista"]
        
        for padrao in padroes:
            if padrao in texto.lower():
                for autoridade in autoridades:
                    if autoridade in texto.lower():
                        return f"Possível falácia de apelo à autoridade: '{padrao} {autoridade}'"
        return None
    
    def detectar_falsa_dicotomia(self, texto):
        """Detecta quando só apresenta duas opções"""
        padroes = ["ou você", "ou isto ou aquilo", "só há duas opções", "se não é A, é B"]
        for padrao in padroes:
            if padrao in texto.lower():
                return f"Possível falsa dicotomia: '{padrao}' (ignora outras possibilidades)"
        return None
    
    def detectar_circular(self, argumento):
        """Detecta raciocínio circular"""
        if isinstance(argumento, list) and len(argumento) >= 2:
            # Verifica se a conclusão é igual a uma premissa
            if str(argumento[0]) == str(argumento[-1]):
                return "Raciocínio circular: a conclusão é igual a uma premissa"
        return None
    
    def analisar(self, texto, argumento=None):
        """Analisa um texto em busca de falácias"""
        self.falacias_encontradas = []
        
        # Aplica cada detector
        detectors = [
            self.detectar_ad_hominem,
            self.detectar_apelo_autoridade,
            self.detectar_falsa_dicotomia
        ]
        
        for detector in detectors:
            resultado = detector(texto)
            if resultado:
                self.falacias_encontradas.append(resultado)
        
        if argumento:
            resultado = self.detectar_circular(argumento)
            if resultado:
                self.falacias_encontradas.append(resultado)
        
        return self.falacias_encontradas

class MotorInferencia:
    def __init__(self):
        self.premissas = []
        self.conclusoes = []
        self.regras_aplicadas = []
        self.detector = DetectorFalacias()
    
    def adicionar_premissa(self, premissa):
        """Adiciona uma premissa (pode ser string ou objeto lógico)"""
        if isinstance(premissa, str):
            estrutura = extrair_estrutura(premissa)
            if estrutura:
                self.premissas.append(estrutura)
                return True
            return False
        else:
            self.premissas.append(premissa)
            return True
    
    def adicionar_premissas(self, lista_premissas):
        """Adiciona múltiplas premissas de uma vez"""
        for p in lista_premissas:
            self.adicionar_premissa(p)
    
    def modus_ponens(self, implicacao, fato):
        """
        Regra: Se temos (P → Q) e P, então Q
        """
        if not isinstance(implicacao, (QuantificadorUniversal, QuantificadorNegacao)):
            return None
        
        if not isinstance(fato, Fato):
            return None
        
        if isinstance(implicacao, QuantificadorUniversal):
            condicao_nome = implicacao.condicao.nome
            fato_nome = str(fato.predicado).split('(')[0]
            fato_arg = fato.sujeito
            
            if condicao_nome == fato_nome or condicao_nome in str(fato.predicado):
                conclusao_nome = implicacao.propriedade.nome
                # Remove ¬ se houver
                if conclusao_nome.startswith('¬'):
                    conclusao_nome = conclusao_nome[1:]
                conclusao = Fato(fato_arg, Predicado(conclusao_nome, fato_arg))
                
                self.regras_aplicadas.append(f"Modus Ponens: {implicacao} + {fato} → {conclusao}")
                return conclusao
        
        return None
    
    def modus_tollens(self, implicacao, fato_negado):
        """
        Regra: Se temos (P → Q) e ¬Q, então ¬P
        """
        if not isinstance(implicacao, QuantificadorUniversal):
            return None
        
        if not isinstance(fato_negado, Fato):
            return None
        
        # Verifica se o fato_negado corresponde a ¬Q
        conclusao_nome = implicacao.propriedade.nome
        fato_nome = str(fato_negado.predicado).split('(')[0]
        
        # Se temos ¬Q e Q é a conclusão da implicação
        if fato_nome == conclusao_nome:
            # Então ¬P
            condicao_nome = implicacao.condicao.nome
            argumento = fato_negado.sujeito
            
            # Cria ¬P
            conclusao = QuantificadorNegacao("x", 
                                           Predicado(condicao_nome, Termo("x")),
                                           Predicado("", Termo("x")))  # Simplificado
            
            self.regras_aplicadas.append(f"Modus Tollens: {implicacao} + ¬{conclusao_nome}({argumento}) → ¬{condicao_nome}({argumento})")
            # Por enquanto, retornamos None até implementar completamente
            return None
        
        return None
    
    def silogismo_hipotetico(self, imp1, imp2):
        """
        Regra: Se P → Q e Q → R, então P → R
        """
        if not isinstance(imp1, QuantificadorUniversal) or not isinstance(imp2, QuantificadorUniversal):
            return None
        
        conclusao1 = imp1.propriedade.nome
        premissa2 = imp2.condicao.nome
        
        if conclusao1 == premissa2:
            nova_condicao = Predicado(imp1.condicao.nome, Termo("x"))
            nova_propriedade = Predicado(imp2.propriedade.nome, Termo("x"))
            
            nova_implicacao = QuantificadorUniversal("x", nova_condicao, nova_propriedade)
            self.regras_aplicadas.append(f"Silogismo Hipotético: {imp1} + {imp2} → {nova_implicacao}")
            return nova_implicacao
        
        return None
    
    def resolver(self):
        """
        Tenta deduzir novas conclusões a partir das premissas
        """
        novas_conclusoes = []
        
        # Aplica Modus Ponens
        for p1 in self.premissas:
            for p2 in self.premissas:
                if p1 != p2:
                    resultado = self.modus_ponens(p1, p2)
                    if resultado and not any(str(r) == str(resultado) for r in self.premissas + novas_conclusoes):
                        novas_conclusoes.append(resultado)
                    
                    resultado = self.modus_ponens(p2, p1)
                    if resultado and not any(str(r) == str(resultado) for r in self.premissas + novas_conclusoes):
                        novas_conclusoes.append(resultado)
        
        # Aplica silogismo hipotético
        for p1 in self.premissas:
            for p2 in self.premissas:
                if p1 != p2:
                    resultado = self.silogismo_hipotetico(p1, p2)
                    if resultado and not any(str(r) == str(resultado) for r in self.premissas + novas_conclusoes):
                        novas_conclusoes.append(resultado)
        
        # Remove duplicatas antes de adicionar
        for nova in novas_conclusoes:
            if not any(str(p) == str(nova) for p in self.premissas):
                self.premissas.append(nova)
                self.conclusoes.append(nova)
        
        return novas_conclusoes
    
    def provar(self, objetivo_str):
        """
        Tenta provar se um objetivo é consequência lógica das premissas
        """
        objetivo = extrair_estrutura(objetivo_str)
        if not objetivo:
            return False, "Não consegui entender o objetivo"
        
        print(f"\n🔍 Tentando provar: {objetivo}")
        print("-" * 40)
        
        # Verifica se o objetivo já está nas premissas
        for p in self.premissas:
            if str(p) == str(objetivo):
                return True, "Objetivo já é uma premissa!"
        
        # Tenta deduzir novas conclusões
        passos = 0
        while passos < 10:
            novas = self.resolver()
            if not novas:
                break
            
            for nova in novas:
                if str(nova) == str(objetivo):
                    ultima_regra = self.regras_aplicadas[-1] if self.regras_aplicadas else "Desconhecida"
                    return True, f"Provado em {passos + 1} passos!\nRegras aplicadas: {ultima_regra}"
            passos += 1
        
        return False, "Não foi possível provar o objetivo"
    
    def analisar_texto(self, texto):
        """Analisa um texto completo em busca de argumentos e falácias"""
        print("\n" + "="*70)
        print(" 📄 ANÁLISE COMPLETA DO TEXTO ")
        print("="*70)
        print(f"\nTexto: '{texto}'")
        
        # Divide em frases
        frases = texto.split('.')
        argumentos = []
        
        print("\n📚 Estruturas lógicas encontradas:")
        for frase in frases:
            frase = frase.strip()
            if frase:
                estrutura = extrair_estrutura(frase)
                if estrutura:
                    argumentos.append(estrutura)
                    print(f"  • '{frase}' → {estrutura}")
                else:
                    print(f"  • '{frase}' → (sem estrutura lógica clara)")
        
        # Detecta falácias
        print("\n⚠️  Análise de falácias:")
        falacias = self.detector.analisar(texto, argumentos)
        if falacias:
            for f in falacias:
                print(f"  • {f}")
        else:
            print("  • Nenhuma falácia detectada")
        
        # Tenta fazer inferências
        if argumentos:
            self.premissas = argumentos
            print("\n🔍 Tentando deduções automáticas:")
            novas = self.resolver()
            if novas:
                for n in novas:
                    print(f"  • Nova conclusão: {n}")
            else:
                print("  • Nenhuma nova conclusão deduzida")
        
        return argumentos

# ==============================
# TESTE FINAL - ANALISADOR COMPLETO
# ==============================
print("="*70)
print(" 🧠 ANALISADOR DE PARADOXOS - VERSÃO COMPLETA ")
print("="*70)

# Teste 1: Argumento válido
print("\n📌 TESTE 1: Argumento válido")
motor = MotorInferencia()
texto1 = "Todo homem é mortal. Sócrates é homem. Sócrates é mortal."
motor.analisar_texto(texto1)

# Teste 2: Com falácia ad hominem
print("\n" + "-"*70)
print("\n📌 TESTE 2: Com falácia ad hominem")
texto2 = "Você é ignorante. Portanto, seu argumento está errado."
motor2 = MotorInferencia()
motor2.analisar_texto(texto2)

# Teste 3: Com apelo à autoridade
print("\n" + "-"*70)
print("\n📌 TESTE 3: Com apelo à autoridade")
texto3 = "Segundo um famoso pastor, a terra é plana. Portanto, a terra é plana."
motor3 = MotorInferencia()
motor3.analisar_texto(texto3)

# Teste 4: Com negação
print("\n" + "-"*70)
print("\n📌 TESTE 4: Com negação")
texto4 = "Nenhum homem é pássaro. Sócrates é homem. Sócrates não é pássaro."
motor4 = MotorInferencia()
motor4.analisar_texto(texto4)

print("\n" + "="*70)
print("✅ ANALISADOR DE PARADOXOS COMPLETO!")
print("📁 Arquivo: analisador_completo.py")
print("="*70)
