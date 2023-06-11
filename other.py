a = 41217

cur = hex(a)[2:]
# print(hex(a))
def trans(num):
    list_1 = list()
    for i in range(0,len(num),2):
        list_1.append(num[i:i+2])
    list_1.reverse()
    print(''.join(list_1))
    return (int(''.join(list_1),16))

# list2 = []
# for i in list2:
#     print(i,trans(i))
b =  0.636292
a = trans(cur)
print(b/a)