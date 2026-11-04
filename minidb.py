import sys
from sql.executor import Executor


def main():
    if len(sys.argv) != 2:
        print("Uso: python minidb.py dados.db")
        return 1

    nome_arquivo = sys.argv[1]
    executor = Executor(nome_arquivo)

    for linha in sys.stdin:
        comando = linha.strip()

        if not comando:
            continue

        try:
            resultado = executor.executar(comando)
            print(resultado)
        except Exception as erro:
            print(f"ERRO: {erro}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
