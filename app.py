from flask import Flask, render_template, session, request, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "Random-Secret-Key12345"
app.config["SESSION_COOKIE_NAME"] = "Random_Secret_Cookie12345"

connection = sqlite3.connect("items.db", check_same_thread=False, )
cursor = connection.cursor()
cursor.execute("PRAGMA journal_mode = OFF")

#Create the table if it does not exist yet 
#cursor.execute("create table items (item text, person text, amount text, date text)")

def insertItemToDB(item, person, amount, date):
    cursor.execute("insert into items(item,person,amount,date) values(?,?,?,?)", (item, person, amount, date))
    connection.commit()
    refreshItems()

def refreshItems():
    data = cursor.execute("select * from items")
    items = [list(row) for row in data]
    print(items)
    return items

def removeItemFromDB(item):
    cursor.execute(f"delete from items where item={item}")
    connection.commit()
    refreshItems()    

@app.route("/remove", methods=["post"])
def removeItems():
    checked_boxes = request.form.getlist("check")

    items_list = [item[0] for item in session["items"]]

    for item in checked_boxes:
        if item in items_list:
            index = items_list.index(item)
            session["items"].pop(index)
            session.modified = True
            removeItemFromDB(item)

    return render_template("index.html", items=session["items"])
#the issue is that it only finds the first item with that item in the list not the correct one marked. Not the biggest deal since there
# shouldnt be duplicates

# Also need to update the db after an item is removed.

@app.route("/", methods=["POST", "GET"])
def home():


    if request.method == "POST":
        item = request.form["Item"]
        person = request.form["Person"]
        amount = request.form["Amount"]
        date = request.form["Date"]

        insertItemToDB(item, person, amount, date)

        session["items"] = refreshItems()

        return render_template("index.html", items=session["items"])

    else:
        session["items"] = refreshItems()
        return render_template("index.html", items=session["items"])
    


app.run("0.0.0.0", 80, True)

connection.close()