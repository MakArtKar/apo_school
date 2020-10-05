import vk_features
from time import sleep
import random

'''

offsets = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

api = vk_features.login_to_vk()

file = open("dates.txt", 'w')

pack_size = 1000

for i in range(40):
    cur = api.groups.getMembers(group_id='hsemem', offset=pack_size * i, count=pack_size, fields=['bdate'])['items']

    sleep(vk_features.request_delay)

    for x in cur:
        if 'bdate' in x:
            d = x['bdate'].split('.')
            print(offsets[int(d[1]) - 1] + int(d[0]) - 1, file=file)

    print(i)
    
file.close()

'''

def calc(people):
    res = 1.0
    num = 1
    den = 1

    for i in range(people):
        num *= 365 - i
        den *= 365

    return 1 - num / den


dates = []
file = open("dates.txt", 'r')

for s in file:
    dates.append(int(s))

file.close()

to_choose = 24
samples = 10000

cnt = 0
for i in range(samples):
    cur = random.sample(dates, to_choose)

    if len(set(cur)) != len(cur):
        cnt += 1

print(cnt / samples)
print(calc(to_choose))
