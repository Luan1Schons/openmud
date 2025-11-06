"""
Sistema de Magias e Perks do MUD
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Spell:
    """Representa uma magia"""
    id: str
    name: str
    description: str
    icon: str
    class_id: str  # Classe que pode usar esta magia
    level_required: int  # Level mínimo para aprender
    stamina_cost: int  # Custo de stamina
    base_damage: int  # Dano base
    damage_multiplier: float  # Multiplicador baseado em stats (ex: 0.5 = 50% do attack)
    damage_type: str  # physical, fire, ice, lightning, etc
    cooldown: int  # Cooldown em segundos
    max_level: int = 5  # Nível máximo da magia
    unlock_requirement: Optional[str] = None  # ID de outra magia que precisa ser aprendida primeiro

@dataclass
class Perk:
    """Representa um perk/passivo"""
    id: str
    name: str
    description: str
    icon: str
    class_id: str
    level_required: int
    effects: Dict[str, float]  # {stat: modifier} ex: {'attack': 1.1, 'defense': 1.05}
    unlock_requirement: Optional[str] = None

class SpellSystem:
    """Sistema de magias e perks"""
    
    def __init__(self):
        self.spells: Dict[str, Spell] = {}
        self.perks: Dict[str, Perk] = {}
        self._initialize_spells()
        self._initialize_perks()
    
    def _initialize_spells(self):
        """Inicializa as magias do jogo"""
        
        # ========== MAGIAS DO MAGO ==========
        
        # Bola de Fogo (inicial)
        self.spells['fireball'] = Spell(
            id='fireball',
            name='Bola de Fogo',
            description='Lança uma bola de fogo que causa dano em área.',
            icon='🔥',
            class_id='mage',
            level_required=1,
            stamina_cost=20,
            base_damage=15,
            damage_multiplier=0.8,  # 80% do attack
            damage_type='fire',
            cooldown=30,
            max_level=5
        )
        
        # Raio de Gelo (inicial)
        self.spells['ice_bolt'] = Spell(
            id='ice_bolt',
            name='Raio de Gelo',
            description='Lança um raio de gelo que causa dano e pode reduzir velocidade do alvo.',
            icon='❄',
            class_id='mage',
            level_required=1,
            stamina_cost=15,
            base_damage=12,
            damage_multiplier=0.7,  # 70% do attack
            damage_type='ice',
            cooldown=30,
            max_level=5
        )
        
        # Relâmpago (desbloqueável nível 5)
        self.spells['lightning'] = Spell(
            id='lightning',
            name='Relâmpago',
            description='Invoca um relâmpago que causa dano elétrico massivo.',
            icon='⚡',
            class_id='mage',
            level_required=5,
            stamina_cost=35,
            base_damage=25,
            damage_multiplier=1.0,  # 100% do attack
            damage_type='lightning',
            cooldown=5,
            max_level=5
        )
        
        # Escudo Arcano (desbloqueável nível 3)
        self.spells['arcane_shield'] = Spell(
            id='arcane_shield',
            name='Escudo Arcano',
            description='Cria um escudo mágico que reduz dano recebido.',
            icon='🛡',
            class_id='mage',
            level_required=3,
            stamina_cost=25,
            base_damage=0,  # Não causa dano
            damage_multiplier=0.0,
            damage_type='arcane',
            cooldown=10,
            max_level=5
        )
        
        # Cura Menor (desbloqueável nível 2)
        self.spells['minor_heal'] = Spell(
            id='minor_heal',
            name='Cura Menor',
            description='Cura uma pequena quantidade de HP.',
            icon='💚',
            class_id='mage',
            level_required=2,
            stamina_cost=20,
            base_damage=0,
            damage_multiplier=0.0,
            damage_type='heal',
            cooldown=5,
            max_level=5
        )
        
        # ========== MAGIAS DO GUERREIRO ==========
        
        # Golpe Feroz (inicial)
        self.spells['fierce_strike'] = Spell(
            id='fierce_strike',
            name='Golpe Feroz',
            description='Um golpe poderoso que causa dano extra.',
            icon='⚔',
            class_id='warrior',
            level_required=1,
            stamina_cost=15,
            base_damage=20,
            damage_multiplier=0.6,  # 60% do attack
            damage_type='physical',
            cooldown=3,
            max_level=5
        )
        
        # Fúria Berserker (desbloqueável nível 5)
        self.spells['berserker_rage'] = Spell(
            id='berserker_rage',
            name='Fúria Berserker',
            description='Entra em fúria, aumentando ataque e reduzindo defesa temporariamente.',
            icon='😠',
            class_id='warrior',
            level_required=5,
            stamina_cost=40,
            base_damage=0,
            damage_multiplier=0.0,
            damage_type='buff',
            cooldown=30,
            max_level=3
        )
        
        # ========== MAGIAS DO ARQUEIRO ==========
        
        # Tiro Preciso (inicial)
        self.spells['precise_shot'] = Spell(
            id='precise_shot',
            name='Tiro Preciso',
            description='Um tiro preciso que causa dano crítico.',
            icon='🎯',
            class_id='ranger',
            level_required=1,
            stamina_cost=15,
            base_damage=18,
            damage_multiplier=0.75,  # 75% do attack
            damage_type='physical',
            cooldown=2,
            max_level=5
        )
        
        # Chuva de Flechas (desbloqueável nível 5)
        self.spells['arrow_volley'] = Spell(
            id='arrow_volley',
            name='Chuva de Flechas',
            description='Lança múltiplas flechas que atingem vários alvos.',
            icon='🌧',
            class_id='ranger',
            level_required=5,
            stamina_cost=35,
            base_damage=15,
            damage_multiplier=0.6,  # 60% do attack por flecha
            damage_type='physical',
            cooldown=8,
            max_level=5
        )
        
        # ========== MAGIAS ESPECIAIS (META GAMING) ==========
        
        # ========== MAGO - Nível 10 ==========
        self.spells['meteor_strike'] = Spell(
            id='meteor_strike',
            name='Queda de Meteoros',
            description='Invoca meteoros que caem do céu causando dano massivo em área.',
            icon='☄',
            class_id='mage',
            level_required=10,
            stamina_cost=60,
            base_damage=50,
            damage_multiplier=1.5,  # 150% do attack
            damage_type='fire',
            cooldown=20,
            max_level=3
        )
        
        # ========== MAGO - Nível 20 ==========
        self.spells['time_stop'] = Spell(
            id='time_stop',
            name='Parar o Tempo',
            description='Para o tempo, permitindo múltiplos ataques sem resposta do inimigo.',
            icon='⏸',
            class_id='mage',
            level_required=20,
            stamina_cost=80,
            base_damage=0,
            damage_multiplier=0.0,
            damage_type='time',
            cooldown=60,
            max_level=2
        )
        
        # ========== MAGO - Nível 30 ==========
        self.spells['arcane_annihilation'] = Spell(
            id='arcane_annihilation',
            name='Aniquilação Arcana',
            description='A magia definitiva. Causa dano verdadeiro que ignora todas as resistências.',
            icon='💀',
            class_id='mage',
            level_required=30,
            stamina_cost=100,
            base_damage=100,
            damage_multiplier=2.0,  # 200% do attack
            damage_type='arcane',
            cooldown=120,
            max_level=1
        )
        
        # ========== GUERREIRO - Nível 10 ==========
        self.spells['earthquake'] = Spell(
            id='earthquake',
            name='Terremoto',
            description='Bate no chão com força sobre-humana, causando dano em área e derrubando inimigos.',
            icon='🌍',
            class_id='warrior',
            level_required=10,
            stamina_cost=50,
            base_damage=45,
            damage_multiplier=1.3,  # 130% do attack
            damage_type='physical',
            cooldown=15,
            max_level=3
        )
        
        # ========== GUERREIRO - Nível 20 ==========
        self.spells['immortal_rage'] = Spell(
            id='immortal_rage',
            name='Fúria Imortal',
            description='Entra em estado de fúria imortal, regenerando HP e aumentando dano drasticamente.',
            icon='👹',
            class_id='warrior',
            level_required=20,
            stamina_cost=70,
            base_damage=0,
            damage_multiplier=0.0,
            damage_type='buff',
            cooldown=45,
            max_level=2
        )
        
        # ========== GUERREIRO - Nível 30 ==========
        self.spells['god_slayer'] = Spell(
            id='god_slayer',
            name='Matador de Deuses',
            description='O golpe definitivo. Um ataque que pode matar qualquer inimigo em um golpe.',
            icon='⚔',
            class_id='warrior',
            level_required=30,
            stamina_cost=90,
            base_damage=150,
            damage_multiplier=3.0,  # 300% do attack
            damage_type='physical',
            cooldown=180,
            max_level=1
        )
        
        # ========== ARQUEIRO - Nível 10 ==========
        self.spells['hunters_mark'] = Spell(
            id='hunters_mark',
            name='Marca do Caçador',
            description='Marca o alvo, aumentando dano crítico e revelando fraquezas.',
            icon='🎯',
            class_id='ranger',
            level_required=10,
            stamina_cost=40,
            base_damage=0,
            damage_multiplier=0.0,
            damage_type='debuff',
            cooldown=12,
            max_level=3
        )
        
        # ========== ARQUEIRO - Nível 20 ==========
        self.spells['nature_wrath'] = Spell(
            id='nature_wrath',
            name='Ira da Natureza',
            description='Invoca a fúria da natureza, causando múltiplos ataques de elementos naturais.',
            icon='🌿',
            class_id='ranger',
            level_required=20,
            stamina_cost=65,
            base_damage=35,
            damage_multiplier=1.2,  # 120% do attack
            damage_type='nature',
            cooldown=25,
            max_level=2
        )
        
        # ========== ARQUEIRO - Nível 30 ==========
        self.spells['perfect_shot'] = Spell(
            id='perfect_shot',
            name='Tiro Perfeito',
            description='O tiro definitivo. Sempre acerta e causa dano crítico massivo.',
            icon='🏹',
            class_id='ranger',
            level_required=30,
            stamina_cost=85,
            base_damage=120,
            damage_multiplier=2.5,  # 250% do attack
            damage_type='physical',
            cooldown=90,
            max_level=1
        )
    
    def _initialize_perks(self):
        """Inicializa os perks do jogo"""
        
        # ========== PERKS DO MAGO ==========
        
        # Intelecto Aprimorado (nível 3)
        self.perks['enhanced_intellect'] = Perk(
            id='enhanced_intellect',
            name='Intelecto Aprimorado',
            description='Aumenta o poder de suas magias em 15%.',
            icon='🧠',
            class_id='mage',
            level_required=3,
            effects={'spell_power': 1.15}
        )
        
        # Regeneração de Mana (nível 5)
        self.perks['mana_regeneration'] = Perk(
            id='mana_regeneration',
            name='Regeneração de Mana',
            description='Regenera stamina mais rapidamente.',
            icon='💫',
            class_id='mage',
            level_required=5,
            effects={'stamina_regen': 1.5}
        )
        
        # ========== PERKS DO GUERREIRO ==========
        
        # Pele de Ferro (nível 3)
        self.perks['iron_skin'] = Perk(
            id='iron_skin',
            name='Pele de Ferro',
            description='Aumenta defesa em 20%.',
            icon='🛡',
            class_id='warrior',
            level_required=3,
            effects={'defense': 1.2}
        )
        
        # Força Bruta (nível 5)
        self.perks['brute_force'] = Perk(
            id='brute_force',
            name='Força Bruta',
            description='Aumenta ataque em 25%.',
            icon='💪',
            class_id='warrior',
            level_required=5,
            effects={'attack': 1.25}
        )
        
        # ========== PERKS DO ARQUEIRO ==========
        
        # Olhos de Falcão (nível 3)
        self.perks['hawk_eyes'] = Perk(
            id='hawk_eyes',
            name='Olhos de Falcão',
            description='Aumenta chance de crítico em 20%.',
            icon='👁',
            class_id='ranger',
            level_required=3,
            effects={'crit_chance': 1.2}
        )
        
        # Agilidade Feline (nível 5)
        self.perks['feline_agility'] = Perk(
            id='feline_agility',
            name='Agilidade Felina',
            description='Aumenta velocidade e evasão em 15%.',
            icon='🐱',
            class_id='ranger',
            level_required=5,
            effects={'evasion': 1.15, 'speed': 1.15}
        )
        
        # ========== PERKS ADICIONAIS ==========
        
        # Mago - Foco Arcano (nível 7)
        self.perks['arcane_focus'] = Perk(
            id='arcane_focus',
            name='Foco Arcano',
            description='Reduz cooldown de magias em 20%.',
            icon='🔮',
            class_id='mage',
            level_required=7,
            effects={'cooldown_reduction': 0.8}
        )
        
        # Mago - Escudo Mágico (nível 10)
        self.perks['magic_shield'] = Perk(
            id='magic_shield',
            name='Escudo Mágico',
            description='Reduz dano recebido em 15%.',
            icon='🛡',
            class_id='mage',
            level_required=10,
            effects={'damage_reduction': 0.85}
        )
        
        # Guerreiro - Sangue Fervente (nível 7)
        self.perks['boiling_blood'] = Perk(
            id='boiling_blood',
            name='Sangue Fervente',
            description='Regenera HP ao derrotar inimigos.',
            icon='💉',
            class_id='warrior',
            level_required=7,
            effects={'hp_on_kill': 10}
        )
        
        # Guerreiro - Vontade de Ferro (nível 10)
        self.perks['iron_will'] = Perk(
            id='iron_will',
            name='Vontade de Ferro',
            description='Resistência a efeitos de status aumentada.',
            icon='⚔',
            class_id='warrior',
            level_required=10,
            effects={'status_resistance': 0.5}
        )
        
        # Arqueiro - Mãos Rápidas (nível 7)
        self.perks['quick_hands'] = Perk(
            id='quick_hands',
            name='Mãos Rápidas',
            description='Aumenta velocidade de ataque em 25%.',
            icon='🏹',
            class_id='ranger',
            level_required=7,
            effects={'attack_speed': 1.25}
        )
        
        # Arqueiro - Instinto Selvagem (nível 10)
        self.perks['wild_instinct'] = Perk(
            id='wild_instinct',
            name='Instinto Selvagem',
            description='Aumenta dano contra monstros em 20%.',
            icon='🐺',
            class_id='ranger',
            level_required=10,
            effects={'monster_damage': 1.2}
        )
    
    def get_spell(self, spell_id: str) -> Optional[Spell]:
        """Retorna uma magia pelo ID"""
        return self.spells.get(spell_id)
    
    def get_perk(self, perk_id: str) -> Optional[Perk]:
        """Retorna um perk pelo ID"""
        return self.perks.get(perk_id)
    
    def get_spells_for_class(self, class_id: str) -> List[Spell]:
        """Retorna todas as magias de uma classe"""
        return [spell for spell in self.spells.values() if spell.class_id == class_id]
    
    def get_perks_for_class(self, class_id: str) -> List[Perk]:
        """Retorna todos os perks de uma classe"""
        return [perk for perk in self.perks.values() if perk.class_id == class_id]
    
    def get_starting_spells(self, class_id: str) -> List[str]:
        """Retorna IDs das magias iniciais de uma classe"""
        if class_id == 'mage':
            return ['fireball', 'ice_bolt']
        elif class_id == 'warrior':
            return ['fierce_strike']
        elif class_id == 'ranger':
            return ['precise_shot']
        return []
    
    def calculate_spell_damage(self, spell: Spell, player_level: int, player_attack: int, 
                               spell_level: int = 1, race_bonus: float = 1.0) -> int:
        """
        Calcula dano da magia baseado em:
        - Dano base da magia
        - Nível da magia
        - Nível do jogador
        - Attack do jogador
        - Bônus de raça
        """
        # Dano base
        base = spell.base_damage
        
        # Bônus por nível da magia (10% por nível)
        level_bonus = base * (spell_level - 1) * 0.1
        
        # Dano baseado em attack do jogador
        attack_damage = int(player_attack * spell.damage_multiplier)
        
        # Bônus por nível do jogador (5% por nível acima de 1)
        level_multiplier = 1.0 + ((player_level - 1) * 0.05)
        
        # Aplica bônus de raça
        total_damage = int((base + level_bonus + attack_damage) * level_multiplier * race_bonus)
        
        return max(1, total_damage)
    
    def calculate_spell_cost(self, spell: Spell, spell_level: int = 1) -> int:
        """Calcula custo de stamina da magia (aumenta 5% por nível)"""
        cost_multiplier = 1.0 + ((spell_level - 1) * 0.05)
        return int(spell.stamina_cost * cost_multiplier)
    
    def can_learn_spell(self, spell: Spell, player_level: int, known_spells: List[str]) -> bool:
        """Verifica se o jogador pode aprender uma magia"""
        if player_level < spell.level_required:
            return False
        
        if spell.unlock_requirement and spell.unlock_requirement not in known_spells:
            return False
        
        return True

