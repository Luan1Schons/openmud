"""
Sistema de Raças para Monstros
"""

from typing import Dict, Optional

MONSTER_RACES: Dict[str, Dict] = {
    'beast': {
        'name': 'Bestas',
        'description': 'Criaturas selvagens e animais',
        'icon': '🐺',
        'examples': ['wolf', 'bear', 'spider']
    },
    'humanoid': {
        'name': 'Humanoides',
        'description': 'Criaturas humanoides inteligentes',
        'icon': '👤',
        'examples': ['goblin', 'orc', 'human']
    },
    'undead': {
        'name': 'Mortos-Vivos',
        'description': 'Criaturas não-mortas',
        'icon': '💀',
        'examples': ['zombie', 'skeleton', 'lich']
    },
    'elemental': {
        'name': 'Elementais',
        'description': 'Criaturas de pura energia elemental',
        'icon': '🔥',
        'examples': ['fire_elemental', 'ice_elemental']
    },
    'demon': {
        'name': 'Demônios',
        'description': 'Criaturas do plano infernal',
        'icon': '😈',
        'examples': ['imp', 'demon', 'devil']
    },
    'dragon': {
        'name': 'Dragões',
        'description': 'Répteis lendários e poderosos',
        'icon': '🐉',
        'examples': ['dragon', 'wyvern', 'drake']
    },
    'construct': {
        'name': 'Constructos',
        'description': 'Criaturas artificiais e mecânicas',
        'icon': '🤖',
        'examples': ['golem', 'automaton']
    },
    'plant': {
        'name': 'Plantas',
        'description': 'Criaturas vegetais',
        'icon': '🌿',
        'examples': ['treant', 'vines', 'mushroom_king']
    }
}

def get_monster_race(race_id: str) -> Optional[Dict]:
    """Retorna informações de uma raça de monstro"""
    return MONSTER_RACES.get(race_id)

def get_race_name(race_id: str) -> str:
    """Retorna o nome de uma raça"""
    race = MONSTER_RACES.get(race_id)
    return race['name'] if race else 'Desconhecida'

def get_race_icon(race_id: str) -> str:
    """Retorna o ícone de uma raça"""
    race = MONSTER_RACES.get(race_id)
    return race['icon'] if race else '❓'

