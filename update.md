O que esse projeto faz atualmente
É uma API REST em Python (Flask), estruturada para rodar localmente ou em ambiente serverless (AWS Lambda/API Gateway).
Expõe múltiplos endpoints para manipulação de dados (ex: /tasks, /users, etc).
Possui lógica de CORS implementada via um handler @app_handler.after_request (em OptionsController.py), que atualmente aceita origens baseadas em variáveis de ambiente.
Quando revertido para o estado original, o CORS está aberto ou controlado por variáveis de ambiente, permitindo que qualquer site (ou qualquer origem definida na env) consuma a API via browser.

O que estou tentando fazer
Restringir o acesso CORS: Permitir apenas origens específicas (ex: seu domínio e localhost para desenvolvimento) a consumir a API via browser.
Centralizar e garantir a segurança do CORS: Ter certeza de que só um ponto do código controla o CORS, sem duplicidade/confusão.
Evitar exposição de origens permitidas no código-fonte (tanto quanto possível) e garantir que o header só seja enviado para origens realmente autorizadas.


Os erros que estão acontecendo:
Tentativa de restringir o CORS no backend:
O header Access-Control-Allow-Origin não era enviado corretamente para origens permitidas.
O navegador bloqueava as requisições com o erro:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
Quando havia múltiplos handlers ou dependência de variáveis de ambiente:
Conflitos e sobrescrita de headers, causando comportamento imprevisível.
Em ambiente AWS/API Gateway:
Possível conflito entre o CORS do backend e o do API Gateway, ou headers não sendo repassados corretamente.

O que estou tentando fazer:
Centralizar o controle de CORS em um único handler (after_request), preferencialmente em OptionsController.py.
Remover dependência de variáveis de ambiente para CORS. Usar uma lista clara de origens permitidas no código/config.
No handler, só adicionar o header CORS se a origem for permitida.
Manter a lógica para OPTIONS (preflight) para garantir que o navegador aceite as requisições.