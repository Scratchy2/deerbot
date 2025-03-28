from json import loads, dumps
from shlex import split
from threading import Thread
from time import sleep
from websocket import WebSocketApp

version = "1.0.9b"
serverVersion = "Helium-1.0.0a"
bot = "replace with your bot name (don't include the @ and don't use display name)"
psw = "replace with your bot password (case-sensitive)"

def ping(ws: WebSocketApp):
	while True:
		ws.send(dumps({"command": "ping"}))
		sleep(5)
def send(ws: WebSocketApp, id, msg: str): # "ws" is the connection itself, "id" is the id of the message, and "msg" is the actual message contents
	ws.send(dumps({"command": "post", "content": msg, "replies": [id], "attachments": []}))

# START OF COMMANDS
# "id" is message id, "name" is username of author, "ws" is the connection itself, and "args" is a tuple of words that follow the command
def help(id, name, ws: WebSocketApp, *args): # make sure the parameters are exactly like this
	send(ws, id, f"Commands\n@{bot} help: shows this message.") # you must add to this manually, so make sure you are showing all the commands
# END OF COMMANDS

def onmessage(ws: WebSocketApp, message):
	global bot
	incoming = loads(message)
	if incoming["command"] == "greet":
		if (incoming["version"] != serverVersion):
			print(f"The server is on a different version than the client. Be wary of issues while using the client. (Expected {incoming["serverVersion"]}, got {serverVersion})")
	if "error" in message:
		if incoming["code"] == "banned":
			print(f"Account is banned for {incoming["ban_reason"]}")
	if incoming["command"] == "new_post":
		if (str(incoming["data"]["content"]).lower().startswith(f"@{bot} ")) and (str(incoming["data"]["author"]["username"]) != bot):
			command = str(incoming["data"]["content"])[len(bot) + 2:]
			args = split(command)
			print(f"Command from {incoming["data"]["author"]["display_name"]} (@{incoming["data"]["author"]["username"]}) with id {incoming["data"]["_id"]}: {command}")
			if command not in ("ping", "send"):
				if len(args) == 1:
					globals()[args[0]](incoming["data"]["_id"], incoming["data"]["username"], ws)
				else:
					globals()[args[0]](incoming["data"]["_id"], incoming["data"]["username"], ws, args[1:])
		else:
			print(f"Message from {incoming["data"]["author"]["display_name"]} (@{incoming["data"]["author"]["username"]}): {incoming["data"]["content"]}")
def onopen(ws: WebSocketApp):
	global bot, psw
	ws.send(dumps({"command": "login_pswd", "username": bot, "password": psw}))
	ping(ws)

def onopenexec(ws: WebSocketApp):
	Thread(target=lambda: onopen(ws), daemon=True).start()

ws = WebSocketApp("wss://sokt.fraudulent.loan", on_message=onmessage, on_open=onopenexec, on_error=lambda ws, *x:print("error: ", x), on_close=lambda ws, *x:print("close: ", x))
while True:
	ws.run_forever()
	ws.close()
