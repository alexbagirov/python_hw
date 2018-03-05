#!/usr/bin/env python3
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import unquote, quote
from collections import deque
import re


wiki_link = 'https://ru.wikipedia.org/wiki/{}'


def get_content(name):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    try:
        return urlopen(name).read().decode('utf-8')
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
    start = page.find('<body') if page.find('<body') != -1 else 0
    end = page.find('<div id="footer"') if page.find('<div id="footer"') != -1 else 0
    return start, end


def extract_links(page, begin, end):
    """
    Функция принимает на вход содержимое страницы и начало и конец интервала,
    задающего позицию содержимого статьи на странице и возвращает все имеющиеся
    ссылки на другие вики-страницы без повторений и с учётом регистра.
    """
    content = page[begin:end + 1]
    return set(map(unquote, re.findall('''<a +href=["']/wiki/([^:#]+?)["']''', content, flags=re.I | re.M | re.U)))


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    visited_pages = set()
    links = deque()
    links.append(wiki_link.format(start))
    transitions = {}

    while not len(links) == 0:
        current_page = links.popleft()
        if current_page in visited_pages:
            continue

        visited_pages.add(current_page)
        page_content = get_content(quote(current_page, safe='/:'))
        if not page_content:
            return None

        new_links = extract_links(page_content, *extract_content(page_content))
        for page in new_links:
            if page not in visited_pages:
                links.append(wiki_link.format(page))
                transitions[wiki_link.format(page)] = current_page

                if page == finish:
                    return build_transitions_list(transitions, start, finish)

    return None


def build_transitions_list(transitions, start, end):
    answer = [wiki_link.format(end)]
    destination = wiki_link.format(start)

    current = wiki_link.format(end)
    while current != destination:
        current = transitions[current]
        answer.append(current)

    return list(reversed(answer))


def main():
    pass


if __name__ == '__main__':
    main()
