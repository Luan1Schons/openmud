# Guia de Criação de NPCs

Os NPCs são definidos no arquivo `worlds/default/npcs.json`.

## Estrutura Básica

```json
{
  "id": "identificador_unico",
  "name": "Nome do NPC",
  "description": "Descrição visual do NPC",
  "npc_type": "normal|shopkeeper|trader|quest_giver",
  "room_id": "id_da_sala",
  "dialogue": [
    "Frase 1 que o NPC pode dizer",
    "Frase 2 que o NPC pode dizer"
  ],
  "lore": "História e contexto do NPC (opcional)"
}
```

## Tipos de NPC

### 1. NPC Normal (normal)
NPC comum que apenas conversa.

```json
{
  "id": "npc_comum",
  "name": "Cidadão",
  "description": "Um cidadão comum caminhando pela rua.",
  "npc_type": "normal",
  "room_id": "central",
  "dialogue": [
    "Olá!",
    "Bom dia!"
  ],
  "lore": "Um cidadão comum da cidade."
}
```

### 2. Vendedor (shopkeeper)
NPC que vende itens por ouro.

```json
{
  "id": "vendedor",
  "name": "Mercador",
  "description": "Um comerciante com sua barraca.",
  "npc_type": "shopkeeper",
  "room_id": "central",
  "dialogue": [
    "Bem-vindo à minha loja!",
    "Tenho ótimos itens!"
  ],
  "shop_items": [
    {
      "item_id": "potion",
      "price": 50
    },
    {
      "item_id": "sword",
      "price": 200
    }
  ],
  "lore": "Um comerciante experiente."
}
```

**Nota:** Os `item_id` devem existir em `items.json`.

### 3. Troca (trader)
NPC que troca itens específicos.

```json
{
  "id": "troca_npc",
  "name": "Navegador",
  "description": "Um viajante que troca itens.",
  "npc_type": "trader",
  "room_id": "praia",
  "dialogue": [
    "Fazemos trocas justas!"
  ],
  "trade_items": {
    "give": ["item1", "item2"],
    "receive": ["item3", "item4"]
  },
  "lore": "Um navegador experiente."
}
```

**Nota:** O jogador precisa ter todos os itens em `give` para receber os itens em `receive`.

### 4. Dador de Quests (quest_giver)
NPC que oferece quests.

```json
{
  "id": "quest_giver",
  "name": "Eremita",
  "description": "Um sábio ancião.",
  "npc_type": "quest_giver",
  "room_id": "floresta",
  "dialogue": [
    "Preciso de sua ajuda!",
    "Tenho uma missão para você."
  ],
  "quests": ["quest_id_1", "quest_id_2"],
  "lore": "Um eremita sábio que conhece os segredos do mundo."
}
```

**Nota:** 
- Se `quests` estiver vazio `[]`, o sistema tentará gerar uma quest dinamicamente (com IA se configurada).
- Os `quest_id` devem existir em `quests.json` ou serem gerados dinamicamente.

## Campos Obrigatórios

- `id`: Identificador único (não pode repetir)
- `name`: Nome do NPC (visível no jogo)
- `description`: Descrição visual
- `room_id`: ID da sala onde o NPC aparece (deve existir em `default.json`)

## Campos Opcionais

- `npc_type`: Tipo do NPC (padrão: "normal")
- `dialogue`: Lista de frases (padrão: [])
- `shop_items`: Lista de itens à venda (apenas para shopkeeper)
- `trade_items`: Objeto com give/receive (apenas para trader)
- `quests`: Lista de IDs de quests (apenas para quest_giver)
- `lore`: História do NPC (usado com comando `read`)

## Exemplo Completo

```json
[
  {
    "id": "merchant_central",
    "name": "Vendedor Amigável",
    "description": "Um comerciante sorridente com uma barraca cheia de mercadorias.",
    "npc_type": "shopkeeper",
    "room_id": "central",
    "dialogue": [
      "Bem-vindo à minha loja!",
      "Tenho os melhores itens da região!",
      "Volte sempre!"
    ],
    "shop_items": [
      {
        "item_id": "potion",
        "price": 50
      },
      {
        "item_id": "sword",
        "price": 200
      }
    ],
    "lore": "Um comerciante experiente que viaja pela região vendendo seus produtos."
  }
]
```

## Comandos no Jogo

- `talk <nome>` - Fala com o NPC
- `shop <nome>` - Ver itens à venda (shopkeeper)
- `buy <item> <nome>` - Comprar item (shopkeeper)
- `sell <item> <nome>` - Vender item
- `trade <nome>` - Ver trocas disponíveis (trader)
- `quest <nome>` - Ver quests disponíveis (quest_giver)
- `read <nome>` - Ler lore do NPC

## Dicas

1. Use IDs descritivos (ex: `merchant_central`, `guard_city`)
2. Os `room_id` devem corresponder aos IDs das salas em `default.json`
3. Para quests dinâmicas, deixe `quests: []` e o sistema gerará automaticamente
4. Adicione `lore` interessante para enriquecer o mundo do jogo

