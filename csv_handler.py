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


def get_medication_dict(file_path):
    result_dict = {}
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter=';')  # Specify the correct delimiter (;)
        next(reader)  # Skip the header row

        for row in reader:
            if len(row) >= 2:  # Ensure the row has at least two columns
                key = row[0].strip()  # First column as the key
                value = row[1].strip()  # Second column as the value
                result_dict[key] = value

    return result_dict

