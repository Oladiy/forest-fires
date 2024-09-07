import csv
import os
import re
from datetime import datetime

import rasterio

from api import call_api

headers = ['time', 'Тсред', 'Тмин', 'Тмакс', 'Осадки всего', 'Направление ветра', 'Скорость ветра', 'Порывы ветра',
           'Давление на уровне моря']


def find_tiff_file(directory):
    """Находит первый .tiff файл в указанной директории с помощью регулярного выражения"""
    tiff_pattern = re.compile(r'.*\.tiff$')
    for file_name in os.listdir(directory):
        if tiff_pattern.match(file_name):
            return os.path.join(directory, file_name)
    raise FileNotFoundError("TIFF файл не найден в указанной директории")


def find_csv_file(directory):
    """Находит первый .csv файл в указанной директории с помощью регулярного выражения"""
    csv_pattern = re.compile(r'.*\.csv$')
    for file_name in os.listdir(directory):
        if csv_pattern.match(file_name):
            print("file_name = ", file_name)
            return file_name
    raise FileNotFoundError("csv файл не найден в указанной директории")


def format_time(time_str):
    try:
        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d')  # Преобразовать дату к нужному формату
    except ValueError:
        return time_str


def saturate_csv(directory):
    try:
        file_path = find_tiff_file(directory)
        print(f"Обнаружен файл: {file_path}")

        with rasterio.open(file_path) as src:
            topleft_lat = src.bounds.top
            topleft_lon = src.bounds.left
            date_str = re.search(r"\d{4}-\d{2}-\d{2}", file_path).group(0)
            data = call_api(topleft_lat, topleft_lon, date_str)

            for key in data.keys():
                if key not in headers:
                    headers.append(key)

            new_csv_file_name = directory + "saturated_" + find_csv_file(directory)
            with open(new_csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                for i in range(len(data['date'])):
                    row = []
                    for key in data.keys():
                        if key == "date":
                            row.append(format_time(data['date'][i]))
                            continue
                        row.append(data.get(key, [''])[i])
                    writer.writerow(row)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except Exception as e:
        print(f'Ошибка: {e}')


if __name__ == "__main__":
    for j in range(0, 21):
        folder_name = str(j) if j > 9 else "0" + str(j)
        directory = f"{folder_name}/"
        saturate_csv(directory)
