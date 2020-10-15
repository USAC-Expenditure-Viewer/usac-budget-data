import os
import string

from spellchecker import SpellChecker
import csv
import json
import datetime
import re

spell = SpellChecker()
correction = {}
skipped_words = set()
dept_dict = {}

corr_file = 'output/corr_dict.json'
dept_file = 'input_data/Department.csv'

def try_convert_date(str):
    try:
        return datetime.datetime.strptime(str, '%b%Y').strftime('%B %Y')
    except ValueError as e:
        pass

    try:
        return datetime.datetime.strptime(str, '%b%y').strftime('%B %Y')
    except ValueError as e:
        pass

    try:
        return datetime.datetime.strptime(str, '%B%y').strftime('%B %Y')
    except ValueError as e:
        pass

    try:
        return datetime.datetime.strptime(str, '%B%Y').strftime('%B %Y')
    except ValueError as e:
        pass

    return None


def check_words(sentence):

    sentence = sentence.replace("'g", "ing")
    sentence = sentence.replace("'G", "ING")
    sentence = sentence.replace("'n", "ion")
    sentence = sentence.replace("'N", "ION")

    # find those words that may be misspelled
    misspelled = spell.unknown(sentence.split())

    for word in misspelled:
        if word.upper() in correction or word in skipped_words: continue
        if re.fullmatch("[a-zA-Z]+\d+", word) is not None:
            skipped_words.add(word)
            continue
        if re.fullmatch("[0-9]+th", word) is not None:
            skipped_words.add(word)
            continue
        if re.fullmatch("[0-9]+1st", word) is not None or re.fullmatch("[0-9]*2nd", word) is not None or re.fullmatch("[0-9]*3rd", word) is not None:
            skipped_words.add(word)
            continue

        date_converted = try_convert_date(word)
        if date_converted is not None:
            correction[word.upper()] = date_converted.upper()
            continue

        # Get the one `most likely` answer, Get a list of `likely` options
        print(word, spell.correction(word), spell.candidates(word))

        ans = input("Correction: ")
        if ans == '-':
            correction[word.upper()] = word.upper()
        elif ans == '--skip':
            skipped_words.add(word)
            print("SKIPPED")
        else:
            correction[word.upper()] = ans.upper()

    out = []
    for word in sentence.split():
        if word.lower() in misspelled and word.lower() not in skipped_words:
            out.append(correction[word.upper()])
        else:
            out.append(word)
    return ' '.join(out)


def get_description():
    with open('expense.csv', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            desc = line[8]
            for i in string.punctuation:
                if i != "'":
                    desc = desc.replace(i, ' ' + i + ' ')
            try:
                print(dept_dict[int(line[3])],':',desc)
            except ValueError:
                pass

            output = check_words(desc)
            print('Output:', output)
            print()
        pass

def load_dict():
    global correction
    with open(corr_file, 'r') as w:
        correction = json.load(w)
def save_dict():
    with open(corr_file, 'w') as w:
        json.dump(correction, w, indent=4)

def load_departments():
    with open(dept_file, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            try:
                dept_dict[int(line[0])] = line[1]
            except ValueError:
                pass


if __name__ == '__main__':
    if os.path.exists(corr_file):
        load_dict()
    load_departments()

    try:
        get_description()
    finally:
        save_dict()