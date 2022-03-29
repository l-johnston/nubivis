# nubivis - Compute everywhere with units

Initial implementation is just the unit expression parser.

The idea is to convert the user's unit expression, e.g. 'mm/s', into the corresponding
SI base units expression internally represented as a set of Factors, e.g.
Factors(multiplier=1/1000, offset=0, m=1, kg=0, s=-1, A=0, K=0, mol=0, cd=0). From here
all computations are in SI base units. For use in Numpy's new DType system:
- convert each array's unit expression string to Factors
- check for valid op based on base unit factors (e.g. can't add 'm' to 's')
- convert each array by applying multiplier/offset before array ops
- perform array ops
- perform Factors arithmetic, e.g. 'm'*'m'=m**2
- do a reverse lookup from Factors to a derived SI unit, e.g. 'V'
- return to user

Mathcad works this way.

The recursive-decent parser is prototyped in `nubivis.prototype`.
```
>>> from nubivis.prototype import parse
>>> parse("mm/s")
Factors(multiplier=1/1000,offset=0,m=1,kg=0,s=-1,A=0,K=0,mol=0,cd=0)
>>> parse("km**2")
Factors(multiplier=1000000,offset=0,m=2,kg=0,s=0,A=0,K=0,mol=0,cd=0)
>>> parse("g")
Factors(multiplier=1/1000,offset=0,m=0,kg=1,s=0,A=0,K=0,mol=0,cd=0)
>>> parse("1/s**(1/2)")
Factors(multiplier=1.0,offset=0,m=0,kg=0,s=-1/2,A=0,K=0,mol=0,cd=0)
```

The prototype was then converted to a C++ equivalent defined in 'parser.cpp'. Since
the Factors are rational numbers, 'parser' depends on boost's multiprecision::cpp_rational.
The example test program 'pe' can be compiled using the Makefile.

```
$ ./pe mm/s
Factors(multiplier=1/1000, offset=0, m=1, kg=0, s=-1, A=0, K=0, mol=0, cd=0)
```
