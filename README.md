# Архитектура компьютера. Лабораторная работа 3

- Антонов Никита Сергеевич, гр. P3216
- `lisp | stack | harv | hw | tick | struct | stream | port | cstr | prob1`
- без усложнения

## Язык программирования

``` ebnf
<program>         ::= <S_expression>

<S_expression>    ::= "(" <Operation> ")"

<Operation>       ::= <A0>  " " + <symbol>
                  |   <A0+> " " + <Argument>
                  |   <A1>  " " + <Argument> " " + <Argument>
                  |   <A1+> " " + <S_expression> " (" + <Arguments> + ")"

<A0>              ::= "read"

<A0+>             ::= "write"

<A1>              ::= "define" | "setq"
                  | "+" | "-" | "*" | "/" |
                  | "<" | ">" | "<=" | ">=" | "=" | "/="

<A1+>             ::= "loop" | "cond"

<Arguments>       ::= <Argument>
                  |   <Argument> <Arguments>

<Argument>        ::= <Atom>
                  |   <S_expression>

<Atom>            ::= <symbol>
                  |   <number>
                  |   <char>
                  |   <string>

<symbol>          ::= [a-zA-Z]+

<number>          ::= [-2^31; 2^31 - 1]

<char>            ::= "."
                  |   '.'

<string>          ::= '.*'
                  |   ".*"
```

Операции могут иметь один или два аргумента, а также более двух аргументов.
Поддерживаемые аргументы:
- атомарные:
  - symbol - имя переменной
  - number - числовое значение переменной
  - char   - символьное значение переменной
  - string - строковое значение переменной
- выражение - результат сначала вычисляется, а потом уже выполняются последующие действия над ним

Операции:
- `define <name> <arg>` -- объявление переменной с именем `name` со значением `arg`
- `setq <name> <arg>` -- переопределение значения переменной с именем `name` на значение `arg`, причем присвоить новое значение можно только числовым переменным
- `+ <arg1> <arg2>` -- функция прибавления `arg2` к `arg1` с возвратом результата
- `- <arg1> <arg2>` -- функция вычитания `arg2` из `arg1` с возвратом результата
- `* <arg1> <arg2>` -- умножение `arg2` с `arg1` с возвратом результата
- `/ <arg1> <arg2>` -- целочисленное деление `arg1` на `arg2` с возвратом результата
- `< <arg1> <arg2>` -- булевый результат сравнения `arg1` `<` `arg2`
- `> <arg1> <arg2>` -- булевый результат сравнения `arg1` `>` `arg2`
- `<= <arg1> <arg2>` -- булевый результат сравнения `arg1` `<=` `arg2`
- `>= <arg1> <arg2>` -- булевый результат сравнения `arg1` `>=` `arg2`
- `= <arg1> <arg2>` -- булевый результат сравнения `arg1` `=` `arg2`
- `/= <arg1> <arg2>` -- булевый результат сравнения `arg1` `/=` `arg2`
- `loop <condition> <operations>` -- цикл, в котором проверяется `condition`, если оно истинно, выполняются `operations`, если нет, происходит переход к следующей операции
                                      после выполнения всех операций, снова проверяется условие, снова выполняются `operations` и т д
- `cond <condition> <operations>` -- проверяется `condition`, если оно истинно, выполняются `operations`, если нет, происходит переход к следующей операции
- `read  <arg>` -- чтение символа из стандартного потока ввода в переменную  `arg`
- `write <arg>` -- печать `arg` в стандартный поток вывода


## Организация памяти

- Есть возможность объявления переменных при помощи операции `define`
- Есть возможность переопределения значения числовых переменных при помощи операции `setq`

Модель памяти процессора:

- Память команд. Машинное слово -- не определено. Реализуется списком словарей, описывающих инструкции (одно слово -- одна ячейка).
- Память данных. Машинное слово -- 32 бит, знаковое. Реализуется списком чисел.

Типы адресации:

- Непосредственная загрузка: операндом является константа, подаваемая как один из аргументов.


## Система команд

Особенности процессора:

- Машинное слово -- 32 бита, знаковое.
- Память данных:
    - доступ к памяти данных только через команды `ld` и `gt`;
    Для `ld`:
      * на шину данных для записи подается самое верхнее значение стека;
      * на шину адреса подается адрес, который расположен на следующей ячейки после верхней стека;
    Для `st`:
      * адрес берется из вершины стека, значение по этому адресу записывается в вершину стека; 
- АЛУ:
    - Правый вход - вершина стека, левый - следующая после вершины
    - АЛУ поддерживает операции: `add`, `sub`, `mul`, `div`, вывод правого входа;
- Стек:
    Вершина стека имеет 2 ячейки для алу и различных команд
- Регистры:
    - регистр аккумулятора `data_addr`:
      - адрес в памяти данных
    - регистр счетчика команд `program_cnter`:
      - адрес текущей команды
    - регистр адреса `stack_pointer`:
      - адрес текущей вершины стека
- Ввод-вывод:
    - port-mapped через 2 порта, отображенных в память данных: input_port, output_port

    
### Набор инструкций

Набор инструкций создается при транслировании языка Lisp.

* `add`  - 2 такта
* `sub`  - 2 такта
* `mul`  - 2 такта
* `div`  - 2 такта
* `ld`   - 2 такта
* `gt`   - 2 такта
* `jz`   - 1 такта
* `beq`  - 2 такта
* `bne`  - 2 такта
* `ble`  - 2 такта
* `blt`  - 2 такта
* `bge`  - 2 такта
* `bgt`  - 2 такта
* `jump` - 1 такт
* `hlt`  - 0 тактов
* `push` - 2 такта
* `pop`  - 1 такт

### Кодирование инструкций

- Код Lisp сериализуется в инструкции из памяти команд, которые записаны в словарь JSON
```

    {"opcode": "push", "arg": 2}
    {"opcode": "push", "arg": 0}
    {"opcode": "ld", "arg": null}
    {"opcode": "pop", "arg": null}
    {"opcode": "pop", "arg": null}
    {"opcode": "push", "arg": 3}
    {"opcode": "push", "arg": 0}
    {"opcode": "ld", "arg": null}
    {"opcode": "pop", "arg": null}
    {"opcode": "pop", "arg": null}
    {"opcode": "push", "arg": 3}
    {"opcode": "gt", "arg": null}
    {"opcode": "push", "arg": 4}
    
    ...

```

где:

- opcode -- строка с кодом операции;
- arg (optional) -- аргумент команды;

Типы данных в модуле isa, где:
- Opcode -- перечисление кодов операций;


## Транслятор

Интерфейс командной строки: `translator.py <input_file> <target_file>`

Реализовано в модуле: [translator](./translator.py)

Этапы трансляции (функция `translate`):

1. Токенизация текста.
2. Формирование AST-дерева.
3. Генерация машинного кода.

Правила генерации машинного кода:

- одна инструкция процессора -- одна инструкция в коде;
- в конце генерации автоматически добавляется инструкция `halt`

## Модель процессора

Реализовано в модуле: [machine](./machine.py).

### Схема DataPath и ControlUnit

![/images/scheme.png](/images/control_unit.png "Схема ControlUnit") 
![/images/scheme.png](/images/data_path.png "Схема DataPath") 

## DataPath

Реализован в классе `DataPath`.

- `data_memory` -- однопортовая, поэтому либо читаем, либо пишем.
- `data_stack` -- стек
- `top_of_stack` -- две верхние ячейки стека.
- `alu` -- АЛУ, выполняющее арифметические операции.

Флаги:
- `zero` -- отражает наличие нулевого значения на вершине стека. Используется для условных переходов.

## ControlUnit
Реализован в классе `ControlUnit`.

Особенности работы модели:

- Для журнала состояний процессора используется стандартный модуль logging.
- Количество инструкций для моделирования ограничено hardcoded константой.
- Остановка моделирования осуществляется при помощи исключений:
    - `EOFError` -- если нет данных для чтения из порта ввода-вывода;
    - `StopIteration` -- если выполнена инструкция `halt`.
- Управление симуляцией реализовано в функции `simulation`.


## Апробация

В качестве тестов использовано четыре алгоритма:

1. hello world
2. cat
3. hello username
4. prob1

Юнит-тесты реализованы тут:
[unit_translate_test](unit_translate_test.py)
[unit_machine_alu_test](unit_machine_alu_test.py)

Интеграционные тесты реализованы тут:
[integration_test](integration_test.py)

Тестирование через golden test:
- Конфигурация юнит-тестов лежит в папке [golden/unit](golden/unit)
- Конфигурация интеграционных тестов лежит в папке [golden/integration](golden/integration)

CI:
```yaml
name: lab3-csa-test

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install coverage pytest pytest-golden

      - name: Run tests with coverage
        run: |
          coverage run -m pytest --verbose --update-goldens
          find . -type f -name "*.py" | xargs -t coverage report
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install linters and pytest
        run: |
          pip install pycodestyle pylint pytest

      - name: Run pycodestyle
        run: |
          find . -type f -name "*.py" | xargs -t pycodestyle --ignore=E501,E125

      - name: Run pylint
        run: |
          find . -type f -name "*.py" | xargs -t pylint --disable C0114,C0116,W0603,R0912,R0915,C0115,R0801,C0103,R0902,W1203,C0209,R0913
```
где:

- `coverage` -- формирование отчёта об уровне покрытия исходного кода.
- `pytest` -- утилита для запуска тестов.
- `pycodestyle` -- утилита для проверки форматирования кода. `E501` (длина строк) `E125` (логические повторения след строки) отключено.
- `pylint` -- утилита для проверки качества кода. Некоторые правила отключены в отдельных модулях с целью упрощения кода.

Пример использования и журнал работы процессора на примере `cat`:

```
  {"opcode": "push", "arg": 2}
  {"opcode": "push", "arg": 0}
  {"opcode": "ld", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "push", "arg": 3}
  {"opcode": "push", "arg": 0}
  {"opcode": "ld", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "push", "arg": 3}
  {"opcode": "gt", "arg": null}
  {"opcode": "push", "arg": 4}
  {"opcode": "blt", "arg": null}
  {"opcode": "jz", "arg": 37}
  {"opcode": "pop", "arg": null}
  {"opcode": "push", "arg": 2}
  {"opcode": "push", "arg": 0}
  {"opcode": "gt", "arg": null}
  {"opcode": "ld", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "push", "arg": 1}
  {"opcode": "push", "arg": 2}
  {"opcode": "gt", "arg": null}
  {"opcode": "ld", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "push", "arg": 3}
  {"opcode": "push", "arg": 3}
  {"opcode": "gt", "arg": null}
  {"opcode": "push", "arg": 1}
  {"opcode": "add", "arg": null}
  {"opcode": "ld", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "pop", "arg": null}
  {"opcode": "jump", "arg": 10}
  {"opcode": "pop", "arg": null}
  {"opcode": "hlt", "arg": null}


  DEBUG    root:machine.py:248 {TICK: 0, PROGRAMM_COUNTER: 0, DATA_ADDR: 0Z: True, TOS: null 0, WRITE: 0, READ: 0 } push 2
  DEBUG    root:machine.py:152 {TICK: 0, PROGRAMM_COUNTER: 0, DATA_ADDR: 0Z: True, TOS: 0 0, WRITE: 0, READ: 0 } push 2
  DEBUG    root:machine.py:152 {TICK: 1, PROGRAMM_COUNTER: 1, DATA_ADDR: 0Z: False, TOS: 0 2, WRITE: 0, READ: 0 } push 0
  DEBUG    root:machine.py:152 {TICK: 2, PROGRAMM_COUNTER: 1, DATA_ADDR: 0Z: True, TOS: 2 0, WRITE: 0, READ: 0 } push 0
  DEBUG    root:machine.py:152 {TICK: 3, PROGRAMM_COUNTER: 2, DATA_ADDR: 0Z: True, TOS: 2 0, WRITE: 0, READ: 0 } ld None
  DEBUG    root:machine.py:152 {TICK: 4, PROGRAMM_COUNTER: 2, DATA_ADDR: 2Z: True, TOS: 2 0, WRITE: 0, READ: 0 } ld None
  DEBUG    root:machine.py:152 {TICK: 5, PROGRAMM_COUNTER: 3, DATA_ADDR: 2Z: True, TOS: 2 0, WRITE: 0, READ: 0 } pop None
  DEBUG    root:machine.py:152 {TICK: 6, PROGRAMM_COUNTER: 4, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 0, READ: 0 } pop None
  DEBUG    root:machine.py:152 {TICK: 7, PROGRAMM_COUNTER: 5, DATA_ADDR: 2Z: True, TOS: null 0, WRITE: 0, READ: 0 } push 3
  DEBUG    root:machine.py:152 {TICK: 8, PROGRAMM_COUNTER: 5, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 0, READ: 0 } push 3
  DEBUG    root:machine.py:152 {TICK: 9, PROGRAMM_COUNTER: 6, DATA_ADDR: 2Z: False, TOS: 0 3, WRITE: 0, READ: 0 } push 0
  DEBUG    root:machine.py:152 {TICK: 10, PROGRAMM_COUNTER: 6, DATA_ADDR: 2Z: True, TOS: 3 0, WRITE: 0, READ: 0 } push 0
  DEBUG    root:machine.py:152 {TICK: 11, PROGRAMM_COUNTER: 7, DATA_ADDR: 2Z: True, TOS: 3 0, WRITE: 0, READ: 0 } ld None
  DEBUG    root:machine.py:152 {TICK: 12, PROGRAMM_COUNTER: 7, DATA_ADDR: 3Z: True, TOS: 3 0, WRITE: 0, READ: 0 } ld None
  DEBUG    root:machine.py:152 {TICK: 13, PROGRAMM_COUNTER: 8, DATA_ADDR: 3Z: True, TOS: 3 0, WRITE: 0, READ: 0 } pop None
  DEBUG    root:machine.py:152 {TICK: 14, PROGRAMM_COUNTER: 9, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 0, READ: 0 } pop None
  DEBUG    root:machine.py:152 {TICK: 15, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 0, READ: 0 } push 3
  DEBUG    root:machine.py:152 {TICK: 16, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 0, READ: 0 } push 3
  DEBUG    root:machine.py:152 {TICK: 17, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 0, READ: 0 } gt None
  DEBUG    root:machine.py:152 {TICK: 18, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 0, READ: 0 } gt None
  DEBUG    root:machine.py:152 {TICK: 19, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: True, TOS: 0 0, WRITE: 0, READ: 0 } push 4
  DEBUG    root:machine.py:152 {TICK: 20, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: True, TOS: 0 0, WRITE: 0, READ: 0 } push 4
  DEBUG    root:machine.py:152 {TICK: 21, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 0 4, WRITE: 0, READ: 0 } blt None
  DEBUG    root:machine.py:152 {TICK: 22, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: True, TOS: 0 0, WRITE: 0, READ: 0 } blt None
  DEBUG    root:machine.py:152 {TICK: 23, PROGRAMM_COUNTER: 14, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 0, READ: 0 } jz 37
  DEBUG    root:machine.py:152 {TICK: 24, PROGRAMM_COUNTER: 15, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 0, READ: 0 } pop None
  DEBUG    root:machine.py:152 {TICK: 25, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 0, READ: 0 } push 2
  DEBUG    root:machine.py:152 {TICK: 26, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 0, READ: 0 } push 2
  DEBUG    root:machine.py:152 {TICK: 27, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 0 2, WRITE: 0, READ: 0 } push 0
  DEBUG    root:machine.py:152 {TICK: 28, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 2 4, WRITE: 0, READ: 0 } push 0
  DEBUG    root:machine.py:152 {TICK: 29, PROGRAMM_COUNTER: 18, DATA_ADDR: 3Z: True, TOS: 2 0, WRITE: 0, READ: 0 } gt None
  DEBUG    root:machine.py:152 {TICK: 30, PROGRAMM_COUNTER: 18, DATA_ADDR: 0Z: True, TOS: 2 0, WRITE: 0, READ: 0 } gt None
  DEBUG    root:machine.py:152 {TICK: 31, PROGRAMM_COUNTER: 19, DATA_ADDR: 0Z: False, TOS: 2 110, WRITE: 0, READ: 110 } ld None
  DEBUG    root:machine.py:152 {TICK: 32, PROGRAMM_COUNTER: 19, DATA_ADDR: 2Z: False, TOS: 2 110, WRITE: 0, READ: 110 } ld None
  DEBUG    root:machine.py:152 {TICK: 33, PROGRAMM_COUNTER: 20, DATA_ADDR: 2Z: False, TOS: 2 110, WRITE: 0, READ: 110 } pop None
  DEBUG    root:machine.py:152 {TICK: 34, PROGRAMM_COUNTER: 21, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 0, READ: 110 } pop None
  DEBUG    root:machine.py:152 {TICK: 35, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: True, TOS: null 0, WRITE: 0, READ: 110 } push 1
  DEBUG    root:machine.py:152 {TICK: 36, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 0, READ: 110 } push 1
  DEBUG    root:machine.py:152 {TICK: 37, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 0 1, WRITE: 0, READ: 110 } push 2
  DEBUG    root:machine.py:152 {TICK: 38, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 1 110, WRITE: 0, READ: 110 } push 2
  DEBUG    root:machine.py:152 {TICK: 39, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 0, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 40, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 0, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 41, PROGRAMM_COUNTER: 25, DATA_ADDR: 2Z: False, TOS: 1 110, WRITE: 0, READ: 110 } ld None
  DEBUG    root:machine.py:152 {TICK: 42, PROGRAMM_COUNTER: 25, DATA_ADDR: 1Z: False, TOS: 1 110, WRITE: 0, READ: 110 } ld None
  DEBUG    root:machine.py:152 {TICK: 43, PROGRAMM_COUNTER: 26, DATA_ADDR: 1Z: False, TOS: 1 110, WRITE: 110, READ: 110 } pop None
  DEBUG    root:machine.py:152 {TICK: 44, PROGRAMM_COUNTER: 27, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 110, READ: 110 } pop None
  DEBUG    root:machine.py:152 {TICK: 45, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: True, TOS: null 0, WRITE: 110, READ: 110 } push 3
  DEBUG    root:machine.py:152 {TICK: 46, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 110, READ: 110 } push 3
  DEBUG    root:machine.py:152 {TICK: 47, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 0 3, WRITE: 110, READ: 110 } push 3
  DEBUG    root:machine.py:152 {TICK: 48, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 3 110, WRITE: 110, READ: 110 } push 3
  DEBUG    root:machine.py:152 {TICK: 49, PROGRAMM_COUNTER: 30, DATA_ADDR: 1Z: False, TOS: 3 3, WRITE: 110, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 50, PROGRAMM_COUNTER: 30, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 110, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 51, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: True, TOS: 3 0, WRITE: 110, READ: 110 } push 1
  DEBUG    root:machine.py:152 {TICK: 52, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: True, TOS: 0 0, WRITE: 110, READ: 110 } push 1
  DEBUG    root:machine.py:152 {TICK: 53, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 110, READ: 110 } add None
  DEBUG    root:machine.py:152 {TICK: 54, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: True, TOS: 3 0, WRITE: 110, READ: 110 } add None
  DEBUG    root:machine.py:152 {TICK: 55, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 1, WRITE: 110, READ: 110 } ld None
  DEBUG    root:machine.py:152 {TICK: 56, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 1, WRITE: 110, READ: 110 } ld None
  DEBUG    root:machine.py:152 {TICK: 57, PROGRAMM_COUNTER: 34, DATA_ADDR: 3Z: False, TOS: 3 1, WRITE: 110, READ: 110 } pop None
  DEBUG    root:machine.py:152 {TICK: 58, PROGRAMM_COUNTER: 35, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 110, READ: 110 } pop None
  DEBUG    root:machine.py:152 {TICK: 59, PROGRAMM_COUNTER: 36, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 110, READ: 110 } jump 10
  DEBUG    root:machine.py:152 {TICK: 60, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 110, READ: 110 } push 3
  DEBUG    root:machine.py:152 {TICK: 61, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 110, READ: 110 } push 3
  DEBUG    root:machine.py:152 {TICK: 62, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 110, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 63, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 110, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 64, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 110, READ: 110 } push 4
  DEBUG    root:machine.py:152 {TICK: 65, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 1 1, WRITE: 110, READ: 110 } push 4
  DEBUG    root:machine.py:152 {TICK: 66, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 1 4, WRITE: 110, READ: 110 } blt None
  DEBUG    root:machine.py:152 {TICK: 67, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 110, READ: 110 } blt None
  DEBUG    root:machine.py:152 {TICK: 68, PROGRAMM_COUNTER: 14, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 110, READ: 110 } jz 37
  DEBUG    root:machine.py:152 {TICK: 69, PROGRAMM_COUNTER: 15, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 110, READ: 110 } pop None
  DEBUG    root:machine.py:152 {TICK: 70, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 110, READ: 110 } push 2
  DEBUG    root:machine.py:152 {TICK: 71, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 110, READ: 110 } push 2
  DEBUG    root:machine.py:152 {TICK: 72, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 0 2, WRITE: 110, READ: 110 } push 0
  DEBUG    root:machine.py:152 {TICK: 73, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 2 4, WRITE: 110, READ: 110 } push 0
  DEBUG    root:machine.py:152 {TICK: 74, PROGRAMM_COUNTER: 18, DATA_ADDR: 3Z: True, TOS: 2 0, WRITE: 110, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 75, PROGRAMM_COUNTER: 18, DATA_ADDR: 0Z: True, TOS: 2 0, WRITE: 110, READ: 110 } gt None
  DEBUG    root:machine.py:152 {TICK: 76, PROGRAMM_COUNTER: 19, DATA_ADDR: 0Z: False, TOS: 2 105, WRITE: 110, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 77, PROGRAMM_COUNTER: 19, DATA_ADDR: 2Z: False, TOS: 2 105, WRITE: 110, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 78, PROGRAMM_COUNTER: 20, DATA_ADDR: 2Z: False, TOS: 2 105, WRITE: 110, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 79, PROGRAMM_COUNTER: 21, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 110, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 80, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: True, TOS: null 0, WRITE: 110, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 81, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 110, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 82, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 0 1, WRITE: 110, READ: 105 } push 2
  DEBUG    root:machine.py:152 {TICK: 83, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 1 105, WRITE: 110, READ: 105 } push 2
  DEBUG    root:machine.py:152 {TICK: 84, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 110, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 85, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 110, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 86, PROGRAMM_COUNTER: 25, DATA_ADDR: 2Z: False, TOS: 1 105, WRITE: 110, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 87, PROGRAMM_COUNTER: 25, DATA_ADDR: 1Z: False, TOS: 1 105, WRITE: 110, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 88, PROGRAMM_COUNTER: 26, DATA_ADDR: 1Z: False, TOS: 1 105, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 89, PROGRAMM_COUNTER: 27, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 90, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: True, TOS: null 0, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 91, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 92, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 0 3, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 93, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 3 105, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 94, PROGRAMM_COUNTER: 30, DATA_ADDR: 1Z: False, TOS: 3 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 95, PROGRAMM_COUNTER: 30, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 96, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: False, TOS: 3 1, WRITE: 105, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 97, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: False, TOS: 1 1, WRITE: 105, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 98, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: False, TOS: 1 1, WRITE: 105, READ: 105 } add None
  DEBUG    root:machine.py:152 {TICK: 99, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: False, TOS: 3 1, WRITE: 105, READ: 105 } add None
  DEBUG    root:machine.py:152 {TICK: 100, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 2, WRITE: 105, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 101, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 2, WRITE: 105, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 102, PROGRAMM_COUNTER: 34, DATA_ADDR: 3Z: False, TOS: 3 2, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 103, PROGRAMM_COUNTER: 35, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 104, PROGRAMM_COUNTER: 36, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 105, READ: 105 } jump 10
  DEBUG    root:machine.py:152 {TICK: 105, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 106, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 107, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 108, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 109, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 0 2, WRITE: 105, READ: 105 } push 4
  DEBUG    root:machine.py:152 {TICK: 110, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 2 2, WRITE: 105, READ: 105 } push 4
  DEBUG    root:machine.py:152 {TICK: 111, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 2 4, WRITE: 105, READ: 105 } blt None
  DEBUG    root:machine.py:152 {TICK: 112, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 0 2, WRITE: 105, READ: 105 } blt None
  DEBUG    root:machine.py:152 {TICK: 113, PROGRAMM_COUNTER: 14, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 105, READ: 105 } jz 37
  DEBUG    root:machine.py:152 {TICK: 114, PROGRAMM_COUNTER: 15, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 115, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 105, READ: 105 } push 2
  DEBUG    root:machine.py:152 {TICK: 116, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 105, READ: 105 } push 2
  DEBUG    root:machine.py:152 {TICK: 117, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 0 2, WRITE: 105, READ: 105 } push 0
  DEBUG    root:machine.py:152 {TICK: 118, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 2 4, WRITE: 105, READ: 105 } push 0
  DEBUG    root:machine.py:152 {TICK: 119, PROGRAMM_COUNTER: 18, DATA_ADDR: 3Z: True, TOS: 2 0, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 120, PROGRAMM_COUNTER: 18, DATA_ADDR: 0Z: True, TOS: 2 0, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 121, PROGRAMM_COUNTER: 19, DATA_ADDR: 0Z: False, TOS: 2 107, WRITE: 105, READ: 107 } ld None
  DEBUG    root:machine.py:152 {TICK: 122, PROGRAMM_COUNTER: 19, DATA_ADDR: 2Z: False, TOS: 2 107, WRITE: 105, READ: 107 } ld None
  DEBUG    root:machine.py:152 {TICK: 123, PROGRAMM_COUNTER: 20, DATA_ADDR: 2Z: False, TOS: 2 107, WRITE: 105, READ: 107 } pop None
  DEBUG    root:machine.py:152 {TICK: 124, PROGRAMM_COUNTER: 21, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 105, READ: 107 } pop None
  DEBUG    root:machine.py:152 {TICK: 125, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: True, TOS: null 0, WRITE: 105, READ: 107 } push 1
  DEBUG    root:machine.py:152 {TICK: 126, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 105, READ: 107 } push 1
  DEBUG    root:machine.py:152 {TICK: 127, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 0 1, WRITE: 105, READ: 107 } push 2
  DEBUG    root:machine.py:152 {TICK: 128, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 1 107, WRITE: 105, READ: 107 } push 2
  DEBUG    root:machine.py:152 {TICK: 129, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 105, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 130, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 105, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 131, PROGRAMM_COUNTER: 25, DATA_ADDR: 2Z: False, TOS: 1 107, WRITE: 105, READ: 107 } ld None
  DEBUG    root:machine.py:152 {TICK: 132, PROGRAMM_COUNTER: 25, DATA_ADDR: 1Z: False, TOS: 1 107, WRITE: 105, READ: 107 } ld None
  DEBUG    root:machine.py:152 {TICK: 133, PROGRAMM_COUNTER: 26, DATA_ADDR: 1Z: False, TOS: 1 107, WRITE: 107, READ: 107 } pop None
  DEBUG    root:machine.py:152 {TICK: 134, PROGRAMM_COUNTER: 27, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 107, READ: 107 } pop None
  DEBUG    root:machine.py:152 {TICK: 135, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: True, TOS: null 0, WRITE: 107, READ: 107 } push 3
  DEBUG    root:machine.py:152 {TICK: 136, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 107, READ: 107 } push 3
  DEBUG    root:machine.py:152 {TICK: 137, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 0 3, WRITE: 107, READ: 107 } push 3
  DEBUG    root:machine.py:152 {TICK: 138, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 3 107, WRITE: 107, READ: 107 } push 3
  DEBUG    root:machine.py:152 {TICK: 139, PROGRAMM_COUNTER: 30, DATA_ADDR: 1Z: False, TOS: 3 3, WRITE: 107, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 140, PROGRAMM_COUNTER: 30, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 107, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 141, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: False, TOS: 3 2, WRITE: 107, READ: 107 } push 1
  DEBUG    root:machine.py:152 {TICK: 142, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: False, TOS: 2 1, WRITE: 107, READ: 107 } push 1
  DEBUG    root:machine.py:152 {TICK: 143, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: False, TOS: 2 1, WRITE: 107, READ: 107 } add None
  DEBUG    root:machine.py:152 {TICK: 144, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: False, TOS: 3 2, WRITE: 107, READ: 107 } add None
  DEBUG    root:machine.py:152 {TICK: 145, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 107, READ: 107 } ld None
  DEBUG    root:machine.py:152 {TICK: 146, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 107, READ: 107 } ld None
  DEBUG    root:machine.py:152 {TICK: 147, PROGRAMM_COUNTER: 34, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 107, READ: 107 } pop None
  DEBUG    root:machine.py:152 {TICK: 148, PROGRAMM_COUNTER: 35, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 107, READ: 107 } pop None
  DEBUG    root:machine.py:152 {TICK: 149, PROGRAMM_COUNTER: 36, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 107, READ: 107 } jump 10
  DEBUG    root:machine.py:152 {TICK: 150, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 107, READ: 107 } push 3
  DEBUG    root:machine.py:152 {TICK: 151, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 107, READ: 107 } push 3
  DEBUG    root:machine.py:152 {TICK: 152, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 107, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 153, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 107, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 154, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 107, READ: 107 } push 4
  DEBUG    root:machine.py:152 {TICK: 155, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 107, READ: 107 } push 4
  DEBUG    root:machine.py:152 {TICK: 156, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 3 4, WRITE: 107, READ: 107 } blt None
  DEBUG    root:machine.py:152 {TICK: 157, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 107, READ: 107 } blt None
  DEBUG    root:machine.py:152 {TICK: 158, PROGRAMM_COUNTER: 14, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 107, READ: 107 } jz 37
  DEBUG    root:machine.py:152 {TICK: 159, PROGRAMM_COUNTER: 15, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 107, READ: 107 } pop None
  DEBUG    root:machine.py:152 {TICK: 160, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 107, READ: 107 } push 2
  DEBUG    root:machine.py:152 {TICK: 161, PROGRAMM_COUNTER: 16, DATA_ADDR: 3Z: False, TOS: 0 1, WRITE: 107, READ: 107 } push 2
  DEBUG    root:machine.py:152 {TICK: 162, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 0 2, WRITE: 107, READ: 107 } push 0
  DEBUG    root:machine.py:152 {TICK: 163, PROGRAMM_COUNTER: 17, DATA_ADDR: 3Z: False, TOS: 2 4, WRITE: 107, READ: 107 } push 0
  DEBUG    root:machine.py:152 {TICK: 164, PROGRAMM_COUNTER: 18, DATA_ADDR: 3Z: True, TOS: 2 0, WRITE: 107, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 165, PROGRAMM_COUNTER: 18, DATA_ADDR: 0Z: True, TOS: 2 0, WRITE: 107, READ: 107 } gt None
  DEBUG    root:machine.py:152 {TICK: 166, PROGRAMM_COUNTER: 19, DATA_ADDR: 0Z: False, TOS: 2 105, WRITE: 107, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 167, PROGRAMM_COUNTER: 19, DATA_ADDR: 2Z: False, TOS: 2 105, WRITE: 107, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 168, PROGRAMM_COUNTER: 20, DATA_ADDR: 2Z: False, TOS: 2 105, WRITE: 107, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 169, PROGRAMM_COUNTER: 21, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 107, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 170, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: True, TOS: null 0, WRITE: 107, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 171, PROGRAMM_COUNTER: 22, DATA_ADDR: 2Z: False, TOS: 0 2, WRITE: 107, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 172, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 0 1, WRITE: 107, READ: 105 } push 2
  DEBUG    root:machine.py:152 {TICK: 173, PROGRAMM_COUNTER: 23, DATA_ADDR: 2Z: False, TOS: 1 105, WRITE: 107, READ: 105 } push 2
  DEBUG    root:machine.py:152 {TICK: 174, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 107, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 175, PROGRAMM_COUNTER: 24, DATA_ADDR: 2Z: False, TOS: 1 2, WRITE: 107, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 176, PROGRAMM_COUNTER: 25, DATA_ADDR: 2Z: False, TOS: 1 105, WRITE: 107, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 177, PROGRAMM_COUNTER: 25, DATA_ADDR: 1Z: False, TOS: 1 105, WRITE: 107, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 178, PROGRAMM_COUNTER: 26, DATA_ADDR: 1Z: False, TOS: 1 105, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 179, PROGRAMM_COUNTER: 27, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 180, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: True, TOS: null 0, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 181, PROGRAMM_COUNTER: 28, DATA_ADDR: 1Z: False, TOS: 0 1, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 182, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 0 3, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 183, PROGRAMM_COUNTER: 29, DATA_ADDR: 1Z: False, TOS: 3 105, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 184, PROGRAMM_COUNTER: 30, DATA_ADDR: 1Z: False, TOS: 3 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 185, PROGRAMM_COUNTER: 30, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 186, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 105, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 187, PROGRAMM_COUNTER: 31, DATA_ADDR: 3Z: False, TOS: 3 1, WRITE: 105, READ: 105 } push 1
  DEBUG    root:machine.py:152 {TICK: 188, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: False, TOS: 3 1, WRITE: 105, READ: 105 } add None
  DEBUG    root:machine.py:152 {TICK: 189, PROGRAMM_COUNTER: 32, DATA_ADDR: 3Z: False, TOS: 3 3, WRITE: 105, READ: 105 } add None
  DEBUG    root:machine.py:152 {TICK: 190, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 4, WRITE: 105, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 191, PROGRAMM_COUNTER: 33, DATA_ADDR: 3Z: False, TOS: 3 4, WRITE: 105, READ: 105 } ld None
  DEBUG    root:machine.py:152 {TICK: 192, PROGRAMM_COUNTER: 34, DATA_ADDR: 3Z: False, TOS: 3 4, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 193, PROGRAMM_COUNTER: 35, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 194, PROGRAMM_COUNTER: 36, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 105, READ: 105 } jump 10
  DEBUG    root:machine.py:152 {TICK: 195, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 196, PROGRAMM_COUNTER: 10, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } push 3
  DEBUG    root:machine.py:152 {TICK: 197, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 198, PROGRAMM_COUNTER: 11, DATA_ADDR: 3Z: False, TOS: 0 3, WRITE: 105, READ: 105 } gt None
  DEBUG    root:machine.py:152 {TICK: 199, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 0 4, WRITE: 105, READ: 105 } push 4
  DEBUG    root:machine.py:152 {TICK: 200, PROGRAMM_COUNTER: 12, DATA_ADDR: 3Z: False, TOS: 4 4, WRITE: 105, READ: 105 } push 4
  DEBUG    root:machine.py:152 {TICK: 201, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 4 4, WRITE: 105, READ: 105 } blt None
  DEBUG    root:machine.py:152 {TICK: 202, PROGRAMM_COUNTER: 13, DATA_ADDR: 3Z: False, TOS: 0 4, WRITE: 105, READ: 105 } blt None
  DEBUG    root:machine.py:152 {TICK: 203, PROGRAMM_COUNTER: 14, DATA_ADDR: 3Z: True, TOS: 0 0, WRITE: 105, READ: 105 } jz 37
  DEBUG    root:machine.py:152 {TICK: 204, PROGRAMM_COUNTER: 37, DATA_ADDR: 3Z: True, TOS: 0 0, WRITE: 105, READ: 105 } pop None
  DEBUG    root:machine.py:152 {TICK: 205, PROGRAMM_COUNTER: 38, DATA_ADDR: 3Z: True, TOS: null 0, WRITE: 105, READ: 105 } hlt None
  INFO     root:machine.py:258 Output buffer: '[110, 105, 107, 105]'
['n', 'i', 'k', 'i']
[110, 105, 107, 105]
Instruction Counter: 124 Ticks: 206
```

| ФИО              | алг.           | LoC | code байт | code инстр. | инстр. | такт. |
|------------------|----------------|-----|-----------|-------------|--------|-------|
| Антонов Н. С.    | hello          | 2   | -         | 127         | 126    | 206   |+
| Антонов Н. С.    | hello_user_name| 16  | -         | 317         | 405    | 664   |+
| Антонов Н. С.    | cat            | 11  | -         | 39          | 124    | 206   |+
| Антонов Н. С.    | prob1          | 33  | -         | 124         | 14490  | 24751 |

```