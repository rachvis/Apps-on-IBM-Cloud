import os
import random
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

from feature_flags import FeatureFlagClient

load_dotenv()

app = Flask(__name__)
flags = FeatureFlagClient(
    app_config_url=os.getenv("APP_CONFIG_URL", ""),
    app_config_guid=os.getenv("APP_CONFIG_GUID", ""),
    app_config_apikey=os.getenv("APP_CONFIG_APIKEY", ""),
    environment_id=os.getenv("APP_CONFIG_ENVIRONMENT_ID", ""),
)

VIBE_MESSAGES = [
    "You are serving pixel-perfect main character energy today.",
    "Build deployed. Skin clear. Inbox ignored. Big win.",
    "Your PR is so clean it needs a ring light.",
    "You debug like a detective in a cyberpunk hoodie.",
    "Today’s vibe: shipping features before coffee gets cold.",
    "No cap, your stack is stacked.",
    "Your code has rizz and lint-free charisma.",
    "You’re in your dev era and it’s iconic.",
    "The sprint feared you, and rightly so.",
    "You just turned chaos into architecture. Respect.",
]

ROAST_MESSAGES = [
    "Your TODO list is a historical document now.",
    "You said ‘quick fix’ and started a trilogy.",
    "Your code runs on vibes and unexplained miracles.",
    "You renamed `final_v2_latest_REAL.py` again, huh?",
    "That bug saw your commit and chose violence.",
    "Your staging environment is basically fan fiction.",
    "You wrote one line and opened seven tabs. Cinematic.",
    "Your rollback strategy is ‘manifesting’.",
    "Your keyboard deserves hazard pay.",
    "You deploy on Friday like it’s a personality trait.",
]



def is_flag_on(flag_key: str, fallback_env: str) -> bool:
    fallback = os.getenv(fallback_env, "false").lower() == "true"
    return flags.is_enabled(flag_key, fallback=fallback)


@app.get("/")
def home():
    show_vibe = is_flag_on("show_vibe", "FLAG_SHOW_VIBE")
    show_roast = is_flag_on("show_roast", "FLAG_SHOW_ROAST")

    return render_template(
        "index.html",
        app_name=os.getenv("APP_NAME", "VibeCheckAPI"),
        show_vibe=show_vibe,
        show_roast=show_roast,
        vibe_message=random.choice(VIBE_MESSAGES),
        roast_message=random.choice(ROAST_MESSAGES),
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": os.getenv("APP_NAME", "VibeCheckAPI")})


@app.get("/vibe")
@app.get("/api/vibe")
def vibe():
    return jsonify({"api": "vibe", "message": random.choice(VIBE_MESSAGES)})


@app.get("/roast")
@app.get("/api/roast")
def roast():
    if not is_flag_on("show_roast", "FLAG_SHOW_ROAST"):
        return jsonify(
            {
                "api": "roast",
                "message": "Roast mode is currently napping. Flip the show_roast flag to wake it up.",
            }
        )

    return jsonify({"api": "roast", "message": random.choice(ROAST_MESSAGES)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
