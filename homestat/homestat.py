#!/usr/bin/env python3


def make_stat(filename):
    """
    Функция вычисляет статистику по именам за каждый год с учётом пола.
    """
    with open(filename, encoding='cp1251') as f:
        s = f.read()

    years = search_all_occurrences(s, '<h3>', '</h3>')
    current_year = years[0][0]
    if len(years) > 1:
        next_year_start = years[1][1]
    else:
        next_year_start = 9999999999999

    stat = {current_year: {}}

    entries = search_all_occurrences(s, '/">', '</a>')
    for entry in entries:
        surname, name = entry[0].split()
        if entry[1] >= next_year_start:
            for i in range(len(years)):
                if years[i][1] == next_year_start:
                    current_year = years[i][0]
                    if i < len(years) - 1:
                        next_year_start = years[i + 1][1]
                    else:
                        next_year_start = 9999999999999
                    break
            if current_year not in stat:
                stat[current_year] = {}

        if name in stat[current_year]:
            stat[current_year][name]['count'] += 1
        else:
            stat[current_year][name] = {}
            stat[current_year][name]['count'] = 1
            if name.endswith(('ая', 'а', 'ия', 'я', 'ь', 'ся')) and not \
                    name.endswith(('ья', 'рь', 'ита', 'ва')):
                stat[current_year][name]['sex'] = 'female'
            else:
                stat[current_year][name]['sex'] = 'male'

    return stat


def search_all_occurrences(s, start, end):
    """
    Функция находит все конструкции вида start***end и возвращает список из
    всех обнаруженных ***.
    :param s: строка для поиска
    :param start: префикс
    :param end: суффикс
    :return: list всех найденных вхождений с индексами их начала
    """
    last_found = 0
    results = []

    while True:
        last_found = s.find(start, last_found + 1)
        if last_found == -1:
            break

        results.append((s[last_found + len(start):s.find(end,
                                                         last_found)],
                        last_found + len(start)))

    return results


def extract_years(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список годов,
    упорядоченный по возрастанию.
    """
    return sorted(list(stat.keys()))


def union_years(stat):
    """
    Функция объединяет статистику по годам в общую.
    :param stat: Посчитанная статистика
    :return: Список tuple'ов
    """
    frequencies = {}

    for year in list(stat.keys()):
        for name in list(stat[year].keys()):
            if name in frequencies:
                frequencies[name]['count'] += stat[year][name]['count']
            else:
                frequencies[name] = {}
                frequencies[name]['count'] = stat[year][name]['count']
                frequencies[name]['sex'] = stat[year][name]['sex']

    return frequencies


def extract_general(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для всех имён.
    Список должен быть отсортирован по убыванию количества.
    """
    frequencies = union_years(stat)
    results = []

    for name in list(frequencies.keys()):
        results.append((name, frequencies[name]['count']))

    return sorted(results, key=lambda x: x[1], reverse=True)


def extract_general_male(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён мальчиков.
    Список должен быть отсортирован по убыванию количества.
    """
    frequencies = union_years(stat)
    results = []

    for name in list(frequencies.keys()):
        if frequencies[name]['sex'] == 'male':
            results.append((name, frequencies[name]['count']))

    return sorted(results, key=lambda x: x[1], reverse=True)


def extract_general_female(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён девочек.
    Список должен быть отсортирован по убыванию количества.
    """
    frequencies = union_years(stat)
    results = []

    for name in list(frequencies.keys()):
        if frequencies[name]['sex'] == 'female':
            results.append((name, frequencies[name]['count']))

    return sorted(results, key=lambda x: x[1], reverse=True)


def extract_year(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    results = []

    for name in list(stat[year].keys()):
        results.append((name, stat[year][name]['count']))

    return sorted(results, key=lambda x: x[1], reverse=True)


def extract_year_male(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён мальчиков в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    results = []

    for name in list(stat[year].keys()):
        if stat[year][name]['sex'] == 'male':
            results.append((name, stat[year][name]['count']))

    return sorted(results, key=lambda x: x[1], reverse=True)


def extract_year_female(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён девочек в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    results = []

    for name in list(stat[year].keys()):
        if stat[year][name]['sex'] == 'female':
            results.append((name, stat[year][name]['count']))

    return sorted(results, key=lambda x: x[1], reverse=True)


if __name__ == '__main__':
    pass
