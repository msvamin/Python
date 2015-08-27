__author__ = 'amin'

import sys



def main():
    my_str = raw_input("Enter your string: ")
    # Check for palindrome strings
    if my_str == my_str[::-1]:
        print("This is a palindrome string!")
    else:
        print("This is NOT a palindrome string!")

if __name__ == "__main__":
    main()