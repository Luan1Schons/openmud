"""
Sistema de combate do MUD
"""

import random
import asyncio
from typing import Optional
from mud.core.models import Player, Monster
from mud.utils.ansi import ANSI
from mud.utils.visuals import get_attack_animation, format_hp_bar, format_stamina_bar

class CombatSystem:
    """Sistema de combate entre jogador e monstros"""
    
    @staticmethod
    async def attack_monster(player: Player, monster: Monster, send_message_func, game_data=None) -> bool:
        """
        Jogador ataca monstro. Retorna True se monstro morreu
        game_data: opcional, usado para calcular stats totais com equipamento
        """
        # Animação de ataque
        animation = get_attack_animation()
        for frame in animation:
            await send_message_func(f"\r{ANSI.BRIGHT_GREEN}{frame}{ANSI.RESET}")
            await asyncio.sleep(0.1)
        
        # Calcula dano do jogador usando ataque total (com equipamento)
        total_attack = player.get_total_attack(game_data) if game_data else player.attack
        player_damage = total_attack + random.randint(-2, 2)
        actual_damage = monster.take_damage(player_damage, "physical")
        
        level_info = f" [Nível {monster.level}]" if monster.level > 1 else ""
        await send_message_func(
            f"\r{ANSI.BRIGHT_GREEN}⚔ Você ataca {monster.name}{level_info} causando {actual_damage} de dano! 💥{ANSI.RESET}\r\n"
        )
        
        # Mostra barra de HP do monstro
        monster_hp_bar = format_hp_bar(monster.current_hp, monster.max_hp, f"{monster.name} HP")
        await send_message_func(f"{monster_hp_bar}\r\n")
        
        if not monster.is_alive():
            await send_message_func(
                f"{ANSI.BRIGHT_YELLOW}✨ {monster.name} foi derrotado! ✨{ANSI.RESET}\r\n"
            )
            return True
        
        # Monstro contra-ataca usando o dano configurado
        await asyncio.sleep(0.3)  # Pequena pausa para melhor visualização
        
        monster_damage = monster.get_attack_damage()
        # Usa defesa total (com equipamento) para reduzir dano
        total_defense = player.get_total_defense(game_data) if game_data else player.defense
        actual_damage = player.take_damage(monster_damage, total_defense)
        
        weapon_info = ""
        if monster.weapon:
            weapon_info = f" com {monster.weapon}"
        
        await send_message_func(
            f"{ANSI.RED}👹 {monster.name}{level_info} ataca você{weapon_info} causando {actual_damage} de dano! 💥{ANSI.RESET}\r\n"
        )
        
        # Mostra barras de HP e Stamina do jogador
        player_hp_bar = format_hp_bar(player.current_hp, player.max_hp)
        player_stamina_bar = format_stamina_bar(player.current_stamina, player.max_stamina)
        await send_message_func(f"{player_hp_bar}\r\n")
        await send_message_func(f"{player_stamina_bar}\r\n")
        
        if not player.is_alive():
            await send_message_func(
                f"{ANSI.BRIGHT_RED}💀 Você foi derrotado! 💀{ANSI.RESET}\r\n"
            )
            return "player_died"
        
        return False
    
    @staticmethod
    def calculate_experience(monster: Monster) -> int:
        """Calcula experiência ganha ao derrotar monstro"""
        return monster.get_experience_value()
    
    @staticmethod
    def drop_loot(monster: Monster) -> Optional[str]:
        """Retorna item droppado pelo monstro (se houver)"""
        if monster.loot and random.random() < monster.loot_chance:
            return random.choice(monster.loot)
        return None
    
    @staticmethod
    def drop_gold(monster: Monster) -> int:
        """Retorna ouro droppado pelo monstro"""
        return monster.get_gold_drop()
    
    @staticmethod
    async def monster_cast_spell(monster: Monster, player: Player, spell_id: str, spell_system, send_message_func, game_data=None) -> bool:
        """
        Monstro usa uma magia. Retorna True se o jogador morreu.
        Inclui chance de falha (20% base para monstros).
        game_data: opcional, usado para calcular defesa total com equipamento
        """
        spell = spell_system.get_spell(spell_id)
        if not spell:
            return False
        
        # Chance de falha da magia do monstro (20% base)
        fail_chance = 0.20
        if random.random() < fail_chance:
            await send_message_func(
                f"{ANSI.YELLOW}❌ {monster.name} tentou lançar {spell.name}, mas a magia falhou! ❌{ANSI.RESET}\r\n"
            )
            return False
        
        # Calcula dano (nível do monstro como base)
        damage = spell_system.calculate_spell_damage(
            spell, monster.level, monster.attack, 1, 1.0  # Monstros usam nível 1 da magia
        )
        
        # Aplica dano ao jogador usando defesa total (com equipamento)
        total_defense = player.get_total_defense(game_data) if game_data else player.defense
        actual_damage = player.take_damage(damage, total_defense)
        
        damage_icon = "🔥" if spell.damage_type == "fire" else "❄" if spell.damage_type == "ice" else "⚡" if spell.damage_type == "lightning" else "✨"
        level_info = f" [Nível {monster.level}]" if monster.level > 1 else ""
        await send_message_func(
            f"{ANSI.RED}{damage_icon} {monster.name}{level_info} lança {spell.name} em você causando {actual_damage} de dano! {damage_icon}{ANSI.RESET}\r\n"
        )
        
        # Mostra barras de HP e Stamina do jogador
        player_hp_bar = format_hp_bar(player.current_hp, player.max_hp)
        player_stamina_bar = format_stamina_bar(player.current_stamina, player.max_stamina)
        await send_message_func(f"{player_hp_bar}\r\n")
        await send_message_func(f"{player_stamina_bar}\r\n")
        
        if not player.is_alive():
            await send_message_func(
                f"{ANSI.BRIGHT_RED}💀 Você foi derrotado! 💀{ANSI.RESET}\r\n"
            )
            return "player_died"
        
        return False

