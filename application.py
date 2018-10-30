from typing import List, Any

import os

from datetime import datetime
from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# configuring session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configuring socketio
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chatlist = []
messagelist = []

@app.route("/")
def index():
    if "user_name" in session:
        return redirect(url_for('chatroomlist'))
    return render_template("index.html")


@app.route("/chatrooms", methods=["GET", "POST"])
def chatroomlist():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        session["user_name"] = user_name

    if request.method == "GET" and "user_name" not in session:
        return render_template("error.html", error_message="Please identify yourself first.")
    return render_template("chatlist.html", chatlist=chatlist)


@app.route("/chatrooms/<int:chat_id>", methods=["GET", "POST"])
def chatroom(chat_id):
    if request.method == "POST":
        chatroom_name = request.form.get("chatroom_name")
        if chatroom_name in chatlist:
            return render_template("error.html", error_message="The chatroom already exists.")
        chatlist.append(chatroom_name)
    if request.method == "GET":
        if "user_name" not in session:
            return render_template("error.html", error_message="Please identify yourself first.")
        if len(chatlist) < chat_id:
            return render_template("error.html", error_message="Chatroom Doesn't Exist."
                                                               " If you want the same chatroom, go back and create one")
    return render_template("chatroom.html", user_name=session["user_name"])


@socketio.on("submit message")
def message(data):
    selection = data["selection"]
    time = datetime.now().strftime("%Y-%m-%d %H:%M")
    messagelist.append({"selection": selection, "time": time, "user_name": session["user_name"]})
    emit("cast message", {"selection": selection, "user_name": session["user_name"], "time": time}, broadcast=True)


@app.route("/listmessages")
def listmessages():
    return jsonify(messagelist)


if __name__ == "__main__":
    app.run(debug=True)
