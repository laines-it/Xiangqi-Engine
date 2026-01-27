#ifndef supports_cpp
#define supports_cpp

#include <vector>
#include <string>
#include <utility>
#include <functional>
#include <cmath>
#include <unordered_set>
#include <iostream>

// =============== Vector Implementation ===============
struct Vector {
    int x;
    int y;

    explicit operator bool() const {
        return x >= 0 && y >= 0;
    }

    Vector(int x = 0, int y = 0) : x(x), y(y) {}

    Vector operator+(const Vector& other) const {
        return Vector(x + other.x, y + other.y);
    }

    Vector operator*(int scalar) const {
        return Vector(x * scalar, y * scalar);
    }

    Vector operator/(int scalar) const {
        return Vector(static_cast<int>(x / scalar), 
                      static_cast<int>(y / scalar));
    }

    bool operator==(const Vector& other) const {
        return x == other.x && y == other.y;
    }

    struct Hash {
        size_t operator()(const Vector& v) const {
            return std::hash<int>()(v.x) ^ (std::hash<int>()(v.y) << 1);
        }
    };

    bool in_area(const std::pair<Vector, Vector>& area) const {
        const auto& [bottom_left, top_right] = area;
        return (x >= bottom_left.x && x <= top_right.x) && 
               (y >= bottom_left.y && y <= top_right.y);
    }

    int length() const { //Manhattan
        return x+y;
    }

    friend std::ostream& operator<<(std::ostream& os, const Vector& vec) {
        os << "(" << vec.x << ", " << vec.y << ")";
        return os;
    }
};

// Board area constants
const Vector FULLBOARD_BL(0, 0);
const Vector FULLBOARD_TR(8, 9);
const std::pair<Vector, Vector> FULLBOARD_AREA = {FULLBOARD_BL, FULLBOARD_TR};

const Vector RED_PALACE_BL(3, 0);
const Vector RED_PALACE_TR(5, 2);
const std::pair<Vector, Vector> RED_PALACE_AREA = {RED_PALACE_BL, RED_PALACE_TR};

const Vector BLACK_PALACE_BL(3, 7);
const Vector BLACK_PALACE_TR(5, 9);
const std::pair<Vector, Vector> BLACK_PALACE_AREA = {BLACK_PALACE_BL, BLACK_PALACE_TR};

const Vector BLACK_HALF_BL(0, 5);
const Vector BLACK_HALF_TR(8, 9);
const std::pair<Vector, Vector> BLACK_HALF = {BLACK_HALF_BL, BLACK_HALF_TR};

const Vector RED_HALF_BL(0, 0);
const Vector RED_HALF_TR(8, 4);
const std::pair<Vector, Vector> RED_HALF = {RED_HALF_BL, RED_HALF_TR};

// =============== Move Implementation ===============
class Move {
private:
    std::vector<Vector> directions;
    bool bigstep;

public:
    Move(std::vector<Vector> directions, bool bigstep = false)
        : directions(directions), bigstep(bigstep) {}

    Vector get_direction(int i) const { return directions[i]; }

    bool is_bigstep() const { return bigstep; }
    const std::vector<Vector>& get_directions() const { return directions; }

    Move operator+(const Vector& vec) {
        directions.push_back(vec);
        return *this;
    }

    Move operator+=(const Vector& vec) {
        directions.push_back(vec);
        return *this;
    }
    
};

// =============== EvaluateSet Implementation ===============
struct EvaluateSet {
    double value_multiplier;
    double attack_bonus;
    double mobility_multiplier;
    double control_multiplier;

    EvaluateSet(double vm = 10.0, double ab = 1.0, 
                double mm = 1.0, double cm = 1.0)
        : value_multiplier(vm), attack_bonus(ab),
          mobility_multiplier(mm), control_multiplier(cm) {}

    std::tuple<double, double, double, double> get() const {
        return std::make_tuple(value_multiplier, attack_bonus, 
                              mobility_multiplier, control_multiplier);
    }
};

// =============== Enumerations ===============
enum class Square_status {
    red = 1,
    neutral = 0,
    black = -1
};

enum class Color {
    RED,
    BLACK
};

Color opposite(Color color) {
    return (color == Color::RED) ? Color::BLACK : Color::RED;
}

enum class GameResult {
    tie = 0,
    red_won = 1,
    black_won = -1
};

// =============== Text Colors ===============

const std::string RED_TEXT = "\033[31m";
const std::string GREEN_TEXT = "\033[32m";
const std::string RESET_TEXT = "\033[0m";

namespace textcolors {
    const std::string black = "\033[30m";
    const std::string red = "\033[31m";
    const std::string green = "\033[32m";
    const std::string orange = "\033[33m";
    const std::string blue = "\033[34m";
    const std::string purple = "\033[35m";
    const std::string cyan = "\033[36m";
    const std::string lightgrey = "\033[37m";
    const std::string darkgrey = "\033[90m";
    const std::string lightred = "\033[91m";
    const std::string lightgreen = "\033[92m";
    const std::string yellow = "\033[93m";
    const std::string lightblue = "\033[94m";
    const std::string pink = "\033[95m";
    const std::string lightcyan = "\033[96m";
    const std::string endc = "\033[0m";
}

#endif