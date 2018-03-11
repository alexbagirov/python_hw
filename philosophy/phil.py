#!/usr/bin/env python3
from urllib.request import urlopen
from urllib.parse import quote, unquote
from urllib.error import URLError, HTTPError
from collections import deque
import re


def get_content(name):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    try:
        return urlopen(name).read().decode()
    except (URLError, HTTPError):
        return None


def extract_content(page):
    """
    Функция принимает на вход содержимое страницы и возвращает 2-элементный
    tuple, первый элемент которого — номер позиции, с которой начинается
    содержимое статьи, второй элемент — номер позиции, на котором заканчивается
    содержимое статьи.
    Если содержимое отсутствует, возвращается (0, 0).
    """
    start = page.find('<div id="mw-content-text"') \
        if '<div id="mw-content-text"' in page else 0
    finish = page.find('<div id="footer"') if '<div id="footer"' in page else 0
    return start, finish


def extract_links(page, begin, end):
    """
    Функция принимает на вход содержимое страницы и начало и конец интервала,
    задающего позицию содержимого статьи на странице и возвращает все имеющиеся
    ссылки на другие вики-страницы без повторений и с учётом регистра.
    """
    return set(map(unquote, re.findall('''<a +href=["']/wiki/([^#:]+?)["']''',
                                       page[begin:end],
                                       flags=re.I | re.M | re.U)))


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    if start == finish:
        return [start, finish]

    visited = set()
    to_visit = deque()
    previous = dict()
    to_visit.appendleft(start)

    while len(to_visit) != 0:
        current = to_visit.pop()
        visited.add(current)
        text = get_content('https://ru.wikipedia.org/wiki/' +
                           quote(current, safe=':/'))
        if not text:
            return None

        new_links = extract_links(text, *extract_content(text))
        for link in new_links:
            if link not in visited:
                to_visit.appendleft(link)
                previous[link] = current

                if link == finish:
                    return build_path(start, finish, previous)

    return None


def build_path(start, finish, previous):
    answer = [finish]
    current = finish

    while current != start:
        current = previous[current]
        answer.append(current)

    return list(reversed(answer))


def main():
    pass


if __name__ == '__main__':
    main()
