from flask import Flask
import threading
import os


app = Flask(__name__)

def run_bot():
    import bot  # só importar já executa

threading.Thread(target=run_bot).start()

@app.route("/")
def home():
    return "Bot rodando!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
