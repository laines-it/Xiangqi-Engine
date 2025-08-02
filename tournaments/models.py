from config import TnmtStatus, Role, months
import bcrypt

class User:
    def __init__(self, id, name = "Noname", pw:str = None, role = Role.user, email = "", current_player_id=None):
        self.id = id
        self.name = name
        self.role = role
        self.email = email
        self.current_player_id = current_player_id
        self.pw = pw
    
    def auth(self, password:str):
        if self.pw == password:
            return True
        return bcrypt.checkpw(password.encode('utf8'), self.pw.encode('utf8'))

class Player:
    def __init__(self, id, user_id, name, city:int, ingo):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.ingo = ingo
        self.city = city
        self.rating = 2750 - 7*ingo

    def __repr__(self):
        return f"{self.name} ({self.rating})"

class TnmtPlayer(Player):
    def __init__(self, id, user_id, name, city, ingo,
                 tnmt_id, points, color_balance, opponents=[]):
        super().__init__(id, user_id, name, city, ingo)
        self.tnmt_id = tnmt_id
        self.points = points
        self.color_balance = color_balance
        self.opponents = opponents
        self.buchholz = 0

    def update_rating(self, total_tournaments, total_rounds, opponents_ingos, time_control_category):
        adjusted_opponents = [
            min(opp_ingo, self.ingo + 50)
            for opp_ingo in opponents_ingos
        ]
        
        # Расчёт среднего скорректированного INGO соперников
        avg_opponents = sum(adjusted_opponents) / len(adjusted_opponents) if adjusted_opponents else 0
        
        # Расчёт нового INGO на основе результатов турнира
        new_ingo = avg_opponents + 50 - self.points * 100
        
        # Определение базового коэффициента k
        if total_tournaments > 14:
            k = 4
        elif total_tournaments > 9:
            k = 3
        elif total_tournaments > 4:
            k = 2
        elif total_tournaments > 0:
            k = 1
        else:
            k = 0
        
        # Корректировка k по правилам
        if self.ingo - new_ingo >= 25:
            k = max(0, k - 1)  # Уменьшение при значительном падении
        
        if total_rounds < 5:
            k += (5 - total_rounds) * 2  # Увеличение за малое количество партий
        
        if time_control_category == 'cat1':  # Контроль времени 45-60 минут
            k += 1
        elif time_control_category == 'cat2':  # Контроль времени 30-45 минут
            k += 2
        
        # Расчёт обновлённого INGO
        if k == 0:
            updated_ingo = new_ingo
        else:
            updated_ingo = (self.self.ingo * k + new_ingo) / (k + 1)
        updated_ingo = round(updated_ingo, 1)  # Округление до одного знака
        
        # Расчёт российского рейтинга
        russian_rating = 2750 - 7 * updated_ingo
        russian_rating = round(russian_rating)  # Округление до целого
        
        # Обновление состояния игрока
        self.ingo = updated_ingo
        self.rating = russian_rating
        
        return russian_rating


class Tournament:
    def __init__(self, id, admin_id, name, date, place, time_control:int, total_rounds, system, fischer_time_control=0, prize=0, status=TnmtStatus.upcoming, players=[], current_round=0):
        self.id = id
        self.admin_id = admin_id
        self.name = name
        self.date = date
        self.status = status
        self.players = players
        self.place = place
        self.system = system
        self.time_control = self.parse_time_control(time_control, fischer_time_control)
        self.prize = prize
        self.ratings = [p.rating for p in players]
        self.matches = []
        self.total_rounds = total_rounds
        self.current_round = current_round
        self.is_finished = self.current_round == self.total_rounds
        self.is_started = self.current_round > 0

    def display_date(self):
        return f"{self.date.day} {months[self.date.month]} {self.date.year}"

    def display_time(self):
        h = self.date.hour
        m = self.date.minute
        return f"{'0' if h<10 else ''}{h}:{'0' if m<10 else ''}{m}"

    def display_time_control(self):
        h = self.time_control['hours']
        m = self.time_control['minutes']
        s = self.time_control['seconds']
        f = self.time_control['fischer']
        time = f"{h}" if h>0 else ''
        time += f"{'0' if m<10 else ''}{m}:{'0' if s<10 else ''}{s}"
        time += f"+{f}s"
        return time

    def parse_time_control(self, time_in_seconds, fischer):
        time_control = ''
        h = time_in_seconds // 3600
        if h>0:
            time_control += f"{h}:"
        m = (time_in_seconds - h*3600) // 60
        s = time_in_seconds - h*3600 - m*60
        return {"hours":h, "minutes":m, "seconds":s, "fischer":fischer}
        

    def create_pairs(self):
        if self.current_round == 0:
            # Первый раунд: сортировка по рейтингу
            sorted_players = sorted(self.players, key=lambda x: x.rating, reverse=True)
            top = sorted_players[:len(self.players)//2]
            bottom = sorted_players[len(self.players)//2:]
            pairs = []
            used = [False] * len(bottom)
            
            for p_top in top:
                # Поиск лучшего соперника по минимальной разнице рейтинга
                min_diff = float('inf')
                candidate_idx = -1
                for j, p_bot in enumerate(bottom):
                    if not used[j]:
                        diff = abs(p_top.rating - p_bot.rating)
                        if diff < min_diff:
                            min_diff = diff
                            candidate_idx = j
                
                if candidate_idx == -1:
                    continue
                    
                candidate = bottom[candidate_idx]
                used[candidate_idx] = True
                
                # Определение цвета фигур для минимизации дисбаланса
                if abs(p_top.color_balance + 1) + abs(candidate.color_balance - 1) <= \
                abs(p_top.color_balance - 1) + abs(candidate.color_balance + 1):
                    pairs.append((p_top, candidate))  # p_top белые
                else:
                    pairs.append((candidate, p_top))  # candidate белые
            
            return pairs
        else:
            # Последующие раунды: сортировка по очкам и рейтингу
            sorted_players = sorted(self.players, key=lambda x: (-x.points, -x.rating))
            n = len(sorted_players)
            used = [False] * n
            pairs = []
            
            for i in range(n):
                if used[i]:
                    continue
                    
                p1 = sorted_players[i]
                candidates = []
                
                # Поиск возможных соперников
                for j in range(i+1, n):
                    if not used[j]:
                        p2 = sorted_players[j]
                        if p2.id not in p1.opponents:
                            point_diff = abs(p1.points - p2.points)
                            rating_diff = abs(p1.rating - p2.rating)
                            candidates.append((j, p2, point_diff, rating_diff))
                
                if not candidates:
                    # Если не нашли подходящего соперника, ищем любого доступного
                    for j in range(i+1, n):
                        if not used[j]:
                            p2 = sorted_players[j]
                            point_diff = abs(p1.points - p2.points)
                            rating_diff = abs(p1.rating - p2.rating)
                            candidates.append((j, p2, point_diff, rating_diff))
                    if not candidates:
                        continue
                
                # Выбор лучшего кандидата
                candidates.sort(key=lambda x: (x[2], x[3]))
                best_idx, p2, _, _ = candidates[0]
                used[i] = True
                used[best_idx] = True
                
                # Определение цвета фигур
                if abs(p1.color_balance + 1) + abs(p2.color_balance - 1) <= \
                abs(p1.color_balance - 1) + abs(p2.color_balance + 1):
                    pairs.append((p1, p2))  # p1 белые
                else:
                    pairs.append((p2, p1))  # p2 белые
            
            return pairs
        
    def calculate_buchholz(self):
        id_points = {player.id: player.points for player in self.players}
        for player in self.players:
            sum_opp_points = 0
            for opp in player.opponents:
                sum_opp_points += id_points[opp]
            player.buchholz = sum_opp_points

    def __repr__(self):
        return f"Tournament {self.id}; {self.name}; {self.status}"

class Match:
    def __init__(self, id, tournament_id, round, player1, player2, result):
        self.id = id
        self.tournament_id = tournament_id
        self.round = round
        self.player1 = player1
        self.player2 = player2
        self.result = result
    
    def has_finished(self):
        return self.result != 'pending'

    def get_expected_scores(self):
        pass

    def calculate_elo(self):
        pass

    def __repr__(self):
        return f"Match {self.player1} vs {self.player2}"
