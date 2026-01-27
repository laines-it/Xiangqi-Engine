#include "pieces.hpp"

Piece::Piece(Color color, Vector position, Move move, std::string name, 
             bool attacking, double value, std::vector<Vector> frontier)
    : color(color), position(position), move(move), 
      name(name), attacking(attacking), value(value), frontier(frontier) {}

bool Piece::is_inside_front(Vector front, Vector square) { 
    return square == front; 
}

bool Piece::need_screen() const { return false; }
bool Piece::can_modify() const { return false; }
bool Piece::is_modified() const { return false; }
void Piece::modify() {}
void Piece::set_default() {}

std::pair<Vector, Vector> Piece::get_area() const { 
    return FULLBOARD_AREA; 
}

bool Piece::is_attacker() const { return attacking; }
void Piece::set_value(double val) { value = val; }
double Piece::get_value() const { return value; }
Vector Piece::get_position() const { return position; }
void Piece::set_position(Vector new_position) { position = new_position; }
void Piece::set_front(std::vector<Vector> new_frontier) { frontier = new_frontier; }
Color Piece::get_color() const { return color; }
const Move& Piece::get_move() const { return move; }
std::string Piece::get_name() const { return name; }

int Piece::get_prolong_direction(Vector square){
    for(int i = 0; i < frontier.size(); ++i){
        if (frontier[i] == square) {
            return i;
        }
    }
    return -1;
}



int Piece::block_direction(Vector square, Color c){
    for(int i = 0; i < frontier.size(); ++i){
        if (is_inside_front(frontier[i], square)) {
            //square particulary blocks direction
            if (color != c)
                frontier[i] = square; // piece on this square can be eaten
            else {
                Vector stepback = frontier[i] - move.get_direction(i)
                if (frontier[i] - move.get_direction(i) == position)
                    frontier[i] = Vector(-1,-1); // blocked
                else
                    frontier[i] = frontier[i] - move.get_direction(i);
            }
            return i;
        }
    }
    return -1;
}

std::ostream& operator<<(std::ostream& os, const Piece& piece) {
    os << "Piece " << (piece.color == Color::RED ? "RED" : "BLACK") 
       << piece.name << " on position (" 
       << piece.position.x << ", " << piece.position.y << ")";
    return os;
}

// General class implementation
General::General(Color color, Vector position)
    : Piece(color, position,
            Move({{1,0}, {-1,0}, {0,1}, {0,-1}}), 
            "G", false, 100.0) {}

int General::get_max_steps() const { return 1; }

std::pair<Vector, Vector> General::get_area() const { 
    return color == Color::RED ? RED_PALACE_AREA : BLACK_PALACE_AREA; 
}

// Advisor class implementation
Advisor::Advisor(Color color, Vector position)
    : Piece(color, position, 
            Move({{1,1}, {1,-1}, {-1,1}, {-1,-1}}),
            "A", false, 2.0) {}

int Advisor::get_max_steps() const { return 1; }

std::pair<Vector, Vector> Advisor::get_area() const { 
    return color == Color::RED ? RED_PALACE_AREA : BLACK_PALACE_AREA; 
}

// Chariot class implementation
Chariot::Chariot(Color color, Vector position)
    : Piece(color, position, 
            Move({{1,0}, {-1,0}, {0,1}, {0,-1}}), 
            "R", true, 9.0) {}

int Chariot::get_max_steps() const { return 10; }

// Horse class implementation
Horse::Horse(Color color, Vector position)
    : Piece(color, position, 
            Move({{2,1}, {2,-1}, {-2,1}, {-2,-1}, {1,2}, {1,-2}, {-1,2}, {-1,-2}}, true), 
            "H", true, 4.0) {}

int Horse::get_max_steps() const { return 1; }

// Elephant class implementation
Elephant::Elephant(Color color, Vector position)
    : Piece(color, position, 
            Move({{2,2}, {2,-2}, {-2,2}, {-2,-2}}, true), 
            "E", false, 2.0) {}

int Elephant::get_max_steps() const { return 1; }

std::pair<Vector, Vector> Elephant::get_area() const { 
    return color == Color::RED ? RED_HALF : BLACK_HALF; 
}

// Cannon class implementation
Cannon::Cannon(Color color, Vector position)
    : Piece(color, position, 
            Move({{1,0}, {-1,0}, {0,1}, {0,-1}}), 
            "C", true, 5.0) {}

bool Cannon::need_screen() const { return true; }

int Cannon::get_max_steps() const { return 10; }

// Soldier class implementation
Soldier::Soldier(Color color, Vector position)
    : Piece(color, position, 
            (color == Color::RED) ? Move({{0,1}}) : Move({{0,-1}}), 
            "S", true, 1.0),
      modified(false),
      originalMove((color == Color::RED) ? Move({{0,1}}) : Move({{0,-1}})) {}



void Soldier::modify() {
    if (modified) return;
    modified = true;
    move += Vector{-1, 0};
    move += Vector{1, 0};
    value = 2.0;
}

void Soldier::set_default() {
    modified = false;
    move = originalMove;
    value = 1.0;
}