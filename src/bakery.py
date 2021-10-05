import numpy as np
import csv

def main():
    filename = "../bakery-datasets/1000/1000-out1.csv"
    with open(filename, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter = ',')
        for line in lines:
            print(line[0])

if __name__ == "__main__":
    main()