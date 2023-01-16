import filter
import io
import pandas as pd
from country_list import countries_for_language
import random
import numpy as np

countries_De = list(dict(countries_for_language('de')).values())
countries_En = list(dict(countries_for_language('en')).values())

# Birthday tests

def birthday_test():

    birthday_list = [
    "15.01.2022", "5.01.22, 05.1.22,", "06.22.94", "6.22.94", "6.2.94", "06.02.1994",
    "15/01/2022", "5/01/22, 05/1/22,", "06/22/94", "6/22/94", "6/2/94", "06/02/1994",
    "15-01-2022", "5-01-22, 05-1-22,", "06-22-94", "6-22-94", "6-2-94", "06-02-1994",
    ]   

    test_string1 = "My birthday is on "
    addon = " and this is great"
    test_string2 = "Birthday:"

    length = len(birthday_list)
    privacy_filter = filter.PrivacyFilter()
    result = []
    for e in birthday_list:
        s = test_string1 + e + addon
        s2 = test_string2 + e
        result.append(privacy_filter.identify_birthdays(s,None))
        result.append(privacy_filter.identify_birthdays(s2, None))
    if len(result) == 2*length:
        return True
    else:
        return False
    
# Email tests

def email_test():
    privacy_filter = filter.PrivacyFilter()
    test_string1 = "My email is "
    addon = " and this is great"
    test_string2 = "Mail:"
    result = []
    positive = None
    negative = None
    with open("emails.txt", encoding="utf8") as file:
        lines = file.readlines()
        length = len(lines)
        for e in lines:
            s = test_string1 + e + addon
            s2 = test_string2 + e
            result.append(privacy_filter.identify_email(s))
            result.append(privacy_filter.identify_email(s2))         
        if len([e for e in result if e is not None]) == 2*length:
            positive = True
        else: 
            return False
    with open("noemails.txt", encoding="utf8") as file:
        lines = file.readlines()
        length = len(lines)
        result = []
        for e in lines:
            s = test_string1 + e + addon
            s2 = test_string2 + e
            result.append(privacy_filter.identify_email(s))
            result.append(privacy_filter.identify_email(s2))
        if len([e for e in result if e is not None]) == 0:
            negative = True
    if negative and positive:
        return True
    else:
        return False
    
# ZIP codes tests

def zip_test():
    zip_codes = pd.read_csv("German-Zip-Codes.csv", delimiter=";", dtype = {'Plz': str, 'Vorwahl': str})
    samples = zip_codes.sample(n = 30)
    teststring = "I live in "
    teststring2 = " and i like Zeiss"
    privacy_filter = filter.PrivacyFilter()
    result = []
    for e in samples.values:
        text = teststring + str(e) + teststring2
        result.append(privacy_filter.identify_postal_codes(text))
    if len([e for e in result if e is not None]) == 30:
        return True
    else:
        return False

# Names tests

def name_test():
    first_names = pd.read_csv("firstnames.csv")
    last_names = pd.read_csv("lastnames.csv")
    names = list(first_names["vorname"].values)
    names.extend(list(last_names["nachname"].values))
    names = random.sample(names, 100, )
    teststring = "Das ist "
    result = []
    privacy_filter = filter.PrivacyFilter()
    for name in names:
        text = teststring + name
        result.append(privacy_filter.identify_names(text))
    return len([e for e in result if e is not None])/len(names)
# Nationalities tests

def nationality_test():
    countries_De.extend(countries_En)
    countries = random.sample(countries_De, 100)
    result = []
    privacy_filter = filter.PrivacyFilter()
    teststring = "I am from "
    for name in countries:
        text = teststring + name
        result.append(privacy_filter.identify_nationality(text))
    if len([e for e in result if e is not None]) == len(countries):
        return True
    else:
        return False
# Overall tests

def test_all():
    print("Birthday test:" + str(birthday_test()))
    #print("Email test:" + str(email_test()))
    print("Name test:" + str(name_test()))
    print("ZIP test:" + str(zip_test()))
    print("Nationalty test:" + str(nationality_test()))


test_all()