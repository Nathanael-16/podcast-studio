from flask import Flask, render_template, request, jsonify, send_from_directory
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "podcast_output")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_script_fallback(topic: str, style: str, length: str, language: str = "de") -> str:
    style_map = {
        "locker": "locker und freundlich",
        "professionell": "professionell und klar",
        "energetisch": "energetisch und motivierend",
        "informativ": "informativ und verständlich",
    }
    tone = style_map.get(style, "locker und freundlich")

    if language.lower() == "en":
        return f"""Host: Welcome back everyone. Today we are diving into {topic}.

Host: We are looking at this topic in a {tone} way, so it stays practical and easy to follow.

Guest: Exactly. {topic} is relevant because it affects everyday decisions, workflows, and opportunities in a real way.

Host: Let’s break it into a few useful points so it becomes clear what matters most.

Guest: First, it creates value because it saves time and helps people work smarter.

Host: And second, it opens up new possibilities for creativity, learning, and better execution.

Guest: That makes it useful for personal growth, business decisions, and everyday life.

Host: The real trick is not just understanding it, but applying it consistently.

Guest: Right. That is where the real progress happens.

Host: Thanks for listening. That was our overview of {topic}."""

    return f"""Host: Herzlich willkommen zurück. Heute sprechen wir über {topic}.

Host: Wir schauen uns das Thema heute in einem {tone}en Stil an, damit es verständlich und praxisnah bleibt.

Guest: Genau. {topic} ist relevant, weil es viele Menschen im Alltag betrifft und echte Vorteile mit sich bringt.

Host: Lass uns das einmal in klaren Punkten aufteilen, damit man die wichtigsten Ideen schnell versteht.

Guest: Erstens spart es Zeit und hilft dabei, Entscheidungen besser zu treffen.

Host: Zweitens eröffnet es neue Möglichkeiten, kreativer zu arbeiten und effizienter zu handeln.

Guest: Genau. Dadurch wird das Thema für viele Menschen spannender und praktischer.

Host: Der wichtigste Punkt ist, dass man es nicht nur versteht, sondern auch konsequent anwendet.

Guest: Genau. Erst dann entsteht echter Mehrwert.

Host: Danke fürs Zuhören. Das war ein kurzer Überblick zu {topic}."""


def generate_podcast_script(topic: str, style: str, length: str, language: str = "de") -> str:
    topic = topic.strip()
    if not topic:
        return "Bitte gib ein Thema oder einen Text ein."
    return generate_script_fallback(topic, style, length, language)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "").strip()
    style = request.form.get("style", "locker")
    length = request.form.get("length", "5min")
    language = request.form.get("language", "de")

    if not topic:
        return jsonify({"error": "Bitte gib ein Thema oder einen Text ein."}), 400

    script = generate_podcast_script(topic, style, length, language)

    script_path = os.path.join(OUTPUT_DIR, f"script_{uuid.uuid4().hex}.txt")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    audio_name = f"podcast_{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_name)

    try:
        lang_code = "en" if language.lower() == "en" else "de"
        tts = gTTS(text=script, lang=lang_code, slow=False)
        tts.save(audio_path)
    except Exception as e:
        return jsonify({"error": f"Audio-Fehler: {str(e)}"}), 500

    return jsonify({
        "script": script,
        "audio": f"/static/audio/{audio_name}",
        "download": f"/download/{audio_name}"
    })


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(AUDIO_DIR, filename, as_attachment=True)


@app.route("/manifest.json")
def manifest():
    return send_from_directory(BASE_DIR, "manifest.json")


@app.route("/service-worker.js")
def sw():
    return send_from_directory(BASE_DIR, "service-worker.js")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
