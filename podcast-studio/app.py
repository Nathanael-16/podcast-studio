import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from gtts import gTTS

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "podcast_output")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_podcast_script(topic: str, style: str, length: str) -> str:
    topic = topic.strip()
    if not topic:
        return "Bitte gib ein Thema oder einen Text ein."

    style_text = {
        "locker": "locker und freundlich",
        "professionell": "professionell und klar",
        "energetisch": "energetisch und motivierend",
        "informativ": "informativ und leicht verständlich",
    }.get(style, "locker und freundlich")

    blocks = [
        f"Host: Hey Leute, heute sprechen wir über: {topic}.",
        f"Host: Heute schauen wir uns das Thema {topic} in einem {style_text} Stil an.",
        "Host: Ich möchte dir kurz erklären, warum dieses Thema wichtig ist.",
        f"Guest: Genau, {topic} betrifft viele Menschen im Alltag und hat echte Vorteile, aber auch viele Fragen.",
        "Host: Lass uns die wichtigsten Punkte Schritt für Schritt durchgehen.",
        "Guest: Der erste Punkt ist, dass man damit schnell wertvolle Ergebnisse erzielen kann.",
        "Host: Genau, und dabei ist es wichtig, immer die richtigen Perspektiven im Blick zu haben.",
        "Guest: Der zweite Punkt ist die praktische Anwendung im echten Leben.",
        "Host: Das macht das Thema nicht nur interessant, sondern auch extrem nutzbar.",
        "Guest: Wenn du das richtig anwendest, kannst du Zeit sparen und effizienter arbeiten.",
        "Host: Zusammengefasst ist das Thema relevant, spannend und für viele Menschen wichtig.",
        "Guest: Genau, und genau deshalb lohnt es sich, mehr darüber zu wissen.",
        "Host: Vielen Dank für eure Aufmerksamkeit. Bis zum nächsten Podcast."
    ]

    return "\n\n".join(blocks)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "").strip()
    style = request.form.get("style", "locker")
    length = request.form.get("length", "5min")

    if not topic:
        return jsonify({"error": "Bitte gib ein Thema oder einen Text ein."}), 400

    script = generate_podcast_script(topic, style, length)

    script_file = os.path.join(OUTPUT_DIR, f"script_{uuid.uuid4().hex}.txt")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script)

    audio_name = f"podcast_{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_name)

    try:
        tts = gTTS(text=script, lang="de", slow=False)
        tts.save(audio_path)
    except Exception as e:
        return jsonify({"error": f"TTS-Fehler: {str(e)}"}), 500

    return jsonify({
        "script": script,
        "audio": f"/static/audio/{audio_name}",
        "download": f"/download/{audio_name}"
    })


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(AUDIO_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
