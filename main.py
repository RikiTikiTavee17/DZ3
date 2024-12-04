import re
import toml
import sys

# Словарь для хранения констант
constants = {}

# Путь к входному файлу по умолчанию
default_input_file = "C://Users//Alexander//configUpr3.txt"


def parse_line(line):
    # Пропуск однострочных комментариев
    if line.startswith("C") or len(line) == 0:
        return None

    # Объявление константы: set имя = значение
    set_match = re.match(r"set\s+([a-zA-Z][a-zA-Z0-9]*)\s*=\s*(.+)", line)
    if set_match:
        const_name, const_value = set_match.groups()
        constants[const_name] = parse_value(const_value)
        return None

    # Присвоение переменной: имя = значение
    assignment_match = re.match(r"([a-zA-Z][a-zA-Z0-9]*)\s*=\s*(.+)", line)
    if assignment_match:
        line = line.replace(',', '')
        if ("{" in line):
            spltLine = line.split("\n")
            spltLine.pop()
            spltLine.pop()
            if (spltLine[0].startswith(" ")):
                splitted = spltLine[0].split(" ")
                for i in range(len(splitted)):
                    if (splitted[i] != ""):
                        key = splitted[i]
            else:
                splitted = spltLine[0].split(" ")
                key = splitted[0]
            value = dict()
            for i in range(1,len(spltLine)):
                dictionary = parse_line(spltLine[i])
                keys = list(dictionary.keys())
                value[keys[0]] = dictionary[keys[0]]
            return {key: value}
        else:
            key, value = assignment_match.groups()
            parsed_value = parse_value(value)
            return {key: parsed_value}

    raise SyntaxError(f"Неверный синтаксис: {line}")


def parse_dict_multiline(dict_str):
    result = {}
    dict_str = substitute_constants(dict_str.strip("{} \n"))
    lines = dict_str.splitlines()
    for line in lines:
        line = line.strip()
        if line:
            key_value_match = re.match(r"([a-zA-Z][a-zA-Z0-9]*)\s*=\s*(.+)", line)
            if key_value_match:
                key, val = key_value_match.groups()
                result[key.strip()] = parse_value(val.strip())
            else:
                raise SyntaxError(f"Неверная запись в словаре: {line}")
    return result


def parse_value(value):
    # Парсинг значения: числа, массивы или словари
    value = value.strip()
    if value.isdigit():
        return int(value)
    elif value.startswith("[") and value.endswith("]"):
        return parse_array(value[1:-1])
    elif value.startswith("{") and value.endswith("}"):
        return parse_dict_multiline(value)
    elif re.match(r"\$([a-zA-Z][a-zA-Z0-9]*)\$", value):
        return substitute_constants(value)
    else:
        return value  # Рассматриваем значение как строку, если оно не подходит ни под один другой тип


def parse_array(array_str):
    # Разделение элементов массива, предполагая пробел как разделитель
    elements = [parse_value(elem.strip()) for elem in array_str.split()]
    return elements


def substitute_constants(text):
    # Подстановка значений констант в текст
    def replace_constant(match):
        const_name = match.group(1)
        if const_name in constants:
            return str(constants[const_name])
        else:
            raise SyntaxError(f"Неопределенная константа: {const_name}")

    return re.sub(r"\$([a-zA-Z][a-zA-Z0-9]*)\$", replace_constant, text)


def main():
    # Проверяем наличие аргумента командной строки или используем путь по умолчанию
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input_file

    config = {}
    try:
        with open(input_file, 'r') as file:
            multiline_buffer = ""
            inside_dict = False

            for line in file:
                line = line.strip()
                if "{" in line:
                    inside_dict = True
                    multiline_buffer += line + "\n"
                elif inside_dict:
                    multiline_buffer += line + "\n"
                    if line.endswith("}"):
                        inside_dict = False
                        parsed = parse_line(multiline_buffer)
                        multiline_buffer = ""
                        if parsed is not None:
                            config.update(parsed)
                else:
                    parsed = parse_line(line)
                    if parsed is not None:
                        config.update(parsed)

        # Вывод в формате TOML
        toml_output = toml.dumps(config)
        sys.stdout.write(toml_output)
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден.")
    except SyntaxError as e:
        print(f"Синтаксическая ошибка: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
