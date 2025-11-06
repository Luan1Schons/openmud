"""
Sistema de criação de personagem (escolha de classe, raça e gênero)
"""

import asyncio
from mud.utils.ansi import ANSI
from mud.systems.classes import ClassSystem

async def create_character(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, 
                          class_system: ClassSystem) -> tuple[str, str, str]:
    """
    Processa criação de personagem
    Retorna (class_id, race_id, gender_id)
    """
    writer.write(f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}=== Criação de Personagem ==={ANSI.RESET}\r\n".encode())
    writer.write(f"{ANSI.BRIGHT_YELLOW}Você precisa escolher sua classe, raça e gênero.{ANSI.RESET}\r\n\r\n".encode())
    await writer.drain()
    
    # Escolha de Classe
    class_id = await choose_class(writer, reader, class_system)
    if not class_id:
        return None, None, None
    
    # Escolha de Raça (compatível com a classe)
    race_id = await choose_race(writer, reader, class_system, class_id)
    if not race_id:
        return None, None, None
    
    # Escolha de Gênero
    gender_id = await choose_gender(writer, reader, class_system)
    if not gender_id:
        return None, None, None
    
    # Confirmação
    confirmed = await confirm_character(writer, reader, class_system, class_id, race_id, gender_id)
    if not confirmed:
        return None, None, None
    
    return class_id, race_id, gender_id

async def choose_class(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, 
                      class_system: ClassSystem) -> str:
    """Escolha de classe"""
    classes = class_system.list_all_classes()
    
    message = f"\r\n{ANSI.BOLD}{ANSI.CYAN}=== Escolha sua Classe ==={ANSI.RESET}\r\n\r\n"
    for i, cls in enumerate(classes, 1):
        message += f"{ANSI.BRIGHT_GREEN}{i}.{ANSI.RESET} {cls['icon']} {ANSI.BRIGHT_CYAN}{cls['name']}{ANSI.RESET}\r\n"
        message += f"   {cls['description']}\r\n\r\n"
    
    message += f"{ANSI.BRIGHT_YELLOW}Digite o número da classe:{ANSI.RESET} "
    writer.write(message.encode())
    await writer.drain()
    
    while True:
        try:
            choice_data = await asyncio.wait_for(reader.readline(), timeout=60.0)
            if not choice_data:
                return None
            
            choice = choice_data.decode().strip()
            
            # Tenta por número
            try:
                num = int(choice)
                if 1 <= num <= len(classes):
                    selected_class = classes[num - 1]
                    # Mostra história da classe
                    cls = class_system.get_class(selected_class['id'])
                    if cls:
                        message = f"\r\n{ANSI.BOLD}{cls.icon} {cls.name}{ANSI.RESET}\r\n"
                        message += f"{ANSI.BRIGHT_MAGENTA}{cls.history}{ANSI.RESET}\r\n"
                        writer.write(message.encode())
                        await writer.drain()
                    return selected_class['id']
            except ValueError:
                pass
            
            # Tenta por ID ou nome
            for cls in classes:
                if choice.lower() in cls['id'].lower() or choice.lower() in cls['name'].lower():
                    selected_class = cls
                    cls_obj = class_system.get_class(selected_class['id'])
                    if cls_obj:
                        message = f"\r\n{ANSI.BOLD}{cls_obj.icon} {cls_obj.name}{ANSI.RESET}\r\n"
                        message += f"{ANSI.BRIGHT_MAGENTA}{cls_obj.history}{ANSI.RESET}\r\n"
                        writer.write(message.encode())
                        await writer.drain()
                    return selected_class['id']
            
            writer.write(f"{ANSI.RED}Opção inválida. Tente novamente:{ANSI.RESET} ".encode())
            await writer.drain()
        except asyncio.TimeoutError:
            writer.write(f"{ANSI.RED}Tempo esgotado.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return None

async def choose_race(writer: asyncio.StreamWriter, reader: asyncio.StreamReader,
                     class_system: ClassSystem, class_id: str) -> str:
    """Escolha de raça (compatível com a classe)"""
    races = class_system.get_races_for_class(class_id)
    
    if not races:
        # Se não houver raças específicas, mostra todas
        races = list(class_system.races.values())
    
    message = f"\r\n{ANSI.BOLD}{ANSI.CYAN}=== Escolha sua Raça ==={ANSI.RESET}\r\n\r\n"
    for i, race in enumerate(races, 1):
        message += f"{ANSI.BRIGHT_GREEN}{i}.{ANSI.RESET} {race.icon} {ANSI.BRIGHT_CYAN}{race.name}{ANSI.RESET}\r\n"
        message += f"   {race.description}\r\n"
        # Mostra bônus
        if race.bonuses:
            bonuses = []
            for stat, val in race.bonuses.items():
                if val > 0:
                    bonuses.append(f"{ANSI.BRIGHT_GREEN}+{val} {stat}{ANSI.RESET}")
                elif val < 0:
                    bonuses.append(f"{ANSI.RED}{val} {stat}{ANSI.RESET}")
            if bonuses:
                message += f"   Bônus: {', '.join(bonuses)}\r\n"
        message += "\r\n"
    
    message += f"{ANSI.BRIGHT_YELLOW}Digite o número da raça:{ANSI.RESET} "
    writer.write(message.encode())
    await writer.drain()
    
    while True:
        try:
            choice_data = await asyncio.wait_for(reader.readline(), timeout=60.0)
            if not choice_data:
                return None
            
            choice = choice_data.decode().strip()
            
            # Tenta por número
            try:
                num = int(choice)
                if 1 <= num <= len(races):
                    selected_race = races[num - 1]
                    # Mostra história da raça
                    message = f"\r\n{ANSI.BOLD}{selected_race.icon} {selected_race.name}{ANSI.RESET}\r\n"
                    message += f"{ANSI.BRIGHT_MAGENTA}{selected_race.history}{ANSI.RESET}\r\n"
                    writer.write(message.encode())
                    await writer.drain()
                    return selected_race.id
            except ValueError:
                pass
            
            # Tenta por ID ou nome
            for race in races:
                if choice.lower() in race.id.lower() or choice.lower() in race.name.lower():
                    message = f"\r\n{ANSI.BOLD}{race.icon} {race.name}{ANSI.RESET}\r\n"
                    message += f"{ANSI.BRIGHT_MAGENTA}{race.history}{ANSI.RESET}\r\n"
                    writer.write(message.encode())
                    await writer.drain()
                    return race.id
            
            writer.write(f"{ANSI.RED}Opção inválida. Tente novamente:{ANSI.RESET} ".encode())
            await writer.drain()
        except asyncio.TimeoutError:
            writer.write(f"{ANSI.RED}Tempo esgotado.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return None

async def choose_gender(writer: asyncio.StreamWriter, reader: asyncio.StreamReader,
                       class_system: ClassSystem) -> str:
    """Escolha de gênero"""
    genders = class_system.list_all_genders()
    
    message = f"\r\n{ANSI.BOLD}{ANSI.CYAN}=== Escolha seu Gênero ==={ANSI.RESET}\r\n\r\n"
    for i, gender in enumerate(genders, 1):
        message += f"{ANSI.BRIGHT_GREEN}{i}.{ANSI.RESET} {gender['icon']} {ANSI.BRIGHT_CYAN}{gender['name']}{ANSI.RESET}\r\n"
    
    message += f"\r\n{ANSI.BRIGHT_YELLOW}Digite o número do gênero:{ANSI.RESET} "
    writer.write(message.encode())
    await writer.drain()
    
    while True:
        try:
            choice_data = await asyncio.wait_for(reader.readline(), timeout=60.0)
            if not choice_data:
                return None
            
            choice = choice_data.decode().strip()
            
            # Tenta por número
            try:
                num = int(choice)
                if 1 <= num <= len(genders):
                    return genders[num - 1]['id']
            except ValueError:
                pass
            
            # Tenta por ID ou nome
            for gender in genders:
                if choice.lower() in gender['id'].lower() or choice.lower() in gender['name'].lower():
                    return gender['id']
            
            writer.write(f"{ANSI.RED}Opção inválida. Tente novamente:{ANSI.RESET} ".encode())
            await writer.drain()
        except asyncio.TimeoutError:
            writer.write(f"{ANSI.RED}Tempo esgotado.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return None

async def confirm_character(writer: asyncio.StreamWriter, reader: asyncio.StreamReader,
                          class_system: ClassSystem, class_id: str, race_id: str, gender_id: str) -> bool:
    """Confirmação final do personagem"""
    cls = class_system.get_class(class_id)
    race = class_system.get_race(race_id)
    gender = class_system.get_gender(gender_id)
    
    if not cls or not race or not gender:
        return False
    
    # Calcula estatísticas finais
    final_stats = class_system.apply_race_bonuses(cls.base_stats, race_id)
    
    message = f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}=== Confirmação do Personagem ==={ANSI.RESET}\r\n\r\n"
    message += f"{cls.icon} {ANSI.BRIGHT_GREEN}Classe:{ANSI.RESET} {cls.name}\r\n"
    message += f"{race.icon} {ANSI.BRIGHT_GREEN}Raça:{ANSI.RESET} {race.name}\r\n"
    message += f"{gender.icon} {ANSI.BRIGHT_GREEN}Gênero:{ANSI.RESET} {gender.name}\r\n\r\n"
    message += f"{ANSI.BOLD}Estatísticas Iniciais:{ANSI.RESET}\r\n"
    message += f"  {ANSI.BRIGHT_RED}Vida:{ANSI.RESET} {final_stats.get('max_hp', 100)}\r\n"
    message += f"  {ANSI.BRIGHT_YELLOW}Ataque:{ANSI.RESET} {final_stats.get('attack', 10)}\r\n"
    message += f"  {ANSI.BRIGHT_BLUE}Defesa:{ANSI.RESET} {final_stats.get('defense', 5)}\r\n"
    message += f"  {ANSI.BRIGHT_MAGENTA}Ouro:{ANSI.RESET} {cls.starting_gold}\r\n\r\n"
    message += f"{ANSI.BRIGHT_YELLOW}Confirmar criação? (sim/não):{ANSI.RESET} "
    
    writer.write(message.encode())
    await writer.drain()
    
    try:
        choice_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
        if not choice_data:
            return False
        
        choice = choice_data.decode().strip().lower()
        if choice in ['sim', 's', 'yes', 'y']:
            writer.write(f"{ANSI.BRIGHT_GREEN}Personagem criado com sucesso!{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return True
        else:
            writer.write(f"{ANSI.YELLOW}Criação cancelada.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return False
    except asyncio.TimeoutError:
        return False

