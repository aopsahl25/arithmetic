'''
This is a "simple" homework to practice parsing grammars and working with the resulting parse tree.
'''


import lark


grammar = r"""
    start: sum

    ?sum: term
        | sum "+" term   -> add
        | sum "-" term   -> sub

    ?term: factor
        | term "*" factor  -> mul
        | term "%" factor  -> mod
        | term "/" factor -> div

    ?factor: atom
        | factor "**" atom -> exp

    ?atom: NUMBER            -> number
        | "(" sum ")"        -> paren
        | atom "(" sum ")"   -> implicit_mul  

    NUMBER: /-?[0-9]+/

    %import common.WS_INLINE
    %ignore WS_INLINE
"""


parser = lark.Lark(grammar)

class Interpreter(lark.visitors.Interpreter):
    '''
    Compute the value of the expression.
    The interpreter class processes nodes "top down",
    starting at the root and recursively evaluating subtrees.

    FIXME:
    Get all the test cases to pass.

    >>> interpreter = Interpreter()
    >>> interpreter.visit(parser.parse("1"))
    1
    >>> interpreter.visit(parser.parse("-1"))
    -1
    >>> interpreter.visit(parser.parse("1+2"))
    3
    >>> interpreter.visit(parser.parse("1-2"))
    -1
    >>> interpreter.visit(parser.parse("(1+2)*3"))
    9
    >>> interpreter.visit(parser.parse("1+2*3"))
    7
    >>> interpreter.visit(parser.parse("1*2+3"))
    5
    >>> interpreter.visit(parser.parse("1*(2+3)"))
    5
    >>> interpreter.visit(parser.parse("(1*2)+3*4*(5-6)"))
    -10
    >>> interpreter.visit(parser.parse("((1*2)+3*4)*(5-6)"))
    -14
    >>> interpreter.visit(parser.parse("(1*(2+3)*4)*(5-6)"))
    -20
    >>> interpreter.visit(parser.parse("((1*2+(3)*4))*(5-6)"))
    -14

    NOTE:
    The grammar for the arithmetic above should all be implemented correctly.
    The arithmetic expressions below, however, will require you to modify the grammar.

    Modular division:

    >>> interpreter.visit(parser.parse("1%2"))
    1
    >>> interpreter.visit(parser.parse("3%2"))
    1
    >>> interpreter.visit(parser.parse("(1+2)%3"))
    0

    Exponentiation:

    >>> interpreter.visit(parser.parse("2**1"))
    2
    >>> interpreter.visit(parser.parse("2**2"))
    4
    >>> interpreter.visit(parser.parse("2**3"))
    8
    >>> interpreter.visit(parser.parse("1+2**3"))
    9
    >>> interpreter.visit(parser.parse("(1+2)**3"))
    27
    >>> interpreter.visit(parser.parse("1+2**3+4"))
    13
    >>> interpreter.visit(parser.parse("(1+2)**(3+4)"))
    2187
    >>> interpreter.visit(parser.parse("(1+2)**3-4"))
    23

    NOTE:
    The calculator is designed to only work on integers.
    Division uses integer division,
    and exponentiation should use integer exponentiation when the exponent is negative.
    (That is, it should round the fraction down to zero.)

    >>> interpreter.visit(parser.parse("2**-1"))
    0
    >>> interpreter.visit(parser.parse("2**(-1)"))
    0
    >>> interpreter.visit(parser.parse("(1+2)**(3-4)"))
    0
    >>> interpreter.visit(parser.parse("1+2**(3-4)"))
    1
    >>> interpreter.visit(parser.parse("1+2**(-3)*4"))
    1

    Implicit multiplication:

    >>> interpreter.visit(parser.parse("1+2(3)"))
    7
    >>> interpreter.visit(parser.parse("1(2(3))"))
    6
    >>> interpreter.visit(parser.parse("(1)(2)(3)"))
    6
    >>> interpreter.visit(parser.parse("(1)(2)+(3)"))
    5
    >>> interpreter.visit(parser.parse("(1+2)(3+4)"))
    21
    >>> interpreter.visit(parser.parse("(1+2)(3(4))"))
    36
    '''

    def visit(self, tree):
        result = super().visit(tree)
        if isinstance(result, list):
            if result:  
                return result[0]
            else:
                return None  
        return result
    def start(self, tree):
        return self.visit(tree.children[0])
    def add(self,tree):
        v0 = self.visit(tree.children[0])
        v1 = self.visit(tree.children[1])
        return v0 + v1
    def mul(self,tree):
         v0 = self.visit(tree.children[0])
         v1 = self.visit(tree.children[1])
         return v0 * v1
    def sub(self, tree):
        v0 = self.visit(tree.children[0])  
        v1 = self.visit(tree.children[1]) 
        return v0-v1
    def mod(self, tree):
        v0 = self.visit(tree.children[0])  
        v1 = self.visit(tree.children[1]) 
        return v0 % v1
    def exp(self, tree):
        v0 = self.visit(tree.children[0]) 
        v1 = self.visit(tree.children[1]) 
        if v1 < 0:
            if v0 == 0:
                return 0
            return 0  
        else:
            return int(v0 ** v1)  
    def implicit_mul(self, tree):
        v0 = self.visit(tree.children[0])
        v1 = self.visit(tree.children[1])
        return v0 * v1
    def div(self, tree):
        v0 = self.visit(tree.children[0])
        v1 = self.visit(tree.children[1]) 
        return v0 / v1
    def number(self, tree):
        return int(tree.children[0].value)
    def paren(self, tree):
        return self.visit(tree.children[0])



class Simplifier(lark.Transformer):
    '''
    Compute the value of the expression.
    The lark.Transformer class processes nodes "bottom up",
    starting at the leaves and ending at the root.
    In general, the Transformer class is less powerful than the Interpreter class.
    But in the case of simple arithmetic expressions,
    both classes can be used to evaluate the expression.

    FIXME:
    This class contains all of the same test cases as the Interpreter class.
    You should fix all the failing test cases.
    You shouldn't need to make any additional modifications to the grammar beyond what was needed for the interpreter class.
    You should notice that the functions in the lark.Transformer class are simpler to implement because you do not have to manage the recursion yourself.

    >>> simplifier = Simplifier()
    >>> simplifier.transform(parser.parse("1"))
    1
    >>> simplifier.transform(parser.parse("-1"))
    -1
    >>> simplifier.transform(parser.parse("1+2"))
    3
    >>> simplifier.transform(parser.parse("1-2"))
    -1
    >>> simplifier.transform(parser.parse("(1+2)*3"))
    9
    >>> simplifier.transform(parser.parse("1+2*3"))
    7
    >>> simplifier.transform(parser.parse("1*2+3"))
    5
    >>> simplifier.transform(parser.parse("1*(2+3)"))
    5
    >>> simplifier.transform(parser.parse("(1*2)+3*4*(5-6)"))
    -10
    >>> simplifier.transform(parser.parse("((1*2)+3*4)*(5-6)"))
    -14
    >>> simplifier.transform(parser.parse("(1*(2+3)*4)*(5-6)"))
    -20
    >>> simplifier.transform(parser.parse("((1*2+(3)*4))*(5-6)"))
    -14

    Modular division:

    >>> simplifier.transform(parser.parse("1%2"))
    1
    >>> simplifier.transform(parser.parse("3%2"))
    1
    >>> simplifier.transform(parser.parse("(1+2)%3"))
    0

    Exponentiation:

    >>> simplifier.transform(parser.parse("2**1"))
    2
    >>> simplifier.transform(parser.parse("2**2"))
    4
    >>> simplifier.transform(parser.parse("2**3"))
    8
    >>> simplifier.transform(parser.parse("1+2**3"))
    9
    >>> simplifier.transform(parser.parse("(1+2)**3"))
    27
    >>> simplifier.transform(parser.parse("1+2**3+4"))
    13
    >>> simplifier.transform(parser.parse("(1+2)**(3+4)"))
    2187
    >>> simplifier.transform(parser.parse("(1+2)**3-4"))
    23

    Exponentiation with negative exponents:

    >>> simplifier.transform(parser.parse("2**-1"))
    0
    >>> simplifier.transform(parser.parse("2**(-1)"))
    0
    >>> simplifier.transform(parser.parse("(1+2)**(3-4)"))
    0
    >>> simplifier.transform(parser.parse("1+2**(3-4)"))
    1
    >>> simplifier.transform(parser.parse("1+2**(-3)*4"))
    1

    Implicit multiplication:

    >>> simplifier.transform(parser.parse("1+2(3)"))
    7
    >>> simplifier.transform(parser.parse("1(2(3))"))
    6
    >>> simplifier.transform(parser.parse("(1)(2)(3)"))
    6
    >>> simplifier.transform(parser.parse("(1)(2)+(3)"))
    5
    >>> simplifier.transform(parser.parse("(1+2)(3+4)"))
    21
    >>> simplifier.transform(parser.parse("(1+2)(3(4))"))
    36
    '''
    def start(self, children):
        return children[0]
    def add(self, children):
        return children[0] + children[1]
    def sub(self, children):
        return children[0] - children[1]
    def mul(self, children):
        return children[0] * children[1]
    def mod(self, children):
        return children[0] % children[1]
    def exp(self, children):
        base = children[0]
        exp = children[1]
        if exp < 0:
            return 0
        else:
            return base ** exp
    def div(self, children):
        return children[0] / children[1] 
    def number(self, children):
        return int(children[0].value)
    def implicit_mul(self, children):
        return children[0] * children[1]
    def paren(self, children):
        return children[0]
    def paren(self, children):
        return children[0]

#class created for minify exercise, but moved doc tests down so they would run with the minify function

class Remover_And_Stringifier(lark.Transformer):

    def start(self, children):
        return children[0]

    def mul(self, children):
        add = "+"
        sub = "-"
        if add in children[0] and add in children[1]:
            children[0] = f"({children[0]})"
            children[1] = f"({children[1]})"
        elif add in children[0]:
            children[0] = f"({children[0]})"
        elif sub in children[0]:
            children[0] = f"({children[0]})"
        elif add in children[1]:
            children[1] = f"({children[1]})"
        elif sub in children[1]:
            children[1] = f"({children[1]})"
        return f"{children[0]}*{children[1]}"

    def div(self, children):
        add = "+"
        sub = "-"
        if add in children[0]:
            children[0] = f"({children[0]})"
        elif sub in children[0]:
            children[0] = f"({children[0]})"
        elif add in children[1]:
            children[1] = f"({children[1]})"
        elif sub in children[1]:
            children[1] = f"({children[1]})"
        return f"{children[0]}/{children[1]}"

    def add(self, children):
        return f"{children[0]}+{children[1]}"

    def sub(self, children):
        return f"{children[0]}-{children[1]}"

    def paren(self, children):
        return children[0]

    def number(self, children):
        return children[0].value

def minify(expr):
    '''
    "Minifying" code is the process of removing unnecessary characters.
    In our arithmetic language, this means removing unnecessary whitespace and unnecessary parentheses.
    It is common to minify code in order to save disk space and bandwidth.
    For example, google penalizes a web site's search ranking if they don't minify their html/javascript code.

    FIXME:
    Implement this function so that the test cases below pass.

    HINT:
    My solution uses two lark.Transformer classes.
    The first one takes an AST and removes any unneeded parentheses.
    The second taks an AST and converts the AST into a string.
    You can solve this problem by calling parser.parse,
    and then applying the two transformers above to the resulting AST.

    NOTE:
    It is important that these types of "syntactic" transformations use the Transformer class and not the Interpreter class.
    If we used the Interpreter class, we could "accidentally do too much computation",
    but the Transformer class's leaf-to-root workflow prevents this class of bug.

    NOTE:
    The test cases below do not require any of the "new" features that you are required to add to the Arithmetic grammar.
    It only uses the features in the starting code.

    >>> minify("1 + 2")
    '1+2'
    >>> minify("1 + ((((2))))")
    '1+2'
    >>> minify("1 + (2*3)")
    '1+2*3'
    >>> minify("1 + (2/3)")
    '1+2/3'
    >>> minify("(1 + 2)*3")
    '(1+2)*3'
    >>> minify("(1 - 2)*3")
    '(1-2)*3'
    >>> minify("(1 - 2)+3")
    '1-2+3'
    >>> minify("(1 + 2)+(3 + 4)")
    '1+2+3+4'
    >>> minify("(1 + 2)*(3 + 4)") 
    '(1+2)*(3+4)'
    >>> minify("1 + (((2)*(3)) + 4)")
    '1+2*3+4'
    >>> minify("1 + (((2)*(3)) + 4 * ((5 + 6) - 7))")
    '1+2*3+4*(5+6-7)'
    '''

    tree = parser.parse(expr)
    return Remover_And_Stringifier().transform(tree)


def infix_to_rpn(expr):
    '''
    This function takes an expression in standard infix notation and converts it into an expression in reverse polish notation.
    This type of translation task is commonly done by first converting the input expression into an AST (i.e. by calling parser.parse),
    and then simplifying the AST in a leaf-to-root manner (i.e. using the Transformer class).

    HINT:
    If you need help understanding reverse polish notation,
    see the eval_rpn function.

    >>> infix_to_rpn('1')
    '1'
    >>> infix_to_rpn('1+2')
    '1 2 +'
    >>> infix_to_rpn('1-2')
    '1 2 -'
    >>> infix_to_rpn('(1+2)*3')
    '1 2 + 3 *'
    >>> infix_to_rpn('1+2*3')
    '1 2 3 * +'
    >>> infix_to_rpn('1*2+3')
    '1 2 * 3 +'
    >>> infix_to_rpn('1*(2+3)')
    '1 2 3 + *'
    >>> infix_to_rpn('(1*2)+3+4*(5-6)')
    '1 2 * 3 + 4 5 6 - * +'
    '''

class InfixToRPN(lark.Transformer):
    """
    This transformer converts an infix arithmetic expression to Reverse Polish Notation (RPN).
    """
    def __init__(self):
        self.output = []  
    def add(self, children):
        left, right = children
        self.output.append('+')  
    def sub(self, children):
        left, right = children
        self.output.append('-')  
    def mul(self, children):
        left, right = children
        self.output.append('*')  
    def div(self, children):
        left, right = children
        self.output.append('/') 
    def number(self, children):
        self.output.append(str(children[0]))
    def paren(self, children):
        return children[0]



def infix_to_rpn(expr):
    """
    Convert an infix expression to reverse Polish notation (RPN).
    """
    tree = parser.parse(expr)
    transformer = InfixToRPN()
    transformer.transform(tree)
    return " ".join(transformer.output)

def eval_rpn(expr):
    '''
    This function evaluates an expression written in RPN.

    RPN (Reverse Polish Notation) is an alternative syntax for arithmetic.
    It was widely used in the first scientific calculators because it is much easier to parse than standard infix notation.
    For example, parentheses are never needed to disambiguate order of operations.
    Parsing of RPN is so easy, that it is usually done at the same time as evaluation without a separate parsing phase.
    More complicated languages (like the infix language above) are basically always implemented with separate parsing/evaluation phases.

    You can find more details on wikipedia: <https://en.wikipedia.org/wiki/Reverse_Polish_notation>.

    NOTE:
    There is nothing to implement for this function,
    it is only provided as a reference for understanding the infix_to_rpn function.

    >>> eval_rpn("1")
    1
    >>> eval_rpn("1 2 +")
    3
    >>> eval_rpn("1 2 -")
    1
    >>> eval_rpn("1 2 + 3 *")
    9
    >>> eval_rpn("1 2 3 * +")
    7
    >>> eval_rpn("1 2 * 3 +")
    5
    >>> eval_rpn("1 2 3 + *")
    5
    >>> eval_rpn("1 2 * 3 + 4 5 6 - * +")
    9
    '''
    tokens = expr.split()
    stack = []
    operators = {
        '+': lambda a, b: a+b,
        '-': lambda a, b: a-b,
        '*': lambda a, b: a*b,
        '/': lambda a, b: a//b,
        }
    for token in tokens:
        if token not in operators.keys():
            stack.append(int(token))
        else:
            assert len(stack) >= 2
            v1 = stack.pop()
            v2 = stack.pop()
            stack.append(operators[token](v1, v2))
    assert len(stack) == 1
    return stack[0]


