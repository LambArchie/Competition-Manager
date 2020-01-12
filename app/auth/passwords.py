"""
Controls passwords checks
"""
from hashlib import sha1
from urllib.request import Request, urlopen
from flask import current_app

PWNED_PASSWORD_API = "https://api.pwnedpasswords.com/range/"

def strength_check(password):
    """Checks if password reaches minimum requirement
    Returns True if meets requirements, or string with error if issue"""
    check = length_check(password)
    if check != 0:
        return check
    if current_app.config['HIBP_PW_CHECK'] is True:
        check = pwned_passwords_check(password)
        if check != 0:
            return "Password has been leaked {} times before".format(check)
    return 0

def pwned_passwords_check(password):
    """Uses pwned passwords api"""
    pw_hash = sha1(password.encode()).hexdigest()
    hash_prefix = pw_hash[:5]
    hash_suffix = pw_hash[5:].upper()
    response = Request(url=PWNED_PASSWORD_API + hash_prefix, headers={
        'User-Agent': 'Competition Manager'})
    for line in urlopen(response).read().decode().split('\r\n'):
        suffix, count = line.split(":")
        if suffix == hash_suffix:
            return count
    return 0

def length_check(password):
    """Checks minimum length, gets value from config"""
    if len(password) < int(current_app.config['MIN_LENGTH']):
        return "Needs to be {} characters long".format(current_app.config['MIN_LENGTH'])
    return 0
