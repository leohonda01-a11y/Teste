from flask import Flask
import os
import subprocess

app = Flask(__name__)

def run_bot():
    subprocess.Popen(["python", "bot.py"])

run_bot()

@app.route("/")
def home():
    return "Bot rodando!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
