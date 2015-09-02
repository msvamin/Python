__author__ = 'amin'

# Check for Anagram strings
def check_anagram(str1, str2):
    str1 = str1.lower()
    str2 = str2.lower()
    str1 = sorted(str1)
    str2 = sorted(str2)
    if str1 == str2:
        return True
    return False

def main():
    str1 = "Amin Mousavi"
    str2 = "Nimaiva SOUM"
    print(check_anagram(str1, str2))

if __name__ == "__main__":
    main()