import copy
from collections import Counter

WORD_LEN = 5
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

with open("./wordlist_hidden.txt", "r") as f:
    answer_words_list = f.read().strip().split("\n")

with open("./wordlist_all.txt", "r") as f:
    all_words_list = f.read().strip().split("\n")


possible_answers = copy.copy(answer_words_list)
excluded = []
exist = []
fixed = [None for _ in range(WORD_LEN)]### word length is fixed
unresolved = {}# characters whose locations are not fixed yet


def prompt():
    while True:
        print("your answer:")
        your_answer = input()
        print("""result:
        o matches
        + exists somewhere
        - never
        """)
        result = input()

        if len(your_answer) != WORD_LEN or len(result) != WORD_LEN:
            continue
        if set(list(your_answer)) <= set(list(ALPHABET)) and set(list(result)) <= set(["o", "+", "-"]):
            break


    while True:
        print("check to confirm (y/n):")
        confirm = input()
        if confirm.lower() in ["y", "n"]:
            break
    if confirm.lower() == 'n':
        return False, (None, None)
    return True, (your_answer, result)


def judge(your_answer, correct_answer):
    result = ["-" for _ in range(WORD_LEN)]
    for i, c in enumerate(your_answer):
        if c == correct_answer[i]:
            result[i] = "o"
        elif c in set(list(correct_answer)):
            result[i] = "+"
    return result

def narrow_down_possible_answers(possible_answers, your_answer, result, dry_run=False):
    global excluded, exist, unresolved, fixed
    if dry_run:
        excluded_ = copy.copy(excluded)
    else:
        excluded_ = excluded
        print(excluded)
    for i, (c, r) in enumerate(zip(your_answer, result)):
        if r == 'o':
            if not dry_run:
                if c in unresolved:
                    unresolved.pop(c)
                exist.append(c)
                fixed[i] = c
            possible_answers = filter(lambda w: w[i] == c, possible_answers)
            if c in excluded_:
                excluded_.remove(c)
        elif r == '+':
            if not dry_run:
                exist.append(c)
                unresolved.setdefault(c, []).append(i)
            possible_answers = filter(lambda w: (w[i] != c) and (c in set(list(w))), possible_answers)
            if c in excluded_:
                excluded_.remove(c)
        elif r == '-':
            if c not in exist:
                excluded_.append(c)
        possible_answers = list(possible_answers)# why needed ? if commented out, possible_answers becomes empty
        #print(c, r, len(possible_answers), possible_answers)# debug

    possible_answers = filter(lambda w: set(list(w)) & set(excluded_) == set(), possible_answers)
    possible_answers = list(possible_answers)
    #print(len(possible_answers), possible_answers, excluded_)# debug
    if not dry_run:
        print(excluded)
    return possible_answers


def check_count(possible_answers):
    global fixed, WORD_LEN
    concat = "".join(possible_answers)
    #count_target = ""
    count_for_each_pos = []
    for i, f in enumerate(fixed):
        ith_pos_chars = concat[i::WORD_LEN]
        #if f is None:
        #    count_target += ith_pos_chars
        count = Counter(ith_pos_chars)
        count_for_each_pos.append( (f is None, count) )
        if f is None:
            print(f"position {i}:", end=" ")
            print(count)
    #count = Counter(count_target)
    #for i, (is_fixed, count) in count_for_each_pos:
    #    if is_fi
    #print(count)
    return count_for_each_pos


def search_next_good_words(count_for_each_pos):
    global possible_answers, ALPHABET, WORD_LEN, all_words_list
    #for s in strategies:
    #    for u, input_pos in unresolved.items():
    #        for i in input_pos:
    #            if s[i] == u:
    #                0

    
    if len(possible_answers) < 30:
        word_score_pair = []
        for my_input in all_words_list:
            score = len(possible_answers) ** 2
            for simulated_answer in possible_answers:
                simulated_result = judge(my_input, simulated_answer)
                pos = narrow_down_possible_answers(possible_answers, my_input, simulated_result, dry_run=True)
                #print(simulated_answer, my_input, simulated_result, pos, len(pos))
                if len(pos) == 0:
                    score -= len(possible_answers)
                else:
                    score -= len(pos)
            word_score_pair.append( (my_input, score) )
        word_score_pair = sorted(word_score_pair, key=lambda x:x[1], reverse=True)
        print(word_score_pair[:100])
        for w in word_score_pair[:100]:
            if w in possible_answers:
                print(f"best candidates: {w}")
                break


    else:
        score_memo = [ { a: len(possible_answers) - count_for_each_pos[j][1].get(a, len(possible_answers)) for a in ALPHABET } for j in range(WORD_LEN) ]
        #print(score_memo)
        word_score_pair = [ (w, sum([ score_memo[i][c] for i, c in enumerate(w) ])) for w in all_words_list ]
        word_score_pair = sorted(word_score_pair, key=lambda x:x[1], reverse=True)

        #_, highest = word_score_pair[0]
        #n = sum([ s == highest for _, s in word_score_pair])
        #n = min(1000, max(n, 10))
        n = 20
        print(word_score_pair[:n])


count_for_each_pos = check_count(possible_answers)
search_next_good_words(count_for_each_pos)


while True:
    res, (your_answer, result) = prompt()
    if res == False:
        continue

    possible_answers = narrow_down_possible_answers(possible_answers, your_answer, result)

    print("# of possible_answers =", len(possible_answers))
    if len(possible_answers) < 150:
        print("\n".join(possible_answers))

    if len(possible_answers) == 1:
        print("clear:", possible_answers[0])
        break

    count_for_each_pos = check_count(possible_answers)

    search_next_good_words(count_for_each_pos)


