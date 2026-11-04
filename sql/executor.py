import struct

from sql.parser import analisa_sql
from sql.catalogo import Catalogo
from storage.data_file import DataFile
from storage.page import CABECALHO_SIZE, PAGE_SIZE


class ErroExecucao(Exception):
    pass

class Executor:
    def __init__(self, nome_arquivo):
        self.arquivo = DataFile(nome_arquivo)
        self.catalogo = Catalogo(self.arquivo)

    def executar(self, sql):
        comando = analisa_sql(sql)
        
        if comando["op"] == "CREATE":
            return self.criar_tabela(comando)

        if comando["op"] == "INSERT":
            return self.inserir(comando)

        if comando["op"] == "SELECT":
            return self.selecionar(comando)
        
        raise ErroExecucao("Operação não suportada")

    def criar_tabela(self, comando):
        self.catalogo.criar_tabela(
            comando["tabela"],
            comando["colunas"]
        )
        return "OK"

    def _serializa_registro(self, colunas, valores):
        if len(colunas) != len(valores):
            raise ErroExecucao("Quantidade de valores diferente das colunas")

        dados = bytearray()

        for coluna, valor in zip(colunas, valores):
            nome, tipo, tamanho = coluna

            if tipo == "INT":
                if type(valor) is not int:
                    raise ErroExecucao(f"A coluna '{nome}' exige um inteiro")

                try:
                    dados.extend(struct.pack("<i", valor))
                except struct.error:
                    raise ErroExecucao(f"Inteiro fora do intervalo: {valor}")

            elif tipo == "CHAR":
                if not isinstance(valor, str):
                    raise ErroExecucao(f"A coluna '{nome}' exige texto")

                texto = valor.encode("utf-8")

                if len(texto) > tamanho:
                    raise ErroExecucao(f"Texto excede CHAR({tamanho})")

                dados.extend(texto.ljust(tamanho, b"\x00"))

            else:
                raise ErroExecucao(f"Tipo desconhecido: {tipo}")
        return bytes(dados)

    def _desserializa_registro(self, colunas, dados):
        valores = []
        posicao = 0

        for nome, tipo, tamanho in colunas:
            trecho = dados[posicao:posicao + tamanho]

            if tipo == "INT":
                valor = struct.unpack("<i", trecho)[0]

            elif tipo == "CHAR":
                valor = trecho.rstrip(b"\x00").decode("utf-8")

            else:
                raise ErroExecucao(f"Tipo desconhecido: {tipo}")

            valores.append(valor)
            posicao += tamanho

        return valores

    def _proxima_pagina(self, pagina):
        return struct.unpack("<I", pagina.dados[4:8])[0]

    def _define_proxima_pagina(self, pagina, numero):
        pagina.dados[4:8] = struct.pack("<I", numero)

    def inserir(self, comando):
        tabela = self.catalogo.buscar_tabela(comando["tabela"])

        if tabela is None:
            raise ErroExecucao("Tabela inexistente")

        colunas = tabela["colunas"]

        # Valida todos os valores antes de gravar.
        dados = self._serializa_registro(colunas, comando["valores"])

        numero = tabela["primeira_pagina"]

        while True:
            pagina = self.arquivo.le_pagina(numero)

            if pagina.quantidade_registros() < (pagina.capacidade(len(dados))):
                pagina.insere_registro(dados)

                self.arquivo.escreve_pagina(numero, pagina.le())

                self.arquivo.sync()
                return "OK 1"

            proxima = self._proxima_pagina(pagina)

            if proxima != 0:
                numero = proxima
                continue

            # A página está cheia: cria outra.
            nova_pagina = self.arquivo.aloca()

            self._define_proxima_pagina(pagina, nova_pagina)

            self.arquivo.escreve_pagina(numero, pagina.le())

            numero = nova_pagina

    def selecionar(self, comando):
        tabela = self.catalogo.buscar_tabela(comando["tabela"])

        if tabela is None:
            raise ErroExecucao("Tabela inexistente")

        if comando["colunas"] != ["*"]:
            raise ErroExecucao("Nesta etapa, use SELECT *")

        if comando["where"] is not None:
            raise ErroExecucao("WHERE ainda não foi implementado")

        colunas = tabela["colunas"]
        tamanho_registro = sum(coluna[2] for coluna in colunas)

        linhas = []
        numero = tabela["primeira_pagina"]

        while numero != 0:
            pagina = self.arquivo.le_pagina(numero)

            for slot in range(pagina.quantidade_registros()):
                dados = pagina.le_registro(slot, tamanho_registro)

                valores = self._desserializa_registro(colunas, dados)

                linhas.append(valores)
            numero = self._proxima_pagina(pagina)

        resultado = [
            "|".join(str(valor) for valor in linha)
            for linha in linhas
        ]

        quantidade = len(linhas)
        palavra = "linha" if quantidade == 1 else "linhas"

        resultado.append(f"({quantidade} {palavra})")

        return "\n".join(resultado)
