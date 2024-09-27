from enum import Enum
import re
import json
import sys
from isa import Opcode
from isa import INPUT_PORT
from isa import OUTPUT_PORT

var_map = {}
var_type_map = {}
var_string_len_map = {}
data_ptr = 0x2
code = []


def resetAllMaps():
    global var_map, var_type_map, var_string_len_map, data_ptr, code

    var_map = {}
    var_type_map = {}
    var_string_len_map = {}
    data_ptr = 0x2
    code = []


class VarType(Enum):
    NUMBER = 'num'
    STRING = 'str'


def tokenize(chars: str) -> str:
    "Преобразовать строку символов в список токенов"
    strings = re.findall("\".*\"", chars)
    for m in strings:
        start, end = chars.find(m), chars.find(m) + len(m)
        chars = chars[: start] + chars[start: end].replace(' ', '[SPACE]') + chars[end:]
    list_chars = chars.replace('(', ' ( ').replace(')', ' ) ').split()
    for i, _ in enumerate(list_chars):
        list_chars[i] = list_chars[i].replace('[SPACE]', ' ')
    return list_chars


def parse(program: str) -> str:
    "Прочитать строку Lisp и вернуть синтаксическое дерево"
    return read_tokens(tokenize(program))


def read_tokens(tokens: str) -> list:
    "Рекурсивно читает и интерпретирует список токенов"
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF")
    token = tokens.pop(0)
    if token == '(':
        lst = []
        while tokens[0] != ')':
            lst.append(read_tokens(tokens))
        tokens.pop(0)
        return lst
    if token == ')':
        raise SyntaxError("unexpected )")
    return atomize(token)


def atomize(token: str) -> str | int:
    "Преобразовывает числовые токены в числа, иначе оставляет как строки"
    try:
        return int(token)
    except ValueError:
        return str(token)


def read_file(filename: str) -> str:
    "Считывает содержимое файла"
    with open(filename, 'r', encoding='utf-8') as f:
        return f"({f.read()})"


def create_opcode(opcode: Opcode, arg: int = None, extra_arg: bool = None):
    if extra_arg is None:
        return {"opcode": opcode.value, "arg": arg}
    return {"opcode": opcode.value, "arg": arg, "extra_arg": extra_arg}


def _pocess_operations(programm: list[str | int | list]):
    if isinstance(programm, str):

        if (programm[0] == '\'' and programm[-1] == '\'') \
            or (programm[0] == '"' and programm[-1] == '"'):

            assert len(programm) == 3, "Only 1 char in operations"
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=ord(programm[1])
            ))
        else:
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=var_map[programm]
            ))
            code.append(create_opcode(Opcode.GT))
    elif isinstance(programm, int):
        code.append(create_opcode(
            opcode=Opcode.PUSH,
            arg=programm
        ))
    else:
        process(programm)


def process_logic_operations(programm: list[str | int | list]) -> None:
    assert programm[0] in [">", "<", ">=", "<=", "/=", "="], "incorrect logic operation"

    _pocess_operations(programm[1])
    _pocess_operations(programm[2])

    if programm[0] == ">":
        code.append(create_opcode(opcode=Opcode.BGT))
    elif programm[0] == "<":
        code.append(create_opcode(opcode=Opcode.BLT))
    elif programm[0] == ">=":
        code.append(create_opcode(opcode=Opcode.BGE))
    elif programm[0] == "<=":
        code.append(create_opcode(opcode=Opcode.BLE))
    elif programm[0] == "=":
        code.append(create_opcode(opcode=Opcode.BEQ))
    elif programm[0] == "/=":
        code.append(create_opcode(opcode=Opcode.BNE))


def process_math_operations(programm: list[str | int | list]) -> None:
    assert programm[0] in ["*", "/", "+", "-"], "incorrect math operation"

    _pocess_operations(programm[1])
    _pocess_operations(programm[2])

    if programm[0] == "+":
        code.append(create_opcode(opcode=Opcode.ADD))
    elif programm[0] == "-":
        code.append(create_opcode(opcode=Opcode.SUB))
    elif programm[0] == "*":
        code.append(create_opcode(opcode=Opcode.MUL))
    elif programm[0] == "/":
        code.append(create_opcode(opcode=Opcode.DIV))


def _parse_for_define(arg: str | int | list[str | int | list]) -> list[str | int]:
    if isinstance(arg, int):
        return arg
    if isinstance(arg, str):
        if (arg[0] == '\'' and arg[-1] == '\'') or (arg[0] == '"' and arg[-1] == '"'):
            out = []
            for i in range(1, len(arg) - 1):
                out.append(arg[i])
            out.append('\0')  # Добавляем нулевой символ в конец
            return out
        return var_map[arg]
    process(arg)
    return None


def process(program: list[str | int | list] | int | str):
    global data_ptr

    if not isinstance(program, list):
        return

    command = program[0]

    if command == "define":
        assert len(program) == 3, "process error"
        assert isinstance(program[1], str), "define name must be string"
        assert not (program[1] in var_map), "define name was taken"

        code.append(create_opcode(
            opcode=Opcode.PUSH,
            arg=data_ptr
        ))
        parsed_arg = _parse_for_define(program[2])
        var_map[program[1]] = data_ptr
        var_type_map[program[1]] = VarType.NUMBER

        if isinstance(parsed_arg, int):
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=parsed_arg
            ))
            code.append(create_opcode(opcode=Opcode.LD))
            code.append(create_opcode(opcode=Opcode.POP))
            code.append(create_opcode(opcode=Opcode.POP))

            data_ptr += 1
        elif parsed_arg is None:
            code.append(create_opcode(opcode=Opcode.LD))
            code.append(create_opcode(opcode=Opcode.POP))
            code.append(create_opcode(opcode=Opcode.POP))
            data_ptr += 1

        else:
            code.pop()
            var_type_map[program[1]] = VarType.STRING
            # Сохраняем адрес нулевого терминатора
            var_string_len_map[program[1]] = data_ptr + len(parsed_arg) - 1
            for arg in parsed_arg:
                code.append(create_opcode(
                    opcode=Opcode.PUSH,
                    arg=data_ptr
                ))
                code.append(create_opcode(
                    opcode=Opcode.PUSH,
                    arg=ord(arg) if isinstance(arg, str) else arg
                ))
                code.append(create_opcode(opcode=Opcode.LD))
                code.append(create_opcode(opcode=Opcode.POP))
                code.append(create_opcode(opcode=Opcode.POP))
                data_ptr += 1

    elif command == "setq":
        assert len(program) == 3, "process error"
        assert isinstance(program[1], str), "setq name must be string"
        assert program[1] in var_map, "setq name must be set"

        if isinstance(program[2], int):
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=var_map[program[1]]
            ))
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=program[2]
            ))
        elif isinstance(program[2], str):
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=var_map[program[1]]
            ))
            if (program[2][0] == '\'' and program[2][-1] == '\'') \
                or (program[2][0] == '"' and program[2][-1] == '"'):

                assert len(program[2]) == 3, "Only 1 char in setq"
                code.append(create_opcode(
                    opcode=Opcode.PUSH,
                    arg=var_map[program[2]]
                ))
            else:
                code.append(create_opcode(
                    opcode=Opcode.PUSH,
                    arg=var_map[program[2]]
                ))
            code.append(create_opcode(opcode=Opcode.GT))
        else:
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=var_map[program[1]]
            ))
            process(program[2])
        code.append(create_opcode(opcode=Opcode.LD))
        code.append(create_opcode(opcode=Opcode.POP))
        code.append(create_opcode(opcode=Opcode.POP))

    elif command == "loop":
        cond = program[1]

        assert cond[0] in [">", "<", ">=", "<=", "/=", "="], "incorrect condition in loop"
        cond_start_ptr = len(code)
        process(cond)

        jz_ptr = len(code)
        code.append(None)
        code.append(create_opcode(opcode=Opcode.POP))

        for line in program[2]:
            process(line)
        code.append(create_opcode(
            opcode=Opcode.JUMP,
            arg=cond_start_ptr
        ))
        loop_end_ptr = len(code)

        code[jz_ptr] = create_opcode(
            opcode=Opcode.JZ,
            arg=loop_end_ptr
        )
        code.append(create_opcode(opcode=Opcode.POP))

    elif command == "cond":
        assert len(program) == 3, "process error"

        cond = program[1]

        assert cond[0] in [">", "<", ">=", "<=", "/=", "="], "incorrect condition"
        process(cond)

        jz_ptr = len(code)
        code.append(None)
        code.append(create_opcode(opcode=Opcode.POP))

        for line in program[2]:
            process(line)
        cond_end_ptr = len(code)

        code[jz_ptr] = create_opcode(
            opcode=Opcode.JZ,
            arg=cond_end_ptr
        )
        code.append(create_opcode(opcode=Opcode.POP))

    elif command == "read":
        assert len(program) == 2, "process error"
        assert isinstance(program[1], str), "must be var to read in"

        code.append(create_opcode(
            opcode=Opcode.PUSH,
            arg=var_map[program[1]]
        ))
        code.append(create_opcode(
            opcode=Opcode.PUSH,
            arg=INPUT_PORT
        ))
        code.append(create_opcode(opcode=Opcode.GT))
        code.append(create_opcode(opcode=Opcode.LD))
        code.append(create_opcode(opcode=Opcode.POP))
        code.append(create_opcode(opcode=Opcode.POP))

    elif command == "write":
        assert len(program) == 2, "process error"

        if isinstance(program[1], int):
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=OUTPUT_PORT
            ))
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=program[1]
            ))
            code.append(create_opcode(opcode=Opcode.LD))
            code.append(create_opcode(opcode=Opcode.POP))
            code.append(create_opcode(opcode=Opcode.POP))

        elif isinstance(program[1], str):
            assert program[1] in var_map, "write name must be set"
            if var_type_map.get(program[1]) == VarType.STRING:
                start_addr = var_map[program[1]]
                end_addr = var_string_len_map[program[1]]

                for addr in range(start_addr, end_addr):
                    code.append(create_opcode(
                        opcode=Opcode.PUSH,
                        arg=OUTPUT_PORT
                    ))
                    code.append(create_opcode(
                        opcode=Opcode.PUSH,
                        arg=addr
                    ))
                    code.append(create_opcode(opcode=Opcode.GT))
                    code.append(create_opcode(opcode=Opcode.LD))
                    code.append(create_opcode(opcode=Opcode.POP))
                    code.append(create_opcode(opcode=Opcode.POP))
            else:
                # Переменная является числом
                code.append(create_opcode(
                    opcode=Opcode.PUSH,
                    arg=OUTPUT_PORT
                ))
                code.append(create_opcode(
                    opcode=Opcode.PUSH,
                    arg=var_map[program[1]]
                ))
                code.append(create_opcode(opcode=Opcode.GT))
                code.append(create_opcode(opcode=Opcode.LD))
                code.append(create_opcode(opcode=Opcode.POP))
                code.append(create_opcode(opcode=Opcode.POP))

        else:
            code.append(create_opcode(
                opcode=Opcode.PUSH,
                arg=OUTPUT_PORT
            ))
            process(program[1])
            code.append(create_opcode(opcode=Opcode.LD))
            code.append(create_opcode(opcode=Opcode.POP))
            code.append(create_opcode(opcode=Opcode.POP))

    elif command in [">", "<", ">=", "<=", "/=", "="]:
        process_logic_operations(program)

    elif command in ["*", "/", "+", "-"]:
        process_math_operations(program)


def main(args):
    resetAllMaps()
    assert len(args) == 2, "Wrong args: machine.py <input_file_name> <output_file_name>"
    input_file_name, output_file_name = args
    program = read_file(input_file_name)
    parsed_program = parse(program)
    for line in parsed_program:
        process(line)
    code.append(create_opcode(opcode=Opcode.HLT))
    out = ""
    for line in code:
        out += json.dumps(line) + "\n"
    with open(output_file_name, 'w+', encoding='utf-8') as f:
        f.write(out)


if __name__ == "__main__":
    main(sys.argv[1:])
