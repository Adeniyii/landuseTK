import os
import re
import sqlite3
from tkinter import *
from dotenv import load_dotenv
from tkinter import messagebox

load_dotenv()

# Create and/or connect to database
db = sqlite3.connect("landuse.db")

# Create cursor
c = db.cursor()

# Create table
c.execute("""CREATE TABLE IF NOT EXISTS users(
    fName text,
    lName text,
    email text UNIQUE PRIMARY KEY,
    pWord text
)""")


root = Tk()
root.title("LandUse Database")
root.geometry("720x480")

rootFrame = Frame(root)
rootFrame.pack(fill="both", expand=True)

current_user = None

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

radioVar = StringVar()
radioVar.set("map")

# Function to select post type using radio buttons
def setPostType():
    selection = radioVar.get()
    if selection == "coord":
        return
    elif selection == "map":
        uploadMap()
    else:
        return


# Welcome page view function
def welcomePage():
    global registerButton, loginButton, welcome_message, welcomeFrame

    welcomeFrame = Frame(rootFrame, pady=20)
    welcomeFrame.pack()

    welcome_message = Label(welcomeFrame, text="Landuse Database Application", font=50, pady=20)
    welcome_message.pack()

    registerButton = Button(welcomeFrame, text="Register", padx=100, pady=50, command=register)
    registerButton.pack(side=LEFT, padx=20, pady=20)

    loginButton = Button(welcomeFrame, text="Login", padx=100, pady=50, command=login)
    loginButton.pack(side=LEFT, padx=20, pady=20)


# Dashboard view function
def dashboard():
    global dashboardFrame

    toggle_hide_window(root)
    welcomeFrame.pack_forget()

    dashboardFrame = Frame(rootFrame, pady=20)
    dashboardFrame.pack()

    dashboardHeader = Label(dashboardFrame, text=f"{current_user[0]}'s dashboard.", font=50, pady=20)
    dashboardHeader.grid(row=0, column=0, columnspan=2)

    addPostButton = Button(dashboardFrame, text="New Post", padx=100, pady=50, command=newPost)
    addPostButton.grid(row=1, column=0, padx=20, pady=20)

    viewPostButton = Button(dashboardFrame, text="View Posts", padx=100, pady=50, command=viewPost)
    viewPostButton.grid(row=1, column=1, padx=20, pady=20)

    logoutButton = Button(dashboardFrame, text="Logout", padx=100, pady=50, command=logout)
    logoutButton.grid(row=2, column=0, columnspan=2, pady=20)

def newPost():
    postWindow = Toplevel()
    postWindow.title("New Post")
    postWindow.geometry("720x480")

    toggle_hide_window(root)

    newPostFrame = Frame(postWindow)
    newPostFrame.pack(fill="both", expand=True)

    postHeader = Label(newPostFrame, text="Select a post type")
    postHeader.grid(row=0, column=0, pady=20)

    coordRadio = Radiobutton(newPostFrame, text="Coordinates", variable=radioVar, value="coord", command=setPostType)
    coordRadio.grid(row=1, column=0, padx=20, sticky=W)

    mapRadio = Radiobutton(newPostFrame, text="Map", variable=radioVar, value="map", command=setPostType)
    mapRadio.grid(row=2, column=0, padx=20, sticky=W)

    postWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(postWindow))


# Function to handle viewing posts
def viewPost():
    return


# Registration view function
def register():
    global fn_entry, ln_entry, em_entry, pw_entry, regWindow
    regWindow = Toplevel()
    regWindow.title("Registration")
    regWindow.geometry("500x500")

    registerButton["state"] = DISABLED
    loginButton["state"] = DISABLED

    toggle_hide_window(root)

    regFrame = Frame(regWindow)
    regFrame.place(anchor=CENTER, relx=.5, rely=.3)

    # =================================================================
    fnLab = Label(regFrame, text="First Name", pady=10, padx=10)
    fnLab.grid(row=0, column=0)
    lnLab = Label(regFrame, text="Last Name", pady=10, padx=10)
    lnLab.grid(row=1, column=0)
    emLab = Label(regFrame, text="Email", pady=10, padx=10)
    emLab.grid(row=2, column=0)
    pwLab = Label(regFrame, text="Password", pady=10, padx=10)
    pwLab.grid(row=3, column=0)
    cpLab = Label(regFrame, text="Confirm Password", pady=10, padx=10)
    cpLab.grid(row=4, column=0)

    fn_entry = Entry(regFrame, width=50)
    fn_entry.grid(row=0, column=1)
    ln_entry = Entry(regFrame, width=50)
    ln_entry.grid(row=1, column=1)
    em_entry = Entry(regFrame, width=50)
    em_entry.grid(row=2, column=1)
    pw_entry = Entry(regFrame, width=50, show="*")
    pw_entry.grid(row=3, column=1)
    cp_entry = Entry(regFrame, width=50, show="*")
    cp_entry.grid(row=4, column=1)

    submit_btn = Button(regFrame, text="Submit", command=addUser)
    submit_btn.grid(row=5, column=0, columnspan=2, padx=20, pady=(50, 0), ipadx=200)
    # ================================================================================

    regWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(regWindow))


# Login view function
def login():
    global loginWindow, em_logEntry, pw_logEntry

    loginWindow = Toplevel()
    loginWindow.title("Log In")
    loginWindow.geometry("500x500")

    registerButton["state"] = DISABLED
    loginButton["state"] = DISABLED

    toggle_hide_window(root)

    loginFrame = Frame(loginWindow)
    loginFrame.place(anchor=CENTER, relx=.5, rely=.2)

    # ==========================================================================
    emLab = Label(loginFrame, text="Email", pady=10, padx=10)
    emLab.grid(row=0, column=0)
    pwLab = Label(loginFrame, text="Password", pady=10, padx=10)
    pwLab.grid(row=1, column=0)

    em_logEntry = Entry(loginFrame, width=50)
    em_logEntry.grid(row=0, column=1)
    pw_logEntry = Entry(loginFrame, width=50, show="*")
    pw_logEntry.grid(row=1, column=1)

    submit_btn = Button(loginFrame, text="Submit", command=findUser)
    submit_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=(50, 0), ipadx=200)
    # ==========================================================================

    loginWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(loginWindow))


# Add user to database
def addUser():
    try:
        c.execute("INSERT INTO users VALUES(:fname, :lname, :email, :pword)",
            {
                "fname": fn_entry.get(),
                "lname": ln_entry.get(),
                "email": em_entry.get(),
                "pword": pw_entry.get()
            })
    except sqlite3.IntegrityError:
        messagebox.showerror("Registration Error", f'User with email "{em_entry.get()}" already exists.')
        # regWindow.focus_force()
        regWindow.attributes("-topmost", True)
        em_entry.delete(0, END)
    else:
        if not (re.search(regex, em_entry.get())):
            messagebox.showerror("Email Error", "An invalid email was submitted.")
            regWindow.attributes("-topmost", True)
            em_entry.delete(0, END)
        else:
            db.commit()

            fn_entry.delete(0, END)
            ln_entry.delete(0, END)
            em_entry.delete(0, END)
            pw_entry.delete(0, END)

            messagebox.showinfo("Registration Successful", "User has been created successfully!")
            exit_window(regWindow)
            toggle_hide_window(root)


# Function to find user in database
def findUser():
    global current_user

    c.execute("SELECT *, oid FROM users WHERE email=? AND pWord=?", (em_logEntry.get(), pw_logEntry.get()))
    user = c.fetchone()
    if user:
        current_user = user
        messagebox.showinfo("Success", "Login successful!")
        loginWindow.destroy()
        dashboard()

    else:
        messagebox.showinfo("Error", "Invalid credentials. Try again or register an account.")
        # Set a topmost window
        loginWindow.attributes("-topmost", True)


# Function to upload maps to database.
def uploadMap():
    return


# Logout function
def logout():
    if messagebox.askokcancel("Logout", "Proceed to logout?"):
        current_user = None
        dashboardFrame.destroy()
        welcomePage()
    else:
        return


# Function to close select window
def exit_window(win):
    win.destroy()
    registerButton["state"] = NORMAL
    loginButton["state"] = NORMAL


# Confirm exit program
def on_closing(win):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        win.destroy()
        if win != root:
            toggle_hide_window(root)
            registerButton["state"] = NORMAL
            loginButton["state"] = NORMAL


# Function to hide or view a window
def toggle_hide_window(win):
    if not win.winfo_viewable():
        win.update()
        win.deiconify()
    else:
        win.withdraw()


welcomePage()


root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

root.mainloop()
