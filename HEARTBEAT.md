# HEARTBEAT

Status: checagem operacional curta.

Quando este arquivo for acionado:
1. Verificar se existe nova tarefa no repositorio.
2. Checar se houve mudanca relevante no estado local.
3. Se nao houver acao pendente, responder `HEARTBEAT_OK`.

Nao criar polling continuo sem instrucao explicita.

