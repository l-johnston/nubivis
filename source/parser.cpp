#include <algorithm>
#include <vector>
#include <string>
#include <sstream>
#include <cstring>
#include <map>
#include <cmath>
#include <cctype>
#include <iostream>
#include "parser.h"

using std::map;
using std::string;
using std::vector;

const int64_t LENMAXINT{2};
const int64_t LENMAXSTR{128};

map<string, Factors> SIUNITS{
    {"m", Factors(1, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"kg", Factors(1, 0, 0, 1, 0, 0, 0, 0, 0)},
    {"g", Factors(Fraction(1, 1000), 0, 0, 1, 0, 0, 0, 0, 0)},
    {"s", Factors(1, 0, 0, 0, 1, 0, 0, 0, 0)},
    {"A", Factors(1, 0, 0, 0, 0, 1, 0, 0, 0)},
    {"K", Factors(1, 0, 0, 0, 0, 0, 1, 0, 0)},
    {"mol", Factors(1, 0, 0, 0, 0, 0, 0, 1, 0)},
    {"cd", Factors(1, 0, 0, 0, 0, 0, 0, 0, 1)},
    {"rad", Factors()},
    {"sr", Factors()},
    {"Hz", Factors(1, 0, 0, 0, -1, 0, 0, 0, 0)},
    {"N", Factors(1, 0, 1, 1, -2, 0, 0, 0, 0)},
    {"Pa", Factors(1, 0, -1, 1, -2, 0, 0, 0, 0)},
    {"J", Factors(1, 0, 2, 1, -2, 0, 0, 0, 0)},
    {"W", Factors(1, 0, 2, 1, -3, 0, 0, 0, 0)},
    {"C", Factors(1, 0, 0, 0, 1, 1, 0, 0, 0)},
    {"V", Factors(1, 0, 2, 1, -3, -1, 0, 0, 0)},
    {"F", Factors(1, 0, -2, -1, 4, 2, 0, 0, 0)},
    {"Ω", Factors(1, 0, 2, 1, -3, -2, 0, 0, 0)},
    {"S", Factors(1, 0, -2, -1, -2, -1, 0, 0, 0)},
    {"Wb", Factors(1, 0, 2, 1, -2, -1, 0, 0, 0)},
    {"T", Factors(1, 0, 0, 1, -2, -1, 0, 0, 0)},
    {"H", Factors(1, 0, 2, 1, -2, -2, 0, 0, 0)},
    {"degC", Factors(1, Fraction(27315, 100), 0, 0, 0, 0, 1, 0, 0)},
    {"lm", Factors(1, 0, 0, 0, 0, 0, 0, 0, 1)},
    {"lx", Factors(1, 0, -2, 0, 0, 0, 0, 0, 1)},
    {"Bq", Factors(1, 0, 0, 0, -1, 0, 0, 0, 0)},
    {"Gy", Factors(1, 0, 2, 0, -2, 0, 0, 0, 0)},
    {"Sv", Factors(1, 0, 2, 0, -2, 0, 0, 0, 0)},
    {"kat", Factors(1, 0, 0, 0, -1, 0, 0, 1, 0)},
    {"L", Factors(Fraction(1, 1000), 0, 3, 0, 0, 0, 0, 0, 0)},
};

map<string, Factors> NONSIUNITS{
    {"Å", Factors(Fraction(1, 10000000000), 1, 0, 0, 0, 0, 0, 0, 0)},
    {"ua", Factors(1.495979e11, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"ch", Factors(2.011684e1, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"fathom", Factors(1.828804, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"fermi", Factors(Fraction(1, 1000000000000000), 0, 1, 0, 0, 0, 0, 0, 0)},
    {"ft", Factors(3.048e-1, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"in", Factors(2.54e-2, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"µ", Factors(Fraction(1, 1000000), 0, 1, 0, 0, 0, 0, 0, 0)},
    {"mil", Factors(Fraction(254, 10000000), 0, 1, 0, 0, 0, 0, 0, 0)},
    {"mi", Factors(1.609344e3, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"yd", Factors(9.144e-1, 0, 1, 0, 0, 0, 0, 0, 0)},
    {"oz", Factors(2.834952e-2, 0, 0, 1, 0, 0, 0, 0, 0)},
    {"lb", Factors(4.535924e-1, 0, 0, 1, 0, 0, 0, 0, 0)},
    {"d", Factors(8.64e4, 0, 0, 0, 1, 0, 0, 0, 0)},
    {"h", Factors(3.6e3, 0, 0, 0, 1, 0, 0, 0, 0)},
    {"min", Factors(60, 0, 0, 0, 1, 0, 0, 0, 0)},
    {"degF", Factors(Fraction(10, 18), 459.67, 0, 0, 0, 0, 1, 0, 0)},
    {"degR", Factors(Fraction(10, 18), 0, 0, 0, 0, 0, 1, 0, 0)},
    {"BTU", Factors(1.05587e3, 0, 2, 1, -2, 0, 0, 0, 0)},
    {"cal", Factors(4.19002, 0, 2, 1, -2, 0, 0, 0, 0)},
    {"eV", Factors(1.602176e-19, 0, 2, 1, -2, 0, 0, 0, 0)},
    {"lbf", Factors(4.448222, 0, 1, 1, -2, 0, 0, 0, 0)},
    {"horsepower", Factors(7.46e2, 0, 2, 1, -3, 0, 0, 0, 0)},
    {"atm", Factors(1.01325e5, 0, -1, 1, -2, 0, 0, 0, 0)},
    {"bar", Factors(Fraction(100000, 1), 0, -1, 1, -2, 0, 0, 0, 0)},
    {"inHg", Factors(3.386389e3, 0, -1, 1, -2, 0, 0, 0, 0)},
    {"psi", Factors(6.894757, 0, -1, 1, -2, 0, 0, 0, 0)},
    {"torr", Factors(1.333224e2, 0, -1, 1, -2, 0, 0, 0, 0)},
    {"rad", Factors(1e-2, 0, 2, 0, -2, 0, 0, 0, 0)},
    {"rem", Factors(1e-2, 0, 2, 0, -2, 0, 0, 0, 0)},
    {"gal", Factors(3.785412e-3, 0, 3, 0, 0, 0, 0, 0, 0)},
};

map<string, Fraction> PREFIXES{
    {"P", Fraction(1000000000000000)},
    {"T", Fraction(1000000000000)},
    {"G", Fraction(1000000000)},
    {"M", Fraction(1000000)},
    {"k", Fraction(1000)},
    {"h", Fraction(100)},
    {"da", Fraction(10)},
    {"d", Fraction(1, 10)},
    {"c", Fraction(1, 100)},
    {"m", Fraction(1, 1000)},
    {"µ", Fraction(1, 1000000)},
    {"n", Fraction(1, 1000000000)},
    {"p", Fraction(1, 1000000000000)},
    {"f", Fraction(1, 1000000000000000)},
};

const vector<string> NUMBERS{"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"};
const vector<string> OPERATORS{"-", "+", "*", "/", "**", "(", ")"};
const vector<string> LETTERS{
    "a",
    "A",
    "B",
    "b",
    "c",
    "C",
    "d",
    "e",
    "E",
    "f",
    "F",
    "g",
    "G",
    "h",
    "H",
    "i",
    "k",
    "K",
    "l",
    "L",
    "m",
    "M",
    "µ",
    "n",
    "N",
    "o",
    "p",
    "P",
    "q",
    "r",
    "S",
    "s",
    "t",
    "T",
    "v",
    "V",
    "W",
    "x",
    "y",
    "Y",
    "z",
    "Z",
    "Ω",
};
vector<string> simpletokens{};

bool Token::startswith(const char *s)
{
    size_t len{std::strlen(s)};
    return (value.substr(0, len) == s);
}

bool Token::endswith(const char *s)
{
    size_t len{std::strlen(s)};
    if (value.size() < len)
        return false;
    return (value.substr(value.size() - len) == s);
}

bool Token::isdecimal()
{
    for (auto ch : value)
    {
        if (std::isdigit(ch))
            continue;
        return false;
    }
    return true;
}

std::ostream &operator<<(std::ostream &os, const Token &t) { return os << t.value; }

Token TokenStream::get_numbers(Token t)
{
    if (expression.size() == 0)
        return t;
    string ch{expression[0]};
    expression = expression.substr(1);
    if (std::find(NUMBERS.begin(), NUMBERS.end(), ch) == NUMBERS.end())
    {
        putback(ch);
        return t;
    }
    t += Token(ch);
    if (t.size() > LENMAXINT)
        throw TokenError();
    return get_numbers(t);
}

Token TokenStream::get_letters(Token t)
{
    if (expression.size() == 0)
        return t;
    string ch{expression[0]};
    expression = expression.substr(1);
    if (std::find(LETTERS.begin(), LETTERS.end(), ch) == LETTERS.end())
    {
        putback(ch);
        return t;
    }
    t += Token(ch);
    if (t.size() > LENMAXSTR)
        throw TokenError();
    return get_letters(t);
}

const vector<string> ops{"-", "+", "/", "(", ")"};

const Token empty_token{""};
const string op_star{"*"};

Token TokenStream::get()
{
    if (expression.size() == 0)
        return empty_token;
    string ch{expression[0]};
    expression = expression.substr(1);
    if (find(ops.begin(), ops.end(), ch) != ops.end())
        return Token(ch);
    if (ch == op_star)
    {
        if (expression[0] == '*')
        {
            ch += op_star;
            expression = expression.substr(1);
        }
        return Token(ch);
    }
    if (std::find(NUMBERS.begin(), NUMBERS.end(), ch) != NUMBERS.end())
        return get_numbers(Token(ch));
    if (std::find(LETTERS.begin(), LETTERS.end(), ch) != LETTERS.end())
        return get_letters(Token(ch));
    throw TokenError();
}

const Fraction zero{0};

Factors Factors::operator*(Factors other)
{
    if (offset != zero && other.offset != zero)
        throw FactorsError();
    Factors res{};
    res.multiplier = multiplier * other.multiplier;
    res.m = m + other.m;
    res.kg = kg + other.kg;
    res.s = s + other.s;
    res.A = A + other.A;
    res.mol = mol + other.mol;
    res.cd = cd + other.cd;
    return res;
}

Factors &Factors::operator*=(Factors other)
{
    if (offset != 0 && other.offset != zero)
        throw FactorsError();
    multiplier *= other.multiplier;
    m += other.m;
    kg += other.kg;
    s += other.s;
    A += other.A;
    K += other.K;
    mol += other.mol;
    cd += other.cd;
    return *this;
}

Factors Factors::operator/(Factors other)
{
    if (offset != zero && other.offset != zero)
        throw FactorsError();
    Factors res{};
    res.multiplier = multiplier / other.multiplier;
    res.m = m - other.m;
    res.kg = kg - other.kg;
    res.s = s - other.s;
    res.A = A - other.A;
    res.mol = mol - other.mol;
    res.cd = cd - other.cd;
    return res;
}

Factors &Factors::operator/=(Factors other)
{
    if (offset != zero && other.offset != zero)
        throw FactorsError();
    multiplier = multiplier / other.multiplier;
    m -= other.m;
    kg -= other.kg;
    s -= other.s;
    A -= other.A;
    mol -= other.mol;
    cd -= other.cd;
    return *this;
}

Factors Factors::operator-()
{
    multiplier *= -1;
    return *this;
}

Factors Factors::operator+()
{
    return *this;
}

Factors &Factors::pow(Factors f)
{
    if (offset != zero)
        throw FactorsError();
    Fraction exponent{f.get_multiplier()};
    double x = static_cast<double>(multiplier);
    double y = static_cast<double>(exponent);
    multiplier = Fraction(std::pow(x, y));
    m *= exponent;
    kg *= exponent;
    s *= exponent;
    A *= exponent;
    mol *= exponent;
    cd *= exponent;
    return *this;
}

std::ostream &operator<<(std::ostream &os, const Factors &f)
{
    std::ostringstream oss{};
    oss << "Factors(multiplier="
        << f.multiplier
        << ", offset="
        << f.offset
        << ", m="
        << f.m
        << ", kg="
        << f.kg
        << ", s="
        << f.s
        << ", A="
        << f.A
        << ", K="
        << f.K
        << ", mol="
        << f.mol
        << ", cd="
        << f.cd
        << ")";
    return os << oss.str();
}

Factors Parser::parse(const std::string &units)
{
    ts = TokenStream(units);
    return get_expression();
}

Factors Parser::get_expression()
{
    Factors f{get_term()};
    Token t{ts.get()};
    while (true)
    {
        if (t == "*")
        {
            f *= get_term();
        }
        else if (t == "/")
            f /= get_term();
        else if (t == "")
            break;
        else
        {
            ts.putback(t);
            break;
        }
        t = ts.get();
    }
    return f;
}

Factors Parser::get_term()
{
    Factors f{get_unit()};
    Token t{ts.get()};
    while (true)
    {
        if (t == "**")
            f = f.pow(get_numberterm());
        else
        {
            ts.putback(t);
            break;
        }
        t = ts.get();
    }
    return f;
}

Factors Parser::get_unit()
{
    Token t{ts.get()};
    Factors f{};
    if (NONSIUNITS.find(t.str()) != NONSIUNITS.end())
        return NONSIUNITS[t.str()];
    if (SIUNITS.find(t.str()) != SIUNITS.end())
        return SIUNITS[t.str()];
    size_t prefixlen{1};
    if (t.startswith("da"))
        prefixlen = 2;
    if (PREFIXES.find(t.str().substr(0, prefixlen)) != PREFIXES.end())
    {
        f = SIUNITS[t.str().substr(prefixlen)];
        Fraction multiplier{f.get_multiplier()};
        multiplier *= PREFIXES[t.str().substr(0, prefixlen)];
        f.set_multiplier(multiplier);
        return f;
    }
    if (t == "(")
    {
        f = get_expression();
        t = ts.get();
        if (t != ")")
            throw TokenError();
        return f;
    }
    throw TokenError();
}

Factors Parser::get_numberterm(bool inpar)
{
    Factors f{get_number()};
    Token t{ts.get()};
    while (true)
    {
        if (inpar && t == "/")
            f /= get_number();
        else if (inpar && t == "*")
            f *= get_number();
        else
        {
            ts.putback(t);
            break;
        }
        t = ts.get();
    }
    return f;
}

Factors Parser::get_number()
{
    Factors f{};
    Token t{ts.get()};
    if (t == "(")
    {
        f = get_numberterm(true);
        t = ts.get();
        if (t != ")")
            throw TokenError();
        return f;
    }
    if (t.isdecimal())
    {
        f.set_multiplier(Fraction(t.str()));
        return f;
    }
    if (t == "-")
        return (-get_number());
    if (t == "+")
        return get_number();
    throw TokenError();
}
