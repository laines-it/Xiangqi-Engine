from enum import Enum

class Role(Enum):
    admin = 'admin'
    organizer = 'organizer'
    user = 'user'

class Status(Enum):
    ok  = 'ok'
    failed = 'failed'

class TnmtStatus(Enum):
    active = 'active'
    upcoming = 'upcoming'
    finished = 'finished'
    canceled = 'canceled'

get_opponents = '''
    SELECT DISTINCT 
            CASE 
                WHEN m.player1_id = tp.player_id THEN m.player2_id 
                WHEN m.player2_id = tp.player_id THEN m.player1_id 
            END AS opponent_id
        FROM matches m
        WHERE m.tournament_id = tp.tournament_id
            AND (m.player1_id = tp.player_id OR m.player2_id = tp.player_id)
            AND m.result <> 'pending'
'''

get_opponents_json = '''
    COALESCE((
        SELECT json_agg(DISTINCT o.opponent_id)
        FROM (''' + get_opponents + ''') o),

        json_array())
    '''
