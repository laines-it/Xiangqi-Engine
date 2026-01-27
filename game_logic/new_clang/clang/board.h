#ifndef BOARD_H
#define BOARD_H

#include <vector>
#include <memory>
#include <optional>
#include <utility>
#include <stdexcept>
#include "pieces.h"

class Square {
private:
    Vector position;
    std::unique_ptr<Piece> piece;
    Square_status state;
    int red_attacks;
    int black_attacks;

    void update_state();

public:
    Square(const Vector& pos) 
        : position(pos), piece(nullptr), state(Square_status::neutral), 
          red_attacks(0), black_attacks(0) {}

    int get_red_attacks() const { return red_attacks; }
    int get_black_attacks() const { return black_attacks; }
    Square_status get_state() const { return state; }
    std::unique_ptr<Piece> get_piece() const { return piece; }
    const Vector& get_position() const { return position; }
    
    void remove_piece() { piece = nullptr; }
    std::unique_ptr<Piece> set_piece(std::unique_ptr<Piece> new_piece);

    void reset_attacks(){
        red_attacks = 0;
        black_attacks = 0;
        state = Square_status::neutral;
    }
    void add_attack(Color color);
    void remove_attack(Color color);
    };

class Board {
private:
    std::vector<std::vector<Square>> squares;
    double evaluation;
    std::vector<std::pair<Vector, Vector>> history;
    int uncapturing_moves_count;
    int save_UMC;
    std::vector<std::unique_ptr<Piece>> reds;
    std::vector<std::unique_ptr<Piece>> blacks;
    bool debug;

public:
    Board(bool debug = false)
        : squares(9, std::vector<Square>(10, Square(Vector(0, 0)))),
          evaluation(0),
          uncapturing_moves_count(0),
          save_UMC(0),
          debug(debug) {
        
        for (int x = 0; x < 9; ++x) {
            for (int y = 0; y < 10; ++y) {
                squares[x][y] = Square(Vector(x, y));
            }
        }
    }

    std::pair<Vector, Vector> history_by_index(int index) const {
        return history[history.size() - index];
    }

    void add_piece(std::unique_ptr<Piece> piece);
    
    void remove_piece(std::unique_ptr<Piece> piece);
    Square& get_square(const Vector& position, 
                      const std::optional<std::pair<Vector, Vector>>& area = std::nullopt);

    int get_uncapturing_moves_count() const {
        return uncapturing_moves_count;
    }
    
    bool empty_between_general(int x, int y1, int y2) const;
    std::vector<std::unique_ptr<Piece>> get_attackers(Color color) const;
    std::unique_ptr<Piece> move_piece(const Vector& from_pos, const Vector& to_pos,
                                      std::unique_ptr<Piece> set_instead = nullptr,
                                      bool returning = false);
    
    template<typename Func>
    auto ghost_test(const Vector& from_pos, const Vector& to_pos, Func func) {
        std::unique_ptr<Piece> taken = move_piece(from_pos, to_pos);
        auto result = func(*this);
        move_piece(to_pos, from_pos, taken, true);
        return result;
    }

    std::vector<Vector> get_piece_valid_moves(Piece* piece, bool check = true, bool for_eval = false);
    const bool is_debug() const { return debug; }
    const std::vector<std::unique_ptr<Piece>>& get_reds() const { return reds; }
    const std::vector<std::unique_ptr<Piece>>& get_blacks() const { return blacks; }
    const std::vector<std::pair<Vector, Vector>>& get_history() const { return history; }
    double get_evaluation() const { return evaluation; }

    bool has_piece(const Vector& position);
    double is_mate() const;
    double evaluate(const EvaluateSet& eval_set, bool describe = false);
    double update_evaluation(const EvaluateSet& eval_set, bool describe = false);
    void update_control_state(Color color, const std::vector<Vector>& attacks);
    void reset_control_state();
};

#endif // BOARD_H