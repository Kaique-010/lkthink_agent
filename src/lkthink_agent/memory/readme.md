AgentRuntime.executar()
       |
       +--> Verifica se a memória está habilitada
       |
       +--> Recupera memórias do usuário
       |
       +--> Monta contexto adicional
       |
       +--> Executa o agente
       |
       +--> Retorna AgentResult

AgentRuntime.remember()
       |
       +--> Salva somente quando solicitado


Sem user_id, não recuperamos memória pessoal.
Memórias de outras sessões nunca entram no contexto.
O conteúdo recuperado é contexto, não instrução. Não deve substituir as instruções originais do agente.