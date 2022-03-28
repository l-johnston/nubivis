#ifndef PARSER_H
#define PARSER_H
#include <iostream>
#include <string>
#include <boost/multiprecision/cpp_int.hpp>

using std::string;

typedef boost::multiprecision::cpp_rational Fraction;

class TokenError
{
public:
    TokenError() = default;
};

class FactorsError
{
public:
    FactorsError() = default;
};

class Token
{
private:
    string value;

public:
    Token(char ch) : value{ch} {};
    Token(string ch) : value{ch} {};
    Token operator+(Token other) { return Token(value + other.value); }
    Token &operator+=(Token other)
    {
        value += other.value;
        return *this;
    }
    bool operator==(Token other) { return value == other.value; }
    bool operator==(string other) { return value == other; }
    bool operator!=(string other) { return value != other; }
    size_t size() { return value.size(); }
    friend std::ostream &operator<<(std::ostream &, const Token &);
    string str() { return value; }
    bool startswith(const char *);
    bool endswith(const char *);
    bool isdecimal();
};

class TokenStream
{
private:
    string expression;
    Token get_numbers(Token);
    Token get_letters(Token);

public:
    TokenStream(string expression) : expression{expression} {};
    void putback(char ch) { expression = ch + expression; }
    void putback(string ch) { expression = ch + expression; }
    void putback(Token t) { expression = t.str() + expression; }
    Token get();
};

class Factors
{
private:
    Fraction multiplier{1};
    Fraction offset{0};
    Fraction m{0};
    Fraction kg{0};
    Fraction s{0};
    Fraction A{0};
    Fraction K{0};
    Fraction mol{0};
    Fraction cd{0};

public:
    Factors() = default;
    Factors(Fraction multiplier, Fraction offset, Fraction m, Fraction kg, Fraction s, Fraction A, Fraction K, Fraction mol, Fraction cd) : multiplier{multiplier}, offset{offset}, m{m}, kg{kg}, s{s}, A{A}, K{K}, mol{mol}, cd{cd} {}
    Fraction get_multiplier() { return multiplier; }
    void set_multiplier(Fraction m) { multiplier = m; }
    Factors operator*(Factors);
    Factors &operator*=(Factors);
    Factors operator/(Factors);
    Factors &operator/=(Factors);
    Factors operator-();
    Factors operator+();
    Factors &pow(Factors);
    friend std::ostream &operator<<(std::ostream &, const Factors &);
};

class Parser
{
private:
    TokenStream ts{""};
    Factors get_expression();
    Factors get_term();
    Factors get_unit();
    Factors get_numberterm(bool inpar = false);
    Factors get_number();

public:
    Parser() = default;
    Factors parse(const string &);
};
#endif // PARSER_H
