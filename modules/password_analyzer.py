import re

def analyze_password(password):
    strength = 0
    remarks = ""

    # Length check
    if len(password) >= 8:
        strength += 1

    # Character type checks
    if re.search("[a-z]", password):
        strength += 1
    if re.search("[A-Z]", password):
        strength += 1
    if re.search("[0-9]", password):
        strength += 1
    if re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        strength += 1

    # Final rating
    if strength <= 2:
        remarks = "Weak Password"
    elif strength == 3:
        remarks = "Moderate Password"
    elif strength >= 4:
        remarks = "Strong Password"

    return remarks
