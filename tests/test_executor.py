import os
import tempfile
import unittest

from sql.executor import Executor, ErroExecucao

class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "dados.db")
        self.executor = Executor(self.caminho)

    def tearDown(self):
        self.pasta.cleanup()

    def test_create_table(self):
        resultado = self.executor.executar("CREATE TABLE aluno (id INT, nome CHAR(20));")
        self.assertEqual(resultado, "OK")

    def test_insert_select(self):
        self.executor.executar("CREATE TABLE aluno (id INT, nome CHAR(20));")

        self.assertEqual(
            self.executor.executar("INSERT INTO aluno VALUES (1, 'Valmir');"),"OK 1")

        resultado = self.executor.executar("SELECT * FROM aluno;")

        self.assertEqual(resultado, "1|Valmir\n(1 linha)")

    def test_varios_registros(self):
        self.executor.executar("CREATE TABLE aluno (id INT, nome CHAR(20));")
        self.executor.executar("INSERT INTO aluno VALUES (1, 'Valmir');")
        self.executor.executar("INSERT INTO aluno VALUES (2, 'Anderson');")

        resultado = self.executor.executar("SELECT * FROM aluno;")

        self.assertEqual(
            resultado,
            "1|Valmir\n2|Anderson\n(2 linhas)"
        )

    def test_persistencia(self):
        self.executor.executar(
            "CREATE TABLE aluno (id INT);"
        )
        self.executor.executar(
            "INSERT INTO aluno VALUES (10);"
        )

        outro_executor = Executor(self.caminho)

        self.assertEqual(
            outro_executor.executar(
                "SELECT * FROM aluno;"
            ),
            "10\n(1 linha)"
        )

    def test_tabelas_separadas(self):
        self.executor.executar(
            "CREATE TABLE aluno (id INT);"
        )
        self.executor.executar(
            "CREATE TABLE curso (codigo INT);"
        )

        self.executor.executar(
            "INSERT INTO aluno VALUES (1);"
        )
        self.executor.executar(
            "INSERT INTO curso VALUES (99);"
        )

        self.assertEqual(
            self.executor.executar(
                "SELECT * FROM aluno;"
            ),
            "1\n(1 linha)"
        )

    def test_tipo_incorreto(self):
        self.executor.executar(
            "CREATE TABLE aluno (id INT);"
        )

        with self.assertRaises(ErroExecucao):
            self.executor.executar(
                "INSERT INTO aluno VALUES ('Ana');"
            )

    def test_quantidade_incorreta(self):
        self.executor.executar(
            "CREATE TABLE aluno (id INT, nome CHAR(20));"
        )

        with self.assertRaises(ErroExecucao):
            self.executor.executar(
                "INSERT INTO aluno VALUES (1);"
            )

    def test_texto_muito_grande(self):
        self.executor.executar("CREATE TABLE aluno (nome CHAR(3));")

        with self.assertRaises(ErroExecucao):
            self.executor.executar("INSERT INTO aluno VALUES ('Carlos');")

    def test_tabela_vazia(self):
        self.executor.executar("CREATE TABLE aluno (id INT);")

        self.assertEqual(
            self.executor.executar(
                "SELECT * FROM aluno;"
            ),
            "(0 linhas)"
        )

    def test_varias_paginas(self):
        self.executor.executar("CREATE TABLE aluno (id INT);")

        # Uma página comporta 1020 registros INT.
        for numero in range(1030):
            self.executor.executar(f"INSERT INTO aluno VALUES ({numero});")

        resultado = self.executor.executar("SELECT * FROM aluno;")

        self.assertIn("0\n", resultado)
        self.assertIn("1029\n", resultado)
        self.assertTrue(resultado.endswith("(1030 linhas)"))


if __name__ == "__main__":
    unittest.main()
