from rply.token import BaseBox
from soda import bytecode
from soda.objects import SodaInt, SodaString, SodaFunction


class Node(BaseBox):
    pass


class List(Node):
    def __init__(self, item=None):
        self.items = []
        if item is not None:
            self.items.append(item)

    def append(self, item):
        self.items.append(item)

    def get(self):
        return self.items


class StatementPair(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def compile(self, compiler):
        self.left.compile(compiler)
        self.right.compile(compiler)


class ExpressionPair(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def compile(self, compiler):
        self.left.compile(compiler)
        self.right.compile(compiler)


class IdentifierPair(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.package = ""
        self.line = ""
        self.col = ""

    def compile(self, compiler):
        self.right.compile(compiler)
        self.left.compile(compiler)


class Statement(Node):
    def __init__(self, expr):
        self.expr = expr

    def compile(self, compiler):
        self.expr.compile(compiler)


class String(Node):
    def __init__(self, value, package, line, col):
        self.value = value
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        ss = SodaString(self.value)
        compiler.emit(bytecode.LOAD_CONST, compiler.register_constant(ss),
                      self.package, self.line, self.col)


class Integer(Node):
    def __init__(self, value, package, line, col):
        self.value = value
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        si = SodaInt(self.value)
        compiler.emit(bytecode.LOAD_CONST, compiler.register_constant(si),
                      self.package, self.line, self.col)


class Variable(Node):
    def __init__(self, value, package, line, col):
        self.value = value
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        compiler.emit(bytecode.LOAD_VAR,
                      compiler.variables.get(self.value, -1),
                      self.package, self.line, self.col)


class RegisterVariable(Node):
    def __init__(self, value):
        self.value = value
        self.package = ""
        self.line = ""
        self.col = ""

    def compile(self, compiler):
        compiler.emit(bytecode.STORE_VAR,
                      compiler.register_variable(self.value),
                      self.package, self.line, self.col)


class Assignment(Node):
    def __init__(self, idens, exprs, package, line, col):
        self.idens = idens
        self.exprs = exprs
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        self.exprs.compile(compiler)
        self.idens.compile(compiler)


class BinOp(Node):
    def __init__(self, operator, left, right, package, line, col):
        self.left = left
        self.right = right
        self.operator = operator
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        self.right.compile(compiler)
        self.left.compile(compiler)
        compiler.emit(bytecode.BINOP_CODE[self.operator], 0,
                      self.package, self.line, self.col)


class UnOp(Node):
    def __init__(self, operator, operand, package, line, col):
        self.operand = operand
        self.operator = operator
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        self.operand.compile(compiler)
        compiler.emit(bytecode.UNOP_CODE[self.operator], 0,
                      self.package, self.line, self.col)


class Function(Node):
    def __init__(self, name, params, body, returnstatement,
                 package, line, col):
        self.name = name
        self.params = params
        self.body = body
        self.returnstatement = returnstatement
        self.package = package
        self.line = line
        self.col = col
        self.compiler = bytecode.Compiler()

    def compile(self, compiler):
        for statement in self.body.get():
            statement.compile(self.compiler)
        self.returnstatement.compile(self.compiler)
        self.compiler.emit(bytecode.RETURN, 0,
                           self.package, self.line, self.col)
        function = SodaFunction(name=self.name, arity=len(self.params),
                                package=self.package, line=self.line,
                                col=self.col)
        compiler.register_function(function)
        self.compiler.register_function(function)


class ReturnStatement(Node):
    def __init__(self, value, package, line, col):
        self.value = value
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        self.value.compile(compiler)
        compiler.emit(bytecode.RETURN, 0,
                      self.package, self.line, self.col)


class PutStatement(Node):
    def __init__(self, expr, package, line, col):
        self.expr = expr
        self.package = package
        self.line = line
        self.col = col

    def compile(self, compiler):
        self.expr.compile(compiler)
        compiler.emit(bytecode.PUT, 0, self.package,
                      self.line, self.col)
