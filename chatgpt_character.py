import time
import keyboard
from rich import print
from openai_chat import OpenAiManager
import json
import os

BACKUP_FILE = "ChatHistoryBackup.txt"
INPUT_FILE = "input.txt"
READ_KEY = "f4"

openai_manager = OpenAiManager()

print("[yellow]Do you need to use the backup file? (y/n)\n")
start = True
while start:
    user_input = input().lower()
    if user_input == "y":
        use_backup = True
        start = False
    if user_input == "n":
        use_backup = False
        start = False

if use_backup:
    # Load chat history from BACKUP_FILE
    with open(BACKUP_FILE, "r") as file:
        chat_history = json.load(file)

    openai_manager.chat_history = chat_history
else:
    FIRST_SYSTEM_MESSAGE = {
        "role": "system",
        "content": '''
        You are a unnamed assistant for a STEM teacher. In this conversation, you will be given code snippets of a student around the ages 7-10. You will then evaluate if the student is struggling and warn the teacher. You will receive the question the student is on and a list of blocks that correspond to simple code. The map is as followed: Block 1 - move forward "value", Block 2 - move backward "value", Block 3 - turn right, Block 4 - turn left, Block 5 - repeat "value", where 'value' is a unit in centimeters. A example of a input is: ["Block 1", "30", "Block 3", "90"] where when translated, "When green flag is clicked, Move forward 30 cm, Turn right 90 degree."

        While responding, you must obey the following rules: 
        1) Provide responses in this format: [question number, bool if student needs help]
        2) Always stay in character, no matter what.
        3) Give the student some time before you flag the teacher.
        4) You will revive a new input every minute.
        5) If you receive the same/similar over a short period of code do not respond.
        6) If you receive the same/similar over a long period of time warn the teacher.
        7) When the student is struggling, flag the teacher.
        8) If the student is not struggling, do not flag the teacher.
        
        Example of a conversation:
        input: 'Q2) Move and Turn - Write a program to make the robot move forward 30 cm and then take a right turn.' ["Block 1", "5", "Block 3", "90"]
        output: [2, false]
                                
        Example of a conversation:
        input: 'Q3) Move in a Square - Write a program to make the robot move in a square with side length of 40 cm.' ["Block1", "40", "Block 3", "90", "Block1", "4"]
        output: [3, false]
        input: 'Q3) Move in a Square - Write a program to make the robot move in a square with side length of 40 cm.' ["Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "0"]
        output: [3, false]
        input: 'Q3) Move in a Square - Write a program to make the robot move in a square with side length of 40 cm.' ["Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1"]
        output: [3, false]
        this happens over a long period of time{
        input: 'Q3) Move in a Square - Write a program to make the robot move in a square with side length of 40 cm.' ["Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1"]
        output: [3, false]
        }
        input: 'Q3) Move in a Square - Write a program to make the robot move in a square with side length of 40 cm.' ["Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1"]
        output: [3, true]
        
        Example of a conversation:
        after a long time {
        some filler conversation
        }
        input: 'Q4) Looping a Square - Write a program to make the robot move in a square of 40 cm using loops.' ["Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90", "Block1", "40", "Block 3", "90"]
        output: [4, true]
        input: 'Q4) Looping a Square - Write a program to make the robot move in a square of 40 cm using loops.' ["Block 5", "4", "Block 1", "25", "Block 3", "90"]
        output: [4, false]

        Okay, let the conversation begin!'''
    }

    openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)


print("\n\n[green]Starting the loop")
print("[green]Press " + READ_KEY + " to read from " + INPUT_FILE + "")
print("[green]Press Ctrl+C to exit the program\n")
while True:

    # Wait until user presses READ_KEY
    if keyboard.read_key() != READ_KEY:
        time.sleep(0.1)
        continue

    print("[green]User pressed " + READ_KEY + " key! Now reading from " + INPUT_FILE + ":")

    input_result = ""
    # Get question from INPUT_FILE
    with open(INPUT_FILE, "r") as file:
        input_result = file.read()
    
    if input_result == "":
        print("[red]Nothing found in " + INPUT_FILE)
        continue

    # Send question to OpenAi
    openai_result = openai_manager.chat_with_history(input_result)
    
    # Write the results to txt file as a backup
    with open(BACKUP_FILE, "w") as file:
        json.dump(openai_manager.chat_history, file, indent=4)

    print("[magenta]" + str(openai_result))

    print("[green]\n------------------------------------\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n------------------------------------\n")
    print("[green]Press " + READ_KEY + " to read from " + INPUT_FILE + "")
    print("[green]Press Ctrl+C to exit the program\n")