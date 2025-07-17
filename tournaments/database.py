import psycopg2
from psycopg2.extras import DictCursor
import os

from config import Role

class Database:
    def __init__(self):
        self.DATABASE_URL = os.environ.get('DATABASE_URL')
        self.init_db()

    def init_db(self):
        with self.connect() as conn:
            with conn.cursor() as c:
                c.execute('''CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(50) UNIQUE NOT NULL,
                            password VARCHAR(128) NOT NULL,
                            role VARCHAR(20) NOT NULL,
                            email VARCHAR(255))''')
                                        
                c.execute('''CREATE TABLE IF NOT EXISTS players ( 
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                                name VARCHAR(100) UNIQUE NOT NULL,
                                rating INTEGER NOT NULL DEFAULT 1000 CHECK (rating >= 0))''')

                c.execute('''CREATE TABLE IF NOT EXISTS tournaments (
                                id SERIAL PRIMARY KEY,
                                admin_id INTEGER NOT NULL REFERENCES users(id),
                                name VARCHAR(100) NOT NULL,
                                date TIMESTAMPTZ NOT NULL,
                                status VARCHAR(20) NOT NULL DEFAULT 'upcoming',
                                total_rounds SMALLINT NOT NULL CHECK (total_rounds > 0),
                                current_round SMALLINT NOT NULL DEFAULT 0 CHECK (current_round >= 0),
                                CONSTRAINT valid_status CHECK (status IN ('upcoming', 'ongoing', 'finished')))''')

                c.execute('''CREATE TABLE IF NOT EXISTS tournament_players (
                                tournament_id INTEGER REFERENCES tournaments(id) ON DELETE CASCADE,
                                player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
                                points REAL NOT NULL DEFAULT 0 CHECK (points >= 0),
                                color_balance SMALLINT NOT NULL DEFAULT 0,
                                PRIMARY KEY (tournament_id, player_id))''')

                c.execute('''CREATE TABLE IF NOT EXISTS matches (
                                id SERIAL PRIMARY KEY,
                                tournament_id INTEGER NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
                                round SMALLINT NOT NULL CHECK (round > 0),
                                player1_id INTEGER REFERENCES players(id) ON DELETE SET NULL,
                                player2_id INTEGER REFERENCES players(id) ON DELETE SET NULL,
                                result VARCHAR(8) NOT NULL DEFAULT 'pending',
                                player1_color VARCHAR(10) NOT NULL,
                                CONSTRAINT valid_result CHECK (result IN ('1-0', '0-1', '1/2-1/2', 'pending')),
                                CONSTRAINT valid_color CHECK (player1_color IN ('red', 'black')),
                                CONSTRAINT no_self_match CHECK (player1_id != player2_id))''')
                                
                c.execute("CREATE INDEX IF NOT EXISTS idx_matches_tournament ON matches(tournament_id)")
                c.execute("CREATE INDEX IF NOT EXISTS idx_matches_player1 ON matches(player1_id)")
                c.execute("CREATE INDEX IF NOT EXISTS idx_matches_player2 ON matches(player2_id)")
                c.execute("CREATE INDEX IF NOT EXISTS idx_tournament_status ON tournaments(status)")
                c.execute("CREATE INDEX IF NOT EXISTS idx_player_rating ON players(rating DESC)")

                c.execute('''INSERT INTO users (username, password, role) 
                            VALUES (%s, %s, %s)
                            ON CONFLICT (username) DO NOTHING''', 
                        (os.environ.get('ADMIN_NAME'), os.environ.get('ADMIN_PASSWORD_HEX'), Role.admin.value))

                conn.commit()

    def connect(self):
        return psycopg2.connect(self.DATABASE_URL, sslmode='require', cursor_factory=DictCursor)

    def execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        with self.connect() as conn:
            with conn.cursor() as c:
                c.execute(query, params)
                result = None
                if fetchone:
                    result = c.fetchone()
                elif fetchall:
                    result = c.fetchall()
                
                if commit or "INSERT" in query:
                    conn.commit()
                    if "RETURNING id" in query:
                        result = c.fetchone()[0]
        return result
    
    def process_query(self, func, query, params=(), limit=0):
        #limit=0 means fetch all
        conn = self.connect()
        c = conn.cursor()
        c.execute(query, params)
        result = []
        if limit:
            row = c.fetchone()
            while limit > 0 and row:
                result.append(func(row))
                row = c.fetchone()
                limit -= 1
        else:
            for row in c:
                result.append(func(row))
        
        conn.close()
        return result
            

    def commit_query(self):
        conn = self.connect()
        conn.commit()
        conn.close()

    def print_table(self, headers, data):
        str_data = [
            [str(item) for item in row] 
            for row in data
        ]
        
        widths = [
            max(len(header), *[len(row[i]) for row in str_data]) 
            for i, header in enumerate(headers)
        ]
        
        fmt = " ".join(f"{{:<{w}}}" for w in widths)
        
        print(fmt.format(*headers))
        
        separator = " ".join("-" * w for w in widths)
        print(separator)
        
        for row in str_data:
            print(fmt.format(*row))