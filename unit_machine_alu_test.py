import contextlib
import io
import logging
import tempfile

import pytest

import machine
from isa import name2opcode


@pytest.mark.golden_test("golden/unit/machine/*.yml")
def test_whole_by_golden(golden, caplog):
    # Установим уровень отладочного вывода на DEBUG
    caplog.set_level(logging.DEBUG)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory():
        with contextlib.redirect_stdout(io.StringIO()):
            data_path = machine.DataPath(100, 100, [])
            data_path.push(int(golden["a"]))
            data_path.latch_stack_pointer(1)
            data_path.push(int(golden["b"]))
            data_path.alu(name2opcode[golden["operation"].replace('\n', '')])
            a = data_path.alu_out

        # Проверяем что ожидания соответствуют реальности.
        assert a == int(golden["result"])
