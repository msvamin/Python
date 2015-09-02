__author__ = 'amin'

# Counting the occurrence of a character in a string
def count_occurr(my_str, ch):
    my_str = my_str.lower()
    ch = ch.lower()
    k = 0
    for i in my_str:
        if i == ch:
            k = k +1
    return k

def main():
    my_str = "Amin Mousavi"
    ch = "M"
    print(count_occurr(my_str, ch))

if __name__ == "__main__":
    main()