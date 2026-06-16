# AGENTS.md

## Objetivo

Definir como este repositorio deve ser trabalhado pelo Hermes e pelo Codex.
O foco: manter o projeto pequeno, rastreavel, seguro e facil de reverter.

## Ordem de leitura

1. `SOUL.md`
2. `USER.md`
3. `README.md`
4. `MODEL.md`
5. `VERSION.md`
6. `HEARTBEAT.md` quando houver heartbeat
7. `MEMORY.md` para contexto historico

## Regras

- Nao implementar nada sem entender o fluxo atual.
- Preferir mudancas pequenas e isoladas.
- Nao adicionar dependencias sem justificativa tecnica clara.
- Nao expor segredos, tokens, `.env` ou credenciais.
- Sempre registrar como testar e como reverter.
- Se houver ambiente VPS acessado via desktop, preferir CLI para tarefas de repo sempre que possivel.

## Para este repo

- Tratar o conteudo como base operacional para Hermes Amazon.
- Manter o conteudo consistente com o que o workspace usa de fato.
- Se houver divergencia entre doc e runtime, confiar no runtime ativo e corrigir a documentacao.
