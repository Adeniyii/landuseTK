import os
import re
import psycopg2
import datetime
from tkinter import *
from tkinter import ttk, Tk
from pathlib import Path
from dotenv import load_dotenv
from tkinter import messagebox
from tkinter import filedialog

# Load environment variables and set current user
path = Path('.') / '.env'
load_dotenv(path)
current_user = None

# Create local connection to database
# conn = psycopg2.connect(
#     host=os.getenv("host"),
#     user=os.getenv("user"),
#     password=os.getenv("password"),
#     database=os.getenv("database")
# )

# Connect to elephantSQL database hosting
conn = psycopg2.connect(
    "postgres://rwnqktkh:rEINi490ai8VpCMpwbTXfE4EsSJn7VJ0@ziggy.db.elephantsql.com:5432/rwnqktkh")

# Create cursor -- to execute commands on database
cur = conn.cursor()

# Create user table
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        fName VARCHAR(15),
        lName VARCHAR(15),
        email VARCHAR(25) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL
    )""")

# Create parcel table
cur.execute("""
    CREATE TABLE IF NOT EXISTS parcels (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        address VARCHAR(255),
        size BIGINT,
        vacant BOOL,
        date_acquired DATE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )""")

# Save changes to database
conn.commit()

# Main window
root = Tk()
root.title("LandUse Database")
root.geometry("720x480")

# Main frame
rootFrame = Frame(root, bg="#3c0303")
rootFrame.pack(fill="both", expand=True)

# Radio button variables
radioVar = StringVar()
radioVar.set("view")


def updateTable(rows, table):
    for i in rows:
        table.insert('', 'end', values=i)


def setPostType(frame, frames, win):
    selection = radioVar.get()

    for i in frames:
        if i != frame:
            hide_frame_grid(i)

    show_frame_grid(frame)

    if selection == "view":
        viewRecord(frame, win)
    elif selection == "create":
        postRecord(frame, win)
    elif selection == "update":
        updateRecord(frame, win)
    elif selection == "delete":
        deleteRecord(frame, win)
    else:
        return


def viewRecord(frame, win):
    viewHeader = Label(
        frame, text="View your cadastral records", font=150, pady=60, bg="#fffe9f")
    viewAllButton = Button(frame, text="View All", padx=100,
                           pady=50, command=lambda: viewAll(win), bg="#fffafa")
    viewOneButton = Button(frame, text="View One", padx=100,
                           pady=50, command=lambda: viewOne(win), bg="#fffafa")
    filler = Frame(frame, bg="#fffe9f", height=50)

    viewHeader.grid(row=0, column=1, columnspan=2)
    filler.grid(row=1, column=1, columnspan=2)
    viewAllButton.grid(row=2, column=1, sticky="n")
    viewOneButton.grid(row=2, column=2, sticky="n")


def viewOne(win):
    # Open new window to input query parameters
    newWindow = nuWindow(win, "Query dialog", "500x500")
    queryFrame = Frame(newWindow, bg="#fffe9f")
    queryFrame.pack(side=TOP, expand=True, fill="both")

    queryLabel = Label(
        queryFrame, text="Query for a parcel of land using address.", pady=50, bg="#fffe9f", font=20)
    queryEntry = Entry(queryFrame, width=70)
    filler = Frame(queryFrame, height=20)
    querySubmit = Button(queryFrame, text="Submit", padx=30,
                         pady=10, command=lambda: viewOneTable(queryEntry), bg="#fffafa")

    queryLabel.pack(side=TOP)
    queryEntry.pack(side=TOP)
    filler.pack()
    querySubmit.pack(side=TOP)

    newWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(newWindow, win))


def viewOneTable(queryEntry):

    # Query database for land information
    cur.execute("SELECT * FROM parcels WHERE user_id=%s AND address=%s",
                (current_user[0], queryEntry.get()))
    landInfo = cur.fetchall()

    # ============================================================
    if len(landInfo) < 1:
        messagebox.showerror(
            "Query Error", f'No parcel of address {queryEntry.get()} was found.')
    else:

        # Open new window to display records in table
        newWindow = nuWindow(title="Land Record", size="1240x720")
        tableFrame = Frame(newWindow, bg="#fffe9f")
        tableFrame.pack(side=TOP, expand=True, fill="both")

        headings = ["Land ID", "Owner", "Address",
                    "Size", "Vacant", "Date Acquired"]
        # Display table showing relevant land records
        table = ttk.Treeview(tableFrame, columns=(
            1, 2, 3, 4, 5, 6), show="headings", height=len(landInfo))
        table.pack()

        for i in range(7):
            table.heading(i, text=headings[i-1])
        updateTable(landInfo, table)


def viewAll(win):

    cur.execute("SELECT * FROM parcels WHERE user_id=%s", (current_user[0],))
    landInfo = cur.fetchall()

    if len(landInfo) < 1:
        messagebox.showerror(
            "Query Error", f'No land information was found for user {current_user[2]}.')
    else:
        # Open new window to input query parameters
        newWindow = nuWindow(win, "Query dialog", "1240x720")
        tableFrame = Frame(newWindow, bg="#fffe9f")
        tableFrame.pack(side=TOP, expand=True, fill="both")

        header = Label(
            tableFrame, text=f'All Land records for {current_user[1]} {current_user[2]}.', pady=30, font=50, bg="#fffe9f")
        header.pack()

        filler = Frame(tableFrame, height=50)
        filler.pack()

        headings = ["Land ID", "Owner", "Address",
                    "Size", "Vacant", "Date Acquired"]
        # Display table showing relevant land records
        table = ttk.Treeview(tableFrame, columns=(
            1, 2, 3, 4, 5, 6), show="headings", height=len(landInfo))
        table.pack()

        for i in range(7):
            table.heading(i, text=headings[i-1])
        updateTable(landInfo, table)

    newWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(newWindow, win))


def postRecord(frame, win):
    postHeader = Label(
        frame, text="Create a new cadastral record", font=150, pady=60, bg="#fffe9f")
    postHeader.grid(row=0, column=1, columnspan=2)

    addressLabel = Label(frame, text="Address")
    sizeLabel = Label(frame, text="Size")
    vacantLabel = Label(frame, text="Vacant")

    filler1 = Frame(frame, height=20)
    filler2 = Frame(frame, height=20)
    filler3 = Frame(frame, height=20)

    addressInput = Entry(frame, width=70)
    sizeInput = Entry(frame, width=70)
    vacantInput = Entry(frame, width=70)

    addressLabel.grid(row=1, column=0)
    addressInput.grid(row=1, column=1)
    filler1.grid(row=2, column=0)

    sizeLabel.grid(row=3, column=0)
    sizeInput.grid(row=3, column=1)
    filler2.grid(row=4, column=0)

    vacantLabel.grid(row=5, column=0)
    vacantInput.grid(row=5, column=1)

    entries = [addressInput, sizeInput, vacantInput]

    submitButton = Button(frame, text="Submit", padx=30,
                          pady=10, command=lambda: uploadPost(entries))
    filler3.grid(row=6, column=0)
    submitButton.grid(row=7, column=1)


def uploadPost(e):

    address = e[0].get()
    size = e[1].get()
    vacant = e[2].get()

    if (address == "" or size == "" or vacant == ""):
        messagebox.showerror(
            "Upload Error", "All fields must be properly filled")

    try:
        cur.execute("""
            INSERT INTO parcels (user_id, address, size, vacant, date_acquired) 
            VALUES (%s, %s, %s, %s, %s)
        """, (current_user[0], address, size, vacant, datetime.datetime.now()))

        conn.commit()

        e[0].delete(0, END)
        e[1].delete(0, END)
        e[2].delete(0, END)

        messagebox.showinfo("Upload Successful",
                            "Your land information was uploaded successfully!")
    except psycopg2.Error as e:
        messagebox.showerror("Upload Error",
                             "There was an error when uploading you information.")
        print(e)


def updateRecord(frame, win):
    updateHeader = Label(
        frame, text="Update an existing cadastral record", font=150, pady=60, bg="green")
    updateHeader.grid(row=0, column=2)
    return


def deleteRecord(frame, win):
    deleteHeader = Label(
        frame, text="Delete an existing cadastral record", font=150, pady=60, bg="pink")
    deleteHeader.grid(row=0, column=2)
    return


def welcomePage():
    global registerButton, loginButton, welcome_message, welcomeFrame

    welcomeFrame = Frame(rootFrame, pady=20, bg="#ffd480")
    welcomeFrame.pack()

    welcome_message = Label(
        welcomeFrame, text="Landuse Database Application", font=50, pady=20, bg="#ffd480")
    registerButton = Button(welcomeFrame, text="Register",
                            padx=100, pady=50, command=register, bg="#fffe9f")
    loginButton = Button(welcomeFrame, text="Login",
                         padx=100, pady=50, command=login, bg="#fffe9f")

    welcome_message.pack()
    registerButton.pack(side=LEFT, padx=20, pady=20)
    loginButton.pack(side=LEFT, padx=20, pady=20)


def register():
    regWindow = Toplevel()
    regWindow.title("Registration")
    regWindow.geometry("500x500")

    registerButton["state"] = DISABLED
    loginButton["state"] = DISABLED

    toggle_hide_window(root)

    regFrame = Frame(regWindow, bg="#fffafa")
    regFrame.pack(side=TOP, expand=True, fill="both")

    # display labels
    # =================================================================
    fnLab = Label(regFrame, text="First Name", pady=10, padx=10, bg="#fffafa")
    lnLab = Label(regFrame, text="Last Name", pady=10, padx=10, bg="#fffafa")
    emLab = Label(regFrame, text="Email", pady=10, padx=10, bg="#fffafa")
    pwLab = Label(regFrame, text="Password", pady=10, padx=10, bg="#fffafa")
    cpLab = Label(regFrame, text="Confirm Password",
                  pady=10, padx=10, bg="#fffafa")

    fnLab.grid(row=0, column=0, sticky="we")
    lnLab.grid(row=1, column=0, sticky="n")
    emLab.grid(row=2, column=0, sticky="n")
    pwLab.grid(row=3, column=0, sticky="n")
    cpLab.grid(row=4, column=0, sticky="n")

    # display entry boxes
    # =================================================================
    fn_entry = Entry(regFrame, width=50)
    ln_entry = Entry(regFrame, width=50)
    em_entry = Entry(regFrame, width=50)
    pw_entry = Entry(regFrame, width=50, show="*")
    cp_entry = Entry(regFrame, width=50, show="*")

    fn_entry.grid(row=0, column=1, sticky="n")
    ln_entry.grid(row=1, column=1, sticky="n")
    em_entry.grid(row=2, column=1, sticky="n")
    pw_entry.grid(row=3, column=1, sticky="n")
    cp_entry.grid(row=4, column=1, sticky="n")

    # call addUser function on submit
    submit_btn = Button(
        regFrame, text="Submit", command=lambda: addUser(fn_entry, ln_entry, em_entry, pw_entry, regWindow))
    submit_btn.grid(row=5, column=0, columnspan=2,
                    padx=20, pady=(50, 0), ipadx=200, sticky="n")
    # ================================================================================

    regWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(regWindow, root))


def login():
    loginWindow = Toplevel()
    loginWindow.title("Log In")
    loginWindow.geometry("500x500")

    registerButton["state"] = DISABLED
    loginButton["state"] = DISABLED

    toggle_hide_window(root)

    loginFrame = Frame(loginWindow, bg="#3c0303")
    loginFrame.pack(expand=True, fill="both")

    # ==========================================================================
    emLab = Label(loginFrame, text="Email", pady=10, padx=10)
    pwLab = Label(loginFrame, text="Password", pady=10, padx=10)

    emLab.grid(row=0, column=0)
    pwLab.grid(row=1, column=0)

    em_logEntry = Entry(loginFrame, width=50)
    pw_logEntry = Entry(loginFrame, width=50, show="*")

    em_logEntry.grid(row=0, column=1)
    pw_logEntry.grid(row=1, column=1)

    submit_btn = Button(
        loginFrame, text="Submit", command=lambda: findUser(em_logEntry, pw_logEntry, loginWindow))
    submit_btn.grid(row=2, column=0, columnspan=2,
                    padx=20, pady=(50, 0), ipadx=200)

    loginWindow.protocol("WM_DELETE_WINDOW",
                         lambda: on_closing(loginWindow, root))


def dashboard():
    toggle_hide_window(root)
    welcomeFrame.pack_forget()

    dashboardFrame = Frame(rootFrame, pady=20, bg="#fca180")
    dashboardFrame.pack()

    dashboardHeader = Label(
        dashboardFrame, text=f"{current_user[2]}'s dashboard.", font=50, pady=20)
    dashboardHeader.grid(row=0, column=0, columnspan=2)

    addPostButton = Button(dashboardFrame, text="Database",
                           padx=100, pady=50, command=newPost)
    viewPostButton = Button(dashboardFrame, text="Map",
                            padx=100, pady=50, command=viewMap)
    logoutButton = Button(dashboardFrame, text="Logout",
                          padx=100, pady=50, command=lambda: logout(dashboardFrame))

    addPostButton.grid(row=1, column=0, padx=20, pady=20)
    viewPostButton.grid(row=1, column=1, padx=20, pady=20)
    logoutButton.grid(row=2, column=0, columnspan=2, pady=20)


def newPost():
    postWindow = Toplevel()
    postWindow.title("New Post")
    postWindow.geometry("1080x720")
    postWindow.columnconfigure(index=2, weight=10)

    toggle_hide_window(root)

    # Post Selection Frames
    # ========================================================================

    selectionFrame = Frame(postWindow, pady=50)
    newPostFrame = Frame(postWindow, bg="#fffe9f")

    selectionFrame.grid(row=0, column=0, sticky="nsew")
    newPostFrame.grid(row=0, column=2, sticky="nsew")

    # Vertical bar separator
    Frame(selectionFrame).grid(row=4, column=0, ipady=500)

    vertBar = ttk.Separator(postWindow, orient=VERTICAL)
    vertBar.grid(column=1, row=0, rowspan=12, sticky="ns")

    # Datebase query frames
    # =====================================================================

    viewRecordFrame = Frame(postWindow, bg="#fffe9f")
    postRecordFrame = Frame(postWindow, bg="#fffe9f")
    updateRecordFrame = Frame(postWindow, bg="#fffe9f")
    deleteRecordFrame = Frame(postWindow, bg="#fffe9f")

    frames = [viewRecordFrame, postRecordFrame,
              updateRecordFrame, deleteRecordFrame]

    # Radio selections
    # =======================================================================
    viewRadio = Radiobutton(selectionFrame, text="View record",
                            variable=radioVar, value="view", command=lambda: setPostType(viewRecordFrame, frames, postWindow))
    postRadio = Radiobutton(selectionFrame, text="Post record",
                            variable=radioVar, value="create", command=lambda: setPostType(postRecordFrame, frames, postWindow))
    updateRadio = Radiobutton(selectionFrame, text="Update record",
                              variable=radioVar, value="update", command=lambda: setPostType(updateRecordFrame, frames, postWindow))
    deleteRadio = Radiobutton(selectionFrame, text="Delete record",
                              variable=radioVar, value="delete", command=lambda: setPostType(deleteRecordFrame, frames, postWindow))

    viewRadio.grid(row=1, column=0, padx=20, sticky=W)
    postRadio.grid(row=2, column=0, padx=20, sticky=W)
    updateRadio.grid(row=3, column=0, padx=20, sticky=W)
    deleteRadio.grid(row=4, column=0, padx=20, sticky=W)

    setPostType(viewRecordFrame, frames, postWindow)

    postWindow.protocol("WM_DELETE_WINDOW",
                        lambda: on_closing(postWindow, root))


# Add user to database
def addUser(fn, ln, em, pw, win):
    # Create regex expression for email matching
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

    # check empty input boxes
    if not (fn.get() == "" or ln.get() == "" or em.get() == "" or pw.get() == ""):
        try:
            cur.execute("INSERT INTO users (fname, lname, email, password) VALUES(%s, %s, %s, %s)",
                        (fn.get(), ln.get(), em.get(), pw.get()))
        except psycopg2.errors.UniqueViolation:
            messagebox.showerror(
                "Registration Error", f'User with email "{em.get()}" already exists.')
            # regWindow.focus_force()
            win.attributes("-topmost", True)
            em.delete(0, END)
        else:
            if not (re.search(regex, em.get())):
                messagebox.showerror(
                    "Email Error", "An invalid email was submitted.")
                win.attributes("-topmost", True)
                em.delete(0, END)
            else:
                conn.commit()

                fn.delete(0, END)
                ln.delete(0, END)
                em.delete(0, END)
                pw.delete(0, END)

                messagebox.showinfo("Registration Successful",
                                    "User has been created successfully!")
                exit_window(win)
                toggle_hide_window(root)
    else:
        messagebox.showerror(
            "Registration Error", f'All fields must be properly filled.')
        # regWindow.focus_force()
        win.attributes("-topmost", True)


# Function to find user in database
def findUser(em, pw, win):
    global current_user

    if not (em.get() == "" or pw.get() == ""):
        try:
            cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                        (em.get(), pw.get()))
            user = cur.fetchone()
            if user:
                current_user = user
                messagebox.showinfo("Success", "Login successful!")
                win.destroy()
                dashboard()

            else:
                messagebox.showinfo(
                    "Error", "Invalid credentials. Try again or register an account.")
                # Set a topmost window
                win.attributes("-topmost", True)
        except psycopg2.Error as e:
            messagebox.showinfo(
                "Unknown error", "Please try again or register an account.")
    else:
        messagebox.showinfo(
            "Login Error", "All fields must be filled.")

        win.attributes("-topmost", True)


# Function to handle viewing maps
def viewMap():
    return


# Create new window
def nuWindow(win=None, title="LandUse", size="500x500"):
    newloginWindow = Toplevel()
    newloginWindow.title(title)
    newloginWindow.geometry(size)
    if win:
        toggle_hide_window(win)

    return newloginWindow


# Logout function
def logout(dbframe):
    if messagebox.askokcancel("Logout", "Proceed to logout?"):
        current_user = None
        dbframe.destroy()
        welcomePage()
    else:
        return


# Function to close selected window
def exit_window(win):
    win.destroy()
    registerButton["state"] = NORMAL
    loginButton["state"] = NORMAL


# Confirm exit program
def on_closing(win, pWin):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        win.destroy()
        if win == root:
            print("closing...")
            cur.close()
            conn.close()
        else:
            toggle_hide_window(pWin)
            registerButton["state"] = NORMAL
            loginButton["state"] = NORMAL


# Function to hide or view a window
def toggle_hide_window(win):
    if not win.winfo_viewable():
        win.update()
        win.deiconify()
    else:
        win.withdraw()


# Function to show a frame
def show_frame_grid(frame):
    if (len(frame.grid_info()) == 0):
        frame.grid(row=0, column=2, sticky="n")
    else:
        return


# Function to hide a frame
def hide_frame_grid(frame):
    if (len(frame.grid_info()) != 0):
        frame.grid_remove()
    else:
        return


welcomePage()


root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, NONE))

root.mainloop()
