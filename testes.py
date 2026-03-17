import unittest
from app import app
import json

class TestAnalisador(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
    
    def analisar(self, texto):
        response = self.app.post('/analisar', 
                                 json={'texto': texto},
                                 content_type='application/json')
        return response.get_json()
    
    def test_silogismo_valido(self):
        texto = "Todo homem é mortal. Sócrates é homem. Sócrates é mortal."
        resultado = self.analisar(texto)
        self.assertIn('estruturas', resultado)
        self.assertEqual(len(resultado['estruturas']), 3)
        self.assertEqual(len(resultado['falacias']), 0)
    
    def test_ad_hominem(self):
        texto = "Você é ignorante. Portanto, seu argumento está errado."
        resultado = self.analisar(texto)
        self.assertTrue(any('Ad hominem' in f for f in resultado['falacias']))
    
    def test_falsa_dicotomia(self):
        texto = "Ou você está comigo, ou contra mim."
        resultado = self.analisar(texto)
        self.assertTrue(any('Falsa dicotomia' in f for f in resultado['falacias']))
    
    def test_generalizacao_temporal(self):
        texto = "Todo mundo sabe que isso é verdade."
        resultado = self.analisar(texto)
        self.assertTrue(any('Generalização temporal' in f for f in resultado['falacias']))
    
    def test_apelo_emocao(self):
        texto = "Isso vai causar sofrimento às crianças."
        resultado = self.analisar(texto)
        self.assertTrue(any('Apelo à emoção' in f for f in resultado['falacias']))
    
    def test_post_hoc_desde_que(self):
        texto = "Desde que comecei a tomar esse remédio, melhorei. Logo, o remédio funcionou."
        resultado = self.analisar(texto)
        self.assertTrue(any('Post hoc' in f for f in resultado['falacias']))
    
    def test_voz_passiva(self):
        texto = "O bolo foi comido por João."
        resultado = self.analisar(texto)
        # Verifica se alguma estrutura foi gerada (não deve ser vazia)
        self.assertGreater(len(resultado['estruturas']), 0)
        # Verifica se a estrutura contém "comido" e "João"
        estrutura_gerada = resultado['estruturas'][0]
        self.assertIn('comido', estrutura_gerada)
        self.assertIn('João', estrutura_gerada)
    
    def test_oracao_relativa_sujeito(self):
        texto = "O homem que matou o leão fugiu."
        resultado = self.analisar(texto)
        self.assertGreater(len(resultado['estruturas']), 0)
        estrutura_str = str(resultado['estruturas'])
        # Verifica se contém os verbos principais
        self.assertIn('fugir', estrutura_str)
        self.assertIn('matar', estrutura_str)
        # Verifica se contém os substantivos
        self.assertIn('homem', estrutura_str)
        self.assertIn('leão', estrutura_str)

    def test_oracao_relativa_objeto(self):
        texto = "A casa que comprei é azul."
        resultado = self.analisar(texto)
        self.assertGreater(len(resultado['estruturas']), 0)
        estrutura_str = str(resultado['estruturas'])
        # Verifica se contém o predicado principal
        self.assertIn('azul', estrutura_str)
        # Verifica se contém o substantivo
        self.assertIn('casa', estrutura_str)
        # Verifica se contém o verbo da relativa
        self.assertIn('comprei', estrutura_str)

if __name__ == '__main__':
    unittest.main()