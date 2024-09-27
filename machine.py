import logging
import json
import sys

from isa import Opcode
from isa import name2opcode
from isa import INPUT_PORT
from isa import OUTPUT_PORT


class DataPath:

    def __init__(self, data_size, stack_size, input_buffer: list[str]) -> None:

        assert data_size > 2, "data size must be > 2"
        assert stack_size > 0, "stack size must be > 0"

        self.data_size = data_size
        self.stack_size = stack_size
        self.data_address = 0
        self.stack_pointer = 0
        self.alu_out = 0
        self.input_buffer = input_buffer
        self.output_buffer = []
        self.data = [0 for _ in range(data_size)]
        self.stack = [0 for _ in range(stack_size)]

        self.input_buffer.reverse()

    def latch_data_address(self, offset: int):
        assert offset in [0, -1], "incorrect offset"
        assert self.__top_of_stack_value(offset) >= 0 and \
            self.__top_of_stack_value(offset) < self.data_size, "data out of range"
        self.data_address = self.__top_of_stack_value(offset)

    def latch_stack_pointer(self, val: int):
        assert val in [-1, 1], "incorrect value for mux"
        assert val + self.stack_pointer >= 0 and val \
            + self.stack_pointer < self.data_size, "stack ptr out of range"
        self.stack_pointer += val

    def __top_of_stack_value(self, offset: int):
        assert offset in [0, -1], "incorrect offset"
        assert self.stack_pointer + offset >= 0 and self.stack_pointer \
            + offset < self.stack_size, "stack out of range"
        return self.stack[self.stack_pointer + offset]

    def push(self, val: int = None):

        if val is not None:
            assert -2 ** 31 < val < 2 ** 31 - 1, "val overflow in stack"
            self.stack[self.stack_pointer] = val
        else:
            if self.data_address == INPUT_PORT and len(self.input_buffer) != 0:
                self.data[self.data_address] = ord(self.input_buffer.pop())
            elif self.data_address == INPUT_PORT:
                raise EOFError
            self.stack[self.stack_pointer] = self.data[self.data_address]

    def pop(self):
        top_of_stack_val = self.__top_of_stack_value(0)
        self.data[self.data_address] = top_of_stack_val
        if self.data_address == OUTPUT_PORT:
            self.output_buffer.append(top_of_stack_val)

    def input_from_port(self, port_number: int):
        if port_number == 0:
            if len(self.input_buffer) != 0:
                self.stack[self.stack_pointer] = ord(self.input_buffer.pop())
            else:
                raise EOFError("Input buffer is empty")
        else:
            raise ValueError(f"Unknown input port: {port_number}")

    def output_to_port(self, port_number: int):
        top_of_stack_val = self.__top_of_stack_value(0)
        if port_number == 0:
            self.output_buffer.append(top_of_stack_val)
        else:
            raise ValueError(f"Unknown output port: {port_number}")

    def z_flag(self) -> bool:
        return self.__top_of_stack_value(0) == 0

    def alu(self, opcode: Opcode):

        def check_overflow(value: int):
            if value > 2 ** 31 - 1 or value < - 2 ** 31:
                return (2 ** 31 - 1) & value
            return value

        assert opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV,
                          Opcode.BGT, Opcode.BLT, Opcode.BGE, Opcode.BLE,
                          Opcode.BEQ, Opcode.BNE], "wrong opcode for alu"

        if opcode == Opcode.ADD:
            self.alu_out = self.__top_of_stack_value(-1) + self.__top_of_stack_value(0)
        elif opcode == Opcode.SUB:
            self.alu_out = self.__top_of_stack_value(-1) - self.__top_of_stack_value(0)
        elif opcode == Opcode.MUL:
            self.alu_out = self.__top_of_stack_value(-1) * self.__top_of_stack_value(0)
        elif opcode == Opcode.DIV:
            self.alu_out = self.__top_of_stack_value(-1) // self.__top_of_stack_value(0)
        elif opcode == Opcode.BGT:
            self.alu_out = (self.__top_of_stack_value(-1) > self.__top_of_stack_value(0))
        elif opcode == Opcode.BLT:
            self.alu_out = (self.__top_of_stack_value(-1) < self.__top_of_stack_value(0))
        elif opcode == Opcode.BGE:
            self.alu_out = (self.__top_of_stack_value(-1) >= self.__top_of_stack_value(0))
        elif opcode == Opcode.BLE:
            self.alu_out = (self.__top_of_stack_value(-1) <= self.__top_of_stack_value(0))
        elif opcode == Opcode.BEQ:
            self.alu_out = (self.__top_of_stack_value(-1) == self.__top_of_stack_value(0))
        elif opcode == Opcode.BNE:
            self.alu_out = (self.__top_of_stack_value(-1) != self.__top_of_stack_value(0))

        self.alu_out = int(self.alu_out)
        self.alu_out = check_overflow(self.alu_out)

    def tos_debug(self):
        if self.stack_pointer != 0:
            return f"{self.__top_of_stack_value(-1)} {self.__top_of_stack_value(0)}"
        return f"null {self.__top_of_stack_value(0)}"


class ControlUnit:

    def __init__(self, program: list[map], program_size, data_path: DataPath) -> None:

        assert program_size > 0, "program size must be > 0"

        self.program = program
        self.program_size = program_size
        self.data_path = data_path
        self._tick = 0
        self.program_cnter = 0

    def __current_instruction(self) -> map:
        return self.program[self.program_cnter]

    def latch_programm_cnter(self, sel_next: bool = True):

        if sel_next:
            assert self.program_cnter + 1 < self.program_size, "programm memory out of range"
            self.program_cnter += 1
        else:
            assert "arg" in self.__current_instruction(), "internal error"
            self.program_cnter = self.__current_instruction()["arg"]

    def tick(self):
        logging.debug('%s', self)
        self._tick += 1

    def current_tick(self):
        return self._tick

    def decode_and_execute_instruction(self):
        instruction = self.__current_instruction()
        opcode: Opcode = name2opcode[instruction["opcode"]]
        arg: int | str = instruction["arg"]

        if isinstance(arg, str):
            assert len(arg) == 1, "only one char for arg"
            arg = ord(arg)

        if opcode == Opcode.HLT:
            raise StopIteration()

        if opcode == Opcode.PUSH:
            self.data_path.latch_stack_pointer(1)
            self.tick()
            self.data_path.push(arg)
            self.latch_programm_cnter()
            self.tick()
        elif opcode == Opcode.POP:
            self.data_path.latch_stack_pointer(-1)
            self.latch_programm_cnter()
            self.tick()
        elif opcode == Opcode.LD:
            self.data_path.latch_data_address(-1)
            self.tick()
            self.data_path.pop()
            self.latch_programm_cnter()
            self.tick()
        elif opcode == Opcode.GT:
            self.data_path.latch_data_address(0)
            self.tick()
            self.data_path.push()
            self.latch_programm_cnter()
            self.tick()

        elif opcode == Opcode.JUMP:
            self.latch_programm_cnter(sel_next=False)
            self.tick()
        elif opcode == Opcode.JZ:
            self.latch_programm_cnter(sel_next=not self.data_path.z_flag())
            self.tick()
        elif opcode in [Opcode.BGT, Opcode.BLT, Opcode.BGE, Opcode.BLE, Opcode.BEQ, Opcode.BNE,
                        Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV]:
            self.data_path.alu(opcode)
            self.data_path.latch_stack_pointer(-1)
            self.tick()
            self.data_path.push(self.data_path.alu_out)
            self.latch_programm_cnter()
            self.tick()

    def __repr__(self):
        state_str = "{{TICK: {}, PROGRAMM_COUNTER: {}, DATA_ADDR: {}" \
            + "Z: {}, TOS: {}, WRITE: {}, READ: {} }}"
        state = state_str.format(
            self._tick,
            self.program_cnter,
            self.data_path.data_address,
            self.data_path.z_flag(),
            self.data_path.tos_debug(),
            self.data_path.data[1],
            self.data_path.data[0],
        )

        instr = self.__current_instruction()
        opcode = instr["opcode"]
        arg = instr["arg"]
        action = "{} {}".format(opcode, arg)

        return "{} {}".format(state, action)


def simulation(code, input_buffer, program_memory_size, data_memory_size, data_stack_size, limit):

    data_path = DataPath(data_memory_size, data_stack_size, input_buffer)
    control_unit = ControlUnit(code, program_memory_size, data_path)
    instruction_counter = 0

    logging.debug("%s", control_unit)
    try:
        while True:
            assert limit > instruction_counter, "Too long execution, increase limit!"
            control_unit.decode_and_execute_instruction()
            instruction_counter += 1
    except EOFError:
        logging.warning('Input buffer is empty!')
    except StopIteration:
        pass
    logging.info('Output buffer: %s', repr(''.join(str(data_path.output_buffer))))
    return data_path.output_buffer, instruction_counter, control_unit.current_tick()


def main(args):
    assert len(args) == 2, "Wrong args: machine.py <code_file_name> <input_file_name>"
    code_file_name, input_file_name = args

    with open(code_file_name, encoding="utf-8") as file:
        input_text = file.readlines()
    program = []
    for line in input_text:
        program.append(json.loads(line))

    with open(input_file_name, encoding="utf-8") as file:
        input_file = file.read()
        input_buffer = []
        for char in input_file:
            input_buffer.append(char)

    output, instruction_counter, ticks \
        = simulation(program, input_buffer, 1000, 1000, 1000, 100000)
    print(list(map(chr, output)))
    print(output)
    print("Instruction Counter:", instruction_counter, "Ticks:", ticks)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
