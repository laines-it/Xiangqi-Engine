from database import Database
from config import Status, Role, get_opponents_json
from models import Tournament, User, Player, TnmtPlayer, Match
import bcrypt



def rating_from(ingo):
    return 2750 - 7*ingo
def ingo_from(rating):
    return (2750 - rating)/7

class UserManager:
    def __init__(self, db : Database):
        self.db = db

    def get_user(self, name, password_bytes) -> User:
        query = '''SELECT u.id, u.username, u.role, u.email,
                          p.id, u.password
                    FROM users u
                    LEFT JOIN players p
                    ON u.id = p.user_id
                    WHERE u.username=%s
                    LIMIT 1
                '''
        
        packed = self.db.process_query(self.parse, query, params=(name,), limit=1)
        if packed:
            user = packed[0]
            return user if user.auth(password_bytes) else User(-1)
        return None
    
    def new_user(self, username, hash_password, role : Role, email):
        password = hash_password.decode('utf-8')
        query = "INSERT INTO users (username, password, role, email) VALUES (%s, %s, %s, %s) RETURNING id"
        try:
            id = self.db.execute_query(query, (username, password, role.value, email), commit=True)
            print(f"USER {username}, id={id} ADDED with Role {role} and email{email}")
            return Status.ok
        except Exception as e:
            print(e)
            return Status.failed

    def parse(self, row):
        us = User(id=row[0],
                name=row[1],
                role=Role(row[2]),
                email=row[3],
                current_player_id=row[4],
                pw=row[5])
        return us
    
class PlayerManager:
    def __init__(self, db : Database):
        self.db = db

    def login_player(self, name, password) -> Player:
        query = '''SELECT u.id, u.username, u.role, u.email, t.id
                FROM users u
                LEFT JOIN tournaments t
                ON u.id = t.admin_id
                WHERE u.username=%s AND u.password=%s
                '''
        packed = self.db.process_query(self.parse, query, params=(name, password), limit=1)
        return packed[0] if packed else None

    def get_player_id(self, name):
        query = '''SELECT p.id
                   WHERE p.name=%s
                '''
        row = self.db.execute_query(query, (name), fetchone=True)
        return row[0] if row else None

    def get_player_tnmt(self, id) -> TnmtPlayer:
        query = '''SELECT p.id, p.user_id, p.name, p.ingo,
                          tp.tournament_id, tp.points, tp.color_balance,
                          ''' + get_opponents_json + '''
                    FROM players p
                    JOIN tournament_players tp
                    ON p.id = tp.player_id
                    WHERE p.id=%s
                '''
        packed = self.db.process_query(self.parse_tnmt, query, params=(id,), limit=1)
        return packed[0] if packed else None

    def get_all(self):
        query = "SELECT id, user_id, name, ingo FROM players ORDER BY ingo ASC"
        return self.db.process_query(self.parse, query)

    def parse(self, row):
        p = Player(id=row[0],
                    user_id=row[1],name=row[2],ingo=ingo_from(row[3]))
        return p
    
    def parse_tnmt(self, row):
        p = TnmtPlayer(id=row[0],
                    user_id=row[1],name=row[2],ingo=ingo_from(row[3]),
                    tnmt_id=row[4],points=row[5],color_balance=row[6],
                    opponents=row[7])
        return p
    
    def new_player(self, name, ingo):
        query = "INSERT INTO players (name, ingo) VALUES (%s, %s) RETURNING id"
        id = self.db.execute_query(query, (name, ingo), commit=True)
        print(f"ADDED PLAYER {name},{rating_from(ingo)}. id = {id}")
        return id

    def delete_player(self, player_id):
        query = "DELETE FROM players WHERE id=%s"
        try:
            self.db.execute_query(query, (player_id,), commit=True)
            return Status.ok
        except:
            return Status.failed
        
    def get_player_by_id(self, id):
        query = "SELECT id, user_id, name, ingo FROM players WHERE id=%s"
        players = self.db.process_query(self.parse, query, (id,), limit=1)
        return players[0] if players else None
    
    def get_player_by_user_id(self, user_id):
        query = "SELECT id, user_id, name, ingo FROM players WHERE user_id=%s"
        players = self.db.process_query(self.parse, query, (user_id,), limit=1)
        return players[0] if players else None

    def new_player_with_user(self, name, ingo, user_id):
        query = "INSERT INTO players (name, ingo, user_id) VALUES (%s, %s, %s) RETURNING id"
        try:
            id = self.db.execute_query(query, (name, ingo, user_id), commit=True)
            return id
        except Exception as e:
            raise Exception("Ошибка при создании игрока: " + str(e))

    def get_player_matches(self, player_id, limit=10):
        query = """
            SELECT m.id, m.tournament_id, t.name AS tournament_name, m.round, 
                p1.name AS player1_name, p2.name AS player2_name,
                m.result, t.date
            FROM matches m
            JOIN tournaments t ON m.tournament_id = t.id
            LEFT JOIN players p1 ON m.player1_id = p1.id
            LEFT JOIN players p2 ON m.player2_id = p2.id
            WHERE (m.player1_id = %s OR m.player2_id = %s) 
            ORDER BY t.date DESC, m.round DESC
            LIMIT %s
        """
        params = (player_id, player_id, limit)
        return self.db.process_query(lambda row: {
            'id': row[0],
            'tournament_id': row[1],
            'tournament_name': row[2],
            'round': row[3],
            'player1_name': row[4],
            'player2_name': row[5],
            'result': row[6],
            'date': row[7]
        }, query, params)

    def get_player_tournaments_ids(self, player_id):
        query = """
            SELECT tournament_id
            FROM tournament_players
            WHERE player_id = %s
        """
        return self.db.execute_query(query, (player_id,), fetchall=True)
    
    def get_player_tournaments(self, player_id):
        query = """
            SELECT t.id, t.name
            FROM tournaments t
            JOIN tournament_players tp ON t.id = tp.tournament_id
            WHERE tp.player_id = %s
            ORDER BY t.date DESC
        """
        return self.db.process_query(lambda row: {
            'id': row[0],
            'name': row[1]
        }, query, (player_id,))


class TnmtManager:
    def __init__(self, db : Database):
        self.db = db
        self.tnmts = []

    def create(self, name, admin_id, date, total_rounds):
        query = "INSERT INTO tournaments (name, admin_id, date, total_rounds) VALUES (%s, %s, %s, %s) RETURNING id"
        id = self.db.execute_query(query, (name, admin_id, date, total_rounds), commit=True)
        print(f"Tournament CREATED with id={id}")
        return id
    
    def delete(self, tournament_id):
        queries = [
            "DELETE FROM tournament_players WHERE tournament_id=%s",
            "DELETE FROM matches WHERE tournament_id=%s",
            "DELETE FROM tournaments WHERE id=%s"
        ]
        for query in queries:
            self.db.execute_query(query, (tournament_id,), commit=True)

    def parse(self, t):
        players = self.get_players(t[0])
        tnmt = Tournament(id=t[0],
                        admin_id=t[1],
                        name=t[2],
                        date=t[3],
                        status=t[4],
                        players=players,
                        current_round=t[5],
                        total_rounds=t[6])
        return tnmt
    
    def parse_print(self, t):
        tnmt = Tournament(id=t[0],
                        admin_id=t[1],
                        name=t[2],
                        date=t[3],
                        status=t[4],
                        current_round=t[5],
                        total_rounds=t[6])
        return tnmt

    def get_all(self, for_print = False) -> list[Tournament]:
        query = '''SELECT id, admin_id, name, date, status, current_round, total_rounds
                    FROM tournaments
                    ORDER BY date DESC
                '''
        process_func = self.parse_print if for_print else self.parse
        return self.db.process_query(process_func, query)

    def get_by_id(self, tournament_id) -> Tournament:
        query = '''SELECT id, admin_id, name, date, status, current_round, total_rounds
                    FROM tournaments WHERE id=%s
                '''
        packed = self.db.process_query(self.parse, query, params=(tournament_id,), limit=1)
        return packed[0] if packed else None

    def get_players_ids(self, tournament_id):
        query = '''
            SELECT player_id
            FROM tournament_players
            WHERE tournament_id = %s
        '''
        rows = self.db.execute_query(query, (tournament_id,), fetchall=True)
        return rows

    def get_players(self, tournament_id) -> list[Player]:
        query = '''
            SELECT pl.id, pl.user_id, pl.name, pl.ingo,
                   tp.tournament_id, tp.points, tp.color_balance,
            ''' + get_opponents_json + '''
            FROM tournament_players tp
            JOIN players pl ON tp.player_id = pl.id
            WHERE tp.tournament_id = %s'''
        pm = PlayerManager(self.db)
        return self.db.process_query(pm.parse_tnmt, query, params=(tournament_id,))

    def add_player(self, tournament_id, player_id):
        query = "INSERT INTO tournament_players VALUES (%s, %s, %s, %s) ON CONFLICT (tournament_id, player_id) DO NOTHING"
        self.db.execute_query(query, (tournament_id, player_id, 0, 0), commit=True)
    
    def get_stats(self, tournament_id):
        queries = [
            ("SELECT COUNT(*) FROM tournament_players WHERE tournament_id=%s", (tournament_id,)),
            ("SELECT COUNT(*) FROM matches WHERE tournament_id=%s", (tournament_id,))
        ]
        stats = {}
        for query, params in queries:
            result = self.db.execute_query(query, params, fetchone=True)
            stats[query.split(" ")[1].lower() + '_count'] = result[0] if result else 0
        return stats

    def get_matches(self, tournament_id) -> list[Match]:
        query = '''
            SELECT m.id, m.tournament_id, m.round, 
                   m.player1_id, m.player2_id, m.result, m.player1_color
            FROM matches m
            WHERE m.tournament_id=%s
            ORDER BY m.round
        '''
        return self.db.process_query(self.parse_match, query, params=(tournament_id,))

    def parse_match(self, row):
        pm = PlayerManager(self.db)
        player1 = pm.get_player_tnmt(row[3])
        player2 = pm.get_player_tnmt(row[4])
        opposite_color = 'black' if row[6]=='red' else 'red'
        match = Match(id=row[0],
                    tournament_id=row[1],
                    round=row[2],
                    player1=player1,
                    player2=player2,
                    result=row[5],
                    color1=row[6],
                    color2=opposite_color)
        print(f"new Match{row[0]} {player1} vs {player2}")
        return match

    def update_match_result(self, match_id, result, p1_id, p2_id):
        query_update = "UPDATE matches SET result=%s WHERE id=%s"
        try:
            self.db.execute_query(query_update, (result, match_id), commit=True)

            query_points = "UPDATE tournament_players SET points = points+%s WHERE player_id=%s"
            points = [0.5,0.5]
            if result=='1-0':
                points = [1,0]
            elif result=='0-1':
                points = [0,1]
            self.db.execute_query(query_points, (points[0], p1_id), commit=True)
            self.db.execute_query(query_points, (points[1], p2_id), commit=True)

            return Status.ok
        except Exception as e:
            print(f"Ошибка при обновлении результата: {e}")
            return Status.failed
        
    def get_tournament_id_for_match(self, match_id):
        query = "SELECT tournament_id FROM matches WHERE id=%s"
        row = self.db.execute_query(query, (match_id,), fetchone=True)
        return row[0] if row else None

    def delete_tournament(self, tournament_id):
        #ON DELETE CASCADE
        query = "DELETE FROM tournaments WHERE id=%s"
        try:
            self.db.execute_query(query, (tournament_id,), commit=True)
            return Status.ok
        except:
            return Status.failed
        
    def create_pairs(self, tournament_id):
        t = self.get_by_id(tournament_id)
        pairs = t.create_pairs()
        
        if pairs is None:
            return Status.failed
        
        for pair in pairs:
            query = '''INSERT INTO matches 
                        (tournament_id, round, player1_id, player2_id)
                        VALUES (%s, %s, %s, %s) RETURNING id'''
            id = self.db.execute_query(query, (tournament_id, t.current_round+1, pair[0].id, pair[1].id), commit=True)
            print(f"ADDED match{id} for t{tournament_id}.{t.current_round}, ({pair[0].name} vs {pair[1].name})")

            update_balance_query = '''
            UPDATE tournament_players SET color_balance = %s WHERE player_id=%s
            '''
            self.db.execute_query(update_balance_query, (pair[0].color_balance, pair[0].id), commit=True)
            self.db.execute_query(update_balance_query, (pair[1].color_balance, pair[1].id), commit=True)
        
        
        update_round_query = '''
            UPDATE tournaments SET current_round = %s WHERE id=%s
        '''
        self.db.execute_query(update_round_query, (t.current_round+1, tournament_id), commit=True)

        
        return Status.ok

if __name__ == '__main__':
    d = Database()
    t = TnmtManager(d)
    rows = t.get_players(1)
    for r in rows:
        print(r)