#!/usr/bin/env python3
from urllib.request import urlopen
from urllib.parse import quote, unquote
from urllib.error import URLError
import re


def get_content(name):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    try:
        return urlopen(name).read().decode('urf-8')
    except URLError:
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
    return set(map(unquote, re.findall('''<a +href=["']\/wiki\/([^#:]+?)["']''',
                                       page[begin:end],
                                       flags=re.I | re.M | re.U)))


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    pass


def main():
    pass


if __name__ == '__main__':
    main()
