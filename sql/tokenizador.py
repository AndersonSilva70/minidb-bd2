PALAVRAS_RESERVADAS = {
    "CREATE", "TABLE", "INSERT", "INTO", "VALUES",
    "SELECT", "FROM", "WHERE", "INT", "CHAR"
}


class ErroLexico(Exception):
    pass


def tokeniza(sql):
    tokens = []
    posicao = 0
    while posicao < len(sql):
        caractere = sql[posicao]
        # Ignora espaços, tabulações e quebras de linha
        if caractere.isspace():
            posicao  += 1
            continue
        # Identifica palavras reservadas e nomes
        if caractere.isalpha() or caractere == "_":
            inicio = posicao
            while posicao < len(sql) and (sql[posicao].isalnum() or sql[posicao] == "_"):
                posicao += 1
            palavra = sql[inicio:posicao]
            if palavra.upper() in PALAVRAS_RESERVADAS:
                tokens.append(("PALAVRA", palavra.upper()))
            else:
                tokens.append(("NOME", palavra))

            continue

        # Identifica números inteiros
        if caractere.isdigit():
            inicio = posicao

            while posicao < len(sql) and sql[posicao].isdigit():
                posicao += 1
            numero = int(sql[inicio:posicao])
            tokens.append(("NUMERO", numero))
            continue

        # Identifica textos entre aspas simples
        if caractere == "'":
            posicao += 1
            texto = ""

            while posicao < len(sql):
                if sql[posicao] == "'":
                    if posicao + 1 < len(sql) and sql[posicao + 1] == "'":
                        texto += "'"
                        posicao += 2
                        continue
                    break
                texto += sql[posicao]
                posicao += 1

            if posicao >= len(sql):
                raise ErroLexico("Texto sem aspas de fechamento")
            tokens.append(("TEXTO", texto))
            posicao += 1
            continue

        # Identifica símbolos SQL
        if caractere in "(),;*=":
            tokens.append(("SIMBOLO", caractere))
            posicao += 1
            continue

        raise ErroLexico(f"Caractere inválido: {caractere!r}")

    tokens.append(("FIM", None))
    return tokens
