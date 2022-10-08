# SPDX-FileCopyrightText: 2021 jfabernathy for Adafruit Industries
# SPDX-License-Identifier: MIT

# adafruit_requests usage with a CircuitPython socket
# this has been tested with Adafruit Metro ESP32-S2 Express
import random
import ssl
import wifi
import socketpool

import adafruit_requests as requests

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


def handle_escapes(question_text):
    return question_text.replace("&#039;", "'").replace("&quot;", '"')


def ask_category():
    category_dict = {'any': 'Any Category', '9': 'General Knowledge', '10': 'Entertainment: Books', '11': 'Entertainment: Film', '12': 'Entertainment: Music', '13': 'Entertainment: Musicals &amp; Theatres', '14': 'Entertainment: Television', '15': 'Entertainment: Video Games', '16': 'Entertainment: Board Games', '17': 'Science &amp; Nature', '18': 'Science: Computers', '19': 'Science: Mathematics', '20': 'Mythology', '21': 'Sports', '22': 'Geography', '23': 'History', '24': 'Politics', '25': 'Art', '26': 'Celebrities', '27': 'Animals', '28': 'Vehicles', '29': 'Entertainment: Comics', '30': 'Science: Gadgets', '31': 'Entertainment: Japanese Anime &amp; Manga', '32': 'Entertainment: Cartoon &amp; Animations'}
    print("Which Category Would You Like?")
    print("-------------")
    for cat_id in category_dict.keys():
        print(f"{cat_id}: {category_dict[cat_id]}")
    print("-------------")

    return input("Enter Id: ")


print("Connecting")
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected!")
print("My IP address is", wifi.radio.ipv4_address)

socket = socketpool.SocketPool(wifi.radio)
https = requests.Session(socket, ssl.create_default_context())


chosen_category = ask_category()

TRIVIA_URL = f"https://opentdb.com/api.php?amount=10&category={chosen_category}"

print("Fetching JSON data from %s" % TRIVIA_URL)
response = https.get(TRIVIA_URL)
# print("-" * 40)

questions = response.json()["results"]
cur_question = 0
score = 0

while cur_question < len(questions):
    cur_question_obj = questions[cur_question]
    unescaped_question = handle_escapes(cur_question_obj["question"])
    print("---------------------")
    print(f"Question {cur_question+1}: {unescaped_question}")

    choices = cur_question_obj["incorrect_answers"]
    choices.append(cur_question_obj['correct_answer'])
    shuffled_choices = []

    unescaped_correct_answer = handle_escapes(cur_question_obj["correct_answer"])

    if cur_question_obj["type"] == "multiple":
        print("---------------------")
        while len(shuffled_choices) < len(choices):
            cur_choice = random.choice(choices)
            if cur_choice not in shuffled_choices:
                shuffled_choices.append(cur_choice)
        for choice in shuffled_choices:
            print(handle_escapes(choice))
    print("-------------------")
    answer = input("What is your answer? ")
    if answer == unescaped_correct_answer:
        print("Correct!")
        score += 1
    else:
        print("Incorrect")
        print(f"The Correct Answer Is: {cur_question_obj['correct_answer']}")

    print(f"Current Score Is: {score}")
    cur_question += 1

print("-------------------")
print(f"You Scored: {score}")
# print("JSON Response: ", questions)
# print("-" * 40)
