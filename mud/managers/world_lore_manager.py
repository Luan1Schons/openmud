"""
Gerenciador de Lore do Mundo (Introdução e Histórias)
"""

import json
from pathlib import Path
from typing import Optional, Dict, List

class WorldLoreManager:
    """Gerencia a lore e introdução do mundo"""
    
    def __init__(self, worlds_dir: str = "worlds"):
        self.worlds_dir = Path(worlds_dir)
        self.world_lore: Dict[str, Dict] = {}
        self._load_world_lore()
    
    def _load_world_lore(self):
        """Carrega a lore do mundo de cada mundo"""
        for world_dir in self.worlds_dir.iterdir():
            if world_dir.is_dir():
                world_id = world_dir.name
                lore_file = world_dir / "world_lore.json"
                
                if lore_file.exists():
                    try:
                        with open(lore_file, 'r', encoding='utf-8') as f:
                            self.world_lore[world_id] = json.load(f)
                            print(f"[WorldLoreManager] Lore carregada para o mundo: {world_id}")
                    except Exception as e:
                        print(f"[WorldLoreManager] Erro ao carregar lore de {world_id}: {e}")
    
    def get_world_lore(self, world_id: str) -> Optional[Dict]:
        """Retorna a lore de um mundo"""
        return self.world_lore.get(world_id)
    
    def format_world_lore(self, world_id: str) -> Optional[str]:
        """Formata a lore do mundo para exibição"""
        lore = self.get_world_lore(world_id)
        if not lore:
            return None
        
        from mud.utils.ansi import ANSI
        
        formatted = f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}{'=' * 60}{ANSI.RESET}\r\n"
        formatted += f"{ANSI.BOLD}{ANSI.BRIGHT_CYAN}{lore.get('title', 'Lore do Mundo').center(60)}{ANSI.RESET}\r\n"
        formatted += f"{ANSI.BOLD}{ANSI.BRIGHT_CYAN}{'=' * 60}{ANSI.RESET}\r\n\r\n"
        
        if 'subtitle' in lore:
            formatted += f"{ANSI.BRIGHT_YELLOW}{lore['subtitle']}{ANSI.RESET}\r\n\r\n"
        
        sections = lore.get('sections', [])
        for i, section in enumerate(sections, 1):
            title = section.get('title', f'Seção {i}')
            content = section.get('content', '')
            
            formatted += f"{ANSI.BOLD}{ANSI.BRIGHT_MAGENTA}{title}{ANSI.RESET}\r\n"
            formatted += f"{ANSI.BRIGHT_BLACK}{'-' * 60}{ANSI.RESET}\r\n"
            formatted += f"{ANSI.WHITE}{content}{ANSI.RESET}\r\n\r\n"
        
        if 'author' in lore:
            formatted += f"{ANSI.BRIGHT_BLACK}{'─' * 60}{ANSI.RESET}\r\n"
            formatted += f"{ANSI.BRIGHT_BLACK}Por: {lore['author']}{ANSI.RESET}\r\n"
        
        formatted += f"{ANSI.BOLD}{ANSI.BRIGHT_CYAN}{'=' * 60}{ANSI.RESET}\r\n"
        
        return formatted

