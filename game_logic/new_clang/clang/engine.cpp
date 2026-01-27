#include "engine.h"

Engine::Engine(const EvaluateSet& eval_set, int depth, bool debug)
    : eval_set(eval_set), depth(depth), debug(debug) {
    std::srand(static_cast<unsigned>(std::time(nullptr)));
}

int Engine::depth_control(int num_children) {
    if (num_children <= 20) {
        return 4;
    } else if (num_children <= 30){
        return 2;
    }
    return 0;
}

std::pair<double, std::optional<std::pair<Vector, Vector>>> Engine::get_best_move(Board& board, Color current_player, bool is_random) {
    double alpha = -std::numeric_limits<double>::infinity();
    double beta = std::numeric_limits<double>::infinity();
    std::vector<std::pair<Vector, Vector>> best_moves;
    std::optional<std::pair<Vector, Vector>> best_move = std::nullopt;

    const auto& pieces = (current_player == Color::RED) ? board.get_reds() : board.get_blacks();
    std::vector<std::tuple<double, Vector, Vector>> moves;

    for (const auto& piece : pieces) {
        Vector from_pos = piece->get_position();
        std::vector<Vector> valid_moves = board.get_piece_valid_moves(piece.get(), true);

        for (const Vector& to_pos : valid_moves) {
            double eval_bonus = 0.0;
            auto target_square = board.get_square(to_pos);
            auto captured_piece = target_square.get_piece();

            if (captured_piece) {
                eval_bonus += captured_piece->get_value() * 0.5;
            }

            if (piece->is_attacker()) {
                eval_bonus += 0.3;
            }

            moves.emplace_back(eval_bonus, from_pos, to_pos);
        }
    }

    if (current_player == Color::RED) {
        std::sort(moves.begin(), moves.end(), [](const auto& a, const auto& b) {
            return std::get<0>(a) > std::get<0>(b);
        });
    } else {
        std::sort(moves.begin(), moves.end(), [](const auto& a, const auto& b) {
            return std::get<0>(a) < std::get<0>(b);
        });
    }

    if (!moves.empty()) {
        best_move = std::make_pair(std::get<1>(moves[0]), std::get<2>(moves[0]));
    }

    int depth_boost = 0;
    //int depth_boost = depth_control(moves.size());
    //std::cout << "DEPTH BOOST: " << depth_boost << std::endl;

    for (const auto& move_eval : moves) {
        double bonus = std::get<0>(move_eval);
        Vector from_pos = std::get<1>(move_eval);
        Vector to_pos = std::get<2>(move_eval);

        if (debug) {
            std::cout << "\n==================================================================\n";
            std::cout << "ENGINE for " << (current_player == Color::RED ? "RED" : "BLACK") 
                      << " with " << from_pos << "->" << to_pos << ":\n";
        }

        double move_value = minimax(
            board, from_pos, to_pos, depth + depth_boost, alpha, beta, (current_player == Color::RED)
        );

        if (debug) {
            std::cout << "ENGINE EVALUATION: " << (current_player == Color::RED ? "BLACK" : "RED") 
                      << " can get " << move_value << "\n";
            std::cout << "==================================================================\n\n";
        }

        if (current_player == Color::RED) {
            if (move_value > alpha) {
                if (is_random && (alpha == -std::numeric_limits<double>::infinity() || move_value / alpha < 1.05)) {
                    best_moves.emplace_back(from_pos, to_pos);
                } else {
                    best_move = std::make_pair(from_pos, to_pos);
                }
                if (move_value == std::numeric_limits<double>::infinity()) break;
                alpha = move_value;
            }
        } else {
            if (move_value < beta) {
                if (is_random && (beta == std::numeric_limits<double>::infinity() || beta / move_value < 1.05)) {
                    best_moves.emplace_back(from_pos, to_pos);
                } else {
                    best_move = std::make_pair(from_pos, to_pos);
                }
                if (move_value == -std::numeric_limits<double>::infinity()) break;
                beta = move_value;
            }
        }
    }

    double move_value = (current_player == Color::RED) ? alpha : beta;
    if (is_random) {
        if (!best_moves.empty()) {
            int index = std::rand() % best_moves.size();
            return { move_value, best_moves[index] };
        }
        return { move_value, handle_gameover(board, current_player) };
    }
    return best_move ? std::make_pair(move_value, best_move) 
                     : std::make_pair(move_value, handle_gameover(board, current_player));
}

std::optional<std::pair<Vector, Vector>> Engine::handle_gameover(Board& board, Color color) {
    // bool old_debug = board.is_debug();
    // board.is_debug() = true;

    const auto& team = (color == Color::RED) ? board.get_reds() : board.get_blacks();
    for (const auto& piece : team) {
        std::vector<Vector> vds = board.get_piece_valid_moves(piece.get(), true);
        //std::cout << "ENGINE GAMEOVER: " << piece->get_name() << " valid moves: ";
        //for (const auto& v : vds) std::cout << v << " ";
        //std::cout << "\n";
    }

    // board.is_debug() = old_debug;
    return std::nullopt;
}

double Engine::minimax(Board& board, const Vector& from_pos, const Vector& to_pos, int depth, double alpha, double beta, bool maximizing_player) {
    return board.ghost_test(from_pos, to_pos, [&](Board& b) {
        return minimax_wrapper(b, depth - 1, !maximizing_player, alpha, beta);
    });
}

double Engine::minimax_wrapper(Board& board, int depth, bool maximizing_player, double alpha, double beta) {
    if (depth == 0) {
        double eval = board.evaluate(eval_set);
        if (debug) std::cout << "ENGINE WRAPPER: Evaluation = " << eval << "\n";
        return eval;
    }

    double extreme_value = maximizing_player 
        ? -std::numeric_limits<double>::infinity() 
        : std::numeric_limits<double>::infinity();
    
    const auto& pieces = maximizing_player ? board.get_reds() : board.get_blacks();

    for (const auto& piece : pieces) {
        Vector piece_pos = piece->get_position();
        std::vector<Vector> valid_moves = board.get_piece_valid_moves(piece.get(), false, false);

        for (const Vector& move : valid_moves) {
            if (debug) {
                std::cout << "--------------------------------------\n";
                std::cout << "MINIMAX " << (maximizing_player ? "RED" : "BLACK")
                          << " with " << piece_pos << "->" << move << "\n";
                std::cout << "depth=" << depth << ", alpha=" << alpha << ", beta=" << beta << "\n";
            }

            double current_value = minimax(
                board, piece_pos, move, depth, alpha, beta, maximizing_player
            );

            if (debug) {
                std::cout << "MINIMAX EVALUATION: " << (maximizing_player ? "BLACK" : "RED") 
                          << " can get " << current_value << "\n";
                std::cout << "--------------------------------------\n";
            }

            if (maximizing_player) {
                extreme_value = std::max(extreme_value, current_value);
                alpha = std::max(alpha, extreme_value);
            } else {
                extreme_value = std::min(extreme_value, current_value);
                beta = std::min(beta, extreme_value);
            }

            if (beta <= alpha) break;
        }
        if (beta <= alpha) break;
    }

    return extreme_value;
}