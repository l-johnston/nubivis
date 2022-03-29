"""A prototype recursive-decent unit expression parser

The parser converts a unit expression string to SI base units.

>>> parse('mm/s')
Factors(multiplier=1/1000,offset=0,m=1,kg=0,s=-1,A=0,K=0,mol=0,cd=0)
>>> parse('s**(-1/2))
Factors(multiplier=1,offset=0,m=0,kg=0,s=-1/2,A=0,K=0,mol=0,cd=0)
"""
from fractions import Fraction

LENMAXINT = 2  # max length of power exponent string
LENMAXSTR = 128  # max length of a unit expression string
# BASEUNITS = ["m", "kg", "s", "A", "K", "mol", "cd"]
PREFIXES = {
    "Y": Fraction(10**24),
    "Z": Fraction(10**21),
    "E": Fraction(10**18),
    "P": Fraction(10**15),
    "T": Fraction(10**12),
    "G": Fraction(10**9),
    "M": Fraction(10**6),
    "k": Fraction(10**3),
    "h": Fraction(10**2),
    "da": Fraction(10**1),
    "": Fraction(1),
    "d": Fraction(1, 10**1),
    "c": Fraction(1, 10**2),
    "m": Fraction(1, 10**3),
    "µ": Fraction(1, 10**6),
    "n": Fraction(1, 10**9),
    "p": Fraction(1, 10**12),
    "f": Fraction(1, 10**15),
    "a": Fraction(1, 10**18),
    "z": Fraction(1, 10**21),
    "y": Fraction(1, 10**24),
}
NUMBERS = [str(n) for n in range(10)]
OPERATORS = ["-", "+", "*", "/", "**", "(", ")"]
LETTERS = [
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
]
SIMPLETOKENS = NUMBERS + OPERATORS + LETTERS


class TokenError(Exception):
    """TokenError"""


class Token:
    """Token"""

    def __init__(self, ch: str):
        self.value = ch

    def __repr__(self):
        return f"Token('{self.value}')"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"{other} not a Token")
        return self.value == other.value

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"{other} not a Token")
        return Token(self.value + other.value)

    def __len__(self):
        return len(self.value)


class TokenStream:
    """Extract tokens from unit expression string"""

    def __init__(self, expression: str):
        self.expression = expression

    def __repr__(self):
        return f"TokenStream('{self.expression})'"

    def __str__(self):
        return f"{self.expression}"

    def putback(self, ch: str) -> None:
        """put token into the buffer because 'ch' starts a different type of token"""
        self.expression = ch + self.expression

    def _get_numbers(self, token: Token) -> Token:
        """compose a numeric token"""
        if len(self.expression) == 0:
            return token
        ch = self.expression[0]
        self.expression = self.expression[1:]
        if ch not in NUMBERS:
            self.putback(ch)
            return token
        token = token + Token(ch)
        if len(token) > LENMAXINT:
            raise TokenError(f"{token} exceeds max int")
        return self._get_numbers(token)

    def _get_letters(self, token: Token) -> Token:
        """compose an alphabetic token"""
        if len(self.expression) == 0:
            return token
        ch = self.expression[0]
        self.expression = self.expression[1:]
        if ch not in LETTERS:
            self.putback(ch)
            return token
        token = token + Token(ch)
        if len(token) > LENMAXSTR:
            raise TokenError(f"{token} exceeds max str length")
        return self._get_letters(token)

    def get(self) -> Token:
        """get a token"""
        if len(self.expression) == 0:
            return Token("")
        ch = self.expression[0]
        self.expression = self.expression[1:]
        if ch in ["-", "+", "/", "(", ")"]:
            return Token(ch)
        if ch == "*":
            if self.expression.startswith("*"):
                ch += "*"
                self.expression = self.expression[1:]
            return Token(ch)
        if ch in NUMBERS:
            return self._get_numbers(Token(ch))
        if ch in LETTERS:
            return self._get_letters(Token(ch))
        raise TokenError(f"{ch} not a simple token")

    def __iter__(self):
        while True:
            if len(self.expression) == 0:
                return None
            yield self.get()


class Factors:
    """SI base unit factors"""

    __slots__ = ["multiplier", "offset", "m", "kg", "s", "A", "K", "mol", "cd"]

    def __init__(self, multiplier=1, offset=0, m=0, kg=0, s=0, A=0, K=0, mol=0, cd=0):
        self.multiplier = Fraction(multiplier)
        self.offset = Fraction(offset)
        self.m = Fraction(m)
        self.kg = Fraction(kg)
        self.s = Fraction(s)
        self.A = Fraction(A)
        self.K = Fraction(K)
        self.mol = Fraction(mol)
        self.cd = Fraction(cd)

    def __mul__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"{other} must of type {self.__class__}")
        if self.offset != 0 and other.offset != 0:
            raise ValueError("offsets must be zero")
        res = Factors()
        for k in self.__slots__:
            if k == "multiplier":
                setattr(res, k, getattr(self, k) * getattr(other, k))
            else:
                setattr(res, k, getattr(self, k) + getattr(other, k))
        return res

    def __truediv__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"{other} must of type {self.__class__}")
        if self.offset != 0 and other.offset != 0:
            raise ValueError("offsets must be zero")
        res = Factors()
        for k in self.__slots__:
            if k == "multiplier":
                setattr(res, k, getattr(self, k) / getattr(other, k))
            elif k == "offset":
                continue
            else:
                setattr(res, k, getattr(self, k) - getattr(other, k))
        return res

    def __neg__(self):
        self.multiplier = -self.multiplier
        return self

    def __pos__(self):
        return self

    def __pow__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"{other} must of type {self.__class__}")
        if self.offset != 0 and other.offset != 0:
            raise ValueError("offsets must be zero")
        multiplier = other.multiplier
        res = Factors()
        for k in self.__slots__:
            if k in ["offset", "slots"]:
                continue
            elif k == "multiplier":
                setattr(res, k, getattr(self, k) ** multiplier)
            else:
                setattr(res, k, getattr(self, k) * multiplier)
        return res

    def __repr__(self):
        params = ",".join([f"{k}={getattr(self, k)}" for k in self.__slots__])
        return "Factors(" + params + ")"

    def __str__(self):
        res = ""
        for factor in self.__slots__:
            if factor == "offset":
                continue
            fraction = getattr(self, factor)
            if factor == "multiplier":
                if fraction.denominator > 1:
                    res += f"({fraction})"
                elif fraction.numerator > 1:
                    res += f"{fraction.numerator}"
            else:
                if fraction.numerator == 0:
                    continue
                if fraction.denominator > 1:
                    res += f"*{factor}**({fraction})"
                elif fraction.numerator > 1:
                    res += f"*{factor}**{fraction.numerator}"
                else:
                    res += f"*{factor}"
        if res == "":
            res = "1"
        elif res.startswith("*"):
            res = res[1:]
        return res


SIUNITS = {
    "m": Factors(m=1),
    "kg": Factors(kg=1),
    "g": Factors(multiplier=Fraction(1, 1000), kg=1),
    "s": Factors(s=1),
    "A": Factors(A=1),
    "K": Factors(K=1),
    "mol": Factors(mol=1),
    "cd": Factors(cd=1),
    "rad": Factors(),
    "sr": Factors(),
    "Hz": Factors(s=-1),
    "N": Factors(m=1, kg=1, s=-2),
    "Pa": Factors(m=-1, kg=1, s=-2),
    "J": Factors(m=2, kg=1, s=-2),
    "W": Factors(m=2, kg=1, s=-3),
    "C": Factors(s=1, A=1),
    "V": Factors(m=2, kg=1, s=-3, A=-1),
    "F": Factors(m=-2, kg=-1, s=4, A=2),
    "Ω": Factors(m=2, kg=1, s=-3, A=-2),
    "S": Factors(m=-2, kg=-1, s=-2, A=-1),
    "Wb": Factors(m=2, kg=1, s=-2, A=-1),
    "T": Factors(kg=1, s=-2, A=-1),
    "H": Factors(m=2, kg=1, s=-2, A=-2),
    "degC": Factors(offset=273.15, K=1),
    "lm": Factors(cd=1),
    "lx": Factors(m=-2, cd=1),
    "Bq": Factors(s=-1),
    "Gy": Factors(m=2, s=-2),
    "Sv": Factors(m=2, s=-2),
    "kat": Factors(s=-1, mol=1),
    "L": Factors(multiplier=1e-3, m=3),
}

NONSIUNITS = {
    "Å": Factors(multiplier=1e-10, m=1),
    "ua": Factors(multiplier=1.495979e11, m=1),
    "ch": Factors(multiplier=2.011684e1, m=1),
    "fathom": Factors(multiplier=1.828804, m=1),
    "fermi": Factors(multiplier=1e-15, m=1),
    "ft": Factors(multiplier=3.048e-1, m=1),
    "in": Factors(multiplier=2.54e-2, m=1),
    "µ": Factors(multiplier=1e-6, m=1),
    "mil": Factors(multiplier=2.54e-5, m=1),
    "mi": Factors(multiplier=1.609344e3, m=1),
    "yd": Factors(multiplier=9.144e-1, m=1),
    "oz": Factors(multiplier=2.834952e-2, kg=1),
    "lb": Factors(multiplier=4.535924e-1, kg=1),
    "d": Factors(multiplier=8.64e4, s=1),
    "h": Factors(multiplier=3.6e3, s=1),
    "min": Factors(multiplier=60, s=1),
    "degF": Factors(multiplier=Fraction(10, 18), offset=459.67, K=1),
    "degR": Factors(multiplier=Fraction(10, 18), K=1),
    "BTU": Factors(multiplier=1.05587e3, m=2, kg=1, s=-2),
    "cal": Factors(multiplier=4.19002, m=2, kg=1, s=-2),
    "eV": Factors(multiplier=1.602176e-19, m=2, kg=1, s=-2),
    "lbf": Factors(multiplier=4.448222, m=1, kg=1, s=-2),
    "horsepower": Factors(multiplier=7.46e2, m=2, kg=1, s=-3),
    "atm": Factors(multiplier=1.01325e5, m=-1, kg=1, s=-2),
    "bar": Factors(multiplier=1e5, m=-1, kg=1, s=-2),
    "inHg": Factors(multiplier=3.386389e3, m=-1, kg=1, s=-2),
    "psi": Factors(multiplier=6.894757, m=-1, kg=1, s=-2),
    "torr": Factors(multiplier=1.333224e2, m=-1, kg=1, s=-2),
    "rad": Factors(multiplier=1e-2, m=2, s=-2),
    "rem": Factors(multiplier=1e-2, m=2, s=-2),
    "gal": Factors(multiplier=3.785412e-3, m=3),
}


class Parser:
    """A recursive-decent parser for unit expressions

    Converts unit expression string to SI base unit Factors
    """

    def __init__(self):
        self.ts = TokenStream("")

    def get_expression(self) -> Factors:
        """Expression"""
        t = self.ts.get()
        if t.value[0] in NUMBERS:
            self.ts.putback(t.value)
            f = self.get_numberterm()
        else:
            self.ts.putback(t.value)
            f = self.get_term()
        t = self.ts.get()
        t = t.value
        while True:
            if t == "*":
                f *= self.get_term()
            elif t == "/":
                f /= self.get_term()
            elif t == "":
                break
            else:
                self.ts.putback(t)
                break
            t = self.ts.get()
            t = t.value
        return f

    def get_term(self) -> Factors:
        """Term"""
        f = self.get_unit()
        t = self.ts.get()
        t = t.value
        while True:
            if t == "**":
                f **= self.get_numberterm()
            else:
                self.ts.putback(t)
                break
            t = self.ts.get()
            t = t.value
        return f

    def get_unit(self) -> Factors:
        """Unit"""
        t = self.ts.get()
        t = t.value
        f = Factors()
        if t in NONSIUNITS:
            return NONSIUNITS[t]
        if t in SIUNITS:
            return SIUNITS[t]
        prefixlen = 1
        if t.startswith("da"):
            prefixlen = 2
        if t[:prefixlen] in PREFIXES:
            f = SIUNITS[t[prefixlen:]]
            f.multiplier *= PREFIXES[t[:prefixlen]]
            return f
        if t == "(":
            f = self.get_expression()
            t = self.ts.get()
            t = t.value
            if t != ")":
                raise TokenError(f"expect ')', not '{t}'")
            return f
        raise TokenError(f"unknown unit '{t}'")

    def get_numberterm(self, inpar=False) -> Factors:
        """NumberTerm"""
        f = self.get_number()
        t = self.ts.get()
        t = t.value
        while True:
            if inpar and t == "/":
                f /= self.get_number()
            elif inpar and t == "*":
                f *= self.get_number()
            else:
                self.ts.putback(t)
                break
            t = self.ts.get()
            t = t.value
        return f

    def get_number(self) -> Factors:
        """Number"""
        t = self.ts.get()
        t = t.value
        if t == "(":
            f = self.get_numberterm(inpar=True)
            t = self.ts.get()
            if t.value != ")":
                raise TokenError(f"expect ')', not '{t}'")
            return f
        if t.isdecimal():
            return Factors(multiplier=int(t))
        if t == "-":
            return -self.get_number()
        if t == "+":
            return self.get_number()
        raise TokenError(f"expected a number, not {t}")

    def __call__(self, units: str):
        self.ts = TokenStream(units)
        return self.get_expression()


parse = Parser()
