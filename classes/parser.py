#!/usr/bin/env python3

from datetime import datetime, date
import math
import re
import unittest


class Parser(object):
    """
    Класс парсера для обработки файла с логами.
    """
    def __init__(self) -> None:
        """Инициализация класса."""
        self.slowest_page = ''
        self.slowest_page_time = 0

        self.slowest_average_page = ''

        self.fastest_page = ''
        self.fastest_page_time = math.inf

        self.pages = {}
        self.browsers = {}
        self.clients = {}
        self.clients_by_days = {}
        self.days = {}

        self.most_popular_pages = LexicographicTop()
        self.most_popular_agents = LexicographicTop()
        self.most_active_clients = LexicographicTop()

        self.pattern = re.compile('(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                                  ' - - \[(?P<date>\d{2}/(Jan|Feb|Mar|Apr|May|'
                                  'Jun|Jul|Aug|Sep|Oct|Nov|Dec)/20\d{2}):[0-2]'
                                  '[0-9]:[0-5]\d:[0-5]\d \+\d{4}] "(GET|PUT|'
                                  'POST|HEAD|OPTIONS|DELETE) (?P<url>\S+) '
                                  '\S+" \d+ \d+ "\S+" "(?P<browser>.+)"( '
                                  '(?P<time>\d+)|)')

    def add_line(self, line) -> None:
        """Получив на вход строку лога, проверяет её на корректность и добавляет
        в статистику."""
        entry_info = self.extract_info(line)
        if entry_info:
            self.update_stats(entry_info)

    def extract_info(self, s: str) -> (None, dict):
        """Проверяет корректность строки и извлекает из неё информацию.
        Возвращает None в случае некорректной информации."""
        data = re.match(self.pattern, s)
        return data.groupdict() if data else None

    def update_stats(self, data: dict) -> None:
        """Обновляет данные в соответствии с новой информацией."""
        if data['time']:
            page_time = int(data['time'])

            if page_time >= self.slowest_page_time:
                self.slowest_page_time = page_time
                self.slowest_page = data['url']

            if page_time <= self.fastest_page_time:
                self.fastest_page_time = page_time
                self.fastest_page = data['url']

            if data['url'] not in self.pages:
                self.pages[data['url']] = Page(page_time)
            else:
                self.pages[data['url']].add_time(page_time)
        else:
            if data['url'] not in self.pages:
                self.pages[data['url']] = Page(0)
            else:
                self.pages[data['url']].add_time(0)

        if data['browser'] not in self.browsers:
            self.browsers[data['browser']] = 1
        else:
            self.browsers[data['browser']] += 1

        if data['ip'] not in self.clients:
            self.clients[data['ip']] = 1
        else:
            self.clients[data['ip']] += 1

        self.most_popular_pages.add_entry(data['url'],
                                          self.pages[data['url']].hits)
        self.most_popular_agents.add_entry(data['browser'],
                                           self.browsers[data['browser']])
        self.most_active_clients.add_entry(data['ip'],
                                           self.clients[data['ip']])

        date = data['date']

        if data['ip'] not in self.clients_by_days:
            self.clients_by_days[data['ip']] = {}
        if date not in self.clients_by_days[data['ip']]:
            self.clients_by_days[data['ip']][date] = 1
        else:
            self.clients_by_days[data['ip']][date] += 1

        if date not in self.days:
            self.days[date] = LexicographicTop()
        self.days[date].add_entry(data['ip'],
                                  self.clients_by_days[data['ip']][date])

    def find_slowest_average(self) -> None:
        """Подсчитывает среднее время загрузки для каждой страницы и находит
        страницу с самым наихудшим временем."""
        slowest_average_page = ''
        slowest_average_page_time = 0

        for page in self.pages.keys():
            average_time = self.pages[page].total_time / self.pages[page].hits
            if average_time > slowest_average_page_time:
                slowest_average_page_time = average_time
                slowest_average_page = page

        self.slowest_average_page = slowest_average_page

    def results(self) -> dict:
        """Возвращает словарь из результатов подсчитанной статистики."""
        self.find_slowest_average()

        return {'FastestPage': self.fastest_page,
                'MostActiveClient': self.most_active_clients.get_top(),
                'MostActiveClientByDay':
                    {datetime.strptime(day, '%d/%b/%Y').date():
                     self.days[day].get_top()
                     for day in sorted(self.days.keys())},
                'MostPopularBrowser': self.most_popular_agents.get_top(),
                'MostPopularPage': self.most_popular_pages.get_top(),
                'SlowestAveragePage': self.slowest_average_page,
                'SlowestPage': self.slowest_page}


class Page(object):
    """
    Класс страницы. Используется для подсчета количества загрузок конкретной
    страницы и суммарного времени, затраченного на её открытие.
    """
    def __init__(self, time: int) -> None:
        """Инициализация. Изначально к сумме прибавляется первое время загрузки
        создаваемой страницы."""
        self.total_time = time
        self.hits = 1

    def add_time(self, time: int) -> None:
        """Прибавляет новое время загрузки к суммарному для страницы."""
        self.total_time += time
        self.hits += 1


class LexicographicTop(object):
    """
    Структура для поддержания топа в наборе элементов. При запросе самого
    популярного объекта возвращает лексикографически наименьшую единицу.
    """
    def __init__(self) -> None:
        """Инициализация."""
        self.top_entries = []
        self.top_result = 0

    def add_entry(self, entry: str, entry_result: int) -> None:
        """Добавляет новый элемент к топу. Если результат элемента лучше
        имеющегося, список лучших элементов очищается, иначе элемент
        добавляется в топ."""
        if entry_result == self.top_result:
            self.top_entries.append(entry)
        elif entry_result > self.top_result:
            self.top_result = entry_result
            self.top_entries.clear()
            self.top_entries.append(entry)

    def get_top(self) -> str:
        """Возвращает лучший наименьший лексикографичеки элемент."""
        return sorted(self.top_entries, reverse=True)[0] \
            if len(self.top_entries) > 0 else ''


def make_stat():
    return Parser()


class LogStatTests(unittest.TestCase):
    def testEmptyLogs(self):
        parser = make_stat()
        self.assertDictEqual(parser.results(),
                             {'FastestPage': '',
                              'MostActiveClient': '',
                              'MostActiveClientByDay': {},
                              'MostPopularBrowser': '',
                              'MostPopularPage': '',
                              'SlowestAveragePage': '',
                              'SlowestPage': ''}
                             )

    def testLexicographicTop(self):
        parser = make_stat()
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:37:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"ABC" 27979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:38:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"ABC" 27979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:39:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"BCD" 27979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:40:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"BCD" 27979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:41:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 27979')
        self.assertDictEqual(parser.results(),
                             {'FastestPage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'MostActiveClient': '192.168.65.56',
                              'MostActiveClientByDay':
                              {date(2013, 2, 17): '192.168.65.56'},
                              'MostPopularBrowser': 'BCD',
                              'MostPopularPage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'SlowestAveragePage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'SlowestPage': ''
                              '/pause/ajaxPause?pauseConfigId=all&admin=1'})

    def testIncorrectLogs(self):
        parser = make_stat()
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:41:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 27979')
        parser.add_line('hi!')
        self.assertDictEqual(parser.results(),
                             {'FastestPage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'MostActiveClient': '192.168.65.56',
                              'MostActiveClientByDay':
                              {date(2013, 2, 17): '192.168.65.56'},
                              'MostPopularBrowser': 'CDE',
                              'MostPopularPage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'SlowestAveragePage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'SlowestPage': ''
                              '/pause/ajaxPause?pauseConfigId=all&admin=1'})

    def testMinMaxBehaviour(self):
        parser = make_stat()
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:40:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 27979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:41:31 +0600] "GET'
                        ' /something HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 28979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:42:31 +0600] "GET'
                        ' /login HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 28979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:43:31 +0600] "GET'
                        ' /exit HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 28979')
        self.assertDictEqual(parser.results(),
                             {'FastestPage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'MostActiveClient': '192.168.65.56',
                              'MostActiveClientByDay':
                              {date(2013, 2, 17): '192.168.65.56'},
                              'MostPopularBrowser': 'CDE',
                              'MostPopularPage': '/something',
                              'SlowestAveragePage': '/something',
                              'SlowestPage': '/exit'})

    def testLogsWithoutTime(self):
        parser = make_stat()
        parser.add_line('192.168.65.20 - - [17/Feb/2013:06:40:31 +0600] "GET'
                        ' /pause/ajaxPause?pauseConfigId=all&admin=1 HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 27979')
        parser.add_line('192.168.65.30 - - [17/Feb/2013:06:41:31 +0600] "GET'
                        ' /something HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 28979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:42:31 +0600] "GET'
                        ' /login HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE" 28979')
        parser.add_line('192.168.65.56 - - [17/Feb/2013:06:43:31 +0600] "GET'
                        ' /exit HTTP/1.1"'
                        ' 200 1046 "http://192.168.65.101/pause/index" '
                        '"CDE"')
        self.assertDictEqual(parser.results(),
                             {'FastestPage':
                              '/pause/ajaxPause?pauseConfigId=all&admin=1',
                              'MostActiveClient': '192.168.65.56',
                              'MostActiveClientByDay':
                              {date(2013, 2, 17): '192.168.65.56'},
                              'MostPopularBrowser': 'CDE',
                              'MostPopularPage': '/something',
                              'SlowestAveragePage': '/something',
                              'SlowestPage': '/login'})


if __name__ == '__main__':
    unittest.main()
