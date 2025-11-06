"""
Gerenciamento de banco de dados SQL para persistência de jogadores
"""

import sqlite3
import json
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

class Database:
    """Gerencia conexão e operações do banco de dados"""
    
    def __init__(self, db_path: str = "mud.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados criando tabelas se necessário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de jogadores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                world_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                class_id TEXT,
                race_id TEXT,
                gender_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                stats TEXT DEFAULT '{}'
            )
        ''')
        
        # Migração: adiciona colunas de classe/raça/gênero se não existirem
        for col in ['class_id', 'race_id', 'gender_id']:
            try:
                cursor.execute(f'ALTER TABLE players ADD COLUMN {col} TEXT')
            except sqlite3.OperationalError:
                pass  # Coluna já existe
        
        # Tabela de contas (para login/registro)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                compatibility_test_done INTEGER DEFAULT 0
            )
        ''')
        
        # Migração: adiciona coluna compatibility_test_done se não existir
        try:
            cursor.execute('ALTER TABLE accounts ADD COLUMN compatibility_test_done INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Tabela de quests (para persistência de quests geradas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quests (
                id TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                npc_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                lore TEXT DEFAULT '',
                objectives TEXT NOT NULL,
                rewards TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                generated_by TEXT DEFAULT 'system'
            )
        ''')
        
        # Migração: adiciona coluna password_hash se não existir
        try:
            cursor.execute('ALTER TABLE players ADD COLUMN password_hash TEXT')
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        
        # Tabela de respawn de monstros (para controlar quando monstros podem respawnar)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monster_respawns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id TEXT NOT NULL,
                room_id TEXT NOT NULL,
                monster_id TEXT NOT NULL,
                instance_id INTEGER NOT NULL,
                death_time TIMESTAMP NOT NULL,
                respawn_time INTEGER NOT NULL,
                UNIQUE(world_id, room_id, monster_id, instance_id)
            )
        ''')
        
        # Índices para melhor performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON players(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_world ON players(world_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON accounts(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quest_world ON quests(world_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quest_npc ON quests(npc_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_respawn_world_room ON monster_respawns(world_id, room_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_respawn_time ON monster_respawns(death_time)')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash da senha usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_connection(self):
        """Retorna uma conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def player_exists(self, name: str) -> bool:
        """Verifica se um jogador existe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM players WHERE name = ?', (name,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def register_account(self, username: str, password: str) -> tuple[bool, str]:
        """Registra uma nova conta. Retorna (sucesso, mensagem)"""
        if not username or not password:
            return False, "Username e senha são obrigatórios"
        
        if len(username) < 3:
            return False, "Username deve ter pelo menos 3 caracteres"
        
        if len(password) < 4:
            return False, "Senha deve ter pelo menos 4 caracteres"
        
        password_hash = self._hash_password(password)
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accounts (username, password_hash)
                VALUES (?, ?)
            ''', (username.lower(), password_hash))
            conn.commit()
            conn.close()
            return True, "Conta criada com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Username já está em uso"
    
    def verify_login(self, username: str, password: str) -> bool:
        """Verifica credenciais de login"""
        password_hash = self._hash_password(password)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT password_hash FROM accounts WHERE username = ?
        ''', (username.lower(),))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] == password_hash:
            # Atualiza último login
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE accounts SET last_login = CURRENT_TIMESTAMP WHERE username = ?
            ''', (username.lower(),))
            conn.commit()
            conn.close()
            return True
        return False
    
    def account_exists(self, username: str) -> bool:
        """Verifica se uma conta existe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM accounts WHERE username = ?', (username.lower(),))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def has_done_compatibility_test(self, username: str) -> bool:
        """Verifica se o usuário já fez o teste de compatibilidade"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT compatibility_test_done FROM accounts WHERE username = ?', (username.lower(),))
        row = cursor.fetchone()
        conn.close()
        return row and row[0] == 1
    
    def mark_compatibility_test_done(self, username: str):
        """Marca o teste de compatibilidade como concluído"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accounts 
            SET compatibility_test_done = 1 
            WHERE username = ?
        ''', (username.lower(),))
        conn.commit()
        conn.close()
    
    def get_player(self, name: str) -> Optional[Dict[str, Any]]:
        """Busca dados de um jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, world_id, room_id, class_id, race_id, gender_id, stats, last_played
            FROM players WHERE name = ?
        ''', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            stats = json.loads(row[6]) if row[6] else {}
            # Se não tem stats básicos, inicializa
            if not stats.get('max_hp'):
                stats['max_hp'] = 100
            if 'current_hp' not in stats:
                stats['current_hp'] = stats.get('max_hp', 100)
            if not stats.get('attack'):
                stats['attack'] = 10
            if not stats.get('defense'):
                stats['defense'] = 5
            
            return {
                'name': row[0],
                'world_id': row[1],
                'room_id': row[2],
                'class_id': row[3] or '',
                'race_id': row[4] or '',
                'gender_id': row[5] or '',
                'stats': stats,
                'last_played': row[7]
            }
        return None
    
    def create_player(self, name: str, world_id: str, room_id: str, 
                     class_id: str = "", race_id: str = "", gender_id: str = "",
                     password_hash: str = None) -> bool:
        """Cria um novo jogador"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if password_hash:
                cursor.execute('''
                    INSERT INTO players (name, password_hash, world_id, room_id, class_id, race_id, gender_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, password_hash, world_id, room_id, class_id, race_id, gender_id))
            else:
                cursor.execute('''
                    INSERT INTO players (name, world_id, room_id, class_id, race_id, gender_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, world_id, room_id, class_id, race_id, gender_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Jogador já existe
            return False
    
    def update_player_class_race_gender(self, name: str, class_id: str, race_id: str, gender_id: str):
        """Atualiza classe, raça e gênero do jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE players
            SET class_id = ?, race_id = ?, gender_id = ?
            WHERE name = ?
        ''', (class_id, race_id, gender_id, name))
        conn.commit()
        conn.close()
    
    def update_player_location(self, name: str, world_id: str, room_id: str):
        """Atualiza localização do jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE players
            SET world_id = ?, room_id = ?, last_played = CURRENT_TIMESTAMP
            WHERE name = ?
        ''', (world_id, room_id, name))
        conn.commit()
        conn.close()
    
    def update_player_stats(self, name: str, stats: Dict[str, Any]):
        """Atualiza estatísticas do jogador"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE players
            SET stats = ?, last_played = CURRENT_TIMESTAMP
            WHERE name = ?
        ''', (json.dumps(stats), name))
        conn.commit()
        conn.close()
    
    def get_all_players(self) -> list:
        """Retorna lista de todos os jogadores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, world_id, room_id FROM players')
        rows = cursor.fetchall()
        conn.close()
        return [{'name': r[0], 'world_id': r[1], 'room_id': r[2]} for r in rows]
    
    def delete_player(self, name: str):
        """Remove um jogador do banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM players WHERE name = ?', (name,))
        conn.commit()
        conn.close()
    
    def save_quest(self, quest: Dict[str, Any], world_id: str, generated_by: str = 'system'):
        """Salva uma quest no banco de dados"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO quests 
                (id, world_id, npc_id, name, description, lore, objectives, rewards, status, generated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                quest['id'],
                world_id,
                quest.get('giver_npc', ''),
                quest['name'],
                quest['description'],
                quest.get('lore', ''),
                json.dumps(quest.get('objectives', []), ensure_ascii=False),
                json.dumps(quest.get('rewards', {}), ensure_ascii=False),
                quest.get('status', 'available'),
                generated_by
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao salvar quest no banco: {e}")
            return False
    
    def get_quests_by_npc(self, world_id: str, npc_id: str) -> List[Dict[str, Any]]:
        """Retorna todas as quests de um NPC do banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, world_id, npc_id, name, description, lore, objectives, rewards, status, generated_by
            FROM quests
            WHERE world_id = ? AND npc_id = ?
        ''', (world_id, npc_id))
        rows = cursor.fetchall()
        conn.close()
        
        quests = []
        for row in rows:
            quests.append({
                'id': row[0],
                'world_id': row[1],
                'giver_npc': row[2],
                'name': row[3],
                'description': row[4],
                'lore': row[5],
                'objectives': json.loads(row[6]) if row[6] else [],
                'rewards': json.loads(row[7]) if row[7] else {},
                'status': row[8],
                'generated_by': row[9]
            })
        return quests
    
    def get_all_quests(self, world_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna todas as quests do banco (opcionalmente filtradas por world_id)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if world_id:
            cursor.execute('''
                SELECT id, world_id, npc_id, name, description, lore, objectives, rewards, status, generated_by
                FROM quests
                WHERE world_id = ?
            ''', (world_id,))
        else:
            cursor.execute('''
                SELECT id, world_id, npc_id, name, description, lore, objectives, rewards, status, generated_by
                FROM quests
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        quests = []
        for row in rows:
            quests.append({
                'id': row[0],
                'world_id': row[1],
                'giver_npc': row[2],
                'name': row[3],
                'description': row[4],
                'lore': row[5],
                'objectives': json.loads(row[6]) if row[6] else [],
                'rewards': json.loads(row[7]) if row[7] else {},
                'status': row[8],
                'generated_by': row[9]
            })
        return quests
    
    def delete_quest(self, quest_id: str):
        """Remove uma quest do banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM quests WHERE id = ?', (quest_id,))
        conn.commit()
        conn.close()
    
    def quest_exists(self, quest_id: str) -> bool:
        """Verifica se uma quest existe no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM quests WHERE id = ?', (quest_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def register_monster_death(self, world_id: str, room_id: str, monster_id: str, instance_id: int, respawn_time: int):
        """Registra a morte de um monstro e quando ele pode respawnar (respawn_time em segundos)"""
        from datetime import datetime, timedelta
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Remove registros antigos deste mesmo monstro (limpeza)
        cursor.execute('''
            DELETE FROM monster_respawns 
            WHERE world_id = ? AND room_id = ? AND monster_id = ? AND instance_id = ?
        ''', (world_id, room_id, monster_id, instance_id))
        
        # Insere novo registro
        cursor.execute('''
            INSERT INTO monster_respawns (world_id, room_id, monster_id, instance_id, death_time, respawn_time)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        ''', (world_id, room_id, monster_id, instance_id, respawn_time))
        
        conn.commit()
        conn.close()
    
    def can_monster_respawn(self, world_id: str, room_id: str, monster_id: str, instance_id: int) -> bool:
        """Verifica se um monstro pode respawnar (se já passou o tempo de respawn)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT death_time, respawn_time 
            FROM monster_respawns 
            WHERE world_id = ? AND room_id = ? AND monster_id = ? AND instance_id = ?
        ''', (world_id, room_id, monster_id, instance_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            # Não há registro, pode respawnar
            return True
        
        from datetime import datetime, timedelta
        death_time = datetime.fromisoformat(row[0])
        respawn_time_seconds = row[1]
        
        # Verifica se já passou o tempo de respawn
        time_since_death = (datetime.now() - death_time).total_seconds()
        return time_since_death >= respawn_time_seconds
    
    def get_room_respawns(self, world_id: str, room_id: str) -> Dict[str, Dict]:
        """Retorna todos os respawns pendentes de uma sala"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT monster_id, instance_id, death_time, respawn_time
            FROM monster_respawns
            WHERE world_id = ? AND room_id = ?
        ''', (world_id, room_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        respawns = {}
        from datetime import datetime
        for row in rows:
            monster_id = row[0]
            instance_id = row[1]
            death_time = datetime.fromisoformat(row[2])
            respawn_time_seconds = row[3]
            
            key = f"{monster_id}_{instance_id}"
            time_since_death = (datetime.now() - death_time).total_seconds()
            time_remaining = max(0, respawn_time_seconds - time_since_death)
            
            respawns[key] = {
                'monster_id': monster_id,
                'instance_id': instance_id,
                'time_remaining': time_remaining,
                'can_respawn': time_remaining <= 0
            }
        
        return respawns
    
    def cleanup_old_respawns(self, world_id: str, room_id: str):
        """Remove registros de respawn que já expiraram"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Remove registros onde o tempo de respawn já passou
        cursor.execute('''
            DELETE FROM monster_respawns
            WHERE world_id = ? AND room_id = ?
            AND (julianday('now') - julianday(death_time)) * 86400 >= respawn_time
        ''', (world_id, room_id))
        
        conn.commit()
        conn.close()

