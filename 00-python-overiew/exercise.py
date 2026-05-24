# Write a python script to input a number
# and tell if the number is divisible by 7 and also 9


# input

# process

# output
# Write a python script to input a number
# and tell if the number is divisible by 7 and also 9

# input
num = int(input("Enter a number: "))

# process and output
if num % 7 == 0 and num % 9 == 0:
    print("The number is divisible by both 7 and 9")
else:
    print("The number is NOT divisible by both 7 and 9")