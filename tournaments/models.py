from config import TnmtStatus, Role

class User:
    def __init__(self, id, name = "Noname", role = Role.user, email = "", tnmts_admin : list = []):
        self.id = id
        self.name = name
        self.role = role
        self.email = email
        self.tournaments_admins = tnmts_admin

class Player:
    def __init__(self, id, user_id, name, rating):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.rating = rating

    def __repr__(self):
        return f"{self.name} ({self.rating})"

class TnmtPlayer(Player):
    def __init__(self, id, user_id, name, rating,
                 tnmt_id, points, color_balance, opponents=[]):
        super().__init__(id, user_id, name, rating)
        self.tnmt_id = tnmt_id
        self.points = points
        self.color_balance = color_balance
        self.opponents = opponents
        self.buchholz = 0

class Tournament:
    def __init__(self, id, admin_id, name, date, total_rounds, status=TnmtStatus.upcoming, players=[], current_round=0):
        self.id = id
        self.admin_id = admin_id
        self.name = name
        self.date = date
        self.status = status
        self.players = players
        self.ratings = [p.rating for p in players]
        self.matches = []
        self.total_rounds = total_rounds
        self.current_round = current_round
        self.is_finished = self.current_round == self.total_rounds

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
    def __init__(self, id, tournament_id, round, player1, player2, result, color1, color2):
        self.id = id
        self.tournament_id = tournament_id
        self.round = round
        self.player1 = player1
        self.player2 = player2
        self.result = result
    
    def has_finished(self):
        return self.result != 'pending'

    def get_winner(self):
        if self.result == '1-0':
            return self.player1
        elif self.result == '0-1':
            return self.player2
        else:
            return None
    
    def get_winner_id(self):
        winner = self.get_winner()
        return winner.id if winner else None
    
    def get_expected_scores(self):
        pass

    def calculate_elo(self):
        pass

    def __repr__(self):
        return f"Match {self.player1} vs {self.player2}"
