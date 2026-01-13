import sqlite3
import os
#import tkinter as tk
#from tkinter import ttk, font, messagebox, PhotoImage

# Creating a path to application relative to main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct full absolute path to the database inside folder db
db_path = os.path.join(BASE_DIR, 'db', 'todo.db')

#print("The database directory: " + db_path)

# Connecting and starting cursor
dbConn = sqlite3.connect(db_path)
dbCursor = dbConn.cursor()

# Make sure the table checks if it exists every time program is opened
dbCursor.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, name TEXT NOT NULL, state INT NOT NULL DEFAULT 0)")

def print_db_rows():
    querry = dbCursor.execute("SELECT * from tasks")
    if len(querry.fetchall()) < 1:
        print("There are no tasks to show yet.")
        return
    for row in dbCursor.execute("SELECT * from tasks"):
        mark = "(undone)"
        if row[2] == 1:
            mark = "(done)"
        print(str(row[0]) + " | " + row[1] + " " + mark)

def check_db_open():
    try:
        dbConn.cursor() # Attempt operation
        stateMessage = str(f"Connection is open.")
        return True, stateMessage
    except sqlite3.ProgrammingError as e:
        stateMessage = str(f"Connection is closed: {e}")
        return False, stateMessage
    except Exception as e:
        stateMessage = str(f"Error: {e}")
        return False, stateMessage

def flip_done_undone(selectId):
    dbCursor.execute("""SELECT * 
                    FROM tasks
                    WHERE id = ?""", (selectId,))
    # resultRow is a single selected task.
    resultRow = dbCursor.fetchone()
    if resultRow == None:
        print("Invalid index value.")
    elif resultRow[2] == 0:
        dbCursor.execute("""
        UPDATE tasks
        SET state = 1
        WHERE id = ?""", (selectId,))
        print("Task marked as done.")
    elif resultRow[2] == 1:
        dbCursor.execute("""
        UPDATE tasks
        SET state = 0
        WHERE id = ?""", (selectId,))
        print("Task marked as undone.")
    # resultRow[2] is the state column of the task. Either 0 (undone) or 1 (done).
    dbConn.commit()

def main():
    print("Program entered.")
    currentinput = '0'    
    print("Type:\n1 - read all tasks inside the database\n2 - add task\n3 - flip done/undone\nexit - closes program")
    while currentinput != 'exit':
        currentinput = input(">").strip()
        dbConnState, dbConnStateMessage = check_db_open()

        if dbConnState == True:

            # Print all rows.
            if currentinput == '1':
                print_db_rows()

            # Write a new task.
            elif currentinput == '2':
                print(dbConnStateMessage)
                taskAtHand = input("Write a new task. Write 1 to cancel.\n>").strip()
                if taskAtHand != '1':
                    dbCursor.execute("""
                        INSERT INTO tasks (name)
                        VALUES (?)
                    """, (taskAtHand,))
                    dbConn.commit()
                    print("Task successfully registered.")
                else:
                    print("Registration cancelled.")

            elif currentinput == '3':
                #Flip task between done and undone.
                selectId = input("Select a task index to flip between done and undone:\n>")
                flip_done_undone(selectId)

            else:
                print("Type:\n1 - read all tasks inside the database\n2 - add task\n3 - flip done/undone\nexit - closes program")

        print('')
    dbConn.close()
    print("Connection has been closed.\nProgram exited.")
# ^^^Function declarations above^^^
main()