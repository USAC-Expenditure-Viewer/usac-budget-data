import csv
import datetime
import json
import os
import re
import string

from nltk.corpus.reader import VERB, NOUN
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

correction = {}

categories = ['Department', 'Division', 'Event', 'Fund', 'GL']
indexes_dict = {}

trans_stop_words = ['REIMBURSEMENT', 'REMITTANCE', 'DISBURSEMENT', 'FEE',
             'EXPENSE', 'CHARGE', 'CASH', 'ADVANCE', 'CHECK', 'PAYMENT']

corr_file = 'output/corr_dict.json'

multiword_match = {"CASH ADV": "CASH ADVANCE"}

def convert_money(string):
    string = string.strip().replace(',', '')
    if string[0] == '(' and string[-1] == ')':
        return -float(string[1:-1])
    else:
        return float(string)

def convert_date(string):
    return datetime.datetime.strptime(string, '%m/%d/%Y').timestamp()

def translate(infile, outfile):
    with open(infile, 'r') as f, open(outfile, 'w') as out:
        reader = csv.reader(f)
        writer = csv.writer(out)
        keyword_sets = []
        referenced_events = set()
        writer.writerow(['date', 'fund', 'division', 'department',
                            'gl', 'event', 'description',  'amount'])
        for line in reader:

            try:
                fund, division, department, gl, event = \
                    line[1], line[2], \
                    line[3], line[4], \
                    line[5]
                referenced_events.add(event)
            except ValueError:
                continue
            except KeyError as e:
                print("Keyerror", e)
                fund, division, department, gl, event = \
                    line[1], line[2], \
                    line[3], line[4], \
                    int(line[5])

            # construct descriptions
            desc = line[8]

            desc = desc.replace("'g", "ing")
            desc = desc.replace("'G", "ING")
            desc = desc.replace("'n", "ion")
            desc = desc.replace("'N", "ION")

            desc = desc.replace('  ', ' ')

            words_list = extract_word_list(desc)

            words_set = extract_word_set(words_list)
            keyword_sets.append(words_set)

            amount = convert_money(line[9]) + convert_money(line[10])
            date = convert_date(line[0])

            if division == 'Mandatory Fee':
                division = 'Membership Fee'

            writer.writerow([date, fund, division, department,
                            gl, event, desc,  amount] + list(words_set))


def extract_word_list(desc):

    words_list = desc
    for i in string.punctuation.replace("'", ''):
        words_list = words_list.replace(i, ' ')

    for p in multiword_match:
        words_list = words_list.replace(p + " ", multiword_match[p] + " ")
        if desc.endswith(p):
            words_list = words_list[:-len(p)] + multiword_match[p]

    words_list = words_list.split()

    new_words_list = []
    for word in words_list:
        if word.upper() in correction:
            corrected_words = correction[word.upper()].split()
            for w in corrected_words: new_words_list.append(w)
        else:
            new_words_list.append(word.upper())

    words_list = new_words_list
    return words_list



lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def extract_word_set(words_list):
    def lemmatize(w):
        w = w.lower()
        w = lemmatizer.lemmatize(w, VERB)
        w = lemmatizer.lemmatize(w, NOUN)
        return lemmatizer.lemmatize(w, VERB).upper()

    # construct words set
    words_set = set()
    words_list = map(lemmatize, words_list)
    for w in words_list:
        if re.fullmatch('[a-zA-Z]*\d+', w) or re.fullmatch('\d+[a-zA-Z]+', w):
            continue
        if w.lower() in stop_words or w.upper() in trans_stop_words or len(w) <= 1:
            continue
        if len(w) <= 4 and w not in ["USAC"] and len(wn.synsets(w)) == 0:
            continue
        words_set.add(w)

    return words_set

def index_keywords(keyword_sets):
    indexes = {}
    for i, s in enumerate(keyword_sets):
        for w in s:
            arr = indexes.get(w, [])
            arr.append(i)
            indexes[w] = arr

    indexes_dict['keyword_index'] = indexes

def load_dict():
    global correction
    with open(corr_file, 'r') as w:
        correction = json.load(w)


def load_all_maps():
    for c in categories:
        indexes_dict[c.lower()] = {}
        load_map('input_data/'+c+'.csv', c.lower())


def load_map(file, category_name):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            try:
                indexes_dict[category_name][int(line[0])] = line[1]
            except ValueError:
                pass

def translate_directory():
    index = []
    for file in filter(lambda f : f.endswith('.csv'), os.listdir('input_data/Expenses')):
        index.append(file.replace('.csv', ''))
        translate(os.path.join('input_data', 'Expenses', file), os.path.join('output', 'expense_summary_'+file))

    index = sorted(index, reverse=True)
    with open('output/datasets.json', 'w') as index_file:
        json.dump(index, index_file)

if __name__ == '__main__':
    if os.path.exists(corr_file):
        load_dict()
    load_all_maps()
    translate_directory()
