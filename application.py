import os
import requests
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = []
channels_messages = {}
count = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/main")
def main():
    return render_template("main.html", channels = channels)

@app.route("/create", methods=["POST"])
def create():
    channel = (request.form.get("channel") or "")
    if (channel in channels or channel == ""):
        return render_template("error.html")
    else:
        channels.append(channel)
        channels_messages[channel] = []
        count[channel] = 0
        return render_template("channel.html", channel = channel)

@app.route("/channel/<string:channel>")
def channel(channel):
    messages = (channels_messages[channel] or "")
    return render_template("channel.html", channel = channel, messages = messages)

@socketio.on("send message")
def send(data):
    now = datetime.now()
    timestamp = str(now)
    message = (data["name"], data["message"], timestamp)
    channel = data["channel"]
    count[channel] += 1;
    if (count[channel] > 100):
        del channels_messages[channel][0]
    channels_messages[channel].append(message)
    receive_message = {"name": data["name"], "message": data["message"], "time": timestamp}
    emit("receive message", receive_message, broadcast = True)

#Remembering the Channel X
