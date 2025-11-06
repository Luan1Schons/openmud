# Guia de Comandos - Quests

<div align="center">
  <img src="openmud.png" alt="OpenMud Logo" width="400">
</div>

## Como Ver e Aceitar Quests

### 1. Falar com o NPC
Use o comando `talk` para conversar com um NPC:
```
talk Pirata
```

Agora, se o NPC for um **quest_giver**, ele mostrará automaticamente que tem quests disponíveis!

### 2. Ver Quests Disponíveis
Use o comando `quest` seguido do nome do NPC:
```
quest Pirata
```

Ou apenas:
```
quest Pirata
```

Isso mostrará todas as quests disponíveis daquele NPC.

### 3. Aceitar uma Quest
Use o comando `accept` seguido do nome da quest e do NPC:
```
accept <nome da quest> <npc>
```

Exemplo:
```
accept Mapa do Tesouro Pirata
```

### 4. Ver Suas Quests Ativas
Para ver todas as suas quests ativas:
```
quest
```

Ou:
```
quests
```

### 5. Ver Progresso de uma Quest
Use `quest` para ver suas quests ativas e o progresso de cada uma.

### 6. Completar uma Quest
Quando você completar os objetivos, use:
```
complete <nome da quest>
```

Ou:
```
finish <nome da quest>
```

### 7. Cancelar uma Quest
Se quiser cancelar uma quest:
```
cancel <nome da quest>
```

Ou:
```
abandon <nome da quest>
```

## Dicas

- Nem todos os NPCs oferecem quests. Apenas NPCs do tipo `quest_giver` oferecem quests
- Quando você fala com um NPC usando `talk`, se ele tiver quests, você verá uma mensagem informando
- Use `quest <nome do NPC>` para ver detalhes completos das quests
- Algumas quests podem ser geradas dinamicamente usando IA (se configurada)

## Comandos Resumidos

| Comando | Descrição |
|---------|-----------|
| `talk <npc>` | Fala com um NPC (mostra se tem quests) |
| `quest <npc>` | Ver quests disponíveis de um NPC |
| `quest` | Ver suas quests ativas |
| `accept <quest> <npc>` | Aceitar uma quest |
| `complete <quest>` | Completar uma quest |
| `cancel <quest>` | Cancelar uma quest |

