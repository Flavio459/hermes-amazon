# Hermes Amazon Operacional

Este repositório contém a estrutura inicial para operacionalizar o agente Hermes integrado ao ecossistema Amazon.

## Conteúdo

- `AGENTS.md`: instrucoes operacionais do repositorio.
- `SOUL.md`: criterio de trabalho e postura do agente.
- `USER.md`: contexto do usuario e preferencias de colaboracao.
- `HEARTBEAT.md`: rotina curta de checagem quando houver heartbeat.
- `MEMORY.md`: memoria operacional de longo prazo.
- `MODEL.md`: Modelo de integração Hermes–Amazon, incluindo visão geral, componentes, arquitetura, habilidades e segurança.
- `VERSION.md`: Especificação de versionamento e guidelines de branch.
- `README.md`: Este arquivo com orientações iniciais.

## Como usar

1. Revise `AGENTS.md`, `SOUL.md` e `USER.md` para entender como trabalhar neste repo.
2. Revise `MODEL.md` para entender a arquitetura e os módulos necessários.
3. Rode `python -m hermes_amazon inspect` para ver o perfil de runtime.
4. Rode `python -m hermes_amazon validate` para checar a configuração.
5. Rode `python -m hermes_amazon process --kind sqs_message --source demo --payload "{}"` para simular roteamento local.
6. Rode `python -m hermes_amazon product add --name "Produto" --category "categoria" --link "https://example.com"` para iniciar o catalogo local.
7. Rode `python -m hermes_amazon watch add <product_id>` para colocar um produto do catalogo em monitoramento local.
8. Siga `VERSION.md` ao realizar commits e releases.
9. Use `HEARTBEAT.md` apenas quando houver checagem periodica.
10. Registre aprendizados relevantes em `MEMORY.md`.

## Próximos passos

- Configurar repositório no GitHub conforme padrão Wii Ops Center (branch `main` e `develop`).  
- Adicionar código-fonte dos módulos mencionados em `MODEL.md`.  
- Criar workflows de CI/CD e scripts de provisionamento para AWS.
