# Standard Libs
import math
import operator
import re
from asyncio import create_task
from decimal import *

# First Party
from core import hook

# Third Party
from pyparsing import (CaselessLiteral, Combine, Forward, Group, Literal,
                       Optional, Word, ZeroOrMore, alphas, nums)

# Global Vars
exprStack = []
terms = None

# map operator symbols to corresponding arithmetic operations
epsilon = 1e-12
opn = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "^": operator.pow
}
fn = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "abs": abs,
    "trunc": lambda a: int(a),
    "round": round,
    "sgn": lambda a: abs(a) > epsilon and cmp(a, 0) or 0
}


def pushFirst(strg, loc, toks):
    exprStack.append(toks[0])


def pushUMinus(strg, loc, toks):
    if toks and toks[0] == '-':
        exprStack.append('unary -')
        #~ exprStack.append( '-1' )
        #~ exprStack.append( '*' )


def parseTerms():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global terms
    if not terms:
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(
            Word("+-" + nums, nums) + Optional(point + Optional(Word(nums))) + Optional(e + Word(
                "+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")

        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")

        expr = Forward()
        atom = (Optional("-") + (pi | e | fnumber | ident + lpar + expr + rpar).setParseAction(
            pushFirst) | (lpar + expr.suppress() + rpar)).setParseAction(pushUMinus)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore((expop + factor).setParseAction(pushFirst))

        term = factor + ZeroOrMore((multop + factor).setParseAction(pushFirst))
        expr << term + ZeroOrMore((addop + term).setParseAction(pushFirst))
        terms = expr
    return terms


def evaluateStack(s):
    try:
        op = s.pop()
        if op == 'unary -':
            return -evaluateStack(s)
        if op in "+-*/^":
            op2 = evaluateStack(s)
            op1 = evaluateStack(s)
            return opn[op](op1, op2)
        elif op == "PI":
            return math.pi    # 3.1415926535
        elif op == "E":
            return math.e    # 2.718281828
        elif op in fn:
            return fn[op](evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)
    except:
        return None


@hook.hook('command', ['c'], autohelp=True)
async def c(bot, msg):
    "c [equation] -- calculates equation with custom calculator"
    global exprStack
    inp = msg.message
    exprStack = []
    #try:
    results = parseTerms().parseString(inp)
    # except: return "I cant let you do that Jim."
    val = evaluateStack(exprStack[:])
    if val is None:
        create_task(bot.send_privmsg([msg.target], "Uwaahh~~ i-its too big onii-chan!"))
    else:
        try:
            val = "{:20,.17f}".format(val)
            val = re.search(r'^(.*\...[1-9+]*).*$', val).group(1)
        except:
            val = val
    create_task(bot.send_privmsg([msg.target], f'{inp} = {val}'))
