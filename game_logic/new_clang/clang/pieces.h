#ifndef PIECES_HPP
#define PIECES_HPP

#include <iostream>
#include <vector>
#include <string>
#include <utility>
#include "supports.cpp"

class Piece {
protected:
    Color color;
    Vector position;
    Move move;
    std::string name;
    bool attacking;
    double value;
    std::vector<Vector> frontier;
    virtual bool is_inside_front(Vector front, Vector square);
    
public:
    Piece(Color color, Vector position, Move move, std::string name, bool attacking, double value, std::vector<Vector> frontier = {});
    virtual ~Piece() = default;

    virtual bool need_screen() const;
    virtual bool can_modify() const;
    virtual bool is_modified() const;
    virtual void modify();
    virtual void set_default();
    virtual int get_max_steps() const = 0;
    
    virtual std::pair<Vector, Vector> get_area() const;
    
    bool is_attacker() const;
    void set_value(double val);
    double get_value() const;
    Vector get_position() const;
    void set_position(Vector new_position);
    void set_front(std::vector<Vector> new_frontier);
    Color get_color() const;
    const Move& get_move() const;
    std::string get_name() const;

    bool is_inside_front(Vector front, Vector square);
    int get_prolong_direction(Vector square);
    int block_direction(Vector square, Color c);
    
    friend std::ostream& operator<<(std::ostream& os, const Piece& piece);
};

class General : public Piece {
public:
    General(Color color, Vector position);
    int get_max_steps() const override;
    std::pair<Vector, Vector> get_area() const override;
};

class Advisor : public Piece {
public:
    Advisor(Color color, Vector position);
    int get_max_steps() const override;
    std::pair<Vector, Vector> get_area() const override;
};

class Chariot : public Piece {
public:
    Chariot(Color color, Vector position);
    int get_max_steps() const override;
};

class Horse : public Piece {
public:
    Horse(Color color, Vector position);
    int get_max_steps() const override;
};

class Elephant : public Piece {
public:
    Elephant(Color color, Vector position);
    int get_max_steps() const override;
    std::pair<Vector, Vector> get_area() const override;
};

class Cannon : public Piece {
public:
    Cannon(Color color, Vector position);
    bool need_screen() const override;
    int get_max_steps() const override;
};

class Soldier : public Piece {
private:
    bool modified;
    Move originalMove;

public:
    Soldier(Color color, Vector position);
    int get_max_steps() const { return 1; }
    bool can_modify() const { return true; }
    bool is_modified() const { return modified; }
    void modify() override;
    void set_default() override;
};

#endif