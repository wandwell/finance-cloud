# Overview

A basic Finance Manager that allows users to keep create a budget, track transactions, and manage liquid assets.

Made for the purpose of learning how to utilize cloud databases, specifically firebase and firestore.

[Software Demo Video]([https://youtu.be/GZEbdH2U78A])

# Cloud Database

Google Firestore
Google Firebase

I used authentication through Google Firebase, passing the userId as the id for the users collection in firestore. Besides users, I have 3 other collections: transactions, budgets, and assets. Each document contains a userId used to filter out access by which user is signed in.

# Development Environment

Google Firebase
Google Firestore
Python
Pyrebase

# Useful Websites

- [Google Firebase]([https://firebase.google.com/])
- [Python Documentation]([https://www.python.org/doc/])

# Future Work

- Create a UI
- Allow for Admin to see data for all users

