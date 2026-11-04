import os
import tempfile
import unittest

from storage.data_file import DataFile
from sql.catalogo import Catalogo, ErroCatalogo

class TestCatalogo(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "dados.db")
        self.arquivo = DataFile(self.caminho)
        self.catalogo = Catalogo(self.arquivo)

    def tearDown(self):
        self.pasta.cleanup()

    def test_reserva_pagina_catalogo(self):
        self.assertEqual(
            self.arquivo.page_count(), 2)

    def test_criar_tabela(self):
        pagina = self.catalogo.criar_tabela("aluno",[("id", "INT", 4), ("nome", "CHAR", 20)])

        self.assertEqual(pagina, 2)

        tabela = self.catalogo.buscar_tabela("aluno")

        self.assertEqual(tabela["nome"], "aluno")
        self.assertEqual(tabela["primeira_pagina"], 2)
        self.assertEqual(tabela["colunas"],[["id", "INT", 4], ["nome", "CHAR", 20]])

    def test_persistencia(self):
        self.catalogo.criar_tabela("aluno", [("id", "INT", 4)])

        # Simula reabrir o banco.
        novo_arquivo = DataFile(self.caminho)
        novo_catalogo = Catalogo(novo_arquivo)

        tabela = novo_catalogo.buscar_tabela("aluno")

        self.assertIsNotNone(tabela)
        self.assertEqual(tabela["nome"], "aluno")

    def test_tabela_duplicada(self):
        self.catalogo.criar_tabela("aluno", [("id", "INT", 4)])

        with self.assertRaises(ErroCatalogo):
            self.catalogo.criar_tabela("aluno", [("id", "INT", 4)])

    def test_colunas_duplicadas(self):
        with self.assertRaises(ErroCatalogo):
            self.catalogo.criar_tabela("aluno",[("id", "INT", 4), ("id", "INT", 4)])

    def test_tabela_inexistente(self):
        self.assertIsNone(self.catalogo.buscar_tabela("inexistente"))

    def test_varias_tabelas(self):
        self.catalogo.criar_tabela("aluno", [("id", "INT", 4)])

        self.catalogo.criar_tabela("curso", [("codigo", "INT", 4)])

        tabelas = self.catalogo.listar_tabelas()

        self.assertEqual(len(tabelas), 2)
        self.assertEqual([tabela["nome"] for tabela in tabelas],["aluno", "curso"])


if __name__ == "__main__":
    unittest.main()
