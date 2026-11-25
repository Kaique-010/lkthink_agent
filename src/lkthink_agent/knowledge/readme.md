No módulo de knowledge temos as seguintes classes:

- `criar_text_reader`
- `criar_estrategia_chunking`

criar estrategia chunking é responsável por criar a estrategia de chunking que será usada para cortar os documentos.
criar text reader é responsável por ler o texto do arquivo e criar os chunks.
cortar os chunks em documentos menores através da configuração que esta em `KnowledgeConfig` e o overlap entre eles.
