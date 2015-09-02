__author__ = 'amin'

def remcharstr(my_str, my_char):
    res = ""
    # For every character checks if it equals to the given character
    for c in my_str:
        if c != my_char:
            res = res + c
    return res

def main():
    my_str = input("Enter your string: ")
    my_char = input("Enter your character: ")
    print(remcharstr(my_str, my_char))

if __name__ == "__main__":
    main()
