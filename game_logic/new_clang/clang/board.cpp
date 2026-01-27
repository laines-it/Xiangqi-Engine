#ifndef board_cpp
#define board_cpp

#include "board.h"
#include <iostream>
#include <vector>
#include <memory>
#include <functional>
#include <algorithm>
#include <cmath>
#include <tuple>
#include <unordered_set>
#include "pieces.h"
#include <optional>

void Square::update_state() {
    if (red_attacks > black_attacks) {
        state = Square_status::red;
    } else if (black_attacks > red_attacks) {
        state = Square_status::black;
    } else {
        state = Square_status::neutral;
    }
}

std::unique_ptr<Piece> Square::set_piece(std::unique_ptr<Piece> new_piece) {
    auto old_piece = piece;
    piece = new_piece;
    if (new_piece) {
        new_piece->set_position(position);
    }
    return old_piece;
}

void Square::add_attack(Color color) {
    if (color == Color::RED) {
        ++red_attacks;
    } else {
        ++black_attacks;
    }
    update_state();
}

void Square::remove_attack(Color color) {
    if (color == Color::RED) {
        red_attacks--;
    } else {
        black_attacks--;
    }
    update_state();
}

void Board::add_piece(std::unique_ptr<Piece> piece) {
    Vector position = piece->get_position();
    Square& square = get_square(position);
    
    if (square.get_piece()) {
        throw std::runtime_error("Square is already occupied");
    }
    
    square.set_piece(piece);
    
    if (piece->get_color() == Color::RED) {
        reds.push_back(piece);
    } else {
        blacks.push_back(piece);
    }
}

void Board::remove_piece(std::unique_ptr<Piece> piece) {
    auto& collection = (piece->get_color() == Color::RED) ? reds : blacks;
    auto it = std::find(collection.begin(), collection.end(), piece);
    if (it != collection.end()) {
        collection.erase(it);
    }
}

Square& Board::get_square(const Vector& position, 
                    const std::optional<std::pair<Vector, Vector>>& area = std::nullopt) {
    if (area) {
        if (!position.in_area(*area)) {
            throw std::out_of_range("Position outside specified area");
        }
    }
    
    if (position.x < 0 || position.x >= 9 || position.y < 0 || position.y >= 10) {
        throw std::out_of_range("Invalid board position");
    }
    
    return squares[position.x][position.y];
}

bool Board::empty_between_general(int x, int y1, int y2) const {
    if (y1 > y2) std::swap(y1, y2);
    for (int y = y1 + 1; y < y2; ++y) {
        if (squares[x][y].get_piece()) {
            return false;
        }
    }
    return true;
}

void Board::get_attackers(Color color) const {
    auto& collection = (color == Color::RED) ? reds : blacks;
    std::vector<std::unique_ptr<Piece>> attackers;
    
    for (auto& piece : collection) {
        if (piece->is_attacker()) {
            attackers.push_back(piece);
        }
    }
    // return attackers;
}

void Board::move_piece(std::unique_ptr<Piece> piece, Vector dest){
    Vector from_pos = piece->get_position();
    piece->set_position(dest);
    for (auto& p : pieces){
        '''
            Цикл по всем фигурам, чтобы проверить, как на них повлиял сделанный ход
        '''
        if (p->get_position == dest) { // if the piece has taken
            remove_piece(p);
        }else{
            int i = p->block_direction(from_pos, p->get_color());
            '''
                Для того чтобы продлить за точку границы нужно найти новую.
                Для этого нужно пробежать по остальным фигурам.
            '''
            int min_dist = 10 // BOARD SIZE 
            for (auto& new_p : pieces) {
                if (new_p->is_reachable_for(p)){
                    Vector dist_v = p->get_position() - new_p->get_position();
                    int dist = dist_v.length()
                    if dist < min_dist{
                        
                    }
                }
            }
            p->block_direction(dest, piece->get_color());
        }
    }
    for (auto& piece : blacks){
        piece->get_blocked_direction(dest, piece->get_color());
    }
    
}

std::unique_ptr<Piece> Board::move_piece(const Vector& from_pos, const Vector& to_pos,
                                    std::unique_ptr<Piece> set_instead = nullptr,
                                    bool returning = false) {
    Square& old_square = get_square(from_pos);
    std::unique_ptr<Piece> the_piece = old_square.get_piece();
    
    if (!the_piece) {
        throw std::runtime_error("No piece at source position");
    }
    
    the_piece->set_position(to_pos);
    Square& new_square = get_square(to_pos);
    std::unique_ptr<Piece> taken = new_square.set_piece(the_piece);
    
    if (taken) {
        // Захват фигуры
        remove_piece(taken);
        save_UMC = uncapturing_moves_count;
        uncapturing_moves_count = 0;
    } else {
        ++uncapturing_moves_count;
    }
    
    old_square.remove_piece();
    
    if (returning) {
        if (!history.empty()) history.pop_back();
        --uncapturing_moves_count;
        --uncapturing_moves_count;
    } else {
        history.emplace_back(std::pair(from_pos, to_pos));
    }
    
    if (set_instead) {
        add_piece(set_instead);
        uncapturing_moves_count = save_UMC;
    }
    
    return taken;
}

std::pair<std::unique_ptr<Piece>, Vector> Board::is_in_check(Color color) {
    
    std::unique_ptr<Piece> gen_red = nullptr;
    std::unique_ptr<Piece> gen_black = nullptr;
    
    for (const auto& piece : reds) {
        if (dynamic_cast<General*>(piece.get())) {
            gen_red = piece;
            break;
        }
    }
    
    for (const auto& piece : blacks) {
        if (dynamic_cast<General*>(piece.get())) {
            gen_black = piece;
            break;
        }
    }
    
    if (gen_red && gen_black) {
        int x = gen_red->get_position().x;
        Vector red_pos = gen_red->get_position();
        Vector black_pos = gen_black->get_position();
        
        if (x == black_pos.x) {
            int y1 = red_pos.y;
            int y2 = black_pos.y;
            
            if (y1 > y2) std::swap(y1, y2);
            
            if (empty_between_general(x, y1, y2)) {
                if (color == Color::BLACK) {
                    return {gen_red, Vector(x, 10)};
                }
                else {
                    return {gen_black, Vector(x, 10)};
                }
            }
        }
    }
    
    // Проверка повторения позиции (правило трехкратного повторения)
    if (history.size() >= 8) {
        bool repeated3 = true;
        for (int i = 0; i < 4; i++) {
            const auto& move1 = history[history.size() - 1 - i];
            const auto& move2 = history[history.size() - 5 - i];
            
            if (move1 != move2) {
                repeated3 = false;
                break;
            }
        }
        
        if (repeated3) {
            //std::cout << "REPEATED" << std::endl;
            const auto& last = history.back();
            return {get_square(last.second).get_piece(), last.second};
        }
    }
    
    // Проверка атак других фигур
    const auto& opponent_pieces = (color == Color::BLACK) ? reds : blacks;
    const auto& palace = (color == Color::RED) ? RED_PALACE_AREA : BLACK_PALACE_AREA;
    
    for (const auto& attacker : opponent_pieces) {
        // Проверяем только атакующие фигуры
        if (!attacker->is_attacker()) continue;
        
        // Получаем возможные ходы без проверки на шах
        std::vector<Vector> attackers_valid_moves = get_piece_valid_moves(
            attacker.get(), 
            false,   // check = false
            false    // for_eval = false
        );
        
        for (const auto& move : attackers_valid_moves) {
            try {
                Square& square = get_square(move, palace);
                auto piece = square.get_piece();
                
                // Проверяем, стоит ли на клетке генерал
                if (piece && dynamic_cast<General*>(piece.get()) && 
                    piece->get_color() == color) {
                    return {attacker, move};
                }
            } catch (const std::out_of_range&) {
                // Пропускаем ходы за пределы дворца
                continue;
            }
        }
    }
    
    // Шах не обнаружен
    return {nullptr, Vector()};
}

std::vector<Vector> Board::get_piece_valid_moves(Piece* piece, bool check = true, bool for_eval = false) {
    std::vector<Vector> valid_moves;
    bool was_modified = false;

    // Модификация солдата при пересечении реки
    if (piece->can_modify() && !piece->is_modified()) {
        int y = piece->get_position().y;
        if ((piece->get_color() == Color::RED && y > 4) || 
            (piece->get_color() == Color::BLACK && y < 5)) {
            piece->modify();
            was_modified = true;
        }
    }

    const Move& move = piece->get_move();
    Vector start_pos = piece->get_position();

    for (const Vector& direction : move.get_directions()) {
        // Проверка для прыгающих фигур (конь, слон)
        if (move.is_bigstep()) {
            Vector midpoint = start_pos + (direction / 2);
            if (has_piece(midpoint)) {
                continue;
            }
        }

        bool has_screen = false;
        Vector current_pos = start_pos;
        int max_steps = piece->get_max_steps();

        for (int step = 0; step < max_steps; step++) {
            current_pos = current_pos + direction;
            
            // Проверка выхода за допустимую область
            try {
                Square& target_square = get_square(current_pos, piece->get_area());
            } catch (const std::out_of_range&) {
                break;
            }

            Square& target_square = get_square(current_pos);
            
            if (target_square.get_piece()) {
                // Обработка захвата фигуры
                if (!piece->need_screen() || has_screen) {
                    // Можно атаковать только вражеские фигуры
                    if (for_eval || target_square.get_piece()->get_color() != piece->get_color()) {
                        if (check) {
                            // Проверка на шах
                            auto [threat, killer_move] = ghost_test(
                                start_pos, current_pos,
                                [&](Board& b) {
                                    return b.is_in_check(piece->get_color());
                                }
                            );
                            
                            if (threat) {
                                if (debug) {
                                    std::cout << "Move by " << piece->get_name() 
                                                << " to " << current_pos 
                                                << " causes mate by " << threat->get_name()
                                                << " with move to " << killer_move << std::endl;
                                }
                                break;
                            }
                        }
                        valid_moves.push_back(current_pos);
                    }
                    break;
                } else {
                    // Фигура становится экраном для пушки
                    has_screen = true;
                }
            } else {
                // Обработка перемещения на пустую клетку
                if (for_eval ? (has_screen == piece->need_screen()) : !has_screen) {
                    if (check) {
                        // Проверка на шах
                        auto [threat, killer_move] = ghost_test(
                            start_pos, current_pos,
                            [&](Board& b) {
                                return b.is_in_check(piece->get_color());
                            }
                        );
                        
                        if (!threat) {
                            valid_moves.push_back(current_pos);
                        } else if (debug) {
                            std::cout << "BOT Move by " << piece->get_name() 
                                        << " to " << current_pos 
                                        << " causes mate by " << threat->get_name()
                                        << " with move to " << killer_move << std::endl;
                        }
                    } else {
                        valid_moves.push_back(current_pos);
                    }
                }
            }
        }
    }

    // Восстановление исходного состояния солдата
    if (piece->can_modify() && piece->is_modified()) {
        piece->set_default();
    }

    return valid_moves;
}

bool Board::has_piece(const Vector& position){
    try {
        Square& sq = get_square(position);
        return static_cast<bool>(sq.get_piece());
    } catch (const std::out_of_range&) {
        return false;
    }
}

double Board::is_mate() const {
    int mate = 3;
    for (int i = 0; i < 2; i++) {
        const auto& team = (i == 0) ? reds : blacks;
        for (const auto& piece : team) {
            if (dynamic_cast<General*>(piece.get())) {
                mate -= i + 1;
                break;
            }
        }
    }
    if (mate == 0) return 0;
    return (mate == 1) ? -std::numeric_limits<double>::infinity()
                        : std::numeric_limits<double>::infinity();
}

double Board::evaluate(const EvaluateSet& eval_set, bool describe = false) {
    if (uncapturing_moves_count > 49) return 0;
    
    double mate_result = is_mate();
    if (std::isinf(mate_result)) return mate_result;
    
    reset_control_state();
    auto [value_multiplier, attack_bonus, mobility_multiplier, control_multiplier] = eval_set.get();
    double total_value = 0;
    
    for (int i = 0; i < 2; i++) {
        Color color = (i == 0) ? Color::RED : Color::BLACK;
        const auto& team = (i == 0) ? reds : blacks;
        
        double team_values = 0;
        double team_attack_bonus = 0;
        double team_mobility = 0;
        std::vector<Vector> vds; // valid moves
        
        for (const auto& piece : team) {
            team_values += piece->get_value() * value_multiplier;
            
            if (attack_bonus && piece->is_attacker()) {
                team_attack_bonus += attack_bonus;
            }
            
            if (mobility_multiplier || control_multiplier) {
                // Заглушка - предполагается реализация get_piece_valid_moves
                vds = get_piece_valid_moves(piece.get(), true, true);
                team_mobility += vds.size() * mobility_multiplier;
            }
            
            if (control_multiplier) {
                update_control_state(color, vds);
            }
            
            if (describe) {
                std::cout << "BOARD: " << (color == Color::RED ? "RED" : "BLACK")
                            << " values = " << team_values << "\n";
                std::cout << "BOARD: " << (color == Color::RED ? "RED" : "BLACK")
                            << " attack bonus = " << team_attack_bonus << "\n";
                std::cout << "BOARD: " << (color == Color::RED ? "RED" : "BLACK")
                            << " mobility = " << team_mobility << "\n";
            }
        }
        
        double team_total = team_values + team_attack_bonus + team_mobility;
        total_value += (i == 0) ? team_total : -team_total;
    }
    
    if (control_multiplier) {
        for (auto& row : squares) {
            for (auto& square : row) {
                if (!square.get_piece()) {
                    double control_value = 0;
                    switch (square.get_state()) {
                        case Square_status::red:
                            control_value = control_multiplier;
                            break;
                        case Square_status::black:
                            control_value = -control_multiplier;
                            break;
                        default:
                            break;
                    }
                    total_value += control_value;
                }
            }
        }
    }
    
    return total_value;
}

double Board::update_evaluation(const EvaluateSet& eval_set, bool describe = false) {
    evaluation = evaluate(eval_set, describe);
    return evaluation;
}

void Board::update_control_state(Color color, const std::vector<Vector>& attacks) {
    for (const auto& attack : attacks) {
        try {
            Square& square = get_square(attack);
            square.add_attack(color);
        } catch (const std::out_of_range&) {
            // Игнорируем атаки за пределами доски
        }
    }
}

void Board::reset_control_state() {
    for (auto& row : squares) {
        for (auto& square : row) {
            square.reset_attacks();
        }
    }
}

void Board::print_visual(Color perspective = Color::RED){

    std::string line = " ╔";
    for (int i = 0; i < 9; ++i) {
        line += "═══";
    }
    line += "╗";
    std::cout << line << std::endl;

    // Основная часть доски (10 строк)
    for (int i = 0; i < 10; ++i) {
        int vert = (perspective == Color::BLACK) ? i : (9 - i);
        line = std::to_string(vert) + "║";

        for (int j = 0; j < 9; ++j) {
            const std::unique_ptr<Piece> piece = squares[j][vert].get_piece();
            std::string between_char;

            // Определяем символ-разделитель для сетки
            if (i == 4 || i == 9) {
                between_char = "┴";
            } else if (i == 0 || i == 5) {
                between_char = "┬";
            } else if (j == 0) {
                between_char = "├";
            } else if (j == 8) {
                between_char = "┤";
            } else {
                between_char = "┼";
            }

            if (piece != nullptr) {
                // Добавляем фигуру с цветом
                line += " ";
                line += (piece->get_color() == Color::RED) ? RED_TEXT : GREEN_TEXT;
                line += piece->get_name();
                line += RESET_TEXT;
                line += " ";
            } else {
                // Добавляем элементы сетки
                if (j == 0) {
                    line += " ";
                } else {
                    line += "─";
                }
                line += between_char;
                if (j == 8) {
                    line += " ";
                } else {
                    line += "─";
                }
            }
        }
        line += "║";
        std::cout << line << std::endl;
    }

    // Нижняя граница доски
    line = " ╚";
    for (int i = 0; i < 9; ++i) {
        line += "═══";
    }
    line += "╝";
    std::cout << line << std::endl;

    // Подпись столбцов
    line = "   ";
    for (int i = 0; i < 9; ++i) {
        line += std::to_string(i);
        line += "  ";
    }
    std::cout << line << std::endl << std::endl;
}

void Board::clear() {
    reds.clear();
    blacks.clear();
    
    history.clear();
    
    uncapturing_moves_count = 0;
    save_UMC = 0;
    evaluation = 0;
    
    squares = std::vector<std::vector<Square>>(9, std::vector<Square>(10, Square(Vector(0, 0))));
    for (int x = 0; x < 9; ++x) {
        for (int y = 0; y < 10; ++y) {
            squares[x][y] = Square(Vector(x, y));
        }
    }
}


#endif