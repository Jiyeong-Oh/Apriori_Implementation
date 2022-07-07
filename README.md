# Apriori_Implementation
## Apriori 알고리즘 구현으로 Association Rules 추출하기 (Association Rules with Apriori Algorithm)

Apriori는, "어떤 itemset이 frequent하다면 그 모든 subset들이 무조건 frequent하다"는 Downward Closure Property를 기반으로 Frequent Pattern을 추출하는 알고리즘이다.

여기서는 Apriori에 대한 이해를 바탕으로, 알고리즘을 직접 구현해 Association Rule을 추출하는 과정을 포스팅할 것이다.
- - -

## 하나, Apriori 구현
먼저 Apriori 알고리즘을 구현하고, 알고리즘을 사용하여 FP를 추출하는 코드를 작성했다.

 

### 1. Initial Frequent Item 만들기
먼저 initial candidate itemset (C1)과 initial frequent itemset(L1)을 만들었다.

c1은 전체 데이터셋에서 모든 길이 1짜리 product itemset을 그 support를 value로 하여 딕셔너리 형태로 만들었고,

L1은 C1 중에서 minimum support 이상의 itemset을 필터링해 역시 딕셔너리 형태로 만들었다.


```
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
```


### 2. 이전 State로부터 다음 Candidate 생성 (Candidate Generation)

L(k)로부터, 길이가 1 더 긴 다음 state(k+1)의 candidate C(k+1)를 생성하는 코드는 두 가지 케이스로 나누어서 작성했다.

이유는, k가 1인 상태에서 C2를 만드는 과정에서는 pruning 과정이 필요하지 않기 때문이었다.

(이미 C2를 구성하는 요소 모두가 frequent item(L1에 속함)임을 생각하면 쉽다.)

 

따라서, (1) k가 1인 경우, (2) k가 2 이상인 경우로 나누어 candidate generation 코드를 작성했다.

k가 1인 경우는 pruning을 진행하지 않고, k가 2 이상인 경우는 self-joining과 pruning을 모두 진행하도록 했다.

이후에, 만든 candidate를 바탕으로 다음 state의 L을 생성했다.


```
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
```

계속해서 itemset의 길이를 1씩 늘리면서, frequent item이 없을때까지 과정을 반복하도록 했다.

 - - -

## 둘, Association Rule 추출하기

구현한 Apriori 알고리즘으로 생성한 frequent pattern을 바탕으로, 전체 데이터를 다시 스캔하면서 각 frequent pattern의 Association Rule을 계산했다.

각 pattern의 support와 confidence가 계산되는 것을 확인할 수 있다.


```
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
 ```
 
