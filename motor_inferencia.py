from parser_logico import extrair_estrutura, QuantificadorUniversal, QuantificadorNegacao, QuantificadorExistencial, Fato, Predicado, Termo, Conjuncao, Disjuncao, Implicacao
import spacy

# Carrega o modelo de português
nlp = spacy.load("pt_core_news_sm")

class MotorInferencia:
    def __init__(self):
        self.premissas = []
        self.conclusoes = []
        self.regras_aplicadas = []
    
    def adicionar_premissa(self, premissa):
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
        for p in lista_premissas:
            self.adicionar_premissa(p)
    
    def modus_ponens(self, implicacao, fato):
        if not isinstance(implicacao, (QuantificadorUniversal, Implicacao)) or not isinstance(fato, Fato):
            return None
        
        if isinstance(implicacao, QuantificadorUniversal):
            condicao_nome = implicacao.condicao.nome
            fato_nome = fato.predicado.nome
            fato_arg = fato.sujeito
            
            if condicao_nome == fato_nome:
                conclusao_nome = implicacao.propriedade.nome
                if isinstance(implicacao.propriedade, str) and conclusao_nome.startswith('¬'):
                    conclusao_nome = conclusao_nome[1:]
                    conclusao = Fato(fato_arg, Predicado(conclusao_nome, fato_arg), negado=True)
                else:
                    conclusao = Fato(fato_arg, Predicado(conclusao_nome, fato_arg))
                return conclusao
        
        elif isinstance(implicacao, Implicacao):
            if str(implicacao.antecedente) == str(fato):
                return implicacao.consequente
        return None
    
    def modus_tollens(self, implicacao, fato_negado):
        if not isinstance(implicacao, (QuantificadorUniversal, Implicacao)) or not isinstance(fato_negado, Fato) or not fato_negado.negado:
            return None
        
        if isinstance(implicacao, QuantificadorUniversal):
            conclusao_nome = implicacao.propriedade.nome
            fato_nome = fato_negado.predicado.nome
            if conclusao_nome == fato_nome:
                condicao_nome = implicacao.condicao.nome
                argumento = fato_negado.sujeito
                return Fato(argumento, Predicado(condicao_nome, argumento), negado=True)
        
        elif isinstance(implicacao, Implicacao):
            if str(implicacao.consequente) == str(fato_negado):
                if isinstance(implicacao.antecedente, Fato):
                    return Fato(implicacao.antecedente.sujeito, implicacao.antecedente.predicado, negado=True)
        return None
    
    def silogismo_hipotetico(self, imp1, imp2):
        if not isinstance(imp1, (QuantificadorUniversal, Implicacao)) or not isinstance(imp2, (QuantificadorUniversal, Implicacao)):
            return None
        
        if isinstance(imp1, QuantificadorUniversal) and isinstance(imp2, QuantificadorUniversal):
            if imp1.propriedade.nome == imp2.condicao.nome:
                nova_condicao = Predicado(imp1.condicao.nome, Termo("x"))
                nova_propriedade = Predicado(imp2.propriedade.nome, Termo("x"))
                return QuantificadorUniversal("x", nova_condicao, nova_propriedade)
        
        elif isinstance(imp1, Implicacao) and isinstance(imp2, Implicacao):
            if str(imp1.consequente) == str(imp2.antecedente):
                return Implicacao(imp1.antecedente, imp2.consequente)
        return None
    
    def silogismo_categorico(self, premissa_universal, premissa_particular):
        if isinstance(premissa_universal, QuantificadorNegacao) and isinstance(premissa_particular, Fato):
            if premissa_universal.condicao.nome == premissa_particular.predicado.nome:
                return Fato(premissa_particular.sujeito, Predicado(premissa_universal.propriedade.nome, premissa_particular.sujeito), negado=True)
        
        if isinstance(premissa_universal, QuantificadorUniversal) and isinstance(premissa_particular, Fato):
            if premissa_universal.condicao.nome == premissa_particular.predicado.nome:
                return Fato(premissa_particular.sujeito, Predicado(premissa_universal.propriedade.nome, premissa_particular.sujeito))
        return None
    
    def simplificacao_conjuncao(self, conjuncao):
        if not isinstance(conjuncao, Conjuncao):
            return None
        conclusoes = []
        if conjuncao.esquerda not in self.premissas:
            conclusoes.append(conjuncao.esquerda)
        if conjuncao.direita not in self.premissas:
            conclusoes.append(conjuncao.direita)
        return conclusoes if conclusoes else None
    
    def silogismo_disjuntivo(self, disjuncao, fato_negado):
        if not isinstance(disjuncao, Disjuncao) or not isinstance(fato_negado, Fato) or not fato_negado.negado:
            return None
        if str(disjuncao.esquerda) == str(fato_negado):
            return disjuncao.direita
        elif str(disjuncao.direita) == str(fato_negado):
            return disjuncao.esquerda
        return None
    
    def resolver(self):
        novas_conclusoes = []
        for p1 in self.premissas:
            for p2 in self.premissas:
                if p1 != p2:
                    for resultado in [self.modus_ponens(p1, p2), self.modus_tollens(p1, p2), 
                                     self.silogismo_hipotetico(p1, p2), self.silogismo_categorico(p1, p2),
                                     self.silogismo_disjuntivo(p1, p2)]:
                        if resultado:
                            if isinstance(resultado, list):
                                for r in resultado:
                                    if r and not any(str(ex) == str(r) for ex in self.premissas + novas_conclusoes):
                                        novas_conclusoes.append(r)
                            else:
                                if resultado and not any(str(ex) == str(resultado) for ex in self.premissas + novas_conclusoes):
                                    novas_conclusoes.append(resultado)
            
            resultado = self.simplificacao_conjuncao(p1)
            if resultado:
                for r in resultado:
                    if r and not any(str(ex) == str(r) for ex in self.premissas + novas_conclusoes):
                        novas_conclusoes.append(r)
        
        for nova in novas_conclusoes:
            if not any(str(p) == str(nova) for p in self.premissas):
                self.premissas.append(nova)
                self.conclusoes.append(nova)
        return novas_conclusoes
