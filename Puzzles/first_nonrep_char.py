__author__ = 'amin'

# Finding the first non-repeated character in a string

def find_fnrchar(my_str):
    my_str = my_str.lower()
    str_len = len(my_str)
    for i in range(str_len):
        fl = 0
        for j in range(i+1, str_len):
            if my_str[i] == my_str[j]:
                fl = 1
        if fl == 0:
            return my_str[i]
    return ""

def main():
    my_str = "Amin Mousavi"
    print(find_fnrchar(my_str))

if __name__ == "__main__":
    main()