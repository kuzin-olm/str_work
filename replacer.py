#!/usr/bin/env python
# coding: utf-8
"""
для стыковки экспортируемых моделей из xscale в matlab
"""

import os
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-f', '--folder', default='work')
args = parser.parse_args(sys.argv[1:])


work_folder = args.folder
filename_extension = '.xscade'

# получаем абсолбтный путь до рабочей папки рядом с основным скриптом
work_dir = os.path.join(os.getcwd(), work_folder)

try:
    _ = os.listdir(work_dir)
except FileNotFoundError as e:
    print(f'в директории нет папки "{work_folder}"')
    exit(0)

# выбираем только пути папок и сами файлы, которые лежат в папке (подпапки исключаем)
dirs = [[dirname, filenames] for dirname, _, filenames in os.walk(work_dir)]

# начинаем бежать по директориям и файлам
for dirname, filenames in dirs:
    # отсеиваем файлы, оставляем только те, у которых разрешение == filename_extension
    files = [item for item in filenames if item.endswith(filename_extension)]

    # бежим по списку файлов (помним, что путь до файла = dirname)
    for file_name in files:
        # получаем абсолютный/полный путь до файла
        # чтобы правильно открывать файл для чтения/записи
        abs_path_file = os.path.join(dirname, file_name)
        
        # создаем новый пустой список, чтобы хранить в нем строки из файла
        nw = []
        # открываем файл с доступом только на чтение - 'r'
        with open(abs_path_file, 'r') as f:
            # так как файл читается как многострочный, то по нему также проходимся в цикле
            for line in f:
                # последовательно добавляем в наш пустой список строки из файла
                nw.append(line)
        
        # теперь пробегаем по сохраненным строкам и заменяем нужные куски
        nw = list(map(lambda x: x.replace('float64', 'float32'), nw))
        nw = list(map(lambda x: x.replace('_f64', '_f32'), nw))
        
        # открываем файл, но уже с доступом на запись - 'w'
        with open(abs_path_file, 'w') as f:
            # пробегаемся по списку сохраненных строк, в которые вносили изменения
            for line in nw:
                # записываем сроку в файл
                f.write(line)

print('completed')

