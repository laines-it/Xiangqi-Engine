#include <iostream>
#include <memory>
#include <optional>
#include <tuple>
#include <chrono>
#include "board.h"
#include "engine.h"

class Game {
private:
    bool debug;
    Board board;
    std::unique_ptr<Piece> selected_piece;
    std::pair<Vector, Vector> last_move;
    EvaluateSet eval_set;
    Color current_player_color;

public:
    Game(const EvaluateSet& eval_set, bool load = false, bool debug = false)
        : debug(debug), board(debug), eval_set(eval_set), 
          current_player_color(Color::RED) {
        initialize_pieces();
        
        // openning_general_sight();
    }

    bool is_50moves_rule() const {
        return board.get_uncapturing_moves_count() >= 50;
    }

    std::tuple<Board, std::pair<Vector, Vector>, 
               std::unique_ptr<Piece>, Color> get_all() const {
        return {board, last_move, selected_piece, current_player_color};
    }

    void initialize_pieces() {

        for (int i = 0; i < 2; i++) {
            Color color = (i == 0) ? Color::RED : Color::BLACK;
            int y_pos = (i == 0) ? 0 : 9;

            board.add_piece(std::make_shared<General>(color, Vector(4, y_pos)));

            std::vector<std::function<std::unique_ptr<Piece>(Color, Vector)>> piece_creators = {
                [](Color c, Vector v) { return std::make_shared<Chariot>(c, v); },
                [](Color c, Vector v) { return std::make_shared<Horse>(c, v); },
                [](Color c, Vector v) { return std::make_shared<Elephant>(c, v); },
                [](Color c, Vector v) { return std::make_shared<Advisor>(c, v); }
            };

            for (int x = 0; x < 4; x++) {
                board.add_piece(piece_creators[x](color, Vector(x, y_pos)));
                board.add_piece(piece_creators[x](color, Vector(8 - x, y_pos)));
            }

            for (int x = 0; x < 5; x++) {
                int soldier_y = (i == 0) ? 3 : 6;
                board.add_piece(std::make_shared<Soldier>(color, Vector(x * 2, soldier_y)));
            }

            int cannon_y = (i == 0) ? 2 : 7;
            board.add_piece(std::make_shared<Cannon>(color, Vector(1, cannon_y)));
            board.add_piece(std::make_shared<Cannon>(color, Vector(7, cannon_y)));
        }

        if (debug) {
            std::cout << "GAME: Board initialized successfully" << std::endl;
        }
    }

    bool select_piece(const Vector& position) {
        if (debug && selected_piece) {
            std::cout << "GAME trying to select on " << position 
                      << ": piece already selected>> " 
                      << selected_piece->get_name() << std::endl;
            return false;
        }

        Square& square = board.get_square(position);
        auto piece = square.get_piece();
        
        if (piece && piece->get_color() == current_player_color) {
            selected_piece = piece;
            if (debug) {
                std::cout << "GAME: Selected " << piece->get_name() 
                          << " at " << position << std::endl;
            }
            return true;
        } else {
            std::cout << "GAME trying to select on " << position 
                      << ": No piece or incorrect color" << std::endl;
            return false;
        }
    }

    bool make_move(const Vector& new_position, bool check = true) {
        if (!selected_piece) {
            std::cout << "GAME trying to move to " << new_position 
                      << ": Please select a piece" << std::endl;
            return false;
        }

        std::vector<Vector> valid_moves;
        if (check) {
            valid_moves = board.get_piece_valid_moves(selected_piece.get(), check);
            if (debug) {
                std::cout << "Valid moves: ";
                for (const auto& move : valid_moves) std::cout << move << " ";
                std::cout << std::endl;
            }
        }

        bool valid = !check || (std::find(valid_moves.begin(), valid_moves.end(), new_position) != valid_moves.end());

        if (valid) {
            Vector from_pos = selected_piece->get_position();
            board.move_piece(from_pos, new_position);
            
            if (debug) {
                std::cout << "GAME: moving " << selected_piece->get_name()
                          << " from " << from_pos << " to " << new_position << std::endl;
                std::cout << "GAME: uncaptured: " 
                          << board.get_uncapturing_moves_count() << std::endl;
            }

            last_move = {from_pos, new_position};
            current_player_color = (current_player_color == Color::RED) 
                                   ? Color::BLACK : Color::RED;
            selected_piece.reset();
            return true;
        } else {
            std::cout << "Move " << selected_piece->get_name() 
                      << " to " << new_position << " is invalid" << std::endl;
            return false;
        }
    }

    std::pair<double, std::optional<std::pair<Vector, Vector>>> engine_best_move(Engine& engine) {
        return engine.get_best_move(board, current_player_color);
    }

    double evaluate() {
        return board.update_evaluation(eval_set, false);
    }

    void openning_general_sight() {
        // Реализация последовательности начальных ходов
        perform_move_sequence({
            {{4,3}, {4,4}},   // RED: soldier 4,3 -> 4,4
            {{4,6}, {4,5}},   // BLACK: soldier 4,6 -> 4,5
            {{4,4}, {4,5}},   // RED: soldier 4,4 -> 4,5
            {{4,9}, {4,8}},   // BLACK: general 4,9 -> 4,8
            {{5,0}, {4,1}},   // BLACK: horse 5,0 -> 4,1
            {{4,8}, {5,8}},   // RED: general 4,8 -> 5,8
            {{8,0}, {8,1}},   // BLACK: chariot 8,0 -> 8,1
            {{5,8}, {5,7}},   // RED: general 5,8 -> 4,8
            {{8,1}, {5,1}},   // BLACK: advisor 4,0 -> 5,0
            {{0,9}, {0,8}},   // RED: general 4,8 -> 4,7
            {{5,0}, {4,0}},   // BLACK: advisor 5,0 -> 4,0
            {{4,7}, {4,8}},   // RED: general 4,7 -> 4,8
            {{4,0}, {5,0}}    // BLACK: advisor 4,0 -> 5,0
        });
    }

    void perform_move_sequence(const std::vector<std::pair<Vector, Vector>>& moves) {
        for (const auto& [from, to] : moves) {
            select_piece(from);
            make_move(to);
            board.print_visual(Color::RED);
        }
    }

    void printResult(const std::pair<double, std::optional<std::pair<Vector, Vector>>>& result) {
        std::cout << "Evaluation: " << result.first << std::endl;

        if (result.second.has_value()) {
            const auto& move = result.second.value();
            std::cout << "Best move: " << move.first << " -> " << move.second << std::endl;
        } else {
            std::cout << "No valid moves available (game over?)" << std::endl;
        }
    }

    void reset() {
        board.clear();
        current_player_color = Color::RED;
        initialize_pieces();
    }

    void bot_play(Engine& engine, int moves = 5){
        if (moves == 0) return;
        const auto best_move = engine_best_move(engine);
        if (best_move.second) {
            const auto& move = best_move.second.value();
            select_piece(move.first);
            make_move(move.second);
            bot_play(engine, moves - 1);
        }
    }

};

int main() {
    EvaluateSet ev(10, 0, 0, 0);
    Game g(ev, false, false);
    std::cout << "===== C++ =====" << std::endl;
    for (int depth = 2; depth < 6; ++depth) {
        std::cout << "---- depth = " << depth << " ----" << std::endl;
        Engine default_engine = Engine(ev, depth);
        for (int moves = 4; moves < 24; moves += 4) {
            g.reset();
            auto start = std::chrono::high_resolution_clock::now();
            g.bot_play(default_engine, moves);
            auto end = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> duration = end - start;
            std::cout << moves << " moves on depth=" << depth << " take " << duration.count() << std::endl;
        }
    }

    
    
    return 0;
}