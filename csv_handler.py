import csv


def csv_to_dict(file_path):
    result_dict = {}
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Überspringe die Kopfzeile (falls vorhanden)

        for row in reader:
            if len(row) >= 2:
                key = row[1].strip()  # Rechte Spalte als Key
                value = row[0].strip()  # Linke Spalte als Value
                result_dict[key] = value

    return result_dict


