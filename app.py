from flask import Flask, render_template, request, jsonify
from game_interface import GameInterface
from players import Human, Bot
from supports import Vector, Color
import json
import threading

app = Flask(__name__)
game = GameInterface()
game.add_players()

# Replace one AI with a Human player
human = Human(name="Human", profile_url="")
game.red_player = human  # Human plays as RED

class VectorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Vector):
            return {'x': obj.x, 'y': obj.y}
        return super().default(obj)

app.json_encoder = VectorEncoder

# Global variable to track match status
match_in_progress = False
selected_piece_position = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_board')
def get_board():
    board_state = []
    for y in range(10):
        row = []
        for x in range(9):
            piece = game.game.board.get_square(Vector(x, y)).get_piece()
            if piece:
                row.append({
                    'type': piece.__class__.__name__,
                    'color': piece.get_color().name,
                    'position': {'x': x, 'y': y}
                })
            else:
                row.append(None)
        board_state.append(row)
    
    return jsonify({
        'board': board_state,
        'current_player': 'red' if game.game.current_player_color == Color.RED else 'black',
        'selected_piece': {
            'position': {
                'x': game.game.selected_piece.get_position().x,
                'y': game.game.selected_piece.get_position().y
            },
            'type': game.game.selected_piece.__class__.__name__,
            'color': game.game.selected_piece.get_color().name
        } if game.game.selected_piece else None,
        'match_in_progress': match_in_progress
    })

@app.route('/select_piece', methods=['POST'])
def select_piece():
    global selected_piece_position
    if not match_in_progress:
        return jsonify({'success': False, 'message': 'Match not started'})
    
    data = request.json
    x, y = data['x'], data['y']
    selected_piece_position = Vector(x, y)
    return jsonify({'success': True})

@app.route('/get_possible_moves', methods=['POST'])
def get_possible_moves():
    if not match_in_progress:
        return jsonify({'success': False, 'message': 'Match not started'})
    
    data = request.json
    x, y = data['x'], data['y']
    position = Vector(x, y)
    
    piece = game.game.board.get_square(position).get_piece()
    if not piece or piece.get_color() != game.game.current_player_color:
        return jsonify({'success': False, 'message': 'Invalid piece selection'})
    
    possible_moves = []
    # Temporarily select the piece to check valid moves
    game.game.select_piece(position)
    
    for move_y in range(10):
        for move_x in range(9):
            target = Vector(move_x, move_y)
            # Check if the move would be valid
            if game.game.make_move(target, check=True):  # check=True means we only validate, don't execute
                possible_moves.append({'x': move_x, 'y': move_y})
    
    # Deselect the piece after checking
    game.game.selected_piece = None
    return jsonify({
        'success': True,
        'possible_moves': possible_moves
    })

@app.route('/make_move', methods=['POST'])
def make_move():
    global selected_piece_position
    if not match_in_progress:
        return jsonify({'success': False, 'message': 'Match not started'})
    if not selected_piece_position:
        return jsonify({'success': False, 'message': 'No piece selected'})
    
    data = request.json
    x, y = data['x'], data['y']
    move_str = f"{selected_piece_position.x},{selected_piece_position.y} to {x},{y}"
    
    # Get current player and execute turn
    current_player = game.red_player if game.game.current_player_color == Color.RED else game.black_player
    current_player.input_method = lambda _: move_str  # Override input method with our move
    
    success = current_player.turn(game.game)
    selected_piece_position = None
    
    # If current player is bot, let it make its move immediately
    if success and isinstance(current_player, Bot):
        next_player = game.black_player if game.game.current_player_color == Color.RED else game.red_player
        if isinstance(next_player, Bot):
            next_player.turn(game.game)
    
    return jsonify({'success': success})

@app.route('/start_match', methods=['POST'])
def start_match():
    global match_in_progress
    if match_in_progress:
        return jsonify({'success': False, 'message': 'Match already in progress'})
    
    match_in_progress = True
    
    def run_match():
        global match_in_progress
        game.start_match(auto_play=False)  # auto_play=False to allow web interaction
        match_in_progress = False
    
    threading.Thread(target=run_match).start()
    return jsonify({'success': True})

@app.route('/evaluate')
def evaluate():
    return jsonify(value=game.game.evaluate())

if __name__ == '__main__':
    app.run(debug=True)