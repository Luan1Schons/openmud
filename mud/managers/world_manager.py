"""
Gerenciador de mundos/histórias do jogo
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from mud.core.models import World, Room

class WorldManager:
    """Gerencia carregamento e acesso aos mundos"""
    
    def __init__(self, worlds_dir: str = "worlds"):
        self.worlds_dir = Path(worlds_dir)
        self.worlds: Dict[str, World] = {}
        self._load_worlds()
    
    def _load_worlds(self):
        """Carrega todos os mundos da pasta worlds (apenas default ativo)"""
        if not self.worlds_dir.exists():
            self.worlds_dir.mkdir(parents=True, exist_ok=True)
            # Cria um mundo padrão se não houver nenhum
            self._create_default_world()
            return
        
        # Carrega apenas o mundo default
        default_file = self.worlds_dir / "default.json"
        if default_file.exists():
            try:
                world = self._load_world_from_file(default_file)
                if world:
                    self.worlds[world.id] = world
                    print(f"Mundo carregado: {world.name} ({world.id})")
            except Exception as e:
                print(f"Erro ao carregar mundo {default_file}: {e}")
                self._create_default_world()
        else:
            self._create_default_world()
    
    def _load_world_from_file(self, file_path: Path) -> Optional[World]:
        """Carrega um mundo de um arquivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Valida estrutura básica
        if 'id' not in data or 'name' not in data or 'rooms' not in data:
            raise ValueError(f"Arquivo {file_path} não tem estrutura válida")
        
        # Carrega salas
        rooms = {}
        for room_data in data['rooms']:
            room = Room(
                id=room_data['id'],
                name=room_data['name'],
                description=room_data['description'],
                exits=room_data.get('exits', {})
            )
            rooms[room.id] = room
        
        # Cria mundo
        world = World(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            start_room=data.get('start_room', data['rooms'][0]['id'] if data['rooms'] else ''),
            rooms=rooms
        )
        
        return world
    
    def _create_default_world(self):
        """Cria um mundo padrão se não houver nenhum"""
        default_world = {
            "id": "default",
            "name": "Mundo Padrão",
            "description": "Um mundo simples para começar sua aventura",
            "start_room": "central",
            "rooms": [
                {
                    "id": "central",
                    "name": "Praça Central",
                    "description": "Uma ampla praça de pedra. No centro há uma fonte antiga com água cristalina. Você pode ver várias saídas em diferentes direções.",
                    "exits": {
                        "norte": "floresta",
                        "sul": "cidade",
                        "leste": "montanha",
                        "oeste": "praia"
                    }
                },
                {
                    "id": "floresta",
                    "name": "Floresta Sombria",
                    "description": "Árvores altas e antigas criam uma sombra densa. Você ouve sons de animais distantes. O caminho de volta está ao sul.",
                    "exits": {
                        "sul": "central"
                    }
                },
                {
                    "id": "cidade",
                    "name": "Cidade Antiga",
                    "description": "Ruas de pedra e casas antigas. Você vê alguns NPCs caminhando. A praça central está ao norte.",
                    "exits": {
                        "norte": "central"
                    }
                },
                {
                    "id": "montanha",
                    "name": "Encosta da Montanha",
                    "description": "Uma trilha íngreme leva para cima. O ar está mais fresco aqui. A praça central está a oeste.",
                    "exits": {
                        "oeste": "central"
                    }
                },
                {
                    "id": "praia",
                    "name": "Praia Deserta",
                    "description": "Areia branca e ondas suaves. O sol brilha intensamente. A praça central está a leste.",
                    "exits": {
                        "leste": "central"
                    }
                }
            ]
        }
        
        default_file = self.worlds_dir / "default.json"
        with open(default_file, 'w', encoding='utf-8') as f:
            json.dump(default_world, f, indent=2, ensure_ascii=False)
        
        # Carrega o mundo criado
        world = self._load_world_from_file(default_file)
        if world:
            self.worlds[world.id] = world
    
    def get_world(self, world_id: str) -> Optional[World]:
        """Retorna um mundo pelo ID"""
        return self.worlds.get(world_id)
    
    def list_worlds(self) -> list:
        """Retorna lista de mundos disponíveis"""
        return [
            {
                'id': world.id,
                'name': world.name,
                'description': world.description
            }
            for world in self.worlds.values()
        ]
    
    def get_room(self, world_id: str, room_id: str, dungeon_manager=None) -> Optional[Room]:
        """Retorna uma sala de um mundo (incluindo dungeons)"""
        # Primeiro tenta nas salas normais
        world = self.get_world(world_id)
        if world:
            room = world.rooms.get(room_id)
            if room:
                return room
        
        # Se não encontrou, tenta nas dungeons
        if dungeon_manager:
            dungeon_room = dungeon_manager.get_dungeon_room(world_id, room_id)
            if dungeon_room:
                return dungeon_room
        
        return None

