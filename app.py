import os
from flask import Flask, jsonify
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


@app.get("/")
def home():
    return jsonify(
        {
            "app": os.getenv("APP_NAME", "VibeCheckAPI"),
            "status": "slaying",
            "message": "No cap, the API is up.",
        }
    )


@app.get("/vibe")
def vibe():
    chaos_mode = flags.is_enabled(
        "enable_chaos_mode",
        fallback=(os.getenv("FLAG_ENABLE_CHAOS_MODE", "false").lower() == "true"),
    )

    if chaos_mode:
        return jsonify(
            {
                "vibe": "CHAOS",
                "message": "Main character energy unlocked. Your to-do list is now a side quest.",
            }
        )

    return jsonify(
        {
            "vibe": "CHILL",
            "message": "Hydrate, commit, and pretend that bug was a feature.",
        }
    )


@app.get("/roast")
def roast():
    roast_enabled = flags.is_enabled(
        "enable_daily_roast",
        fallback=(os.getenv("FLAG_ENABLE_DAILY_ROAST", "false").lower() == "true"),
    )

    if not roast_enabled:
        return jsonify({"error": "Feature disabled. Roast not available."}), 404

    return jsonify(
        {
            "roast": "You said 'it works on my machine' like your laptop is a production environment.",
            "emoji_support": "💀",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
