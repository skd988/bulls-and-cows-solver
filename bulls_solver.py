import random as rnd

LENGTH_OF_CODE = 4
DIGIT = 0
INDEX = 1

def subsets(lst, size):
    subsets_by_length = [[[]]]
    for _ in range(size):
        curr_subsets = []
        for sub in subsets_by_length[-1]:
            for i in range(lst.index(sub[-1]) + 1 if len(sub) else 0, len(lst)):
                curr_subsets += [sub[:] + [lst[i]]]
        subsets_by_length += [curr_subsets]
        
    return subsets_by_length


def produce_number(possibilities):
    if len(possibilities) == 0:
        return random_code(False)

    open = set(range(LENGTH_OF_CODE))
    suggestion = [-1] * LENGTH_OF_CODE
    bulls, cows, misses = rnd.choice(list(possibilities))
    possible_digits = set(range(10)) - set(misses)

    for bull in bulls:
        suggestion[bull[INDEX]] = bull[DIGIT]
        open -= {bull[INDEX]}
        possible_digits -= {bull[DIGIT]}

    cows_indices_dict = {}
    for cow in cows:
        cow_places = open - cow[INDEX]
        if len(cow_places) == 0:
            replacements = [rep for rep in cows if rep[DIGIT] in cows_indices_dict.keys() 
                                                and (open - rep[INDEX]) 
                                                and cows_indices_dict[rep[DIGIT]] not in cow[INDEX]]

            if len(replacements) == 0:
                possibilities.remove((bulls, cows, misses))
                return produce_number(possibilities)
            
            rep = rnd.choice(replacements)
            index = cows_indices_dict[rep[DIGIT]]
            suggestion[index] = cow[DIGIT]
            cows_indices_dict[cow[DIGIT]] = index
            cow_places = open - rep[INDEX]
            cow = rep
        index = rnd.choice(list(cow_places))
        suggestion[index] = cow[DIGIT]
        open -= {index}
        possible_digits -= {cow[DIGIT]}
        cows_indices_dict[cow[DIGIT]] = index
    
    for i in open:
        if len(possible_digits) == 0:
            possibilities.remove((bulls, cows, misses))
            return produce_number(possibilities)
        dig = rnd.choice(list(possible_digits))
        suggestion[i] = dig
        possible_digits -= {dig}
    
    return suggestion
    
def poss_for_score(score):
    guess, bulls, cows = score
    possibilities = []
    possible_bulls = subsets(range(LENGTH_OF_CODE), bulls)[-1]
    for bull_subset in possible_bulls:
        cows_choice = list(set(range(LENGTH_OF_CODE)) - set(bull_subset))
        possible_cows = subsets(cows_choice, cows)[-1]
        for cow_subset in possible_cows:
            misses_subset = list(set(cows_choice) - set(cow_subset))
            possibilities += [(frozenset({(guess[i], i) for i in bull_subset}), 
                                frozenset({(guess[i], frozenset({i})) for i in cow_subset}), 
                                frozenset({guess[i] for i in misses_subset}))]
    
    return possibilities

def solver(scores, possibilities=[]):
    if not type(scores) is list:
        scores = [scores]

    for score in scores:
        poss = poss_for_score(score)
        if len(possibilities) == 0:
            possibilities = poss
        else:
            possibilities = combine_possibilities_lists(possibilities, poss)

    return possibilities
    
def combine_possibilities_lists(poss_lst1, poss_lst2):
    combined = set()
    for poss1 in poss_lst1:
        for poss2 in poss_lst2:
            combination = combine_possibilities(poss1, poss2)
            if combination:
                combined.add(combination)

    return list(combined)

def validate_hits_misses(hits, misses):
    return len({h[DIGIT] for h in hits} & misses) == 0

def validate_bulls(bulls1, bulls2):
    for bull1 in bulls1:
        for bull2 in bulls2:    
            #if the digits are equal
            if bull1[DIGIT] == bull2[DIGIT]:
                #if the digits are equal but the indices are different
                if bull1[INDEX] != bull2[INDEX]:
                    return False
            
            #if the bulls are overlapping (and the digits aren't equal)
            elif bull1[INDEX] == bull2[INDEX]:
                return False

    return True

def create_combined_cows(bulls1, cows1, bulls2, cows2):
    new_bulls = set()

    cows1 = validate_bulls_cows(bulls2, cows1)
    cows2 = validate_bulls_cows(bulls1, cows2)

    if cows1 == None or cows2 == None:
        return
    
    combined_cows = cows1 | cows2
    for cow1 in cows1:
        for cow2 in cows2:
            if cow1[DIGIT] == cow2[DIGIT]:
                combined_cows.discard(cow1)
                combined_cows.discard(cow2)
                index = frozenset(cow1[INDEX] | cow2[INDEX])
                if len(index) == LENGTH_OF_CODE:
                    return
                elif len(index) == LENGTH_OF_CODE - 1:
                    new_bulls.add((cow1[DIGIT], list(set(range(LENGTH_OF_CODE)) - index)[0]))
                else:
                    combined_cows.add((cow1[DIGIT], index))
                
                break

    return combined_cows, new_bulls

def validate_bulls_cows(bulls, cows):
    new_cows = set(cows)
    for bull in bulls:
        for cow in cows:
            if bull[DIGIT] == cow[DIGIT]:
                if bull[INDEX] in cow[INDEX]:
                    return
                new_cows.remove(cow)
            
    return new_cows
  
def combine_possibilities(poss1, poss2):
    bulls1, cows1, misses1 = poss1
    bulls2, cows2, misses2 = poss2

    bulls_combined = bulls1 | bulls2
    misses_combined = misses1 | misses2
    if not validate_hits_misses(bulls_combined | cows1 | cows2, misses_combined):
        return

    if not validate_bulls(bulls1, bulls2):
        return
    
    ret = create_combined_cows(bulls1, cows1, bulls2, cows2)
    if not ret:
        return
    
    cows_combined, new_bulls = ret

    bulls_combined |= new_bulls

    if len(bulls_combined) + len(cows_combined) > LENGTH_OF_CODE:
        return
    
    if LENGTH_OF_CODE - len(bulls_combined) - len(cows_combined) > 10 - len(misses_combined):
        return

    return (frozenset(bulls_combined), frozenset(cows_combined), frozenset(misses_combined))


def score(code, guess):
    bulls = 0

    cnt_code = [0] * 10
    cnt_guess = [0] * 10
    for c, g in zip(code, guess):
        if c == g:
            bulls += 1
        else:
            cnt_code[c] += 1
            cnt_guess[g] += 1
                            
    return bulls, sum([min(c, g) for c,g in zip(cnt_code, cnt_guess)])


def random_code(dups):
    return [rnd.randint(0, 9) for _ in range(LENGTH_OF_CODE)] if dups else \
            rnd.sample(range(10), LENGTH_OF_CODE)


def game(code, dups, to_solve=False):
    guess = ''
    num_of_guesses = 0
    scores = []
    possibilities = []
    while guess != code:
        num_of_guesses += 1
        guess = ''
        while not guess.isdigit() or len(guess) != LENGTH_OF_CODE or (not dups and len(set(guess)) != LENGTH_OF_CODE):
            suggestion = "".join([str(s) for s in produce_number(possibilities)])
            print(suggestion)
            if to_solve:
                guess = suggestion
            else:
                guess = input('Enter your guess:')

            if guess == 'tell me':
                print('cheater!', code)
            elif guess == 'i give up':
                print('loser!', code)
                exit()
        
        guess = [int(dig) for dig in guess]
        bulls, cows = score(code, guess)
        
        print(bulls, 'bulls', ',', cows, 'cows')
        scores += [(guess, bulls, cows)]
        possibilities = solver(scores[-1], possibilities)
        
    
    print('you\'ve won! in', num_of_guesses, 'guesses')
    return num_of_guesses

def main():
    if type(LENGTH_OF_CODE) is not int or not 0 < LENGTH_OF_CODE <= 10:
        print('Error: invalid length of code')
        exit()
        
    dups = False
    guesses = []
    for _ in range(100):
        guesses.append(game(random_code(dups), dups, True))
        print(sum(guesses) / len(guesses))
        

if __name__ == '__main__':
    main()