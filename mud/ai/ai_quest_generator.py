"""
Gerador de quests usando IA (preparado para múltiplas APIs)
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from mud.core.models import Quest

# Carrega variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    # Carrega .env do diretório raiz do projeto
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv não instalado, usa apenas variáveis de ambiente do sistema
    pass

class AIQuestGenerator:
    """Gerador de quests usando IA"""
    
    def __init__(self, api_key: Optional[str] = None, provider: Optional[str] = None):
        # Tenta carregar do .env ou variáveis de ambiente
        self.provider = provider or os.getenv("AI_PROVIDER", "openai")
        
        if self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        else:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("[INFO] Geração de quests com IA desabilitada (nenhuma API key configurada)")
    
    async def generate_quest(self, npc_name: str, npc_lore: str, world_context: Dict) -> Optional[Dict]:
        """
        Gera uma quest usando IA
        Retorna dict com dados da quest ou None se falhar
        """
        if not self.enabled:
            return None
        
        prompt = self._build_prompt(npc_name, npc_lore, world_context)
        
        try:
            if self.provider == "openai":
                return await self._generate_with_openai(prompt)
            elif self.provider == "anthropic":
                return await self._generate_with_anthropic(prompt)
            else:
                return None
        except Exception as e:
            print(f"Erro ao gerar quest com IA: {e}")
            return None
    
    def _build_prompt(self, npc_name: str, npc_lore: str, world_context: Dict) -> str:
        """Constrói o prompt para a IA"""
        return f"""
Crie uma quest interessante para um jogo MUD (Multi-User Dungeon) baseado nas seguintes informações:

NPC: {npc_name}
Lore do NPC: {npc_lore}
Contexto do Mundo: {json.dumps(world_context, ensure_ascii=False)}

A quest deve ter:
1. Nome criativo e envolvente (máximo 50 caracteres)
2. Descrição clara do que o jogador precisa fazer (2-3 frases)
3. Lore rica que conecta a quest com o NPC e o mundo (3-4 frases)
4. Objetivos específicos (pode incluir: matar monstros, coletar itens, explorar locais)
5. Recompensas apropriadas (ouro, experiência, itens)

Formato de resposta JSON:
{{
    "name": "Nome da Quest",
    "description": "Descrição da quest",
    "lore": "História e contexto da quest",
    "objectives": [
        {{"type": "kill", "target": "monster_id", "amount": 5}},
        {{"type": "collect", "target": "item_id", "amount": 3}}
    ],
    "rewards": {{
        "gold": 100,
        "experience": 50,
        "items": ["item_id"]
    }}
}}

Retorne APENAS o JSON, sem markdown ou código.
"""
    
    async def _generate_with_openai(self, prompt: str) -> Optional[Dict]:
        """Gera quest usando OpenAI API"""
        try:
            import openai
            
            if not self.api_key:
                return None
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente que cria quests interessantes para jogos MUD. Sempre retorne apenas JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks se houver
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            return json.loads(content)
        except ImportError:
            print("OpenAI não instalado. Instale com: pip install openai")
            return None
        except Exception as e:
            print(f"Erro ao chamar OpenAI: {e}")
            return None
    
    async def _generate_with_anthropic(self, prompt: str) -> Optional[Dict]:
        """Gera quest usando Anthropic Claude API"""
        try:
            import anthropic
            
            if not self.api_key:
                return None
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                temperature=0.8,
                system="Você é um assistente que cria quests interessantes para jogos MUD. Sempre retorne apenas JSON válido.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text.strip()
            
            # Remove markdown code blocks se houver
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            return json.loads(content)
        except ImportError:
            print("Anthropic não instalado. Instale com: pip install anthropic")
            return None
        except Exception as e:
            print(f"Erro ao chamar Anthropic: {e}")
            return None


