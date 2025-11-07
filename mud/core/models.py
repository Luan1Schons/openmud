"""
Modelos de dados do MUD
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional, List, Tuple
import asyncio

@dataclass
class Room:
    """Representa uma sala no mundo do jogo"""
    id: str
    name: str
    description: str
    exits: Dict[str, str]  # direção -> room_id
    
    def to_dict(self):
        return asdict(self)

@dataclass
class World:
    """Representa um mundo/história do jogo"""
    id: str
    name: str
    description: str
    start_room: str
    rooms: Dict[str, Room]
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_room': self.start_room,
            'rooms': {k: v.to_dict() for k, v in self.rooms.items()}
        }

@dataclass
class Item:
    """Representa um item do jogo"""
    id: str
    name: str
    description: str
    type: str  # weapon, armor, consumable, misc
    stats: Dict[str, int] = None  # attack, defense, hp, stamina, mana, etc
    value: int = 0  # Valor em moedas
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    
    def __post_init__(self):
        if self.stats is None:
            self.stats = {}
    
    def get_rarity_color(self) -> str:
        """Retorna código ANSI para cor da raridade"""
        from mud.utils.ansi import ANSI
        colors = {
            "common": ANSI.WHITE,
            "uncommon": ANSI.GREEN,
            "rare": ANSI.BLUE,
            "epic": ANSI.MAGENTA,
            "legendary": ANSI.BRIGHT_YELLOW
        }
        return colors.get(self.rarity, ANSI.WHITE)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Monster:
    """Representa um monstro do jogo"""
    id: str
    name: str
    description: str
    max_hp: int
    current_hp: int
    attack: int
    defense: int
    level: int = 1
    level_min: int = 1  # Level mínimo do monstro
    level_max: int = 1  # Level máximo do monstro
    damage_min: int = 1  # Dano mínimo do ataque
    damage_max: int = 10  # Dano máximo do ataque
    weapon: str = ""  # ID da arma equipada
    armor: str = ""  # ID da armadura equipada
    loot: List[str] = None  # IDs de itens que podem dropar
    experience: int = 0
    experience_per_level: int = 10  # Experiência adicional por level acima do mínimo
    loot_chance: float = 0.5  # Chance de dropar loot (0.0 a 1.0)
    gold_min: int = 0  # Ouro mínimo que pode dropar
    gold_max: int = 0  # Ouro máximo que pode dropar
    lore: str = ""
    race_id: str = ""  # Raça do monstro (organização)
    resistances: Dict[str, float] = None  # Resistências a tipos de dano (ex: {'fire': 0.5, 'ice': 0.0})
    weaknesses: Dict[str, float] = None  # Fraquezas a tipos de dano (ex: {'fire': 1.5})
    spells: List[str] = None  # IDs de magias que o monstro pode usar
    spell_chance: float = 0.3  # Chance de usar magia (se tiver arma, reduzida)
    
    def __post_init__(self):
        if self.loot is None:
            self.loot = []
        if self.resistances is None:
            self.resistances = {}
        if self.weaknesses is None:
            self.weaknesses = {}
        if self.spells is None:
            self.spells = []
    
    def can_use_spell(self) -> bool:
        """Verifica se o monstro pode usar magia (considera se tem arma)"""
        if not self.spells:
            return False
        
        import random
        chance = self.spell_chance
        # Se tem arma equipada, reduz chance de usar magia
        if self.weapon:
            chance *= 0.5  # Reduz pela metade
        
        return random.random() < chance
    
    def get_random_spell(self) -> Optional[str]:
        """Retorna uma magia aleatória do monstro"""
        if self.spells:
            import random
            return random.choice(self.spells)
        return None
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def take_damage(self, damage: int, damage_type: str = "physical") -> int:
        """Aplica dano e retorna o dano real recebido"""
        # Aplica resistências/fraquezas
        multiplier = 1.0
        if damage_type in self.resistances:
            multiplier *= (1.0 - self.resistances[damage_type])
        if damage_type in self.weaknesses:
            multiplier *= self.weaknesses[damage_type]
        
        final_damage = int(damage * multiplier)
        actual_damage = max(1, final_damage - self.defense)
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def get_attack_damage(self) -> int:
        """Retorna o dano de ataque do monstro (aleatório dentro do range)"""
        import random
        return random.randint(self.damage_min, self.damage_max)
    
    def get_experience_value(self) -> int:
        """Calcula experiência baseada no level do monstro"""
        level_bonus = (self.level - self.level_min) * self.experience_per_level
        return self.experience + level_bonus
    
    def get_gold_drop(self) -> int:
        """Retorna ouro que o monstro pode dropar"""
        if self.gold_max <= 0:
            return 0
        import random
        return random.randint(self.gold_min, self.gold_max)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'attack': self.attack,
            'defense': self.defense,
            'level': self.level,
            'level_min': self.level_min,
            'level_max': self.level_max,
            'damage_min': self.damage_min,
            'damage_max': self.damage_max,
            'weapon': self.weapon,
            'armor': self.armor,
            'loot': self.loot,
            'experience': self.experience,
            'experience_per_level': self.experience_per_level,
            'loot_chance': self.loot_chance,
            'gold_min': self.gold_min,
            'gold_max': self.gold_max,
            'lore': self.lore,
            'resistances': self.resistances,
            'weaknesses': self.weaknesses
        }

@dataclass
class Quest:
    """Representa uma quest/missão"""
    id: str
    name: str
    description: str
    lore: str  # História da quest
    objectives: List[Dict]  # [{type: 'kill', target: 'monster_id', amount: 5}, {type: 'collect', target: 'item_id', amount: 3}]
    rewards: Dict[str, int]  # {gold: 100, experience: 50, items: ['item_id']}
    giver_npc: str  # ID do NPC que dá a quest
    status: str = 'available'  # available, active, completed
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'lore': self.lore,
            'objectives': self.objectives,
            'rewards': self.rewards,
            'giver_npc': self.giver_npc,
            'status': self.status
        }

@dataclass
class NPC:
    """Representa um NPC (Non-Player Character)"""
    id: str
    name: str
    description: str
    dialogue: List[str]  # Frases que o NPC pode dizer
    quests: List[str] = None  # IDs de quests
    shop_items: List[Dict] = None  # [{item_id: 'sword', price: 100}, ...]
    trade_items: Dict[str, List[str]] = None  # {give: ['item1'], receive: ['item2']}
    lore: str = ""
    npc_type: str = "normal"  # normal, shopkeeper, trader, quest_giver
    
    def __post_init__(self):
        if self.quests is None:
            self.quests = []
        if self.shop_items is None:
            self.shop_items = []
        if self.trade_items is None:
            self.trade_items = {}
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Player:
    """Representa um jogador conectado"""
    name: str
    world_id: str
    room_id: str
    writer: asyncio.StreamWriter
    reader: asyncio.StreamReader
    
    # Classe, Raça e Gênero
    class_id: str = ""
    race_id: str = ""
    gender_id: str = ""
    
    # Atributos do jogador
    max_hp: int = 100
    current_hp: int = 100
    max_stamina: int = 100
    current_stamina: int = 100
    level: int = 1
    experience: int = 0
    attack: int = 10
    defense: int = 5
    gold: int = 0
    
    # Inventário
    inventory: List[str] = None  # IDs de itens
    equipment: Dict[str, str] = None  # slot -> item_id
    
    # Quest tracking
    active_quests: List[str] = None  # IDs de quests ativas
    quest_progress: Dict[str, Dict] = None  # {quest_id: {objective_type: progress}}
    completed_quests: List[str] = None
    
    # Magias e Perks
    known_spells: Dict[str, int] = None  # {spell_id: level}
    equipped_spells: List[str] = None  # IDs de magias equipadas (max 3)
    active_perks: List[str] = None  # IDs de perks ativos
    spell_cooldowns: Dict[str, float] = None  # {spell_id: timestamp}
    unspent_points: int = 0  # Pontos não distribuídos ao subir de nível
    
    # Status AFK (para lobby)
    is_afk: bool = False
    afk_message: str = ""
    
    # Canais de chat (channels)
    channels: List[str] = None  # Lista de canais que o jogador está inscrito
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
        if self.equipment is None:
            self.equipment = {}
        if self.active_quests is None:
            self.active_quests = []
        if self.quest_progress is None:
            self.quest_progress = {}
        if self.completed_quests is None:
            self.completed_quests = []
        if self.known_spells is None:
            self.known_spells = {}
        if self.equipped_spells is None:
            self.equipped_spells = []
        if self.active_perks is None:
            self.active_perks = []
        if self.spell_cooldowns is None:
            self.spell_cooldowns = {}
        if not hasattr(self, 'unspent_points'):
            self.unspent_points = 0
        if not hasattr(self, 'is_afk'):
            self.is_afk = False
        if not hasattr(self, 'afk_message'):
            self.afk_message = ""
        if self.channels is None:
            # Canal "local" sempre está ativo por padrão
            self.channels = ["local"]
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def take_damage(self, damage: int, defense: Optional[int] = None) -> int:
        """Aplica dano e retorna o dano real recebido. Se defense for None, usa self.defense"""
        if defense is None:
            defense = self.defense
        actual_damage = max(1, damage - defense)
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int):
        """Cura o jogador"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def add_item(self, item_id: str, amount: int = 1):
        """Adiciona item ao inventário (empilha itens do mesmo tipo como no Minecraft)"""
        for _ in range(amount):
            self.inventory.append(item_id)
    
    def remove_item(self, item_id: str, amount: int = 1):
        """Remove item do inventário (remove apenas a quantidade especificada)"""
        for _ in range(amount):
            if item_id in self.inventory:
                self.inventory.remove(item_id)
    
    def has_item(self, item_id: str, amount: int = 1) -> bool:
        """Verifica se tem item no inventário"""
        return self.inventory.count(item_id) >= amount
    
    def get_item_count(self, item_id: str) -> int:
        """Retorna quantidade de um item no inventário"""
        return self.inventory.count(item_id)
    
    def add_gold(self, amount: int):
        """Adiciona ouro"""
        self.gold += amount
    
    def spend_gold(self, amount: int) -> bool:
        """Tenta gastar ouro. Retorna True se conseguiu"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def use_stamina(self, amount: int) -> bool:
        """Tenta gastar stamina. Retorna True se conseguiu"""
        if self.current_stamina >= amount:
            self.current_stamina -= amount
            return True
        return False
    
    def restore_stamina(self, amount: int):
        """Restaura stamina"""
        self.current_stamina = min(self.max_stamina, self.current_stamina + amount)
    
    def has_stamina(self, amount: int) -> bool:
        """Verifica se tem stamina suficiente"""
        return self.current_stamina >= amount
    
    def learn_spell(self, spell_id: str, level: int = 1):
        """Aprende uma magia ou aumenta seu nível"""
        self.known_spells[spell_id] = level
    
    def improve_spell(self, spell_id: str) -> bool:
        """Melhora uma magia em 1 nível. Retorna True se conseguiu"""
        if spell_id in self.known_spells:
            self.known_spells[spell_id] += 1
            return True
        return False
    
    def get_spell_level(self, spell_id: str) -> int:
        """Retorna o nível de uma magia"""
        return self.known_spells.get(spell_id, 0)
    
    def has_spell(self, spell_id: str) -> bool:
        """Verifica se conhece uma magia"""
        return spell_id in self.known_spells
    
    def activate_perk(self, perk_id: str):
        """Ativa um perk"""
        if perk_id not in self.active_perks:
            self.active_perks.append(perk_id)
    
    def has_perk(self, perk_id: str) -> bool:
        """Verifica se tem um perk ativo"""
        return perk_id in self.active_perks
    
    def equip_spell(self, spell_id: str) -> bool:
        """Equipa uma magia (max 3). Retorna True se conseguiu"""
        if len(self.equipped_spells) >= 3:
            return False
        if spell_id not in self.equipped_spells and spell_id in self.known_spells:
            self.equipped_spells.append(spell_id)
            return True
        return False
    
    def unequip_spell(self, spell_id: str):
        """Desequipa uma magia"""
        if spell_id in self.equipped_spells:
            self.equipped_spells.remove(spell_id)
    
    def is_spell_equipped(self, spell_id: str) -> bool:
        """Verifica se uma magia está equipada"""
        return spell_id in self.equipped_spells
    
    def get_address(self):
        return self.writer.get_extra_info('peername')
    
    def get_total_attack(self, game_data=None) -> int:
        """Retorna o ataque total (base + equipamento)"""
        total = self.attack
        if game_data and self.equipment:
            for slot, item_id in self.equipment.items():
                if item_id:  # Ignora slots vazios
                    item = game_data.get_item(item_id) if hasattr(game_data, 'get_item') else None
                    if item and item.stats:
                        total += item.stats.get('attack', 0)
        return total
    
    def get_total_defense(self, game_data=None) -> int:
        """Retorna a defesa total (base + equipamento)"""
        total = self.defense
        if game_data and self.equipment:
            for slot, item_id in self.equipment.items():
                if item_id:  # Ignora slots vazios
                    item = game_data.get_item(item_id) if hasattr(game_data, 'get_item') else None
                    if item and item.stats:
                        total += item.stats.get('defense', 0)
        return total
    
    def equip_item(self, item_id: str, game_data=None) -> Tuple[bool, str]:
        """
        Equipa um item. Retorna (sucesso, mensagem)
        Slots: weapon, armor, accessory
        """
        if item_id not in self.inventory:
            return False, "Item não está no inventário"
        
        if game_data:
            item = game_data.get_item(item_id)
            if not item:
                return False, "Item não encontrado"
            
            # Determina o slot baseado no tipo
            if item.type == 'weapon':
                slot = 'weapon'
            elif item.type == 'armor':
                slot = 'armor'
            else:
                return False, f"Item do tipo '{item.type}' não pode ser equipado"
            
            # Se já tem algo equipado nesse slot, desequipa primeiro
            if slot in self.equipment and self.equipment[slot]:
                old_item_id = self.equipment[slot]
                # Não remove do inventário, apenas desequipa
            
            # Equipa o novo item
            self.equipment[slot] = item_id
            return True, f"{item.name} equipado em {slot}"
        
        return False, "Sistema de dados do jogo não disponível"
    
    def unequip_item(self, slot: str) -> Tuple[bool, str]:
        """
        Desequipa um item de um slot. Retorna (sucesso, mensagem)
        """
        if slot not in self.equipment or not self.equipment.get(slot):
            return False, f"Nada equipado em {slot}"
        
        item_id = self.equipment[slot]
        # Remove o slot do dicionário
        del self.equipment[slot]
        return True, f"Item desequipado de {slot}"
    
    def get_equipped_item(self, slot: str) -> Optional[str]:
        """Retorna o ID do item equipado em um slot, ou None"""
        return self.equipment.get(slot)
    
    def is_item_equipped(self, item_id: str) -> bool:
        """Verifica se um item está equipado"""
        return item_id in [v for v in self.equipment.values() if v]
