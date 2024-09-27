from enum import Enum


class Opcode(Enum):
    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    DIV = 'div'
    PUSH = 'push'
    POP = 'pop'
    JUMP = 'jump'
    JZ = 'jz'
    BEQ = 'beq'
    BNE = 'bne'
    BLE = 'ble'
    BLT = 'blt'
    BGE = 'bge'
    BGT = 'bgt'
    LD = 'ld'
    GT = 'gt'
    IN = 'in'
    OUT = 'out'
    HLT = 'hlt'


name2opcode = {
    'add': Opcode.ADD,
    'sub': Opcode.SUB,
    'mul': Opcode.MUL,
    'div': Opcode.DIV,
    'ld': Opcode.LD,
    'gt': Opcode.GT,
    'jz': Opcode.JZ,
    'beq': Opcode.BEQ,
    'bne': Opcode.BNE,
    'ble': Opcode.BLE,
    'blt': Opcode.BLT,
    'bge': Opcode.BGE,
    'bgt': Opcode.BGT,
    'jump': Opcode.JUMP,
    'hlt': Opcode.HLT,
    'push': Opcode.PUSH,
    'pop': Opcode.POP,
    'in': Opcode.IN,
    'out': Opcode.OUT,
}
