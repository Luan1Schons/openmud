# Sistema de Respawn de Monstros

<div align="center">
  <img src="openmud.png" alt="OpenMud Logo" width="400">
</div>

## Visão Geral

O sistema de respawn controla quando monstros podem reaparecer após serem mortos. Cada monstro tem um tempo de respawn configurável que é salvo no banco de dados.

## Funcionalidades

- **Tempo de respawn configurável**: Cada sala pode ter um tempo de respawn diferente
- **Configuração por monstro**: Cada tipo de monstro pode ter seu próprio tempo de respawn
- **Persistência**: Os tempos de respawn são salvos no banco de dados SQLite
- **Tempo aleatório**: O tempo de respawn é aleatório entre um mínimo e máximo configurado

## Configuração no JSON

### Configuração Geral da Sala

```json
{
  "id": "sala_exemplo",
  "name": "Sala Exemplo",
  "monsters": ["goblin", "wolf"],
  "respawn_time": {
    "min": 300,  // 5 minutos (em segundos)
    "max": 600   // 10 minutos (em segundos)
  }
}
```

### Configuração Específica por Monstro

```json
{
  "id": "sala_exemplo",
  "name": "Sala Exemplo",
  "monsters": ["goblin", "wolf"],
  "monster_respawns": {
    "goblin": {
      "min": 180,  // 3 minutos
      "max": 360   // 6 minutos
    },
    "wolf": {
      "min": 600,  // 10 minutos
      "max": 1200  // 20 minutos
    }
  }
}
```

### Configuração com Tempo Fixo

Você também pode usar um tempo fixo (sem variação):

```json
{
  "respawn_time": 300  // 5 minutos fixo
}
```

Ou por monstro:

```json
{
  "monster_respawns": {
    "goblin": 300  // 5 minutos fixo
  }
}
```

## Prioridade de Configuração

1. **Configuração específica do monstro** (`monster_respawns[monster_id]`) - tem maior prioridade
2. **Configuração geral da sala** (`respawn_time`) - usado se não houver configuração específica
3. **Padrão**: 5-10 minutos (300-600 segundos) - usado se nenhuma configuração for fornecida

## Como Funciona

1. **Quando um monstro morre**:
   - O sistema registra a morte no banco de dados
   - Calcula um tempo de respawn aleatório entre min e max
   - Salva o timestamp da morte e o tempo de respawn

2. **Quando verifica se pode spawnar**:
   - Verifica se há monstros vivos na sala
   - Verifica respawns pendentes no banco de dados
   - Só spawna monstros cujo tempo de respawn já expirou

3. **Limpeza automática**:
   - Registros de respawn expirados são removidos automaticamente
   - Limpeza acontece quando o jogador entra na sala ou usa `look`

## Exemplo Completo

```json
{
  "id": "dungeon_floresta_entrada",
  "name": "Entrada da Caverna",
  "description": "A entrada da caverna...",
  "exits": {
    "norte": "corredor1",
    "sair": "floresta"
  },
  "monsters": ["goblin", "goblin", "wolf"],
  "items": ["herb"],
  "spawn_chance": 0.7,
  "respawn_time": {
    "min": 300,  // Padrão: 5-10 minutos
    "max": 600
  },
  "monster_respawns": {
    "goblin": {
      "min": 180,  // Goblins respawnam mais rápido: 3-6 minutos
      "max": 360
    },
    "wolf": {
      "min": 600,  // Lobos respawnam mais devagar: 10-15 minutos
      "max": 900
    }
  }
}
```

## Banco de Dados

O sistema usa a tabela `monster_respawns` com os seguintes campos:

- `world_id`: ID do mundo
- `room_id`: ID da sala
- `monster_id`: ID do monstro
- `instance_id`: ID da instância única do monstro
- `death_time`: Timestamp da morte
- `respawn_time`: Tempo de respawn em segundos

## Notas Importantes

- O tempo de respawn é calculado **aleatoriamente** entre min e max a cada morte
- Se não houver configuração, o padrão é **5-10 minutos** (300-600 segundos)
- Monstros só respawnam se **todos os daquele tipo** tiverem sido mortos ou se o tempo de respawn expirou
- O sistema funciona tanto para dungeons quanto para salas normais (se configurado)

## Conversão de Tempos

- 1 minuto = 60 segundos
- 5 minutos = 300 segundos
- 10 minutos = 600 segundos
- 15 minutos = 900 segundos
- 30 minutos = 1800 segundos
- 1 hora = 3600 segundos

