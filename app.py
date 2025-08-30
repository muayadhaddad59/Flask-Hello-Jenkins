from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", title="Ridgeway • Hello Jenkins")

@app.route("/health")
def health():
    return jsonify(ok=True)

if __name__ == "__main__":
    # use an explicit port for smoke tests
    app.run(host="0.0.0.0", port=5001)
