import sys
import os
import pandas as pd
import xlrd

if __name__ == '__main__':

    directory = 'input_data/Expenses'

    for file in os.listdir('input_data/Expenses'):
        if file.endswith('xlsx'):
            read_file = pd.read_excel(os.path.join(directory, file))
            for col in read_file.select_dtypes('float64'):
                if col.find('Code') >= 0:
                    read_file[col] = read_file[col].fillna(-1).astype('int64')
                    read_file[col] = read_file[col].astype(str).replace('-1', '')
            new_file_name = file[:file.index('-')] + '.csv'
            read_file.to_csv(os.path.join(directory, new_file_name), index=None, header=True)