import unittest
from sql.tokenizador import tokeniza, ErroLexico

class TestTokenizador(unittest.TestCase):

    def test_create_table(self):
        tokens = tokeniza("CREATE TABLE aluno (id INT, nome CHAR(20));")
        self.assertEqual(tokens[0], ("PALAVRA", "CREATE"))
        self.assertIn(("NOME", "aluno"), tokens)
        self.assertIn(("NUMERO", 20), tokens)
        self.assertEqual(tokens[-1], ("FIM", None))
        
#Teste insert
    def test_insert(self):
        tokens = tokeniza("INSERT INTO aluno VALUES (1, 'valmir');")
        self.assertIn(("NUMERO", 1), tokens)
        self.assertIn(("TEXTO", "valmir"), tokens)
        
#Teste select
    def test_select(self):
        tokens = tokeniza("SELECT * FROM aluno;")
        self.assertEqual(tokens[0], ("PALAVRA", "SELECT"))
        self.assertIn(("SIMBOLO", "*"), tokens)
        
#Teste where
    def test_where(self):
        tokens = tokeniza("SELECT * FROM aluno WHERE id = 1;")
        self.assertIn(("PALAVRA", "WHERE"), tokens)
        self.assertIn(("NUMERO", 1), tokens)
        
#teste minusculas
    def test_minusculas(self):
        tokens = tokeniza("select * from aluno;")
        self.assertEqual(tokens[0], ("PALAVRA", "SELECT"))
        
#Teste texto com apostrofo
    def test_texto_com_apostrofo(self):
        tokens = tokeniza("INSERT INTO aluno VALUES ('D''valmir');")
        self.assertIn(("TEXTO", "D'valmir"), tokens)

#Teste de caractere invalido
    def test_caractere_invalido(self):
        with self.assertRaises(ErroLexico):
            tokeniza("SELECT @ FROM aluno;")

#Teste de aspas sem fechamento
    def test_aspas_sem_fechamento(self):
        with self.assertRaises(ErroLexico):
            tokeniza("INSERT INTO aluno VALUES ('valmir);")


if __name__ == "__main__":
    unittest.main()
