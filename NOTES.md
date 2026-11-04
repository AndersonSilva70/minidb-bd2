# Módulo 1 — Armazenamento

A decisão de projeto deste módulo foi representar o armazenamento físico usando páginas de tamanho fixo de 4096 bytes e registros de tamanho fixo. A classe Page representa uma página em memória, FixedRecord transforma os valores inteiros do registro em bytes, e DataFile é responsável por persistir páginas no arquivo de dados.
Também foi incluída a página 0 como página de metadados, contendo número mágico, versão do formato, tamanho da página, total de páginas e a primeira página com espaço livre. As páginas de dados começam a partir da página 1.
Para um registro de 8 bytes inserido no slot 0 da página 1, o registro começa no byte 4112 do arquivo. A página 0 ocupa os bytes 0 a 4095, a página 1 começa em 4096 e seus primeiros 16 bytes são o cabeçalho. Portanto, o primeiro registro começa em 4096 + 16 = 4112.
A responsabilidade de páginas sujas e escrita controlada pelo cache fica para o Módulo 2, quando será implementado o Buffer Pool.

# Módulo 2 — Cache de páginas

A decisão de projeto deste módulo foi implementar um cache de páginas (Buffer Pool) em memória para evitar acessos desnecessários ao arquivo de dados. A classe Cache mantém as páginas carregadas em frames e controla a quantidade de vezes em que cada página está sendo utilizada.
Foi utilizado o algoritmo LRU para escolher qual página será removida quando o cache estiver cheio. A página menos recentemente utilizada é escolhida para expulsão, desde que não esteja fixada.
Foi implementado também o controle de páginas sujas. Quando uma página é modificada, ela é marcada como suja e, antes de ser removida do cache, seu conteúdo é gravado novamente no arquivo de dados. O método descarrega() permite gravar todas as páginas sujas no disco.
A capacidade padrão escolhida para o cache foi de 16 páginas. Nos testes foram utilizadas capacidades menores, como 1 e 3 páginas, para forçar situações de expulsão e verificar o funcionamento do LRU.
A principal decisão do módulo foi utilizar LRU em vez de FIFO, pois a ordem de acesso às páginas precisa ser atualizada a cada acesso para identificar corretamente a página menos recentemente utilizada.
A implementação da árvore B+ e suas operações de busca e inserção serão realizadas no Módulo 3.

# Módulo 3 — Árvore B+

A classe `ArvoreBPlusIndice` implementa uma árvore B+ com nós armazenados em páginas de 4096 bytes, utilizando o cache do Módulo 2. O índice permite localizar registros por chave sem precisar percorrer toda a tabela.
Cada nó é representado em uma página. Os três primeiros bytes armazenam o tipo do nó e a quantidade de chaves, seguidos pelas chaves em inteiros de 64 bits. Nos nós folha, também são armazenados o número da página da próxima folha e os RIDs dos registros, compostos pelo número da página e pela posição do registro. Nos nós internos, são armazenadas as referências às páginas dos filhos.
A busca percorre a árvore a partir da raiz até encontrar a folha correspondente. A inserção mantém as chaves em ordem crescente e rejeita chaves duplicadas. Quando um nó ultrapassa o limite definido pela ordem da árvore, ocorre uma divisão. Nas folhas, a primeira chave da folha direita é promovida ao pai e permanece na folha; nos nós internos, a chave do meio é promovida. Se necessário, a divisão continua até a criação de uma nova raiz.
Os metadados armazenam a identificação do índice e o número da página da raiz, permitindo recuperar a árvore após reabrir o arquivo. Os testes verificam a serialização e desserialização dos nós, a busca, a inserção, as divisões em vários níveis e a persistência do índice.
No Módulo 4, será desenvolvido o analisador e catálogo, responsável por traduzir comandos SQL textuais em instruções que o motor do MiniDB consiga executar.

# Módulo 4 - SQL e catálogo persistente

A decisão de projeto deste módulo foi implementar um analisador de comandos SQL e um catálogo persistente, permitindo criar tabelas, inserir registros e consultar os dados armazenados. O tokenizador identifica palavras reservadas, nomes, números, textos e símbolos, enquanto a classe Parser verifica a estrutura dos comandos e transforma as instruções SQL em informações que o MiniDB consegue interpretar.
A classe Catalogo é responsável por armazenar as informações das tabelas, incluindo nome, colunas e número da primeira página de dados. Foi utilizada a página 1 para armazenar o catálogo, mantendo a página 0 reservada para os metadados do arquivo. Cada registro do catálogo possui 236 bytes, sendo 32 bytes para o nome da tabela, 4 bytes para a primeira página e 200 bytes para a descrição das colunas. O formato JSON foi utilizado para serializar e recuperar as informações das colunas.
A classe Executor integra o analisador SQL, o catálogo e o armazenamento físico desenvolvido nos módulos anteriores. Os comandos CREATE TABLE, INSERT INTO e SELECT * permitem criar tabelas, inserir valores dos tipos INT e CHAR e recuperar os registros. Também foram implementadas validações para tipos incorretos, quantidade de valores e tamanho dos textos. Quando uma página de dados fica cheia, uma nova página é alocada e vinculada à anterior, permitindo armazenar registros em múltiplas páginas sem misturar os dados de tabelas diferentes.
A persistência foi verificada por meio da reabertura do arquivo de dados, confirmando que as tabelas e os registros permanecem armazenados após o encerramento do programa. Também foi criada uma interface de linha de comando para receber instruções SQL a partir da entrada padrão e apresentar os resultados das operações.
Os testes verificam a identificação dos tokens, a interpretação dos comandos SQL, a criação e recuperação das tabelas, a inserção e consulta de registros, as validações de dados e o armazenamento em múltiplas páginas. Ao final da implementação, foram executados 64 testes automatizados referente aos módulos 1,2,3 e 4, todos aprovados.
A implementação atual permite consultas SELECT * sem filtros. Embora o parser reconheça a cláusula WHERE, sua execução ainda não foi implementada. O executor também utiliza o DataFile diretamente, sem integração com o Buffer Pool do Módulo 2.