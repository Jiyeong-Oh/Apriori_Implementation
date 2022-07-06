from itertools import combinations
minimum_support, input_file_name, output_file_name = input().split()
minimum_support = int(minimum_support)

min_sup = minimum_support
file_path = '{}'.format(input_file_name) #'input.txt'

with open(file_path) as f:
    lines = f.read().splitlines()
db = [i.split('\t') for i in lines]
db = [list(map(int, i)) for i in db]

f = open("./{}".format(output_file_name), 'w')
######################################################################################
# C1, L1
c1 = {}
for transaction in db:
    for itemset in transaction:
        if itemset in c1.keys():
            c1[itemset] += 1
        else:
            c1.update({itemset: 0})
            c1[itemset] += 1
c1 = {itemset: sup/len(db)*100 for itemset, sup in c1.items()}
l1 =  {itemset for itemset, sup in c1.items() if sup >= min_sup}

freq_pat = l1
ck = c1
lk = l1
k = 1
######################################################################################

while len(lk) > 0:
    if k == 1: # k가 1에서 2로 갈 때
        #L building
        ckNext = list(combinations(lk, 2))
        ckNext = {itemset: 0 for itemset in ckNext}
        for transaction in db:
            for itemset in ckNext.keys():
                if set(itemset)<=set(transaction):
                    ckNext[itemset] += 1
        ckNext = {itemset: sup/len(db)*100 for itemset, sup in ckNext.items()}
        lkNext =  {itemset for itemset, sup in ckNext.items() if sup >= min_sup}
        
    elif k >= 2: # k가 2 이상에서 3 이상으로 갈 때
        #self joining
        ckNext = list(combinations(lk, 2))
        ckNext = [tuple(set(i[0]) | set(i[1])) for i in ckNext]
        
        temp = []
        for itemset in ckNext:
            if len(itemset)== k+1 and set(itemset) not in temp:
                temp.append(set(itemset))       
        ckNext = temp
        #pruning
        temp = {}
        for itemset in ckNext:
            issubsetCheck = 0
            for subset in list(lk):
                if set(subset) <= itemset:
                    issubsetCheck += 1
                else:
                    continue
            if issubsetCheck == k+1:
                temp[tuple(itemset)] = 0
        ckNext = temp

        #L building
        for transaction in db:
            for itemset in ckNext.keys():
                if set(itemset)<=set(transaction):
                    ckNext[itemset] += 1
        ckNext = {itemset: sup/len(db)*100 for itemset, sup in ckNext.items()}
        lkNext =  {itemset for itemset, sup in ckNext.items() if sup >= min_sup}
    
    freq_pat = freq_pat | lkNext
    lk = lkNext
    
    # association rules writing
    k += 1
    
    for i in lk:
        for j in range(len(i)-1):
            for itemset in list(combinations(list(i), j+1)):
                support = 0
                conf_itemset = 0
                conf_both = 0
                associative_item_set = set(i) - set(itemset)
                for transaction in db:
                    if set(i) <= set(transaction): 
                        support += 1
                    if set(itemset) <= set(transaction):
                        conf_itemset += 1
                        if set(associative_item_set) <= set(transaction):
                            conf_both +=1        
                support = round(support/len(db)*100, 2)
                confidence = round((conf_both/len(db))/(conf_itemset/len(db))*100, 2)
                
                # result printing
                f.write("{}\t{}\t{:.2f}\t{:.2f}\n".format(set(itemset),
                                                  associative_item_set,
                                                  support,
                                                  confidence))
f.close()
