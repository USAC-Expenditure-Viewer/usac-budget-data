import json

from nltk.corpus import wordnet as wn

def load_words(filename):
    words = {}
    with open(filename, 'r') as f:
        obj = json.load(f)
        for entry in obj:
            amount = entry['amount']
            for w in entry['words']:
                words[w.lower()] = words.get(w.lower(), 0) + amount

    return words

def remain_entry(filename, limit_list):
    remain_ent = []
    total_amount = 0
    with open(filename, 'r') as f:
        obj = json.load(f)
        for entry in obj:
            amount = entry['amount']
            remain = True
            for w in entry['words']:
                if w.lower() in limit_list:
                    remain = False
                    break
            if remain:
                total_amount += amount
                remain_ent.append(entry['description'])

    return total_amount, len(remain_ent), remain_ent


if __name__ == '__main__':
    words = load_words('output/expense_summary.json')
    for w in words:
        sets = wn.synsets(w, 'n')
        if len(sets) > 0:
            sets = wn.synsets(w)
            net = sets[0]
            print(w, net)
            while net is not None:
                net = net.hypernyms()
                print(net)
                if len(net) != 0:
                    net = net[0]
                else: net = None
        # if len(sets) > 0: print(sets[0].definition())
        # if len(sets) == 0: print(w)