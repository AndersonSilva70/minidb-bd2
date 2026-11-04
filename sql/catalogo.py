import json
import struct

from storage.page import PAGE_SIZE, CABECALHO_SIZE

PAGINA_CATALOGO = 1
TAMANHO_NOME = 32
TAMANHO_COLUNAS = 200
TAMANHO_REGISTRO = 236


class ErroCatalogo(Exception):
    pass


class Catalogo:
    def __init__(self, arquivo):
        self.arquivo = arquivo

        # A página 0 já é reservada para metadados.
        # A página 1 será utilizada pelo catálogo.
        if self.arquivo.page_count() == 1:
            self.arquivo.aloca()

    def _codifica_texto(self, texto, tamanho):
        dados = texto.encode("utf-8")

        if len(dados) > tamanho:
            raise ErroCatalogo(f"Texto excede o limite de {tamanho} bytes")

        return dados.ljust(tamanho, b"\x00") #completa com zeros a direita para garantir o tamanho fixo do campo de texto

    def _decodifica_texto(self, dados):
        return dados.rstrip(b"\x00").decode("utf-8") #remove os zeros à direita e decodifica de volta para string

    def _serializa(self, nome, primeira_pagina, colunas):
        nome_bytes = self._codifica_texto(nome, TAMANHO_NOME)
#Json.dumps: converte a lista de colunas em uma string JSON, garantindo que caracteres especiais sejam preservados.
        colunas_texto = json.dumps(colunas, ensure_ascii=False)
        colunas_bytes = self._codifica_texto(colunas_texto, TAMANHO_COLUNAS)
        pagina_bytes = struct.pack("<I", primeira_pagina)

        return nome_bytes + pagina_bytes + colunas_bytes

    def _desserializa(self, dados):
        nome = self._decodifica_texto(dados[:TAMANHO_NOME])

        primeira_pagina = struct.unpack("<I", dados[32:36])[0]

        colunas_texto = self._decodifica_texto(dados[36:236])
#Json.loads: converte a string JSON de volta para uma lista de colunas, permitindo que os metadados sejam utilizados no código.
        colunas = json.loads(colunas_texto)

        return {
            "nome": nome,
            "primeira_pagina": primeira_pagina,
            "colunas": colunas
        }

    def listar_tabelas(self):
        pagina = self.arquivo.le_pagina(PAGINA_CATALOGO)

        tabelas = []

        for slot in range(pagina.quantidade_registros()):
            dados = pagina.le_registro(slot, TAMANHO_REGISTRO)

            tabelas.append(self._desserializa(dados))

        return tabelas

    def buscar_tabela(self, nome):
        for tabela in self.listar_tabelas():
            if tabela["nome"] == nome:
                return tabela

        return None

    def criar_tabela(self, nome, colunas):
        if self.buscar_tabela(nome) is not None:
            raise ErroCatalogo(f"Tabela '{nome}' já existe")

        if not colunas:
            raise ErroCatalogo("A tabela precisa ter pelo menos uma coluna")

        nomes = [coluna[0] for coluna in colunas]

        if len(nomes) != len(set(nomes)):
            raise ErroCatalogo("Existem colunas com nomes repetidos")

        tamanho_linha = sum(coluna[2] for coluna in colunas)

        if tamanho_linha > PAGE_SIZE - CABECALHO_SIZE:
            raise ErroCatalogo("O registro não cabe em uma página")

        #Valida os metadados antes de alocar a página.
        self._serializa(nome, 0, colunas)

        pagina_catalogo = self.arquivo.le_pagina(PAGINA_CATALOGO)

        if pagina_catalogo.quantidade_registros() >= (
            pagina_catalogo.capacidade(TAMANHO_REGISTRO)):
            raise ErroCatalogo("O catálogo está cheio")

        primeira_pagina = self.arquivo.aloca()

        dados = self._serializa(nome, primeira_pagina, colunas)

        pagina_catalogo.insere_registro(dados)

        self.arquivo.escreve_pagina(PAGINA_CATALOGO,pagina_catalogo.le())

        self.arquivo.sync()

        return primeira_pagina
