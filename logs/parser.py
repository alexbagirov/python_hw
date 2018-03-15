#!/usr/bin/env python3
import sys
import math
import re


class Parser(object):
    """
    Класс парсера для обработки файла с логами.
    """
    def __init__(self) -> None:
        """Инициализация класса."""
        self.slowest_page = ''
        self.slowest_page_time = 0

        self.fastest_page = ''
        self.fastest_page_time = math.inf

        self.pages = {}

        self.most_popular_page = ''
        self.most_popular_page_hits = 0

    def parse(self) -> None:
        """Основная функция обработки логов."""
        for line in sys.stdin:
            entry_info = self.extract_info(line)
            self.update_stats(entry_info)

        self.print_stats()

    @staticmethod
    def extract_info(s: str) -> (None, dict):
        """Проверяет корректность строки и извлекает из неё информацию.
        Возвращает None в случае некорректной информации."""
        data = re.match('(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \['
                        '(?P<date>\d{2}\/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|'
                        'Oct|Nov|Dec)\/20\d{2}:[0-2][0-9]:[0-5]\d:[0-5]\d '
                        '\+\d{4})] "(GET|PUT|POST|HEAD|OPTIONS|DELETE) '
                        '(?P<url>\S+) \S+" \d+ \d+ "\S+" "(?P<browser>.+)"( '
                        '(?P<time>\d+)|)', s)
        return data.groupdict() if data else None

    def update_stats(self, data: dict) -> None:
        """Обновляет данные в соответствии с новой информацией."""
        page_time = int(data['time'])

        if page_time >= self.slowest_page_time:
            self.slowest_page_time = page_time
            self.slowest_page = data['url']

        if page_time <= self.fastest_page_time:
            self.fastest_page_time = page_time
            self.fastest_page = data['url']

    def print_stats(self) -> None:
        """Выводит статистику в нужном формате на консоль."""
        print('Самая медленная - ' + self.slowest_page)
        print('Самая быстрая - ' + self.fastest_page)


class Page(object):
    """Класс страницы. Используется для подсчета количества загрузок конкретной
    страницы и суммарного времени, затраченного на её открытие."""
    def __init__(self, time: int) -> None:
        """Инициализация. Изначально к сумме прибавляется первое время загрузки
        создаваемой страницы."""
        self.total_time = time
        self.hits = 1


def main():
    parser = Parser()
    parser.parse()


if __name__ == '__main__':
    main()
