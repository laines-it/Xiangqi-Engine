from flask import Flask, render_template, request, redirect, url_for, session

import hashlib
import os
import re
from functools import wraps

from database import Database
from managers import TnmtManager, UserManager, PlayerManager
from config import Role, Status, EMAIL_REGEX, HEADERS

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')

db = Database()
tm = TnmtManager(db)
um = UserManager(db)
pm = PlayerManager(db)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != Role.admin.value:
            return f"Доступ запрещен. Требуются права администратора. Ваша текущая роль: {session['role']}", 403
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():

    is_local = os.environ.get('ISLOCAL')
        
    all_tournaments = tm.get_all(for_print=True)

    tnmt_stats = []

    players = pm.get_all()

    return render_template('index.html', 
                           tournaments=all_tournaments,
                           players=players,
                           tournament_stats=tnmt_stats,
                           is_admin=session.get('role') == Role.admin.value,
                           is_local=is_local)

@app.route('/analytics')
def exec_query():
    rows = db.execute_query(os.environ.get('QUERY'), fetchall=True)
    db.print_table(HEADERS['user'], rows)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login(username=None, hashed_password=None):
    if request.method == 'POST':

        if not (username and hashed_password):
            username = request.form['username']
            password = request.form['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = um.get_user(username, hashed_password)

        if user:
            session['user_id'] = user.id
            session['username'] = user.name
            session['role'] = user.role.value
            session['email'] = user.email
            # session['tnmts'] = user.tournaments_admins
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверное имя пользователя или пароль")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']

        email = request.form['email']
        if not re.match(EMAIL_REGEX,email):
            return render_template('register.html', error="Некоррентный email")
        
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('register.html', error="Пароли не совпадают")
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if um.new_user(username, hashed_password, Role.user, email) == Status.ok:
            return redirect(url_for('login', username=username, hashed_password=hashed_password))
        else:
            return render_template('register.html', error="Имя пользователя уже занято")
    
    return render_template('register.html')

@app.route('/tournaments/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_tournament():
    if request.method == 'POST':
        # admins = session['tnmts']
        name = request.form['name']
        date = request.form['date']
        rounds = request.form['rounds']
        t_id = tm.create(name, session['user_id'], date, rounds)
        # if admins:
        #     session['tnmts'].append(t_id)
        #     session.modified = True
        # else:
        #     session['tnmts'] = [t_id]
        #     session.modified = True
        print("CREATED Tournament with id=",t_id)
        return redirect(url_for('manage_tournament', tournament_id=t_id))
    return render_template('create_tournament.html')

@app.route('/players/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form.get('rating', 1000)
        try:
            pm.new_player(name, rating)
            return redirect(url_for('players_list'))
        except:
            return render_template('add_player.html', error="Игрок с таким именем уже существует")
    
    return render_template('add_player.html')

@app.route('/players')
def players_list():
    
    players = pm.get_all()
    
    return render_template('players_list.html', 
                           players=players,
                           is_admin=session.get('role') == Role.admin.value)

@app.route('/tournaments/<int:tournament_id>')
def manage_tournament(tournament_id):
    tournament = tm.get_by_id(tournament_id)
    if not tournament:
        return page_not_found(f"Tournament {tournament_id} not found")
    
    players = tournament.players

    matches = tm.get_matches(tournament_id)

    is_admin = 'role' in session and session['role'] == Role.admin.value
    
    player_rounds = {}
    player_standings = []
    player_buchholz = []

    rounds = {}
    for match in matches:
        if match.round not in rounds:
            rounds[match.round] = []
        rounds[match.round].append(match)

    for player in players:
        player_results = {}
        for round_num in range(1, tournament.total_rounds + 1):
            player_results[round_num] = {'opponent': None, 'result': None, 'points': 0}
        
        for round_num, round_matches in rounds.items():
            for match in round_matches:
                if match.player1 and match.player1.id == player.id:
                    opponent = match.player2
                    if match.result == '1-0':
                        points = 1
                    elif match.result == '0-1':
                        points = 0
                    elif match.result == '1/2-1/2':
                        points = 0.5
                    else:
                        points = 0
                    player_results[round_num] = {
                        'opponent': opponent.id,
                        'result': match.result,
                        'points': points
                    }
                elif match.player2 and match.player2.id == player.id:
                    opponent = match.player1
                    if match.result == '1-0':
                        points = 0
                    elif match.result == '0-1':
                        points = 1
                    elif match.result == '1/2-1/2':
                        points = 0.5
                    else:
                        points = 0
                    player_results[round_num] = {
                        'opponent': opponent.id,
                        'result': match.result,
                        'points': points
                    }
        
        player_rounds[player.id] = player_results
    
    # Рассчитываем итоговое место
    if tournament.is_finished:
        tournament.calculate_buchholz()
        sorted_players = sorted(tournament.players, key=lambda p: (p.points, p.buchholz), reverse=True)
        place = 1
        last_points = -1
        last_buch = -1
        for idx, player in enumerate(sorted_players):
            if player.points != last_points or last_buch != player.buchholz:
                place = idx + 1
                last_points = player.points
                last_buch = player.buchholz
            player_standings.append({
                'id': player.id,
                'place': place
            })
            player_buchholz.append({
                'id': player.id,
                'coef': player.buchholz
            })

    
    return render_template('manage_tournament.html',
                           tournament_id=tournament.id,
                           tournament=tournament,
                           players=players,
                           player_rounds=player_rounds,
                           player_standings=player_standings,
                           player_buchholz=player_buchholz,
                           matches=matches,
                           is_admin=is_admin,
                           is_finished=tournament.is_finished)

@app.route('/players/add/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_players(tournament_id):
    if request.method == 'POST':
        all_players = pm.get_all() 
        for player in all_players:
            if request.form.get(f'player_{player.id}'):
                tm.add_player(tournament_id, player.id)
        
        return redirect(url_for('manage_tournament', tournament_id=tournament_id))
    
    else:
        all_players = pm.get_all()
        tournament_player_ids = tm.get_players_ids(tournament_id)

        return render_template('add_players.html', 
                           tournament_id=tournament_id,
                           all_players=all_players,
                           tournament_player_ids=tournament_player_ids)

@app.route('/tournaments/<int:tournament_id>/pairs', methods=['POST'])
@login_required
@admin_required
def generate_pairs(tournament_id):
    status = tm.create_pairs(tournament_id)
    if status == Status.failed:
        return "Количество игроков должно быть четным!", 400
    return redirect(url_for('manage_tournament', tournament_id=tournament_id))

@app.route('/matches/<int:match_id>/result', methods=['POST'])
@login_required
def submit_result(match_id):
    result = request.form.get('result')
    if not result:
        return "Не выбран результат!", 400
    
    valid_results = ['1-0', '0-1', '1/2-1/2']
    if result not in valid_results:
        return "Некорректный результат!", 400
    
    player1_id = request.form.get('player1_id')
    player2_id = request.form.get('player2_id')

    status = tm.update_match_result(match_id, result, player1_id, player2_id)
    if status == Status.failed:
        return "Ошибка при обновлении результата", 400

    tournament_id = tm.get_tournament_id_for_match(match_id)
    return redirect(url_for('manage_tournament', tournament_id=tournament_id))

@app.route('/players/<int:player_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_player(player_id):
    status = pm.delete_player(player_id)
    if status == Status.ok:
        return redirect(url_for('players_list'))
    else:
        return "Ошибка при удалении игрока", 400

@app.route('/tournaments/<int:tournament_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tournament(tournament_id):

    tournament = tm.get_by_id(tournament_id)
    if not tournament:
        return page_not_found(f"Tournament {tournament_id} not found")
    
    if tournament.status != 'upcoming':
        return "Можно удалять только турниры со статусом 'upcoming'", 400
    
    status = tm.delete_tournament(tournament_id)
    if status == Status.ok:
        return redirect(url_for('index'))
    else:
        return "Ошибка при удалении турнира", 400

@app.route('/player')
@login_required
def player_profile():
    user_id = session['user_id']
    player = pm.get_player_by_user_id(user_id)
    
    if not player:
        return render_template('player_profile.html', player=None)
    
    recent_matches = pm.get_player_matches(player.id, limit=10)
    
    tournaments = pm.get_player_tournaments(player.id)
    
    return render_template('player_profile.html',
                           player=player,
                           recent_matches=recent_matches,
                           tournaments=tournaments)

@app.route('/player/create', methods=['GET', 'POST'])
@login_required
def create_player():
    if request.method == 'POST':
        name = request.form['surname'] + ' ' + request.form['name']
        rating = request.form.get('rating', 1000)
        user_id = session['user_id']
        
        try:
            pm.new_player_with_user(name, rating, user_id)
            return redirect(url_for('player_profile'))
        except Exception as e:
            return render_template('create_player.html', error=str(e))
    
    return render_template('create_player.html')

if __name__ == '__main__':
    app.run(debug=True)