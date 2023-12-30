# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 23:52:14 2023

@author: magnn
"""
import random

listemots = ["Python", "Math", "Robotique", "Voiture"]

points = 0

while True:
    motchois = random.choice(listemots)  # Select a random word
    anagramme = list(motchois)
    random.shuffle(anagramme)
    anagramme = ''.join(anagramme)

    print("Anagramme:", anagramme)

    user_guess = input("Enter the correct word (or 'exit' to quit): ")

    if user_guess == "exit":
        break
    elif user_guess == motchois:
        print("Correct! You gain 10 points.")
        points += 10
    else:
        print("Incorrect. You lose 1 point.")
        points -= 1

print("Game Over. Your total points:", points)
