import csv

def load_csv(filename):
    data = []
    with open(filename, 'r',encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    return data

# Example usage:
filename = 'sent_data.csv'  # Replace 'data.csv' with your CSV file's name
csv_data = load_csv(filename)
print(type(csv_data))