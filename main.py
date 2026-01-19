import sqlite3
import os
import tkinter as tk
from tkinter import ttk#, messagebox, font, PhotoImage

def print_db_rows():
    querry = dbCursor.execute("SELECT * from tasks")
    if len(querry.fetchall()) < 1:
        print("There are no tasks to show yet.")
        return
    state = ""
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

def get_database_items():
    dbCursor.execute("SELECT * from tasks")
    querry = dbCursor.fetchall()
    if len(querry) < 1:
        print("There are no tasks to show yet.")
    return querry

def add_entry_GUI_button(entryText, tasks_frame, labels, buttons):
    # Appends a new entry to the list
    register_task(entryText)
    querry = select_last()
    database_length = len(get_database_items())
    if querry[2] == 1:
        state = "(done)"
    else:
        state = "(to-do)"

    label = tk.Label(tasks_frame, text=database_length) 
    button = tk.Button(tasks_frame, text=entryText, command=lambda value=database_length: wrapped_functions_GUI_button(value, labels[value - 1]))
    buttons.append(button)
    labelState = tk.Label(tasks_frame, text=state)
    labels.append(labelState)

    label.grid(column=0, row=database_length, padx=15)
    button.grid(column=1, row=database_length, sticky='we', pady=5, padx=5)
    labelState.grid(column=3, row=database_length)
    # INFO: possible refactor opportunity

def select_last():
    dbCursor.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 1")
    querry = dbCursor.fetchone()
    return querry

def draw_tasks_GUI(querry, root):
    # Tasks frame
    tasks_frame = tk.Frame(root, bg="lightblue")
    tasks_frame.pack()
    # Defaults
    state = ""
    index = 0
    # Lists to directly access tkinter widgets generated in the loop
    labels = [] # For done/to-do
    buttons = [] # Buttons that flip done/to-do

    for row in querry:
        # 1 means done 0 means to-do
        if row[2] == 1:
            state = "(done)"
        else:
            state = "(to-do)"
        #row[0] is the internal id of the task. Index is a tidier number ordering system.
        label = tk.Label(tasks_frame, text=str(index + 1))

        # the lambda function ensures the value sent to flip_done_undone is the internal id of when the button was created in the loop, not some random static id.
        button = tk.Button(tasks_frame, text=(row[1]), command=lambda value=[row[0], index]: wrapped_functions_GUI_button(value[0], labels[value[1]]))# update live done and undone states
        buttons.append(button)

        labelState = tk.Label(tasks_frame, text=state)
        labels.append(labelState)

        # Creating grid
        content = ttk.Frame(tasks_frame)
        content.grid(column=0, row=index)
        
        # Placing the grid and everything inside
        label.grid(column=0, row=index, padx=15)
        button.grid(column=1, row=index, sticky='we', pady=5, padx=5)
        labelState.grid(column=3, row=index)
        index += 1

    # Options frame
    options_frame = tk.Frame(root)
    options_frame.pack()
    # Print data in terminal
    buttonPrint = tk.Button(options_frame, text="Print Database", command=print_db_rows)
    buttonPrint.grid(column=1, row=0)
    # Add entry
    entryAdd = tk.Entry(options_frame)
    entryAdd.grid(column=1, row=1)
    # Add button to submit entry
    buttonForEntry = tk.Button(options_frame, text="Add entry", command=lambda : add_entry_GUI_button(entryAdd.get().strip(), tasks_frame, labels, buttons))
    buttonForEntry.grid(column=2, row=1)

def terminal_version():
    currentinput = '0'    
    print("Type help for commands or exit to close")
    dbConnState, dbConnStateMessage = check_db_open()
    while currentinput != 'exit' and dbConnState == True:
        currentinput = input("\n> ").strip()

        # Print all rows.
        if currentinput == '1':
            print_db_rows()

        # Write a new task.
        elif currentinput == '2':
            taskAtHand = input(str(dbConnStateMessage) + "\nWrite a new task. Write 1 to cancel.\n>").strip()
            register_task(taskAtHand)

        # Flip task between done and undone.
        elif currentinput == '3':
            selectId = input("Select a task index to flip between done and undone:\n>")
            flip_done_undone(selectId)

        # If no available commands are given.
        elif currentinput == 'help':
            print("Type:\n1 - read all tasks inside the database\n2 - add task\n3 - flip done/undone\nexit - closes program")

def GUI_version():
    querry = get_database_items()
    # Main window
    root = tk.Tk()
    root.title("To-do list")

    draw_tasks_GUI(querry, root)

    # Starting
    root.mainloop()

    #TODO: make temporary buffer for tasks, then dbConn.commit()

# ^^^Function declarations above^^^

# Creating a path to application relative to main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct full absolute path to the database inside folder db
db_path = os.path.join(BASE_DIR, 'db', 'todo.db')
# Connecting and starting cursor
dbConn = sqlite3.connect(db_path)
dbCursor = dbConn.cursor()
# Make sure the table checks if it exists every time program is opened
dbCursor.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, name TEXT NOT NULL, state INT NOT NULL DEFAULT 0)")

# Entering
print("Program entered.")
GUI_version()
#terminal_version()

# Exiting
dbConn.close()
print("Connection has been closed.\nProgram exited.")