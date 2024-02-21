
# Example usage:


input_folder = r'C:\Users\Deepak\Downloads\data'
output_file = r'D:\Project\output.csv'
import os
import csv

def extract_data(input_folder, output_file):
    with open(output_file, 'a', newline='') as output_csv:
        output_writer = csv.writer(output_csv)

        for filename in os.listdir(input_folder):
            if filename.endswith('.csv'):
                file_path = os.path.join(input_folder, filename)
                print(filename)
                with open(file_path, 'r') as input_csv:
                    input_reader = csv.reader(input_csv)
                    
                    current_data = []
                    for row in input_reader:
                        current_data.extend(row)
                        current_data.extend("0")
                        output_writer.writerow(current_data)
                        current_data = []


extract_data(input_folder, output_file)