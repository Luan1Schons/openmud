"""
Gerenciador de quests e sistema de geração com IA
"""

import json
import random
from pathlib import Path
from typing import Dict, Optional, List
from mud.core.models import Quest

class QuestManager:
    """Gerencia quests do jogo"""
    
    def __init__(self, worlds_dir: str = "worlds", database=None):
        self.worlds_dir = Path(worlds_dir)
        self.database = database
        self.quests: Dict[str, Dict[str, Quest]] = {}  # world_id -> {quest_id -> Quest}
        self._load_quests()
    
    def _load_quests(self):
        """Carrega quests dos arquivos e do banco de dados"""
        for world_dir in self.worlds_dir.iterdir():
            if world_dir.is_dir() and world_dir.name == "default":
                world_id = world_dir.name
                self._load_world_quests(world_id)
        
        # Carrega quests do banco de dados (persistência)
        if self.database:
            self._load_quests_from_database()
    
    def _load_world_quests(self, world_id: str):
        """Carrega quests de um mundo"""
        world_dir = self.worlds_dir / world_id
        quests_file = world_dir / "quests.json"
        
        self.quests[world_id] = {}
        
        if quests_file.exists():
            try:
                with open(quests_file, 'r', encoding='utf-8') as f:
                    quests_data = json.load(f)
                    for quest_data in quests_data:
                        quest = Quest(
                            id=quest_data['id'],
                            name=quest_data['name'],
                            description=quest_data['description'],
                            lore=quest_data.get('lore', ''),
                            objectives=quest_data.get('objectives', []),
                            rewards=quest_data.get('rewards', {}),
                            giver_npc=quest_data.get('giver_npc', ''),
                            status='available'
                        )
                        self.quests[world_id][quest.id] = quest
            except Exception as e:
                print(f"Erro ao carregar quests de {world_id}: {e}")
    
    def _load_quests_from_database(self):
        """Carrega quests persistidas no banco de dados"""
        if not self.database:
            return
        
        try:
            db_quests = self.database.get_all_quests()
            for quest_data in db_quests:
                world_id = quest_data['world_id']
                if world_id not in self.quests:
                    self.quests[world_id] = {}
                
                # Não sobrescreve se já existe (quests de arquivo têm prioridade)
                if quest_data['id'] not in self.quests[world_id]:
                    quest = Quest(
                        id=quest_data['id'],
                        name=quest_data['name'],
                        description=quest_data['description'],
                        lore=quest_data.get('lore', ''),
                        objectives=quest_data.get('objectives', []),
                        rewards=quest_data.get('rewards', {}),
                        giver_npc=quest_data.get('giver_npc', ''),
                        status=quest_data.get('status', 'available')
                    )
                    self.quests[world_id][quest.id] = quest
                    print(f"[QuestManager] Quest carregada do banco: {quest.name} (NPC: {quest.giver_npc})")
        except Exception as e:
            print(f"Erro ao carregar quests do banco: {e}")
    
    def get_quest(self, world_id: str, quest_id: str) -> Optional[Quest]:
        """Retorna uma quest"""
        if world_id in self.quests:
            return self.quests[world_id].get(quest_id)
        return None
    
    def get_quests_by_npc(self, world_id: str, npc_id: str) -> List[Quest]:
        """Retorna quests de um NPC (da memória e do banco)"""
        quests_list = []
        
        # Busca em memória
        if world_id in self.quests:
            quests_list = [q for q in self.quests[world_id].values() if q.giver_npc == npc_id]
        
        # Busca no banco de dados (se não encontrou em memória ou quer garantir)
        if self.database:
            db_quests = self.database.get_quests_by_npc(world_id, npc_id)
            for quest_data in db_quests:
                quest_id = quest_data['id']
                # Só adiciona se não estiver em memória
                if world_id not in self.quests or quest_id not in self.quests[world_id]:
                    quest = Quest(
                        id=quest_data['id'],
                        name=quest_data['name'],
                        description=quest_data['description'],
                        lore=quest_data.get('lore', ''),
                        objectives=quest_data.get('objectives', []),
                        rewards=quest_data.get('rewards', {}),
                        giver_npc=quest_data.get('giver_npc', ''),
                        status=quest_data.get('status', 'available')
                    )
                    # Adiciona em memória para cache
                    if world_id not in self.quests:
                        self.quests[world_id] = {}
                    self.quests[world_id][quest_id] = quest
                    quests_list.append(quest)
        
        return quests_list
    
    def generate_quest(self, world_id: str, npc_id: str, npc_name: str, context: Dict) -> Optional[Quest]:
        """
        Gera uma quest dinamicamente usando IA ou templates
        context: informações sobre o mundo, NPC, etc.
        """
        # Por enquanto usa templates, mas pode ser substituído por chamada de IA
        quest_templates = [
            {
                'name': f'Missão de {npc_name}',
                'description': f'{npc_name} precisa de sua ajuda!',
                'objectives': [
                    {'type': 'kill', 'target': 'goblin', 'amount': random.randint(3, 7)}
                ],
                'rewards': {
                    'gold': random.randint(50, 200),
                    'experience': random.randint(25, 100)
                }
            },
            {
                'name': f'Coleta para {npc_name}',
                'description': f'{npc_name} precisa de itens específicos.',
                'objectives': [
                    {'type': 'collect', 'target': 'herb', 'amount': random.randint(5, 10)}
                ],
                'rewards': {
                    'gold': random.randint(30, 150),
                    'experience': random.randint(20, 80),
                    'items': ['potion']
                }
            }
        ]
        
        template = random.choice(quest_templates)
        quest_id = f"generated_{npc_id}_{random.randint(1000, 9999)}"
        
        quest = Quest(
            id=quest_id,
            name=template['name'],
            description=template['description'],
            lore=f"Uma missão oferecida por {npc_name}. {template['description']}",
            objectives=template['objectives'],
            rewards=template['rewards'],
            giver_npc=npc_id,
            status='available'
        )
        
        # Salva quest gerada em memória
        if world_id not in self.quests:
            self.quests[world_id] = {}
        self.quests[world_id][quest_id] = quest
        
        # Salva quest gerada no banco de dados para persistência
        if self.database:
            quest_dict = quest.to_dict()
            self.database.save_quest(quest_dict, world_id, generated_by='template')
            print(f"[QuestManager] Quest gerada salva no banco: {quest.name}")
        
        return quest
    
    async def generate_quest_with_ai(self, world_id: str, npc_id: str, npc_name: str, 
                                     npc_lore: str, world_context: Dict) -> Optional[Quest]:
        """
        Gera quest usando IA (preparado para integração com API de IA)
        Pode usar OpenAI, Anthropic, ou outra API
        """
        from mud.ai.ai_quest_generator import AIQuestGenerator
        
        ai_generator = AIQuestGenerator()
        
        if not ai_generator.enabled:
            return None
        
        # Gera quest usando IA
        quest_data = await ai_generator.generate_quest(npc_name, npc_lore, world_context)
        
        if not quest_data:
            return None
        
        # Cria quest a partir dos dados gerados pela IA
        quest_id = f"ai_{npc_id}_{random.randint(1000, 9999)}"
        
        quest = Quest(
            id=quest_id,
            name=quest_data.get('name', f'Missão de {npc_name}'),
            description=quest_data.get('description', ''),
            lore=quest_data.get('lore', ''),
            objectives=quest_data.get('objectives', []),
            rewards=quest_data.get('rewards', {}),
            giver_npc=npc_id,
            status='available'
        )
        
        # Salva quest gerada em memória
        if world_id not in self.quests:
            self.quests[world_id] = {}
        self.quests[world_id][quest_id] = quest
        
        # Salva quest gerada pela IA no banco de dados para persistência
        if self.database:
            quest_dict = quest.to_dict()
            self.database.save_quest(quest_dict, world_id, generated_by='ai')
            print(f"[QuestManager] Quest gerada pela IA salva no banco: {quest.name} (NPC: {npc_id})")
        
        return quest
    
    def check_quest_completion(self, quest: Quest, player_progress: Dict) -> bool:
        """Verifica se uma quest foi completada"""
        for objective in quest.objectives:
            obj_type = objective.get('type')
            target = objective.get('target')
            amount = objective.get('amount', 1)
            
            if obj_type == 'kill':
                progress_key = f"kill_{target}"
                if player_progress.get(progress_key, 0) < amount:
                    return False
            elif obj_type == 'collect':
                progress_key = f"collect_{target}"
                if player_progress.get(progress_key, 0) < amount:
                    return False
            elif obj_type == 'sacrifice_ability':
                # Sacrifício é verificado durante a completação, não no progresso
                # Mas precisamos verificar se o item foi coletado
                progress_key = f"sacrifice_{target}"
                # Se já foi marcado como sacrificado, está completo
                if player_progress.get(progress_key, 0) >= amount:
                    continue
                # Caso contrário, precisa verificar se tem o item primeiro
                # (isso será verificado no cmd_complete_quest)
                pass
        
        return True
    
    def complete_quest(self, quest: Quest, player) -> Dict:
        """Completa uma quest e retorna recompensas"""
        rewards = quest.rewards.copy()
        
        # Aplica recompensas
        if 'gold' in rewards:
            player.add_gold(rewards['gold'])
        if 'experience' in rewards:
            player.experience += rewards['experience']
        if 'items' in rewards:
            for item_id in rewards['items']:
                player.add_item(item_id)
        
        # Remove da lista de ativas
        if quest.id in player.active_quests:
            player.active_quests.remove(quest.id)
        
        # Adiciona às completadas
        if quest.id not in player.completed_quests:
            player.completed_quests.append(quest.id)
        
        # Limpa progresso
        if quest.id in player.quest_progress:
            del player.quest_progress[quest.id]
        
        return rewards


