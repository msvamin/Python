__author__ = 'amin'

# Removing duplicate names in a list

def rem_dupl(my_ls):
    new_ls = [my_ls[0]]
    for n in my_ls[1:]:
        fl = 0
        for m in new_ls:
            if n == m:
                fl = 1
        if fl == 0:
            new_ls.append(n)
    return new_ls

def main():
    my_ls = ['Joe', 'Jack', 'Amin', 'Joe', 'Rose', 'Amin', 'Joe', 'Jack']
    print(rem_dupl(my_ls))

if __name__ == "__main__":
    main()


