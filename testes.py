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
    
    def test_ad_hominem_circunstancial(self):
        texto = "Você só defende isso porque ganha dinheiro com isso."
        resultado = self.analisar(texto)
        self.assertTrue(any('circunstancial' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_autoridade(self):
        texto = "Segundo o professor, isso é verdade."
        resultado = self.analisar(texto)
        self.assertTrue(any('autoridade' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_forca(self):
        texto = "Se não concordar, vai sofrer as consequências."
        resultado = self.analisar(texto)
        self.assertTrue(any('força' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_popularidade(self):
        texto = "Todo mundo está fazendo isso, então é certo."
        resultado = self.analisar(texto)
        self.assertTrue(any('popularidade' in f.lower() for f in resultado['falacias']))
    
    def test_falsa_dicotomia(self):
        texto = "Ou você está comigo, ou contra mim."
        resultado = self.analisar(texto)
        self.assertTrue(any('Falsa dicotomia' in f for f in resultado['falacias']))
    
    def test_post_hoc(self):
        texto = "Desde que comecei a tomar esse remédio, melhorei. Logo, o remédio funcionou."
        resultado = self.analisar(texto)
        self.assertTrue(any('Post hoc' in f for f in resultado['falacias']))
    
    def test_generalizacao_apressada(self):
        texto = "Conheci dois cariocas simpáticos, portanto todos os cariocas são simpáticos."
        resultado = self.analisar(texto)
        self.assertTrue(any('generalização apressada' in f.lower() for f in resultado['falacias']))
    
    def test_generalizacao_temporal(self):
        texto = "Todo mundo sabe que isso é verdade."
        resultado = self.analisar(texto)
        self.assertTrue(any('generalização temporal' in f.lower() for f in resultado['falacias']))
    
    def test_falso_consenso(self):
        texto = "É óbvio que isso é verdade."
        resultado = self.analisar(texto)
        self.assertTrue(any('falso consenso' in f.lower() for f in resultado['falacias']))
    
    def test_espantalho(self):
        texto = "Você está dizendo que Deus não existe, então você é ateu e não tem moral."
        resultado = self.analisar(texto)
        self.assertTrue(any('espantalho' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_emocao(self):
        texto = "Isso vai causar sofrimento às crianças."
        resultado = self.analisar(texto)
        self.assertTrue(any('Apelo à emoção' in f for f in resultado['falacias']))
    
    def test_composicao(self):
        texto = "As partes são excelentes, portanto o todo é excelente."
        resultado = self.analisar(texto)
        self.assertTrue(any('composição' in f.lower() for f in resultado['falacias']))
    
    def test_divisao(self):
        texto = "O time é excelente, logo cada jogador é excelente."
        resultado = self.analisar(texto)
        self.assertTrue(any('divisão' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_ignorancia(self):
        texto = "Ninguém provou que Deus não existe, portanto Deus existe."
        resultado = self.analisar(texto)
        self.assertTrue(any('ignorância' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_natureza(self):
        texto = "Este remédio é natural, portanto é melhor."
        resultado = self.analisar(texto)
        self.assertTrue(any('natureza' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_tradicao(self):
        texto = "Sempre foi assim, então está certo."
        resultado = self.analisar(texto)
        self.assertTrue(any('tradição' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_novidade(self):
        texto = "É a tecnologia mais nova, logo é superior."
        resultado = self.analisar(texto)
        self.assertTrue(any('novidade' in f.lower() for f in resultado['falacias']))
    
    def test_questao_complexa(self):
        texto = "Você ainda bate na sua esposa?"
        resultado = self.analisar(texto)
        self.assertTrue(any('questão complexa' in f.lower() for f in resultado['falacias']))
    
    def test_falacia_apostador(self):
        texto = "Já perdi 5 vezes, agora a chance de ganhar é maior."
        resultado = self.analisar(texto)
        self.assertTrue(any('apostador' in f.lower() for f in resultado['falacias']))
    
    def test_apelo_piedade(self):
        texto = "Pense nas crianças sofrendo, você precisa apoiar esta causa."
        resultado = self.analisar(texto)
        self.assertTrue(any('piedade' in f.lower() for f in resultado['falacias']))
    
    def test_falso_equilibrio(self):
        texto = "Alguns cientistas concordam, outros não – é polêmico."
        resultado = self.analisar(texto)
        self.assertTrue(any('equilíbrio' in f.lower() for f in resultado['falacias']))
    
    def test_voz_passiva(self):
        texto = "O bolo foi comido por João."
        resultado = self.analisar(texto)
        self.assertGreater(len(resultado['estruturas']), 0)
        estrutura_gerada = resultado['estruturas'][0]
        self.assertIn('comido', estrutura_gerada)
        self.assertIn('João', estrutura_gerada)
    
    def test_oracao_relativa_sujeito(self):
        texto = "O homem que matou o leão fugiu."
        resultado = self.analisar(texto)
        self.assertGreater(len(resultado['estruturas']), 0)
        estrutura_str = str(resultado['estruturas'])
        self.assertIn('fugir', estrutura_str)
        self.assertIn('matar', estrutura_str)
        self.assertIn('homem', estrutura_str)
        self.assertIn('leão', estrutura_str)

    def test_oracao_relativa_objeto(self):
        texto = "A casa que comprei é azul."
        resultado = self.analisar(texto)
        self.assertGreater(len(resultado['estruturas']), 0)
        estrutura_str = str(resultado['estruturas'])
        self.assertIn('azul', estrutura_str)
        self.assertIn('casa', estrutura_str)
        self.assertIn('comprei', estrutura_str)

if __name__ == '__main__':
    unittest.main()