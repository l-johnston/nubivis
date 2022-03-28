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
BASEUNITS = ["m", "kg", "s", "A", "K", "mol", "cd"]
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
    "c",
    "d",
    "E",
    "f",
    "g",
    "G",
    "h",
    "k",
    "K",
    "l",
    "m",
    "µ",
    "M",
    "o",
    "p",
    "P",
    "s",
    "T",
    "y",
    "Y",
    "z",
    "Z",
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
        if t.endswith("g"):
            f = Factors(multiplier=Fraction(1, 1000), kg=1)
            if len(t) > 1:
                f.multiplier *= PREFIXES[t[:-1]]
        elif t.startswith("da") and len(t) > 2:
            f = Factors(multiplier=PREFIXES[t[:2]])
            try:
                setattr(f, t[2:], 1)
            except AttributeError:
                raise TokenError(f"{t[2:]} not a base unit") from None
        elif t[0] in PREFIXES and len(t) > 1:
            f = Factors(multiplier=PREFIXES[t[0]])
            try:
                setattr(f, t[1:], 1)
            except AttributeError:
                raise TokenError(f"{t[1:]} not a base unit") from None
        elif t in BASEUNITS:
            f = Factors()
            setattr(f, t, 1)
        elif t == "(":
            f = self.get_expression()
            t = self.ts.get()
            t = t.value
            if t != ")":
                raise TokenError(f"expect ')', not '{t}'")
        else:
            raise TokenError(f"expected '(' not '{t}'")
        return f

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
