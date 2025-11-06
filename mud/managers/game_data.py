"""
Gerenciador de dados do jogo (monstros, itens, NPCs)
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from mud.core.models import Monster, Item, NPC

class GameDataManager:
    """Gerencia carregamento de monstros, itens e NPCs"""
    
    def __init__(self, worlds_dir: str = "worlds"):
        self.worlds_dir = Path(worlds_dir)
        self.monsters: Dict[str, Dict[str, Monster]] = {}  # world_id -> {monster_id -> Monster}
        self.items: Dict[str, Item] = {}
        self.npcs: Dict[str, Dict[str, NPC]] = {}  # world_id -> {npc_id -> NPC}
        self.room_entities: Dict[str, Dict[str, List]] = {}  # world_id -> {room_id -> [monsters, npcs, items]}
        self.rooms_config: Dict[str, Dict] = {}  # world_id -> {room_id -> config}
        self._load_all_data()
    
    def _load_all_data(self):
        """Carrega todos os dados do jogo"""
        for world_dir in self.worlds_dir.iterdir():
            if world_dir.is_dir() and world_dir.name == "default":
                world_id = world_dir.name
                self._load_world_data(world_id)
    
    def _load_world_data(self, world_id: str):
        """Carrega dados de um mundo específico"""
        world_dir = self.worlds_dir / world_id
        self.monsters[world_id] = {}
        self.npcs[world_id] = {}
        self.room_entities[world_id] = {}
        
        # Carrega monstros
        monsters_file = world_dir / "monsters.json"
        if monsters_file.exists():
            try:
                with open(monsters_file, 'r', encoding='utf-8') as f:
                    monsters_data = json.load(f)
                    for monster_data in monsters_data:
                        monster = Monster(
                            id=monster_data['id'],
                            name=monster_data['name'],
                            description=monster_data['description'],
                            max_hp=monster_data['max_hp'],
                            current_hp=monster_data['max_hp'],
                            attack=monster_data['attack'],
                            defense=monster_data.get('defense', 0),
                            level=monster_data.get('level', 1),
                            level_min=monster_data.get('level_min', monster_data.get('level', 1)),
                            level_max=monster_data.get('level_max', monster_data.get('level', 1)),
                            damage_min=monster_data.get('damage_min', monster_data.get('attack', 1)),
                            damage_max=monster_data.get('damage_max', monster_data.get('attack', 10)),
                            weapon=monster_data.get('weapon', ''),
                            armor=monster_data.get('armor', ''),
                            loot=monster_data.get('loot', []),
                            experience=monster_data.get('experience', 0),
                            experience_per_level=monster_data.get('experience_per_level', 10),
                            loot_chance=monster_data.get('loot_chance', 0.5),
                            gold_min=monster_data.get('gold_min', 0),
                            gold_max=monster_data.get('gold_max', 0),
                            lore=monster_data.get('lore', ''),
                            race_id=monster_data.get('race_id', ''),
                            resistances=monster_data.get('resistances', {}),
                            weaknesses=monster_data.get('weaknesses', {}),
                            spells=monster_data.get('spells', []),
                            spell_chance=monster_data.get('spell_chance', 0.3)
                        )
                        self.monsters[world_id][monster.id] = monster
                        
                        # Adiciona monstro à sala
                        room_id = monster_data.get('room_id', '')
                        if room_id:
                            if room_id not in self.room_entities[world_id]:
                                self.room_entities[world_id][room_id] = {'monsters': [], 'npcs': [], 'items': []}
                            self.room_entities[world_id][room_id]['monsters'].append(monster.id)
            except Exception as e:
                print(f"Erro ao carregar monstros de {world_id}: {e}")
        
        # Carrega itens
        items_file = world_dir / "items.json"
        if items_file.exists():
            try:
                with open(items_file, 'r', encoding='utf-8') as f:
                    items_data = json.load(f)
                    for item_data in items_data:
                        item = Item(
                            id=item_data['id'],
                            name=item_data['name'],
                            description=item_data['description'],
                            type=item_data.get('type', 'misc'),
                            stats=item_data.get('stats', {}),
                            value=item_data.get('value', 0),
                            rarity=item_data.get('rarity', 'common')
                        )
                        self.items[item.id] = item
            except Exception as e:
                print(f"Erro ao carregar itens: {e}")
        
        # Carrega NPCs
        npcs_file = world_dir / "npcs.json"
        if npcs_file.exists():
            try:
                with open(npcs_file, 'r', encoding='utf-8') as f:
                    npcs_data = json.load(f)
                    for npc_data in npcs_data:
                        npc = NPC(
                            id=npc_data['id'],
                            name=npc_data['name'],
                            description=npc_data['description'],
                            dialogue=npc_data.get('dialogue', []),
                            quests=npc_data.get('quests', []),
                            shop_items=npc_data.get('shop_items', []),
                            trade_items=npc_data.get('trade_items', {}),
                            lore=npc_data.get('lore', ''),
                            npc_type=npc_data.get('npc_type', 'normal')
                        )
                        self.npcs[world_id][npc.id] = npc
                        
                        # Adiciona NPC à sala
                        room_id = npc_data.get('room_id', '')
                        if room_id:
                            if room_id not in self.room_entities[world_id]:
                                self.room_entities[world_id][room_id] = {'monsters': [], 'npcs': [], 'items': []}
                            self.room_entities[world_id][room_id]['npcs'].append(npc.id)
            except Exception as e:
                print(f"Erro ao carregar NPCs de {world_id}: {e}")
        
        # Carrega itens no chão
        items_ground_file = world_dir / "items_ground.json"
        if items_ground_file.exists():
            try:
                with open(items_ground_file, 'r', encoding='utf-8') as f:
                    items_ground = json.load(f)
                    for room_id, item_ids in items_ground.items():
                        if room_id not in self.room_entities[world_id]:
                            self.room_entities[world_id][room_id] = {'monsters': [], 'npcs': [], 'items': []}
                        self.room_entities[world_id][room_id]['items'].extend(item_ids)
            except Exception as e:
                print(f"Erro ao carregar itens no chão: {e}")
        
        # Carrega configuração de salas (níveis e monstros agressivos)
        rooms_config_file = world_dir / "rooms_config.json"
        if rooms_config_file.exists():
            try:
                with open(rooms_config_file, 'r', encoding='utf-8') as f:
                    rooms_config_data = json.load(f)
                    self.rooms_config[world_id] = rooms_config_data.get('rooms', {})
                    print(f"[GameData] Configuração de salas carregada para {world_id}")
            except Exception as e:
                print(f"Erro ao carregar configuração de salas: {e}")
    
    def get_room_config(self, world_id: str, room_id: str) -> Optional[Dict]:
        """Retorna configuração de uma sala (nível, monstros agressivos, etc)"""
        if world_id in self.rooms_config:
            return self.rooms_config[world_id].get(room_id)
        return None
    
    def should_spawn_monsters_in_room(self, world_id: str, room_id: str) -> bool:
        """Verifica se deve spawnar monstros em uma sala"""
        config = self.get_room_config(world_id, room_id)
        if config and config.get('monsters'):
            return len(config['monsters']) > 0
        return False
    
    def get_room_monsters(self, world_id: str, room_id: str) -> List[str]:
        """Retorna lista de monstros que devem spawnar em uma sala"""
        config = self.get_room_config(world_id, room_id)
        if config:
            return config.get('monsters', [])
        return []
    
    def is_room_aggressive(self, world_id: str, room_id: str) -> bool:
        """Verifica se uma sala tem monstros agressivos"""
        config = self.get_room_config(world_id, room_id)
        if config:
            return config.get('aggressive_monsters', False)
        return False
    
    def get_room_level_range(self, world_id: str, room_id: str) -> tuple:
        """Retorna range de nível de uma sala (min, max)"""
        config = self.get_room_config(world_id, room_id)
        if config:
            return (config.get('min_level', 1), config.get('max_level', 1))
        return (1, 1)
    
    def get_monster(self, world_id: str, monster_id: str, level: Optional[int] = None) -> Optional[Monster]:
        """
        Retorna um monstro (cria nova instância)
        Se level não for especificado, gera aleatório dentro do range
        """
        if world_id in self.monsters and monster_id in self.monsters[world_id]:
            template = self.monsters[world_id][monster_id]
            
            # Gera level aleatório se não especificado
            if level is None:
                import random
                level = random.randint(template.level_min, template.level_max)
            
            # Calcula stats baseadas no level
            level_diff = level - template.level_min
            hp_bonus = int(template.max_hp * 0.1 * level_diff)  # +10% HP por level acima do mínimo
            attack_bonus = int(template.attack * 0.1 * level_diff)  # +10% ataque por level
            defense_bonus = int(template.defense * 0.1 * level_diff)  # +10% defesa por level
            
            return Monster(
                id=template.id,
                name=template.name,
                description=template.description,
                max_hp=template.max_hp + hp_bonus,
                current_hp=template.max_hp + hp_bonus,
                attack=template.attack + attack_bonus,
                defense=template.defense + defense_bonus,
                level=level,
                level_min=template.level_min,
                level_max=template.level_max,
                damage_min=template.damage_min,
                damage_max=template.damage_max,
                weapon=template.weapon,
                armor=template.armor,
                loot=template.loot.copy(),
                experience=template.experience,
                experience_per_level=template.experience_per_level,
                loot_chance=template.loot_chance,
                gold_min=template.gold_min,
                gold_max=template.gold_max,
                lore=template.lore,
                race_id=template.race_id,
                resistances=template.resistances.copy(),
                weaknesses=template.weaknesses.copy(),
                spells=template.spells.copy(),
                spell_chance=template.spell_chance
            )
        return None
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Retorna um item"""
        return self.items.get(item_id)
    
    def get_npc(self, world_id: str, npc_id: str) -> Optional[NPC]:
        """Retorna um NPC"""
        if world_id in self.npcs:
            return self.npcs[world_id].get(npc_id)
        return None
    
    def get_room_entities(self, world_id: str, room_id: str) -> Dict:
        """Retorna entidades em uma sala (cria se não existir)"""
        if world_id not in self.room_entities:
            self.room_entities[world_id] = {}
        
        if room_id not in self.room_entities[world_id]:
            self.room_entities[world_id][room_id] = {'monsters': [], 'npcs': [], 'items': []}
        
        return self.room_entities[world_id][room_id]
    
    def remove_monster_from_room(self, world_id: str, room_id: str, monster_id: str):
        """Remove monstro de uma sala"""
        if world_id in self.room_entities and room_id in self.room_entities[world_id]:
            if monster_id in self.room_entities[world_id][room_id]['monsters']:
                self.room_entities[world_id][room_id]['monsters'].remove(monster_id)

