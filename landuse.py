import os
import re
# import fiona
# from fiona.crs import from_epsg
import psycopg2
import datetime
# import numpy as np
# import pandas as pd
from tkinter import *
# import matplotlib.pyplot as plt
# import geopandas as gpd
from pathlib import Path
from tkinter import ttk, Tk
from dotenv import load_dotenv
from tkinter import messagebox
from tkinter import filedialog
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from shapely.geometry import Point, Polygon

# Load environment variables and set current user
path = Path(".") / ".env"
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
try:
    conn = psycopg2.connect(
        "postgres://xmersysu:7t2_-ej6IafyXlvHGIuR8unVy1nG7Ovg@castor.db.elephantsql.com/xmersysu"
    )
except psycopg2.OperationalError as e:
    print(e)
    messagebox.showerror(
        "Network Error", "Please ensure you have an internet connection."
    )
    os.abort()

# Create cursor -- to execute commands on database
cur = conn.cursor()

# Create user table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        fName VARCHAR(15),
        lName VARCHAR(15),
        email VARCHAR(25) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL
    )"""
)

# cur.execute(
#     """
#     DROP TABLE parcels
#     """
# )

# Create parcel table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS parcels (
        id SERIAL PRIMARY KEY,
        owner VARCHAR(255),
        address VARCHAR(255),
        plot_no INTEGER,
        plan_no text,
        volume_no INTEGER,
        block text,
        local_gov text,
        xCoordinates text,
        yCoordinates text,
        nature_of_Parcel text,
        land_use text,
        C_of_O BOOL,
        date_acquired DATE,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )"""
)

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
        table.insert("", "end", values=i)


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
        frame, text="View your cadastral records", font=150, pady=60, bg="#fffe9f"
    )
    viewAllButton = Button(
        frame,
        text="View All",
        padx=100,
        pady=50,
        command=lambda: viewAll(win),
        bg="#fffafa",
    )
    viewOneButton = Button(
        frame,
        text="View One",
        padx=100,
        pady=50,
        command=lambda: viewOne(win),
        bg="#fffafa",
    )
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
        queryFrame,
        text="Query for a parcel of land using address.",
        pady=50,
        bg="#fffe9f",
        font=20,
    )
    queryEntry = Entry(queryFrame, width=70)
    filler = Frame(queryFrame, height=20)
    querySubmit = Button(
        queryFrame,
        text="Submit",
        padx=30,
        pady=10,
        command=lambda: viewOneTable(queryEntry),
        bg="#fffafa",
    )

    queryLabel.pack(side=TOP)
    queryEntry.pack(side=TOP)
    filler.pack()
    querySubmit.pack(side=TOP)

    newWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(newWindow, win))


def viewOneTable(queryEntry):

    # Query database for land information
    cur.execute(
        "SELECT * FROM parcels WHERE user_id=%s AND address=%s",
        (current_user[0], queryEntry.get()),
    )
    landInfo = cur.fetchall()

    # ============================================================
    if len(landInfo) < 1:
        messagebox.showerror(
            "Query Error", f"No parcel of address {queryEntry.get()} was found."
        )
    else:

        # Open new window to display records in table
        newWindow = nuWindow(title="Land Record", size="1240x720")
        tableFrame = Frame(newWindow, bg="#fffe9f")
        tableFrame.pack(side=TOP, expand=True, fill="both")

        headings = ["Land ID", "Owner", "Address", "Plot No", "Plan No", "Volume No", "Block", "Local Gov", "X-Coordinates", "Y-Coordinates", "Nature of Parcel", "Land Use", "C of O", "Date Acquired"]
        # Display table showing relevant land records
        table = ttk.Treeview(
            tableFrame,
            columns=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
            show="headings",
            height=len(landInfo),
        )
        table.pack()

        for i in range(len(headings) + 1):
            table.heading(i, text=headings[i - 1])
        updateTable(landInfo, table)

def viewAll(win):

    cur.execute("SELECT * FROM parcels WHERE user_id=%s", (current_user[0],))
    landInfo = cur.fetchall()
    print(landInfo)

    if len(landInfo) < 1:
        messagebox.showerror(
            "Query Error", f"No land information was found for user {current_user[2]}."
        )
    else:
        # Open new window to input query parameters
        newWindow = nuWindow(win, "Query dialog", "1750x830")
        newWindow.resizable(False, False)
        tableFrame = Frame(newWindow, bg="#fff")
        tableFrame.pack(expand=True, fill="both", padx=20, pady=10)

        # tableLength = 10 if len(landInfo) > 10 else len(landInfo)
        headings = ["Land ID", "Owner", "Address", "Plot No", "Plan No", "Volume No", "Block", "Local Gov", "X-Coordinates", "Y-Coordinates", "Nature of Parcel", "Land Use", "C of O", "Date Acquired"]
        # Display table showing relevant land records
        table = ttk.Treeview(
            tableFrame,
            columns=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
            show="headings",
            height=25,
            # height=tableLength,
        )
        tableStyle = ttk.Style(table)
        tableStyle.configure('Treeview', rowheight=30)

        table.pack(side="left")
        table.place(x=0, y=0)

        # Vertical ScrollBar
        yScrollBar = ttk.Scrollbar(tableFrame, orient="vertical", command=table.yview)
        yScrollBar.pack(side="right", fill="y")

        # Horizontal ScrollBar
        xScrollBar = ttk.Scrollbar(tableFrame, orient="horizontal", command=table.xview)
        xScrollBar.pack(side="bottom", fill="x")

        table.configure(yscrollcommand=yScrollBar.set, xscrollcommand=xScrollBar.set)

        for i in range(len(headings) + 1):
            table.heading(i, text=headings[i - 1])
            table.column(i, width=120, minwidth=200)
        updateTable(landInfo, table)

    newWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(newWindow, win))


def postRecord(frame, win):
    postHeader = Label(
        frame, text="Create a new cadastral record", font=150, pady=60, bg="#fffe9f"
    )
    postHeader.grid(row=0, column=1, columnspan=2)

    addressLabel = Label(frame, text="Address")
    xLabel = Label(frame, text="X-Coordinates")
    yLabel = Label(frame, text="Y-Coordinates")
    natureOfParcelLabel = Label(frame, text="Nature-of-parcel")
    ownerLabel = Label(frame, text="Owner")
    landUseLabel = Label(frame, text="LandUse")
    plotNoLabel = Label(frame, text="PlotNo")
    localGovLabel = Label(frame, text="LocalGov")
    blockLabel = Label(frame, text="Block")
    cofoLabel = Label(frame, text="C-of-O")
    planNoLabel = Label(frame, text="PlanNo")
    volNoLabel = Label(frame, text="VolumeNo")

    filler1 = Frame(frame, height=20)
    filler2 = Frame(frame, height=20)
    filler3 = Frame(frame, height=20)
    filler4 = Frame(frame, height=20)
    filler5 = Frame(frame, height=20)
    filler6 = Frame(frame, height=20)
    filler7 = Frame(frame, height=20)
    filler8 = Frame(frame, height=20)
    filler9 = Frame(frame, height=20)
    filler10 = Frame(frame, height=20)
    filler11 = Frame(frame, height=20)
    filler12 = Frame(frame, height=20)

    addressInput = Entry(frame, width=70)
    xInput = Entry(frame, width=70)
    yInput = Entry(frame, width=70)
    natureOfParcelInput = Entry(frame, width=70)
    ownerInput = Entry(frame, width=70)
    landUseInput = Entry(frame, width=70)
    plotNoInput = Entry(frame, width=70)
    localGovInput = Entry(frame, width=70)
    blockInput = Entry(frame, width=70)
    cofoInput = Entry(frame, width=70)
    planNoInput = Entry(frame, width=70)
    volNoInput = Entry(frame, width=70)


    addressLabel.grid(row=1, column=0)
    addressInput.grid(row=1, column=1)
    filler1.grid(row=2, column=0)

    xLabel.grid(row=3, column=0)
    xInput.grid(row=3, column=1)
    filler2.grid(row=4, column=0)

    yLabel.grid(row=5, column=0)
    yInput.grid(row=5, column=1)
    filler3.grid(row=6, column=0)

    natureOfParcelLabel.grid(row=7, column=0)
    natureOfParcelInput.grid(row=7, column=1)
    filler4.grid(row=8, column=0)

    ownerLabel.grid(row=9, column=0)
    ownerInput.grid(row=9, column=1)
    filler5.grid(row=10, column=0)

    landUseLabel.grid(row=11, column=0)
    landUseInput.grid(row=11, column=1)
    filler6.grid(row=12, column=0)

    plotNoLabel.grid(row=13, column=0)
    plotNoInput.grid(row=13, column=1)
    filler7.grid(row=14, column=0)

    localGovLabel.grid(row=15, column=0)
    localGovInput.grid(row=15, column=1)
    filler8.grid(row=16, column=0)

    blockLabel.grid(row=17, column=0)
    blockInput.grid(row=17, column=1)
    filler9.grid(row=18, column=0)

    cofoLabel.grid(row=19, column=0)
    cofoInput.grid(row=19, column=1)
    filler10.grid(row=19, column=0)

    planNoLabel.grid(row=20, column=0)
    planNoInput.grid(row=20, column=1)
    filler11.grid(row=21, column=0)

    volNoLabel.grid(row=22, column=0)
    volNoInput.grid(row=22, column=1)

    entries = [addressInput, xInput, yInput, natureOfParcelInput, ownerInput, landUseInput, plotNoInput, localGovInput, blockInput, cofoInput, volNoInput, planNoInput]

    submitButton = Button(
        frame, text="Submit", padx=30, pady=10, command=lambda: uploadPost(entries)
    )
    filler12.grid(row=23, column=0)
    submitButton.grid(row=24, column=1)


def uploadPost(e):

    address = e[0].get()
    coordinatesX = e[1].get()
    coordinatesY = e[2].get()
    natureOfParcelInput = e[3].get()
    owner = e[4].get()
    landUse = e[5].get()
    plotNo = e[6].get()
    localGov = e[7].get()
    block = e[8].get()
    cofo = e[9].get()
    volNo = e[10].get()
    planNo = e[11].get()

    if address == "" or coordinatesX == "" or coordinatesY =="" or natureOfParcelInput == "" or owner == "" or landUse == "" or plotNo == "" or localGov == "" or block == "" or cofo == "":
        messagebox.showerror("Upload Error", "All fields must be properly filled")
    try:
        cur.execute(
            """
            INSERT INTO parcels (owner, user_id, address, xCoordinates, yCoordinates, plan_no, volume_no, nature_of_Parcel, land_use, plot_no, local_gov, block, C_of_O, date_acquired)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (owner, current_user[0], address, coordinatesX, coordinatesY, planNo, volNo, natureOfParcelInput, landUse, plotNo, localGov, block, cofo, datetime.datetime.now()),
        )

        conn.commit()

        e[0].delete(0, END)
        e[1].delete(0, END)
        e[2].delete(0, END)
        e[3].delete(0, END)
        e[4].delete(0, END)
        e[5].delete(0, END)
        e[6].delete(0, END)
        e[7].delete(0, END)
        e[8].delete(0, END)
        e[9].delete(0, END)
        e[10].delete(0, END)
        e[11].delete(0, END)

        messagebox.showinfo(
            "Upload Successful", "Your land information was uploaded successfully!"
        )
    except psycopg2.Error as e:
        messagebox.showerror(
            "Upload Error", "There was an error when uploading you information."
        )
        print(e)


def updateRecord(frame, win):
    updateHeader = Label(
        frame, text="Update an existing cadastral record", font=150, pady=60, bg="green"
    )
    updateHeader.grid(row=0, column=2)
    return


def deleteRecord(frame, win):
    deleteHeader = Label(
        frame, text="Delete an existing cadastral record", font=150, pady=60, bg="pink"
    )
    deleteHeader.grid(row=0, column=2)
    return


def welcomePage():
    global registerButton, loginButton, welcome_message, welcomeFrame

    welcomeFrame = Frame(rootFrame, pady=20, bg="#ffd480")
    welcomeFrame.pack()

    welcome_message = Label(
        welcomeFrame,
        text="Landuse Database Application",
        font=50,
        pady=20,
        bg="#ffd480",
    )
    registerButton = Button(
        welcomeFrame, text="Register", padx=100, pady=50, command=register, bg="#fffe9f"
    )
    loginButton = Button(
        welcomeFrame, text="Login", padx=100, pady=50, command=login, bg="#fffe9f"
    )

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
    cpLab = Label(regFrame, text="Confirm Password", pady=10, padx=10, bg="#fffafa")

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
        regFrame,
        text="Submit",
        command=lambda: addUser(fn_entry, ln_entry, em_entry, pw_entry, regWindow),
    )
    submit_btn.grid(
        row=5, column=0, columnspan=2, padx=20, pady=(50, 0), ipadx=200, sticky="n"
    )
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
        loginFrame,
        text="Submit",
        command=lambda: findUser(em_logEntry, pw_logEntry, loginWindow),
    )
    submit_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=(50, 0), ipadx=200)

    loginWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(loginWindow, root))


def dashboard():
    toggle_hide_window(root)
    welcomeFrame.pack_forget()

    dashboardFrame = Frame(rootFrame, pady=20, bg="#fca180")
    dashboardFrame.pack()

    dashboardHeader = Label(
        dashboardFrame, text=f"{current_user[2]}'s dashboard.", font=50, pady=20
    )
    dashboardHeader.grid(row=0, column=0, columnspan=2)

    addPostButton = Button(
        dashboardFrame, text="Database", padx=100, pady=50, command=newPost
    )
    viewMapButton = Button(
        dashboardFrame, text="Map", padx=100, pady=50, command=viewMap
    )
    logoutButton = Button(
        dashboardFrame,
        text="Logout",
        padx=100,
        pady=50,
        command=lambda: logout(dashboardFrame),
    )

    addPostButton.grid(row=1, column=0, padx=20, pady=20)
    viewMapButton.grid(row=1, column=1, padx=20, pady=20)
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

    frames = [viewRecordFrame, postRecordFrame, updateRecordFrame, deleteRecordFrame]

    # Radio selections
    # =======================================================================
    viewRadio = Radiobutton(
        selectionFrame,
        text="View record",
        variable=radioVar,
        value="view",
        command=lambda: setPostType(viewRecordFrame, frames, postWindow),
    )
    postRadio = Radiobutton(
        selectionFrame,
        text="Post record",
        variable=radioVar,
        value="create",
        command=lambda: setPostType(postRecordFrame, frames, postWindow),
    )
    updateRadio = Radiobutton(
        selectionFrame,
        text="Update record",
        variable=radioVar,
        value="update",
        command=lambda: setPostType(updateRecordFrame, frames, postWindow),
    )
    deleteRadio = Radiobutton(
        selectionFrame,
        text="Delete record",
        variable=radioVar,
        value="delete",
        command=lambda: setPostType(deleteRecordFrame, frames, postWindow),
    )

    viewRadio.grid(row=1, column=0, padx=20, sticky=W)
    postRadio.grid(row=2, column=0, padx=20, sticky=W)
    updateRadio.grid(row=3, column=0, padx=20, sticky=W)
    deleteRadio.grid(row=4, column=0, padx=20, sticky=W)

    setPostType(viewRecordFrame, frames, postWindow)

    postWindow.protocol("WM_DELETE_WINDOW", lambda: on_closing(postWindow, root))


# Add user to database
def addUser(fn, ln, em, pw, win):
    # Create regex expression for email matching
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

    # check empty input boxes
    if not (fn.get() == "" or ln.get() == "" or em.get() == "" or pw.get() == ""):
        try:
            cur.execute(
                "INSERT INTO users (fname, lname, email, password) VALUES(%s, %s, %s, %s)",
                (fn.get(), ln.get(), em.get(), pw.get()),
            )
        except psycopg2.errors.UniqueViolation:
            messagebox.showerror(
                "Registration Error", f'User with email "{em.get()}" already exists.'
            )
            # regWindow.focus_force()
            win.attributes("-topmost", True)
            em.delete(0, END)
        else:
            if not (re.search(regex, em.get())):
                messagebox.showerror("Email Error", "An invalid email was submitted.")
                win.attributes("-topmost", True)
                em.delete(0, END)
            else:
                conn.commit()

                fn.delete(0, END)
                ln.delete(0, END)
                em.delete(0, END)
                pw.delete(0, END)

                messagebox.showinfo(
                    "Registration Successful", "User has been created successfully!"
                )
                exit_window(win)
                toggle_hide_window(root)
    else:
        messagebox.showerror(
            "Registration Error", f"All fields must be properly filled."
        )
        # regWindow.focus_force()
        win.attributes("-topmost", True)


# Function to find user in database
def findUser(em, pw, win):
    global current_user

    if not (em.get() == "" or pw.get() == ""):
        try:
            cur.execute(
                "SELECT * FROM users WHERE email=%s AND password=%s",
                (em.get(), pw.get()),
            )
            user = cur.fetchone()
            if user:
                current_user = user
                messagebox.showinfo("Success", "Login successful!")
                win.destroy()
                dashboard()

            else:
                messagebox.showinfo(
                    "Error", "Invalid credentials. Try again or register an account."
                )
                # Set a topmost window
                win.attributes("-topmost", True)
        except psycopg2.Error as e:
            messagebox.showinfo(
                "Unknown error", "Please try again or register an account."
            )
    else:
        messagebox.showinfo("Login Error", "All fields must be filled.")

        win.attributes("-topmost", True)


# Function to handle viewing maps
def viewMap():

    # mapWindow = Toplevel()
    # mapWindow.title("New Map")
    # mapWindow.geometry("1080x760")
    # mapWindow.columnconfigure(index=2, weight=10)

    # lf = ttk.Labelframe(mapWindow, text="Plot Area")
    # lf.pack()
# =========================================================================================================================
# ============================================================================================================================

    # coordinates = [
    #     (26.722117, 58.380184),
    #     (26.724853, 58.380676),
    #     (26.724961, 58.380518),
    #     (26.722372, 58.379933),
    # ]

    # poly = Polygon(boros)

    # print(newdata)

    # nybb_path = gpd.datasets.get_path('nybb')
    # boros = gpd.read_file(nybb_path)
    # boros.set_index('BoroCode', inplace=True)
    # boros.sort_index(inplace=True)
    # boros['geometry'].convex_hull
    # print(boros)

    # fig = Figure(figsize=(10, 7), dpi=100)
    # ax = fig.add_subplot(111)

    # newdata.plot(ax=ax, column="gdp_per_cap")
    # boros.plot(ax=ax)
    # poly.plot(ax=ax)

    # canvas = FigureCanvasTkAgg(fig, master=lf)
    # canvas.draw()
    # canvas.get_tk_widget().grid(row=0, column=0)

    # Determine the output path for the Shapefile
    # out_file = "./shapefiles/newshp.shp"

    # Write the data into that Shapefile
    # newdata.to_file(out_file)

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
    if len(frame.grid_info()) == 0:
        frame.grid(row=0, column=2, sticky="n")
    else:
        return


# Function to hide a frame
def hide_frame_grid(frame):
    if len(frame.grid_info()) != 0:
        frame.grid_remove()
    else:
        return


welcomePage()


root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, NONE))

root.mainloop()
