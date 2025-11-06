# Como Criar Novos NPCs

<div align="center">
  <img src="openmud.png" alt="OpenMud Logo" width="400">
</div>

## Localização

Os NPCs são criados no arquivo:
```
worlds/default/npcs.json
```

## Forma Rápida

1. Abra o arquivo `worlds/default/npcs.json`
2. Adicione um novo objeto JSON ao array
3. Siga o formato dos exemplos já existentes

## Exemplo Rápido - NPC Normal

```json
{
  "id": "meu_npc",
  "name": "Meu NPC",
  "description": "Descrição do NPC",
  "npc_type": "normal",
  "room_id": "central",
  "dialogue": ["Olá!", "Como vai?"],
  "lore": "História do NPC"
}
```

## Exemplo Rápido - Vendedor

```json
{
  "id": "vendedor_custom",
  "name": "Vendedor",
  "description": "Um vendedor",
  "npc_type": "shopkeeper",
  "room_id": "central",
  "shop_items": [
    {"item_id": "potion", "price": 50}
  ]
}
```

## Exemplo Rápido - Dador de Quests

```json
{
  "id": "quest_master",
  "name": "Mestre de Quests",
  "description": "Um NPC que dá quests",
  "npc_type": "quest_giver",
  "room_id": "central",
  "quests": [],
  "lore": "Este NPC pode gerar quests dinamicamente!"
}
```

## Verificar IDs de Salas

As salas disponíveis estão em `worlds/default.json`. Use o campo `id` das salas como `room_id`.

## Após Criar

1. Salve o arquivo `npcs.json`
2. Reinicie o servidor (`python3 server.py`)
3. O NPC aparecerá na sala especificada

## Documentação Completa

Veja [`worlds/default/NPCS_README.md`](../worlds/default/NPCS_README.md) para documentação completa.

