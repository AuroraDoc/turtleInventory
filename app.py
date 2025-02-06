from flask import Flask, render_template, session, request, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "Random-Secret-Key12345"
app.config["SESSION_COOKIE_NAME"] = "Random_Secret_Cookie12345"

connection = sqlite3.connect("items.db", check_same_thread=False, )
cursor = connection.cursor()

cursor.execute("PRAGMA journal_mode = OFF")
cursor.execute("create table if not exists items (item_id integer primary key autoincrement, item text, person text, amount text, date text)")

def insertItemToDB(item):
    cursor.execute("insert into items(item,person,amount,date) values(?,?,?,?)", (item["item"], item["person"], item["amount"], item["date"]))
    connection.commit()
    refreshItems()

def refreshItems():
    data = cursor.execute("select * from items")
    items = []

    for row in data:
        newItem = {
            "item_id": row[0],
            "item": row[1],
            "person": row[2],
            "amount": row[3],
            "date": row[4]
        }
        items.append(newItem)
    return items

def removeItemFromDB(itemId):
    cursor.execute(f"delete from items where item_id={itemId}")
    connection.commit()
    session["items"] = refreshItems()    

@app.route("/remove", methods=["post"])
def removeItems():
    checked_boxes = request.form.getlist("check")

    for id in checked_boxes:
        removeItemFromDB(id)

    return render_template("index.html", items=session["items"])
#the issue is that it only finds the first item with that item in the list not the correct one marked. Not the biggest deal since there
# shouldnt be duplicates

# Also need to update the db after an item is removed.

@app.route("/", methods=["POST", "GET"])
def home():

    if request.method == "POST":
        newItem = {
            "item": request.form["Item"],
            "person": request.form["Person"],
            "amount": request.form["Amount"],
            "date": request.form["Date"]
        }
        
        insertItemToDB(newItem)

        session["items"] = refreshItems()

        return render_template("index.html", items=session["items"])

    else:
        session["items"] = refreshItems()
        return render_template("index.html", items=session["items"])
    


app.run("0.0.0.0", 80, True)

cursor.close()
connection.close()
