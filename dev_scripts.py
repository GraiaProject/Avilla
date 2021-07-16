import os

def black():
    os.system("black src/avilla")

def isort():
    os.system('isort --profile black src/avilla')

def format():
    isort()
    black()
    