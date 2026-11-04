import unittest
from sql.parser import analisa_sql, ErroSintatico


class TestParser(unittest.TestCase):

    def test_create(self):
        resultado = analisa_sql("CREATE TABLE aluno (id INT, nome CHAR(20));")

        self.assertEqual(resultado["op"], "CREATE")
        self.assertEqual(resultado["tabela"], "aluno")
        self.assertEqual(resultado["colunas"], [("id", "INT", 4), ("nome", "CHAR", 20)])

#Test insert
    def test_insert(self):
        resultado = analisa_sql("INSERT INTO aluno VALUES (1, 'valmir');")
    
        self.assertEqual(resultado["op"], "INSERT")
        self.assertEqual(resultado["tabela"], "aluno")
        self.assertEqual(resultado["valores"], [1, "valmir"])
#Test select
    def test_select(self):
        resultado = analisa_sql("SELECT * FROM aluno;")

        self.assertEqual(resultado["op"], "SELECT")
        self.assertEqual(resultado["colunas"], ["*"])
        self.assertIsNone(resultado["where"])

    def test_select_colunas(self):
        resultado = analisa_sql("SELECT id, nome FROM aluno;")

        self.assertEqual(resultado["colunas"], ["id", "nome"])

#Test select with where
    def test_select_where(self):
        resultado = analisa_sql("SELECT * FROM aluno WHERE id = 1;")

        self.assertEqual(resultado["where"], ("id", "=", 1))

#Test sem ponto e virgula
    def test_sem_ponto_virgula(self):
        resultado = analisa_sql("SELECT * FROM aluno")

        self.assertEqual(resultado["op"], "SELECT")

#Test comando invalido
    def test_comando_invalido(self):
        with self.assertRaises(ErroSintatico):
            analisa_sql("DELETE FROM aluno;")

#Test coluna sem tipo
    def test_coluna_sem_tipo(self):
        with self.assertRaises(ErroSintatico):
            analisa_sql("CREATE TABLE aluno (id);")

#Test char tamanho invalido
    def test_char_tamanho_invalido(self):
        with self.assertRaises(ErroSintatico):
            analisa_sql("CREATE TABLE aluno (nome CHAR(0));")

#Test token extra
    def test_tokens_extras(self):
        with self.assertRaises(ErroSintatico):
            analisa_sql("SELECT * FROM aluno; INSERT")


if __name__ == "__main__":
    unittest.main()
