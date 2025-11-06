"""
Sistema de Classes, Raças e Gêneros do MUD
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Race:
    """Representa uma raça"""
    id: str
    name: str
    description: str
    history: str
    icon: str
    bonuses: Dict[str, int]  # {attack: 2, defense: -1, etc}
    classes: List[str]  # IDs de classes compatíveis

@dataclass
class GameClass:
    """Representa uma classe do jogo"""
    id: str
    name: str
    description: str
    history: str
    icon: str
    base_stats: Dict[str, int]  # HP, attack, defense, etc
    starting_items: List[str]  # IDs de itens iniciais
    starting_gold: int

@dataclass
class Gender:
    """Representa um gênero"""
    id: str
    name: str
    icon: str

class ClassSystem:
    """Sistema de classes, raças e gêneros"""
    
    def __init__(self):
        self.classes: Dict[str, GameClass] = {}
        self.races: Dict[str, Race] = {}
        self.genders: Dict[str, Gender] = {}
        self._initialize_classes()
        self._initialize_races()
        self._initialize_genders()
    
    def _initialize_classes(self):
        """Inicializa as classes do jogo"""
        # Guerreiro
        self.classes['warrior'] = GameClass(
            id='warrior',
            name='Guerreiro',
            description='Um combatente corpo a corpo especializado em armas pesadas e armaduras.',
            history='Os Guerreiros são mestres do combate próximo. Treinados desde jovens nas artes marciais, eles protegem os fracos e defendem os valores da honra e coragem. Sua força bruta e resistência os tornam a primeira linha de defesa em qualquer batalha.',
            icon='⚔',
            base_stats={
                'max_hp': 150,
                'attack': 15,
                'defense': 12,
                'level': 1
            },
            starting_items=['sword', 'armor'],
            starting_gold=50
        )
        
        # Mago
        self.classes['mage'] = GameClass(
            id='mage',
            name='Mago',
            description='Um estudioso das artes arcanas que manipula energia mágica para lançar feitiços poderosos.',
            history='Os Magos dedicam suas vidas ao estudo das artes arcanas. Passam anos em bibliotecas antigas, decifrando grimórios e dominando os elementos. Embora frágeis fisicamente, seu poder mágico pode devastar exércitos inteiros.',
            icon='🔮',
            base_stats={
                'max_hp': 80,
                'attack': 20,
                'defense': 5,
                'level': 1
            },
            starting_items=['staff', 'spellbook'],
            starting_gold=100
        )
        
        # Arqueiro
        self.classes['ranger'] = GameClass(
            id='ranger',
            name='Arqueiro',
            description='Um especialista em combate à distância, ágil e versátil, capaz de atacar dos mais variados ângulos.',
            history='Os Arqueiros são filhos da natureza, criados nas florestas e montanhas. Sua afinidade com a natureza e precisão lendária fazem deles caçadores formidáveis. Movem-se como sombras e suas flechas nunca erram o alvo.',
            icon='🏹',
            base_stats={
                'max_hp': 110,
                'attack': 18,
                'defense': 8,
                'level': 1
            },
            starting_items=['bow', 'leather_armor'],
            starting_gold=75
        )
    
    def _initialize_races(self):
        """Inicializa as raças do jogo"""
        # Humanos (compatível com todas as classes)
        self.races['human'] = Race(
            id='human',
            name='Humano',
            description='Versáteis e adaptáveis, os humanos não possuem especializações extremas mas são bons em tudo.',
            history='Os Humanos são a raça mais numerosa e diversa. Sem bônus ou penalidades extremas, eles dependem de sua versatilidade e determinação para prosperar. Sua capacidade de adaptação os torna aptos para qualquer classe.',
            icon='👤',
            bonuses={'attack': 0, 'defense': 0, 'hp': 0},
            classes=['warrior', 'mage', 'ranger']
        )
        
        # Anões (melhor para Guerreiro)
        self.races['dwarf'] = Race(
            id='dwarf',
            name='Anão',
            description='Robustos e resistentes, os anões têm grande afinidade com armaduras pesadas e armas de duas mãos.',
            history='Os Anões são mestres da forja e da mineração. Vivem nas profundezas das montanhas, onde constroem impérios subterrâneos. Sua resistência física e força os tornam excelentes guerreiros, capazes de suportar golpes que derrubariam outros.',
            icon='⛏',
            bonuses={'attack': 2, 'defense': 5, 'hp': 20},
            classes=['warrior']
        )
        
        # Elfos (melhor para Mago e Arqueiro)
        self.races['elf'] = Race(
            id='elf',
            name='Elfo',
            description='Elegantes e longevos, os elfos têm grande afinidade com magia e natureza.',
            history='Os Elfos são imortais e conectados com as forças mágicas do mundo. Vivem em harmonia com a natureza há milênios, desenvolvendo habilidades arcanas e de combate à distância. Sua sabedoria e agilidade são lendárias.',
            icon='🌿',
            bonuses={'attack': 3, 'defense': 2, 'hp': -10},
            classes=['mage', 'ranger']
        )
        
        # Orcs (melhor para Guerreiro)
        self.races['orc'] = Race(
            id='orc',
            name='Orc',
            description='Bárbaros e ferozes, os orcs são guerreiros naturais com força bruta incomparável.',
            history='Os Orcs são uma raça de guerreiros nascidos para a batalha. Sua cultura valoriza força e honra em combate. Embora sejam vistos como selvagens por outras raças, possuem um código de honra rígido e são leais à sua tribo.',
            icon='⚒',
            bonuses={'attack': 5, 'defense': 3, 'hp': 15},
            classes=['warrior']
        )
        
        # Gnomos (melhor para Mago)
        self.races['gnome'] = Race(
            id='gnome',
            name='Gnomo',
            description='Pequenos mas inteligentes, os gnomos são especialistas em magia arcana e engenharia.',
            history='Os Gnomos são pequenos mas extremamente inteligentes. Passam suas vidas em laboratórios e bibliotecas, criando engenhocas mágicas e estudando os segredos do universo. Sua curiosidade insaciável os torna excelentes magos.',
            icon='🔧',
            bonuses={'attack': 4, 'defense': -2, 'hp': -15},
            classes=['mage']
        )
        
        # Halflings (melhor para Arqueiro)
        self.races['halfling'] = Race(
            id='halfling',
            name='Halfling',
            description='Ágeis e sortudos, os halflings são especialistas em combate à distância e sobrevivência.',
            history='Os Halflings são pequenos e ágeis, conhecidos por sua sorte e habilidades de sobrevivência. Vivem em comunidades pacíficas mas quando necessário, são arqueiros formidáveis. Sua natureza alegre esconde coragem de sobra.',
            icon='🍀',
            bonuses={'attack': 2, 'defense': 4, 'hp': -5},
            classes=['ranger']
        )
    
    def _initialize_genders(self):
        """Inicializa os gêneros disponíveis"""
        self.genders['male'] = Gender(
            id='male',
            name='Masculino',
            icon='♂'
        )
        
        self.genders['female'] = Gender(
            id='female',
            name='Feminino',
            icon='♀'
        )
        
        self.genders['other'] = Gender(
            id='other',
            name='Outro',
            icon='⚧'
        )
    
    def get_class(self, class_id: str) -> GameClass:
        """Retorna uma classe pelo ID"""
        return self.classes.get(class_id)
    
    def get_race(self, race_id: str) -> Race:
        """Retorna uma raça pelo ID"""
        return self.races.get(race_id)
    
    def get_gender(self, gender_id: str) -> Gender:
        """Retorna um gênero pelo ID"""
        return self.genders.get(gender_id)
    
    def get_races_for_class(self, class_id: str) -> List[Race]:
        """Retorna raças compatíveis com uma classe"""
        return [race for race in self.races.values() if class_id in race.classes]
    
    def get_classes_for_race(self, race_id: str) -> List[GameClass]:
        """Retorna classes compatíveis com uma raça"""
        race = self.get_race(race_id)
        if not race:
            return []
        return [self.classes[cid] for cid in race.classes if cid in self.classes]
    
    def apply_race_bonuses(self, base_stats: Dict[str, int], race_id: str) -> Dict[str, int]:
        """Aplica bônus de raça às estatísticas base"""
        race = self.get_race(race_id)
        if not race:
            return base_stats.copy()
        
        stats = base_stats.copy()
        for stat, bonus in race.bonuses.items():
            if stat in stats:
                stats[stat] += bonus
            elif stat == 'hp':
                stats['max_hp'] = stats.get('max_hp', 100) + bonus
                stats['current_hp'] = stats.get('current_hp', stats['max_hp'])
        
        return stats
    
    def list_all_classes(self) -> List[Dict]:
        """Retorna lista de todas as classes"""
        return [
            {
                'id': cls.id,
                'name': cls.name,
                'icon': cls.icon,
                'description': cls.description
            }
            for cls in self.classes.values()
        ]
    
    def list_all_races(self) -> List[Dict]:
        """Retorna lista de todas as raças"""
        return [
            {
                'id': race.id,
                'name': race.name,
                'icon': race.icon,
                'description': race.description
            }
            for race in self.races.values()
        ]
    
    def list_all_genders(self) -> List[Dict]:
        """Retorna lista de todos os gêneros"""
        return [
            {
                'id': gender.id,
                'name': gender.name,
                'icon': gender.icon
            }
            for gender in self.genders.values()
        ]

