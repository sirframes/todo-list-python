import sqlite3
import os
import tkinter as tk
from tkinter import messagebox, ttk#, font, PhotoImage

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
    state = ""
    querry = dbCursor.execute("SELECT * from tasks")
    if len(querry.fetchall()) < 1:
        print("There are no tasks to show yet.")
        return
    for row in dbCursor.execute("SELECT * from tasks"):
        if row[2] == 1:
            state = "(done)"
        else:
            state = "(to-do)"
        print(str(row[0]) + " | " + row[1] + " " + state)

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
    dbCursor.execute("""SELECT state 
                    FROM tasks
                    WHERE id = ?""", (selectId,))
    # result[0] is the state column of the task. Either 0 (undone) or 1 (done).
    result = dbCursor.fetchone()
    if result[0] == None:
        print("Invalid index value.")
    elif result[0] == 0:
        dbCursor.execute("""
        UPDATE tasks
        SET state = 1
        WHERE id = ?""", (selectId,))
        print("Task marked as done.")
    elif result[0] == 1:
        dbCursor.execute("""
        UPDATE tasks
        SET state = 0
        WHERE id = ?""", (selectId,))
        print("Task marked as undone.")
    dbConn.commit()

def register_task(taskAtHand):
    # if user wrote 1 to cancel:
    if taskAtHand == '1':
        print("Registration cancelled.")
    else:
    # if user wrote a task:
        dbCursor.execute("""
            INSERT INTO tasks (name)
            VALUES (?)
        """, (taskAtHand,))
        dbConn.commit()
        print("Task successfully registered.")

def main():
    print("Program entered.")
    currentinput = '0'    
    print("Type:\n1 - read all tasks inside the database\n2 - add task\n3 - flip done/undone\nexit - closes program")
    dbConnState, dbConnStateMessage = check_db_open()
    while currentinput != 'exit' and dbConnState == True:
        currentinput = input("\n> ").strip()

        # Print all rows.
        if currentinput == '1':
            print_db_rows()

        # Write a new task.
        elif currentinput == '2':
            print(dbConnStateMessage)
            taskAtHand = input("Write a new task. Write 1 to cancel.\n>").strip()
            register_task(taskAtHand)

        # Flip task between done and undone.
        elif currentinput == '3':
            selectId = input("Select a task index to flip between done and undone:\n>")
            flip_done_undone(selectId)

        # If no available commands are given.
        elif currentinput != 'exit':
            print("Type:\n1 - read all tasks inside the database\n2 - add task\n3 - flip done/undone\nexit - closes program")
    dbConn.close()
    print("Connection has been closed.\nProgram exited.")

def flip_text_label(label):
# label = where the text label that needs to change in that row is.
    if label["text"] == "(done)":
        label["text"] = "(to-do)"
    else:
        label["text"] = "(done)"

def wrapped_functions_GUI_button(internalTaskID, label):
# Tkinter buttons can only call a single function.
    flip_done_undone(internalTaskID)
    flip_text_label(label)

class MyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("To-do list")
        #def print_db_rows_GUI():
        querry = dbCursor.execute("SELECT * from tasks")
        if len(querry.fetchall()) < 1:
            print("There are no tasks to show yet.")
            return
        state = ""
        index = 0
        # Lists needed to directly access tkinter widgets generated in the loop
        labels = []
        buttons = []

        for row in dbCursor.execute("SELECT * from tasks"):
            # 1 means done 0 means to-do
            if row[2] == 1:
                state = "(done)"
            else:
                state = "(to-do)"
            #row[0] is the internal id of the task. Index is a tidier number ordering system.
            self.label = tk.Label(self.root, text=str(index + 1))

            # the lambda function ensures the value sent to flip_done_undone is the internal id of when the button was created in the loop, not some random static id.
            self.button = tk.Button(self.root, text=(row[1]), command=lambda value=[row[0], index]: wrapped_functions_GUI_button(value[0], labels[value[1]]))# update live done and undone states
            buttons.append(self.button)

            self.labelState = tk.Label(self.root, text=state)
            labels.append(self.labelState)

            # Creating grid
            self.content = ttk.Frame(self.root)
            self.content.grid(column=0, row=index)
            
            # Placing the grid and everything inside
            self.label.grid(column=0, row=index, padx=15)
            self.button.grid(column=1, row=index, sticky='we', pady=5, padx=5)
            self.labelState.grid(column=3, row=index)
            index += 1

        # Print data in terminal
        self.buttonPrint = tk.Button(self.root, text="Print Database", command=print_db_rows)
        self.buttonPrint.grid(column=1, row=index)
        # Add entry
        self.entryAdd = tk.Entry(self.root)
        self.entryAdd.grid(column=1, row=index+1)
        # Add button to submit entry
        self.buttonForEntry = tk.Button(self.root, text="Add entry", command=lambda : print(self.entryAdd.get()))
        self.buttonForEntry.grid(column=2, row=index+1)
        # Starting
        self.root.mainloop()

    #dbConn.commit()
    #dbConn.close()
# ^^^Function declarations above^^^
# entering = 0
# while entering not in("1", "2"):
#     entering = input("Select 1 for GUI and 2 for terminal: ").strip()
# if entering == "1":
#     MyGUI()
# elif entering == "2":
#     main()
MyGUI()