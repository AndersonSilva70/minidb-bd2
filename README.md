# minidb-bd2
# MiniDB - Banco de Dados 2

Mini sistema gerenciador de banco de dados desenvolvido em Python para a disciplina de Banco de Dados 2.

## Objetivo
Implementar um pequeno SGBD capaz de armazenar dados, executar consultas SQL e realizar operações de transação e recuperação.

## Funções
[x] M1 — Página e arquivo de dados: Escrita e leitura física de blocos (páginas) de 4096 bytes em disco.

[x] M2 — Cache de páginas (Buffer Pool): Páginas em memória, marcação de página suja, escrita no disco.

[x] M3 — Árvore B+: Busca e inserção com divisão de nó.

[x] M4 — Analisador e catálogo: Interpretação de comandos SQL, catálogo persistente e execução de CREATE TABLE, INSERT INTO e SELECT *.

## Como executar

O MiniDB utiliza Python e permite executar comandos SQL por meio do terminal.

### Executar os testes automatizados

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Executar comandos SQL

No PowerShell:

```powershell
Get-Content consultas.sql | python minidb.py dados.db
```

No CMD:

```cmd
python minidb.py dados.db < consultas.sql
```

### Exemplo de comandos SQL

```sql
CREATE TABLE aluno (id INT, nome CHAR(20));
INSERT INTO aluno VALUES (1, 'Valmir');
INSERT INTO aluno VALUES (2, 'Anderson');
SELECT * FROM aluno;
```

### Resultado esperado

Ao executar os comandos em um banco de dados novo:

```text
OK
OK 1
OK 1
1|Valmir
2|Anderson
(2 linhas)
```

Os dados são armazenados em arquivos `.db` e permanecem disponíveis após o encerramento do programa.

## Testes
Foram executados 64 testes automatizados referentes aos Módulos 1, 2, 3 e 4, todos aprovados.

## Limitações
O executor SQL atualmente permite consultas SELECT * sem filtros. A cláusula WHERE é reconhecida pelo parser, mas ainda não é executada.

## Segunda parte
Implementação de um tema escolhido entre as opções disponibilizadas pelo professor.

## Linguagem
- Python

## Equipe
- Valmir Ferreira
- Anderson Silva
  
