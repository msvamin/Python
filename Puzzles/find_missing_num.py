__author__ = 'amin'

# Find missing number in an array of 1-100
def find_missing(my_arr):
    my_arr.sort()
    for i in range(len(my_arr)):
        if my_arr[i] != i+1:
            return i+1

def main():
    my_arr = [i for i in range(1,100)]
    del my_arr[55]
    print(my_arr)
    print(find_missing(my_arr))

if __name__ == "__main__":
    main()

