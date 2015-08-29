__author__ = 'amin'

# Finding all permutations of a string in an iterative way
def perm_iter(my_str):
    N = len(my_str)
    p = range(N)
    i = 1

# Finding all permutations of a string in a recursive way
def perm_recur(my_str):
    if len(my_str) == 1:
        return my_str
    prev_perms = perm_recur(my_str[1:])
    ch = my_str[0]
    result = []

    for p in prev_perms:
        for i in range(len(p)+1):
            result.append(p[:i] + ch + p[i:])
    return result

def main():
    my_str = "Amin"
    print(perm_recur(my_str))

if __name__ == "__main__":
    main()
