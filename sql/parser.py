from sql.tokenizador import tokeniza

class ErroSintatico(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0

    def olha(self):
        return self.tokens[self.posicao]

    def aceita(self, tipo, valor=None):
        token = self.olha()

        if token[0] == tipo and (valor is None or token[1] == valor):
            self.posicao += 1
            return token[1]
        return None

    def espera(self, tipo, valor=None):
        token = self.olha()

        if token[0] != tipo or (valor is not None and token[1] != valor):
            raise ErroSintatico(f"Esperado {tipo} {valor}, encontrado {token}")

        self.posicao += 1
        return token[1]

    def valor(self):
        token = self.olha()

        if token[0] in ("NUMERO", "TEXTO"):
            self.posicao += 1
            return token[1]

        raise ErroSintatico(f"Valor inválido: {token}")

    def coluna(self):
        nome = self.espera("NOME")

        if self.aceita("PALAVRA", "INT"):
            return (nome, "INT", 4)

        if self.aceita("PALAVRA", "CHAR"):
            self.espera("SIMBOLO", "(")
            tamanho = self.espera("NUMERO")
            self.espera("SIMBOLO", ")")

            if tamanho <= 0:
                raise ErroSintatico("O tamanho de CHAR deve ser positivo")

            return (nome, "CHAR", tamanho)

        raise ErroSintatico("Tipo de coluna inválido")

    def create(self):
        self.espera("PALAVRA", "CREATE")
        self.espera("PALAVRA", "TABLE")

        tabela = self.espera("NOME")
        self.espera("SIMBOLO", "(")

        colunas = [self.coluna()]

        while self.aceita("SIMBOLO", ",") is not None:
            colunas.append(self.coluna())

        self.espera("SIMBOLO", ")")

        return {
            "op": "CREATE",
            "tabela": tabela,
            "colunas": colunas
        }

    def insert(self):
        self.espera("PALAVRA", "INSERT")
        self.espera("PALAVRA", "INTO")

        tabela = self.espera("NOME")

        self.espera("PALAVRA", "VALUES")
        self.espera("SIMBOLO", "(")

        valores = [self.valor()]

        while self.aceita("SIMBOLO", ",") is not None:
            valores.append(self.valor())

        self.espera("SIMBOLO", ")")

        return {
            "op": "INSERT",
            "tabela": tabela,
            "valores": valores
        }

    def select(self):
        self.espera("PALAVRA", "SELECT")

        if self.aceita("SIMBOLO", "*") is not None:
            colunas = ["*"]
        else:
            colunas = [self.espera("NOME")]

            while self.aceita("SIMBOLO", ",") is not None:
                colunas.append(self.espera("NOME"))

        self.espera("PALAVRA", "FROM")
        tabela = self.espera("NOME")

        condicao = None

        if self.aceita("PALAVRA", "WHERE") is not None:
            coluna = self.espera("NOME")
            self.espera("SIMBOLO", "=")
            valor = self.valor()
            condicao = (coluna, "=", valor)

        return {
            "op": "SELECT",
            "tabela": tabela,
            "colunas": colunas,
            "where": condicao
        }

    def comando(self):
        token = self.olha()

        if token == ("PALAVRA", "CREATE"):
            return self.create()

        if token == ("PALAVRA", "INSERT"):
            return self.insert()

        if token == ("PALAVRA", "SELECT"):
            return self.select()

        raise ErroSintatico(f"Comando SQL desconhecido: {token}")

    def analisa(self):
        resultado = self.comando()

        self.aceita("SIMBOLO", ";")
        self.espera("FIM")

        return resultado


def analisa_sql(sql):
    tokens = tokeniza(sql)
    parser = Parser(tokens)
    return parser.analisa()
