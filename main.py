import sqlite3
import os
import tkinter as tk
#from tkinter import ttk, messagebox, font, PhotoImage

def print_db_rows():
    dbCursor.execute("SELECT * from tasks")
    querry = dbCursor.fetchall()
    if len(querry) < 1:
        print("There are no tasks to show yet.")
        return

    for row in querry:
        print(str(row[0]) + " | " + row[1] + " | " + get_task_state_str(row[2]))

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
    # result[0] is the state column. 0 = (to-do) | 1 = (done).
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
    dbCursor.execute("""
        INSERT INTO tasks (name)
        VALUES (?)
    """, (taskAtHand,))
    dbConn.commit()
    print("Task successfully registered.")

def delete_task(taskAtHand):
    dbCursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (taskAtHand,))
    dbConn.commit()
    print("Task successfully deleted.")

def get_db_items():
    dbCursor.execute("SELECT * from tasks")
    querry = dbCursor.fetchall()
    return querry

def select_db_last():
    dbCursor.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 1")
    return dbCursor.fetchone()

def flip_text_label(label):
    # label = where the text label that needs to change in that row is.
    if label["text"] == "(done)":
        label["text"] = "(to-do)"
    else:
        label["text"] = "(done)"

def get_task_state_str(internalTaskID):
    # inside the database, 1 = done, 0 = to-do
    if internalTaskID == 1:
        return "(done)"
    else:
        return "(to-do)"

def wrap_func_flip_button(internalTaskID, stateLabels, internalTaskIDList):
    # Tkinter flipButtons can only call a single function.
    index = internalTaskIDList.index(internalTaskID)
    flip_done_undone(internalTaskID)
    flip_text_label(stateLabels[index])

def add_task_to_GUI(entryText, tasks_frame, stateLabels, flipButtons, deleteButtons, labelEmpty, taskIndexLabels, internalTaskIDList):
    """Function for the entry addition button."""
    register_task(entryText)

    row = select_db_last() # Because of register_task this will select the entry just added.
    index = len(get_db_items()) - 1 # The database lenght minus one is the position index.

    if labelEmpty.winfo_ismapped():
        labelEmpty.grid_forget() # Forget (instead of destroy) allows to show the widget again if needed.

    draw_task(row, index, taskIndexLabels, stateLabels, flipButtons, deleteButtons, tasks_frame, labelEmpty, internalTaskIDList)

def change_to_terminal(root):
    """For the menubar button"""
    root.destroy()
    terminal_version()

def draw_task(row, index, taskIndexLabels, stateLabels, flipButtons, deleteButtons, tasks_frame, labelEmpty, internalTaskIDList):

    internalTaskID = row[0]
    internalTaskIDList.append(internalTaskID)
    #index = internalTaskIDList.index(internalTaskID)
    state = get_task_state_str(row[2]) # word that goes inside the label that says done/to-do

    labelIndex = tk.Label(tasks_frame, text=str(index + 1))
    taskIndexLabels.append(labelIndex)

    # the lambda function ensures the value sent to wrap_func_flip_button is the internal id of when the button was created in the loop, not some random static id.
    buttonFlip = tk.Button(tasks_frame, text=(row[1]), command=lambda : wrap_func_flip_button(internalTaskID, stateLabels, internalTaskIDList))# update live done and undone states
    flipButtons.append(buttonFlip)

    labelState = tk.Label(tasks_frame, text=state)
    stateLabels.append(labelState)


    buttonDel = tk.Button(tasks_frame, text=" X ")
    deleteButtons.append(buttonDel)
    buttonDel.config(command=lambda : destroy_row(taskIndexLabels, flipButtons, stateLabels, deleteButtons, internalTaskID, labelEmpty, internalTaskIDList))

    # Placing everything inside the grid
    labelIndex.grid(column=0, row=index, padx=15)
    buttonFlip.grid(column=1, row=index, sticky='we', pady=5)
    labelState.grid(column=2, row=index, padx=10)
    buttonDel.grid(column=3, row=index)

def destroy_row(taskIndexLabels, flipButtons, stateLabels, deleteButtons, internalTaskID, labelEmpty, internalTaskIDList):

    if len(get_db_items()) < 1:
        labelEmpty.grid(column=0, row=0)
        return
    
    # This gets the index inside the unique id list. Since ids are unique, this is an easy way to identify a task.
    index = internalTaskIDList.index(internalTaskID) 

    # Remove widgets
    taskIndexLabels[index].destroy()
    flipButtons[index].destroy()
    stateLabels[index].destroy()
    deleteButtons[index].destroy()

    # Remove the reference to the widgets that just got removed
    taskIndexLabels.pop(index)
    flipButtons.pop(index)
    stateLabels.pop(index)
    deleteButtons.pop(index)

    # Remove the reference to the task
    internalTaskIDList.pop(index)

    # Delete task from database
    delete_task(internalTaskID)

    # Fix the remaining widgets position to correctly display in the grid after a deletion
    i = 0
    for row in taskIndexLabels:
        row["text"] = (i + 1)
        row.grid(row = i)
        flipButtons[i].grid(row = i)
        stateLabels[i].grid(row = i)
        deleteButtons[i].grid(row = i)
        i += 1


def GUI_version():
    """Draws the GUI of the to-do list"""
    # Main window
    root = tk.Tk()
    root.title("To-do list")
    root.minsize(320, 320)
    root.focus()

    # Tasks frame (holds grid that holds task rows)
    tasks_frame = tk.Frame(root, bg="lightblue")
    tasks_frame.pack()

    # Menubar (to access the terminal version)
    menubar = tk.Menu(root)
    fileMenu = tk.Menu(menubar, tearoff=0)
    fileMenu.add_command(label="Terminal Mode", command=lambda: change_to_terminal(root))
    menubar.add_cascade(menu=fileMenu, label="Action")
    root.config(menu=menubar)

    # Lists to directly access tkinter widgets generated in the loop
    taskIndexLabels = [] # For the numbers right next to tasks
    stateLabels = [] # For done/to-do
    flipButtons = [] # Buttons that flip done/to-do
    internalTaskIDList = []
    deleteButtons = []

    labelEmpty = tk.Label(tasks_frame, text="There are no tasks to show yet.")

    # Draw the starting task list if tasks are already present
    querry = get_db_items()
    if len(querry) < 1:
        labelEmpty.grid(column=0, row=0)
    else:
        index = 0 # Index is tidier to use than the internal ids, which can have gaps in number order.
        for row in querry: # row[0] = internal id of the task | row[1] = task name | row[2] = to-do(0) or done(1)
            draw_task(row, index, taskIndexLabels, stateLabels, flipButtons, deleteButtons, tasks_frame, labelEmpty, internalTaskIDList)
            index += 1

    # Options frame
    options_frame = tk.Frame(root)
    options_frame.pack(pady=5)
    # Print data in terminal
    buttonPrint = tk.Button(options_frame, text="Print Database to Terminal", command=print_db_rows)
    buttonPrint.grid(column=1, columnspan=2, sticky='we', row=0, pady=5)
    # Add entry
    entryAdd = tk.Entry(options_frame, width=40)
    entryAdd.grid(column=1, row=1)
    # Add button to submit entry
    buttonForEntry = tk.Button(options_frame, text="Add entry", command=lambda : add_task_to_GUI(entryAdd.get().strip(), tasks_frame, stateLabels, flipButtons, deleteButtons, labelEmpty, taskIndexLabels, internalTaskIDList))
    buttonForEntry.grid(column=2, row=1)

    # Starting
    root.mainloop()

    #TODO: make temporary buffer for tasks, then dbConn.commit()

def terminal_version():
    """Provides terminal access to the to-do list"""
    currentinput = '0'
    print("TERMINAL MODE\nType help for commands or exit to close")
    dbConnState, _ = check_db_open()
    while currentinput != 'exit' and dbConnState == True:
        currentinput = input("\n> ").strip()

        # Print all rows.
        if currentinput == '1':
            print_db_rows()

        # Write a new task.
        elif currentinput == '2':
            taskAtHand = input("Write a new task. Write 1 to cancel.\n>").strip()                
            if taskAtHand == '1': # if user wrote 1 to cancel:
                print("Registration cancelled.")
            else: # if user wrote a task:
                register_task(taskAtHand)

        # Flip task between done and undone.
        elif currentinput == '3':
            selectId = input("Select a task index to flip between done and undone:\n>")
            flip_done_undone(selectId)

        # If no available commands are given.
        elif currentinput == 'help':
            print("Type:\n1 - read all tasks inside the database\n2 - add task\n3 - flip done/undone\nGUI - open interface mode\nexit - closes program")

        elif currentinput == 'GUI':
            GUI_version()
            currentinput = 'exit'

# Creating a path to application relative to main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct full absolute path to the database inside folder db
db_path = os.path.join(BASE_DIR, 'db', 'todo.db')
# Connecting and starting cursor
dbConn = sqlite3.connect(db_path)
dbCursor = dbConn.cursor()
# Table checks if it exists every start
dbCursor.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, name TEXT NOT NULL, state INT NOT NULL DEFAULT 0)")
# Entering
#print("Program entered.")
GUI_version()
# Exiting
dbConn.close()
#print("Connection has been closed.\nProgram exited.")