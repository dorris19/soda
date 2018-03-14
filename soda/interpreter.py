from soda import bytecode
from soda.errors import sodaError
from rpython.rlib import jit
import os

driver = jit.JitDriver(greens=["pc", "code", "bc"],
                       reds=["frame"],
                       is_recursive=True)


class Frame(object):
    def __init__(self, bc):
        self.valuestack = [None] * len(bc.code)
        self.valuestack_pos = 0

    def push(self, value):
        pos = jit.hint(self.valuestack_pos, promote=True)
        assert pos >= 0
        self.valuestack[pos] = value
        self.valuestack_pos = pos + 1

    def pop(self):
        pos = jit.hint(self.valuestack_pos, promote=True)
        new_pos = pos - 1
        assert new_pos >= 0
        value = self.valuestack[new_pos]
        self.valuestack_pos = new_pos
        return value


def run(frame, bc):
    code = bc.code
    positions = bc.positions
    pc = 0
    posc = 0
    while pc < len(bc.code):
        driver.jit_merge_point(pc=pc, code=code, bc=bc, frame=frame)
        c = code[pc]
        arg = code[pc + 1]
        package = positions[posc]
        line = positions[posc + 1]
        col = positions[posc + 2]
        posc += 3
        pc += 2
        if c == bytecode.LOAD_CONST:
            const = bc.constants[arg]
            frame.push(const)
        elif c == bytecode.NEG:
            operand = frame.pop()
            if not operand.isint():
                try:
                    operand = operand.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot negate non-integer string")
            result = operand.neg()
            frame.push(result)
        elif c == bytecode.ADD:
            right = frame.pop()
            left = frame.pop()
            if not right.isint():
                try:
                    right = right.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot add non-integer strings")
            if not left.isint():
                try:
                    left = left.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot add non-integer strings")
            result = right.add(left)
            frame.push(result)
        elif c == bytecode.CONCAT:
            right = frame.pop()
            left = frame.pop()
            if not left.isstr():
                left = left.tostr()
            if not right.isstr():
                right = right.tostr()
            result = right.concat(left)
            frame.push(result)
        elif c == bytecode.DIFF:
            right = frame.pop()
            left = frame.pop()
            if not left.isstr():
                left = left.tostr()
            if not right.isstr():
                right = right.tostr()
            result = right.diff(left)
            frame.push(result)
        elif c == bytecode.SUB:
            right = frame.pop()
            left = frame.pop()
            if not right.isint():
                try:
                    right = right.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot subtract non-integer strings")
            if not left.isint():
                try:
                    left = left.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot subtract non-integer strings")
            result = right.sub(left)
            frame.push(result)
        elif c == bytecode.MUL:
            right = frame.pop()
            left = frame.pop()
            if not right.isint():
                try:
                    right = right.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot multiply non-integer strings")
            if not left.isint():
                try:
                    left = left.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot multiply non-integer strings")
            result = right.mul(left)
            frame.push(result)
        elif c == bytecode.DIV:
            right = frame.pop()
            left = frame.pop()
            if not right.isint():
                try:
                    right = right.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot divide non-integer strings")
            if not left.isint():
                try:
                    left = left.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot divide non-integer strings")
            try:
                result = right.div(left)
            except ZeroDivisionError:
                sodaError(package, line, col,
                          "cannot divide by zero")
                break
            frame.push(result)
        elif c == bytecode.MOD:
            right = frame.pop()
            left = frame.pop()
            if not right.isint():
                try:
                    right = right.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot modulo non-integer strings")
            if not left.isint():
                try:
                    left = left.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot modulo non-integer strings")
            try:
                result = right.mod(left)
            except ZeroDivisionError:
                sodaError(package, line, col,
                          "cannot modulo by zero")
                break
            frame.push(result)
        elif c == bytecode.POW:
            right = frame.pop()
            left = frame.pop()
            if not right.isint():
                try:
                    right = right.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot exponentiate non-integer strings")
            if not left.isint():
                try:
                    left = left.toint()
                except Exception:
                    sodaError(package, line, col,
                              "cannot exponentiate non-integer strings")
            try:
                result = right.pow(left)
            except ValueError:
                sodaError(package, line, col,
                          "cannot exponentiate by a negative integer")
                break
            frame.push(result)
        elif c == bytecode.EQ:
            right = frame.pop()
            left = frame.pop()
            if left.isstr() and right.isstr() or left.isint()\
               and right.isint():
                result = right.eq(left)
                frame.push(result)
                continue
            try:
                right = right.toint()
                left = left.toint()
                result = right.eq(left)
                frame.push(result)
                continue
            except Exception:
                right = right.tostr()
                left = left.tostr()
                result = right.eq(left)
                frame.push(result)
                continue
        elif c == bytecode.NE:
            right = frame.pop()
            left = frame.pop()
            if left.isstr() and right.isstr() or left.isint()\
               and right.isint():
                result = right.ne(left)
                frame.push(result)
                continue
            try:
                right = right.toint()
                left = left.toint()
                result = right.ne(left)
                frame.push(result)
                continue
            except Exception:
                right = right.tostr()
                left = left.tostr()
                result = right.ne(left)
                frame.push(result)
                continue
        elif c == bytecode.GT:
            right = frame.pop()
            left = frame.pop()
            if left.isstr() and right.isstr() or left.isint()\
               and right.isint():
                result = right.gt(left)
                frame.push(result)
                continue
            try:
                right = right.toint()
                left = left.toint()
                result = right.gt(left)
                frame.push(result)
                continue
            except Exception:
                right = right.tostr()
                left = left.tostr()
                result = right.gt(left)
                frame.push(result)
                continue
        elif c == bytecode.LT:
            right = frame.pop()
            left = frame.pop()
            if left.isstr() and right.isstr() or left.isint()\
               and right.isint():
                result = right.lt(left)
                frame.push(result)
                continue
            try:
                right = right.toint()
                left = left.toint()
                result = right.lt(left)
                frame.push(result)
                continue
            except Exception:
                right = right.tostr()
                left = left.tostr()
                result = right.lt(left)
                frame.push(result)
                continue
        elif c == bytecode.GE:
            right = frame.pop()
            left = frame.pop()
            if left.isstr() and right.isstr() or left.isint()\
               and right.isint():
                result = right.ge(left)
                frame.push(result)
                continue
            try:
                right = right.toint()
                left = left.toint()
                result = right.ge(left)
                frame.push(result)
                continue
            except Exception:
                right = right.tostr()
                left = left.tostr()
                result = right.ge(left)
                frame.push(result)
                continue
        elif c == bytecode.LE:
            right = frame.pop()
            left = frame.pop()
            if left.isstr() and right.isstr() or left.isint()\
               and right.isint():
                result = right.le(left)
                frame.push(result)
                continue
            try:
                right = right.toint()
                left = left.toint()
                result = right.le(left)
                frame.push(result)
                continue
            except Exception:
                right = right.tostr()
                left = left.tostr()
                result = right.le(left)
                frame.push(result)
                continue
        elif c == bytecode.AND:
            right = frame.pop()
            left = frame.pop()
            if not left.isstr():
                left = left.tostr()
            if not right.isstr():
                right = right.tostr()
            result = right.land(left)
            frame.push(result)
        elif c == bytecode.OR:
            right = frame.pop()
            left = frame.pop()
            if not left.isstr():
                left = left.tostr()
            if not right.isstr():
                right = right.tostr()
            result = right.lor(left)
            frame.push(result)
        elif c == bytecode.NOT:
            operand = frame.pop()
            if not operand.isstr():
                operand = operand.tostr()
            result = operand.lnot()
            frame.push(result)
        elif c == bytecode.PUT:
            output = frame.pop().str()
            os.write(1, output)
        else:
            sodaError("test", "-1", "-1", "unrecognized bytecode %s" % c)


def interpret(bc):
    frame = Frame(bc)
    run(frame, bc)
    return 0
