import random

# Jokes
jokes = {"Why do birds fly south in the winter?":
             "Because it's too far to walk.",
         "How are an elephant and a plum alike?":
             "They're both purple, except the elephant.",
         "Why didn't the toilet paper cross the road?":
             "It got stuck in a crack.",
         "What's the difference between a bicycle?":
             "An orange, because a vest has no sleeves.",
         "What is love?":
             "Baby don't hurt me.",
         "Dogs can't see your bones.":
             "But CAT scan.",
         "Don't you know vampires aren't real?":
             "Unless you Count Dracula.",
         "Speak to a representative.":
             "I'll get right on that.",
         "What kind of bear is best?":
             "False. Black bear.",
         "Fact: bears eat beets.":
             "Bears. Beets. Battlestar Galactica.",
         "Why did the student go to GA Tech?":
             "To get a valuable degree in a STEM field.",
         "Why did the elephant fall out of a tree?":
             "The hippopotamus pushed him out.",
         "Why do ducks have webbed feet?":
             "To stamp out forest fires.",
         "Why do elephants have flat feet?":
             "To stamp out flaming ducks."}

# Funny messages
messages = ["Asking Steve Jobs for permission...",
            "Engaging the retro-thrusters...",
            "Correct! Self-destruct sequence terminated.",
            "Finishing my game of Candy Crush...",
            "Checking my Facebook notifications...",
            "If you insist...",
            "Ok, but only because you asked nicely.",
            "Calculating pi to 2 billion digits...",
            "Your wish is my command..."]

# Funny error messages
errmsgs = ["Incorrect PIN! Notifying the authorities...",
           "Really? Is that your best guess?",
           "Hint: try 1234.",
           "Incorrect PIN! 32,568 tries remaining.",
           "May God have mercy upon your soul.",
           "Poop.",
           "Try again after coffee.",
           "No way!",
           "Try asking nicely next time.",
           "Incorrect PIN! Initiating self-destruct sequence..."]

def joke():
    setup = random.choice(list(jokes.keys()))
    punch = jokes[setup]
    return setup, punch

def funny_message():
    return random.choice(messages)

def funny_error_message():
    return random.choice(errmsgs)
