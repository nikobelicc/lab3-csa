import contextlib
import io
import logging
import os
import tempfile

import pytest

import translator


@pytest.mark.golden_test("golden/unit/translate/*.yml")
def test_whole_by_golden(golden, caplog):
    # Установим уровень отладочного вывода на DEBUG
    caplog.set_level(logging.DEBUG)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.lsp")
        target = os.path.join(tmpdirname, "target.txt")

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])

        # Запускаем транлятор и собираем весь стандартный вывод в переменную
        # stdout
        with contextlib.redirect_stdout(io.StringIO()) as _:
            translator.main([source, target])

        # Выходные данные также считываем в переменные.
        with open(target, encoding="utf-8") as file:
            code = file.read()

        # Проверяем что ожидания соответствуют реальности.
        try:
            assert code == golden.out["code"]
        except AssertionError:
            print("code and golden out code are not the same.")
