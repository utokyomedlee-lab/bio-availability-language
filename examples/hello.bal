# Variables, lists, functions and loops in BAL.
let language = "BAL"
print "Hello from " + language + "!"

fn square(value) {
    return value * value
}

let numbers = [1, 2, 3, 4, 5]
let total = 0
let index = 0
while index < numbers.length {
    total = total + square(numbers[index])
    index = index + 1
}
print "Sum of squares:"
print total
