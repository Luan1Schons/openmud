# Como Funcionam as Quests Geradas pela IA

## ✅ Vinculação com NPCs (IMPLEMENTADO)

### Como Funciona

1. **Vinculação pelo ID do NPC:**
   - Quando uma quest é gerada pela IA, ela recebe o campo `giver_npc` com o `npc_id` (linha 147 de `quest_manager.py`)
   - Exemplo: `giver_npc="quest_giver_forest"`

2. **ID da Quest inclui o NPC:**
   - O ID da quest gerada inclui o ID do NPC: `ai_{npc_id}_{random}`
   - Exemplo: `ai_quest_giver_forest_1234`

3. **Busca por NPC:**
   - O método `get_quests_by_npc()` busca todas as quests onde `giver_npc == npc_id`
   - Isso vincula as quests ao NPC que as gerou

### Exemplo de Código

```python
# Em quest_manager.py, linha 147
quest = Quest(
    id=f"ai_{npc_id}_{random.randint(1000, 9999)}",
    name=quest_data.get('name'),
    ...
    giver_npc=npc_id,  # ← VINCULADO AQUI pelo ID do NPC
    status='available'
)
```

## ✅ Persistência no Banco de Dados (IMPLEMENTADO)

### Como Funciona Agora

**Tabela `quests` criada no banco:**
- `id` - ID único da quest
- `world_id` - Mundo onde a quest existe
- `npc_id` - ID do NPC que dá a quest (vinculação)
- `name`, `description`, `lore` - Dados da quest
- `objectives` - Objetivos (JSON)
- `rewards` - Recompensas (JSON)
- `status` - Status da quest
- `generated_by` - 'ai', 'template', ou 'system'
- `created_at` - Data de criação

### Fluxo de Persistência

1. **Quest gerada pela IA:**
   ```python
   quest = await generate_quest_with_ai(...)
   # Automaticamente salva no banco
   database.save_quest(quest.to_dict(), world_id, generated_by='ai')
   ```

2. **Carregamento na inicialização:**
   - QuestManager carrega quests de arquivos JSON
   - Depois carrega quests do banco de dados
   - Quests do banco são mescladas com as de arquivo

3. **Busca híbrida:**
   - `get_quests_by_npc()` busca em memória E no banco
   - Se não encontrar em memória, busca no banco e adiciona ao cache

### Vantagens

✅ **Persistência:** Quests geradas persistem entre reinicializações  
✅ **Vinculação:** Quests sempre vinculadas ao NPC pelo `npc_id`  
✅ **Histórico:** Todas as quests geradas são salvas  
✅ **Performance:** Cache em memória + busca no banco quando necessário  
✅ **Rastreabilidade:** Campo `generated_by` mostra origem da quest

## Como Funciona na Prática

1. **NPC sem quests pré-definidas:**
   ```json
   {
     "id": "quest_giver_forest",
     "quests": []  // ← Vazio
   }
   ```

2. **Jogador usa comando `quest quest_giver_forest`:**
   - Sistema verifica se NPC tem quests em memória
   - Se não tiver, busca no banco de dados
   - Se ainda não tiver, tenta gerar com IA
   - IA gera quest vinculada ao `npc_id`

3. **Quest gerada:**
   ```python
   Quest(
       id="ai_quest_giver_forest_5678",
       giver_npc="quest_giver_forest",  // ← Vinculado
       ...
   )
   # Salvo automaticamente no banco
   ```

4. **Persistência:**
   - Quest salva em `quests` table
   - `npc_id = "quest_giver_forest"` (vinculação)
   - `generated_by = "ai"`
   - Mesmo após reiniciar servidor, quest ainda existe!

5. **Busca futura:**
   - `get_quests_by_npc("quest_giver_forest")` retorna a quest
   - Busca primeiro em memória, depois no banco
   - Quest persiste entre reinicializações

## Estrutura da Tabela

```sql
CREATE TABLE quests (
    id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL,
    npc_id TEXT NOT NULL,          -- ← VINCULAÇÃO COM NPC
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    lore TEXT DEFAULT '',
    objectives TEXT NOT NULL,
    rewards TEXT NOT NULL,
    status TEXT DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by TEXT DEFAULT 'system'  -- 'ai', 'template', 'system'
);
```

## Métodos do Database

- `save_quest(quest_dict, world_id, generated_by)` - Salva quest no banco
- `get_quests_by_npc(world_id, npc_id)` - Busca quests de um NPC
- `get_all_quests(world_id)` - Busca todas as quests
- `quest_exists(quest_id)` - Verifica se quest existe
- `delete_quest(quest_id)` - Remove quest do banco

## Exemplo de Consulta

```sql
-- Buscar todas as quests de um NPC
SELECT * FROM quests WHERE npc_id = 'quest_giver_forest';

-- Buscar quests geradas pela IA
SELECT * FROM quests WHERE generated_by = 'ai';

-- Buscar quests de um mundo
SELECT * FROM quests WHERE world_id = 'default';
```
