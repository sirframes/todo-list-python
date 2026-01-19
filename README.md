This application is a simple to-do list meant as program practicing, only documentation and text searches are allowed. NO AI.
A to-do list does not sound exciting, but the journey with no tutorials is tougher than one would expect.
This project doubles down as my introduction to version control.

Being in doubt between Java and Python, the language I choose to practice first was python, which comes bundled with two useful modules for the express
purpose of this kind of app, tkinter (for GUI's) and sqlite3 (data storage/retrival).

My first challenge after setting things up and having a way to receive data (through the terminal, no GUI yet) was how to modify specific data on demand. 
The solution was creating an unique id for each row, a column that stores primary keys. This is sufficient for a simple internal system like this.

#dbCursor.execute("CREATE TABLE IF NOT EXISTS tasks(name, state)")
became
#dbCursor.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, name TEXT NOT NULL, state INT NOT NULL DEFAULT 0)")

After making the user able to fetch written tasks and mark them as done, work began on making the GUI.

Keeping references for each widget has proven to be quite challenging, but using arrays to store the widgets during their creation worked wonders for referencing them.

The tasks and extra option buttons have been separated to make things more organized. "lightblue" bg color is used to debug where frames are.

to make a way for the user to add new tasks, I had to choose between a function that forgets all widgets then rebuilds the list with a new entry, or somehow appends the new entry to the list. The later was chosen because rebuilding the list just to update values seems wasteful.