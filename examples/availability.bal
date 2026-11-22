# BAL's native bio-availability function.
let dds_rate = 0.70
let first_pass = 0.15
let feedback = 0.40
let alpha = 2.0
let beta = 1.2
let y = availability(dds_rate, first_pass, feedback, alpha, beta)
let assessment = threshold(dds_rate, first_pass, feedback, alpha, beta)
print "Normalized availability:"
print y
if assessment["above"] {
    print "The modeled value is above the y=1 threshold."
} else {
    print "The modeled value is at or below the y=1 threshold."
}
