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
        FROM (''' + get_opponents + ''') o), json_array())
    '''

EMAIL_REGEX = '''(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'''

HEADERS = {
    'user': ['id','name','role','email']
}

months = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря'
}