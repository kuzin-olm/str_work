#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
import os
import re
from collections import defaultdict


REGULAR_TIME = r'\d+:\d+:\d+'


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--folder', default='source')
parser.add_argument('-s', '--save', default='res.txt')
args = parser.parse_args(sys.argv[1:])

FOLDER = args.folder
OUT_FILE = args.save if args.save.endswith('.txt') else f'{args.save}.txt'


path = os.path.join(os.getcwd(), FOLDER)

try:
    _ = os.listdir(path)
except FileNotFoundError as e:
    print(f'в директории нет папки "{FOLDER}"')
    exit(0)

# если надо удалить ненужные файлы из папки
# file_to_remove = list(filter(lambda x: x[-4:] != '.txt', os.listdir(path)))
# [os.remove(os.path.join(path, x)) for x in file_to_remove]

file_work = list(filter(lambda x: x.endswith('.txt'), os.listdir(path)))
file_work = [os.path.join(path, file) for file in file_work]


def reader(file):
    with open(file, 'r') as f:
        for f_line in f:
            yield f_line


# выбираем только те файлы, в которых есть упоминание о "Заваодской номер"
STR_FIND = 'Заводской номер'

files = []
for file in file_work:
    for line in reader(file):
        if STR_FIND in line:
            files.append(file)
            break


def search_time_table(file, re_time):
    """
    из файла цепляет только строку с заводским номером и строки со временем

    :param file: путь до файла
    :param re_time: регулярное выражение REGULAR_TIME
    :return: серийный номер, таблица->list
    """
    str_find = 'Заводской номер'
    nw = []
    for line in reader(file):
        time_str = re.search(re_time, line)
        number_zav = re.search(str_find, line)
        
        if number_zav:
            nw.append(line.strip().split()[-1])
            continue
        elif time_str:
            nw.append(line.strip())
            
    return nw[0], nw[1:]


def get_sec(file, re_time=REGULAR_TIME):
    """
    достает из файла наработку
    если строк много, то берем время от начала первой проверки и до последней
    (предполагаю, что самая длинная проверка == 24ч)
    если всего одна строка (одна проверка), то беру время выполнения этой проверки

    :param file: путь до файла
    :param re_time: регулярное выражение REGULAR_TIME
    :return: серийный номер, наработка в секундах
    """
    
    def to_sec(date: str):
        h, m, s, *other = list(map(int, date.split(':')))
        sec = h*3600 + m*60 + s
        return sec

    s_number, table = search_time_table(file, re_time)
    total = 0
    
    if len(table) >= 2:
        start = re.findall(re_time, table[0])[0]        
        end = re.findall(re_time, table[-1])[0]
        last_test = re.findall(re_time, table[-1])[-1]

        start_sec = to_sec(start)
        end_sec = to_sec(end)
        last_test_sec = to_sec(last_test)

        if end_sec >= start_sec:
            total = end_sec - start_sec + last_test_sec
        elif end_sec < start_sec:
            total = 24*3600 - start_sec + end_sec + last_test_sec
    
    elif len(table) == 1:
        total = re.findall(re_time, table[0])[-1]
        total = to_sec(total)
        
    return s_number, total


result = defaultdict(int)
for file in files:
    number, total_sec = get_sec(file)
    result[number] += total_sec


all_time = 0
with open(OUT_FILE, 'w') as f:
    for key, value in result.items():
        all_time += value

        wr_str = f'{key}: {round(value/3600, 2)} ч'
        f.writelines(wr_str + '\n')
        print(wr_str)

    wr_str = f'всего: {round(all_time / 3600, 2)} ч'
    f.writelines('\n\n\n\n')
    f.writelines(wr_str + '\n')

    print('_' * 20)
    print(wr_str)

print(f'записано в "{OUT_FILE}"')
