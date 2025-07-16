import sqlite3
from functools import wraps

from config import Role, ADMIN, DATABASE

class Database:
    def __init__(self):
        self.name = DATABASE
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.name)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT)''')
    
        c.execute('''CREATE TABLE IF NOT EXISTS players ( 
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT UNIQUE NOT NULL,
                    rating INTEGER DEFAULT 1000,
                    FOREIGN KEY(user_id) REFERENCES users(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS tournaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    date TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'upcoming',
                    total_rounds INTEGER NOT NULL,
                    current_round INTEGER DEFAULT 0,
                    FOREIGN KEY(admin_id) REFERENCES users(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS tournament_players (
                    tournament_id INTEGER,
                    player_id INTEGER,
                    points REAL DEFAULT 0,
                    color_balance INTEGER DEFAULT 0,
                    PRIMARY KEY (tournament_id, player_id),
                    FOREIGN KEY(tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
                    FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE SET NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tournament_id INTEGER,
                    round INTEGER,
                    player1_id INTEGER,
                    player2_id INTEGER,
                    result TEXT DEFAULT 'pending',
                    player1_color TEXT,
                    CHECK(result IN ('1-0', '0-1', '1/2-1/2', 'pending')),
                    CHECK(player1_color IN ('red', 'black')),
                    FOREIGN KEY(tournament_id) REFERENCES tournaments(id) ON DELETE CASCADE,
                    FOREIGN KEY(player1_id) REFERENCES players(id) ON DELETE SET NULL,
                    FOREIGN KEY(player2_id) REFERENCES players(id) ON DELETE SET NULL)''')
        
        c.execute("CREATE INDEX IF NOT EXISTS idx_matches_tournament ON matches(tournament_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_matches_players ON matches(player1_id, player2_id)")

        admin_username, admin_password = ADMIN

        c.execute("SELECT id FROM users WHERE username=?", (admin_username,))
        admin_exists = c.fetchone()

        if not admin_exists:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                        (admin_username, admin_password, Role.admin.value))

        conn.commit()
        conn.close()

    def connect(self):
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        conn = self.connect()
        c = conn.cursor()
        c.execute(query, params)

        result = None
        if fetchone:
            result = c.fetchone()
        elif fetchall:
            result = c.fetchall()
        
        if commit:
            if "INSERT" in query:
                result = c.lastrowid
            conn.commit()
        
        
        conn.close()
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

    # def get_tournaments(self, conn : sqlite3.Connection):
    #     rows = conn.execute(
    #         "SELECT id, name, date_created, status FROM tournaments ORDER BY date_created DESC"
    #     ).fetchall()
    #     return rows

    # def get_players(self, conn : sqlite3.Connection):
    #     rows = conn.execute(
    #         "SELECT id, name, rating FROM players ORDER BY rating DESC"
    #     ).fetchall()
    #     return rows

    # def row_to_namedtuple(row, tuple_type : Data):
    #     return tuple_type(**{field: row[field] for field in tuple_type._fields})

    # @connect
    # def get_tournament_stats(tournament, conn : sqlite3.Connection = None):
    #     stats = []

    #     player_count = conn.execute(
    #         "SELECT COUNT(*) FROM tournament_players WHERE tournament_id=?",
    #         (tournament.id,)
    #     ).fetchone()[0]
        
    #     match_count = conn.execute(
    #         "SELECT COUNT(*) FROM matches WHERE tournament_id=?",
    #         (tournament.id,)
    #     ).fetchone()[0]

    #     stats.append({
    #         'id': tournament.id,
    #         'player_count': player_count,
    #         'match_count': match_count
    #     })

    #     return stats
    
    # @connect
    # def get_user(name, password, conn : sqlite3.Connection = None):
    #     user = conn.cursor().execute("SELECT id, username, role FROM users WHERE username=? AND password=?", 
    #               (name, password)).fetchone()
    #     return user
    
    # @connect
    # def new_user(username, hashed_password, conn : sqlite3.Connection = None):
    #     try:
    #         conn.cursor().execute("INSERT INTO users (username, password) VALUES (?, ?)", 
    #                     (username, hashed_password))
    #         conn.commit()
    #         return Status.ok
    #     except sqlite3.IntegrityError:
    #         return Status.failed
    
    # @connect
    # def new_tournament(username, hashed_password, conn : sqlite3.Connection):
    #     try:
    #         conn.cursor().execute("INSERT INTO users (username, password) VALUES (?, ?)", 
    #                     (username, hashed_password))
    #         conn.commit()
    #         return Status.ok
    #     except sqlite3.IntegrityError:
    #         return Status.failed
    
    # @connect
    # def add_player_to_tournament(tournament_id, player_id, conn : sqlite3.Connection):
    #     c = conn.cursor()
    #     try:
    #         c.execute("INSERT OR IGNORE INTO tournament_players VALUES (?, ?)", 
    #                 (tournament_id, player_id))
    #         conn.commit()
    #         return Status.ok
    #     except:
    #         return Status.failed
