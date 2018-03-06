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
    pc = 0
    while pc < len(bc.code):
        driver.jit_merge_point(pc=pc, code=code, bc=bc, frame=frame)
        c = code[pc]
        arg = code[pc + 1]
        pc += 2
        if c == bytecode.LOAD_CONST:
            const = bc.constants[arg]
            frame.push(const)
        elif c == bytecode.ADD:
            right = frame.pop()
            left = frame.pop()
            result = left.add(right)
            frame.push(result)
        elif c == bytecode.SUB:
            right = frame.pop()
            left = frame.pop()
            result = right.sub(left)
            frame.push(result)
        elif c == bytecode.MUL:
            right = frame.pop()
            left = frame.pop()
            result = left.mul(right)
            frame.push(result)
        elif c == bytecode.DIV:
            right = frame.pop()
            left = frame.pop()
            result = right.div(left)
            frame.push(result)
        elif c == bytecode.MOD:
            right = frame.pop()
            left = frame.pop()
            result = right.mod(left)
            frame.push(result)
        elif c == bytecode.POW:
            right = frame.pop()
            left = frame.pop()
            result = right.pow(left)
            frame.push(result)
        elif c == bytecode.EQ:
            right = frame.pop()
            left = frame.pop()
            result = right.eq(left)
            frame.push(result)
        elif c == bytecode.NEQ:
            right = frame.pop()
            left = frame.pop()
            result = right.neq(left)
            frame.push(result)
        elif c == bytecode.GRE:
            right = frame.pop()
            left = frame.pop()
            result = right.gre(left)
            frame.push(result)
        elif c == bytecode.LES:
            right = frame.pop()
            left = frame.pop()
            result = right.les(left)
            frame.push(result)
        elif c == bytecode.GEQ:
            right = frame.pop()
            left = frame.pop()
            result = right.geq(left)
            frame.push(result)
        elif c == bytecode.LEQ:
            right = frame.pop()
            left = frame.pop()
            result = right.leq(left)
            frame.push(result)
        elif c == bytecode.AND:
            right = frame.pop()
            left = frame.pop()
            result = right.land(left)
            frame.push(result)
        elif c == bytecode.OR:
            right = frame.pop()
            left = frame.pop()
            result = right.lor(left)
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
