__author__ = 'amin'

# This is a program to find the longest palindrome in a string

import sys

def longest_palin(my_str):
    l = len(my_str)
    for i in range(l):
        for j in range(i):
            st = my_str[i-j:l-j]
            if st == st[::-1] and len(st) != 1:
                return st
    return ""

def main():
    my_str = input("Enter your string: ")
    print(longest_palin(my_str))

if __name__ == "__main__":
    main()

