import csv
import json
import os
import re
from datetime import datetime


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
    csv_filename = find_csv_file(directory)
    with open(directory + csv_filename, mode='r', newline='', encoding='utf-8') as csvfile:
        rows = list(csv.reader(csvfile))

    headers = rows[0]
    rows = rows[1:]

    with open(directory + "tobytes().json", "rb") as f:
        data = json.loads(f.read())

    for key in data.keys():
        if key not in headers:
            headers.append(key)

    new_csv_file_name = directory + "saturated_" + csv_filename
    with open(new_csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for i in range(len(data['date'])):
            try:
                row = rows[i]
            except IndexError:
                break
            for key in data.keys():
                if key == "date":
                    row.append(format_time(data['date'][i]))
                    continue
                try:
                    row.append(data.get(key, [''])[i])
                except IndexError:
                    row.append(None)
            writer.writerow(row)


if __name__ == "__main__":
    for j in range(0, 1):
        folder_name = str(j) if j > 9 else "0" + str(j)
        directory = f"{folder_name}/"
        saturate_csv(directory)
