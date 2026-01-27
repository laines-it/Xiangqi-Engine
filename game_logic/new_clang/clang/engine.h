#pragma once
#include "board.h"
#include <optional>
#include <tuple>
#include <vector>
#include <limits>
#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <iostream>

class Engine {
private:
    bool debug;
    int depth;
    EvaluateSet eval_set;

    std::optional<std::pair<Vector, Vector>> handle_gameover(Board& board, Color color);
    double minimax(Board& board, const Vector& from_pos, const Vector& to_pos, int depth, double alpha, double beta, bool maximizing_player);
    double minimax_wrapper(Board& board, int depth, bool maximizing_player, double alpha, double beta);
    int depth_control(int num_children);
public:
    Engine(const EvaluateSet& eval_set, int depth = 3, bool debug = false);
    std::pair<double, std::optional<std::pair<Vector, Vector>>> get_best_move(Board& board, Color current_player, bool is_random = false);
};