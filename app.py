import os
import string
import requests
from flask import Flask, jsonify

HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "3000"))
EPGSTATION_HOST = os.getenv("EPGSTATION_HOST", "epgstation")
EPGSTATION_PORT = int(os.getenv("EPGSTATION_PORT", "8888"))
USE_HALF_WIDTH = int(os.getenv("USE_HALF_WIDTH", "0")) == 1

app = Flask(__name__)

def call_epgstation_api(path):
    return requests.get(f"http://{EPGSTATION_HOST}:{EPGSTATION_PORT}/api{path}").json()

@app.route("/schedule.json", methods=["GET"])
def get_schedule():
    # 扱いやすいように id をキーとして辞書を作る
    channels = {
        x["id"]: x
        for x in call_epgstation_api("/channels")
    }

    return jsonify([
        {
            "type": channels[x["channel"]["id"]]["channelType"],
            "channel": channels[x["channel"]["id"]]["channel"],
            "name": channels[x["channel"]["id"]]["halfWidthName" if USE_HALF_WIDTH else "name"],
            "id": to_base_36(x["channel"]["id"]),
            "sid": channels[x["channel"]["id"]]["serviceId"],
            "nid": channels[x["channel"]["id"]]["networkId"],
            "hasLogoData": channels[x["channel"]["id"]]["hasLogoData"],
            "n": channels[x["channel"]["id"]]["remoteControlKeyId"],
            "programs": [
                {
                    "id": to_base_36(y["id"]),
                    "category": {
                        0x0: "news",
                        0x1: "sports",
                        0x2: "information",
                        0x3: "drama",
                        0x4: "music",
                        0x5: "variety",
                        0x6: "cinema",
                        0x7: "anime",
                        0x8: "documentary",
                        0x9: "theater",
                        0xA: "hobby",
                        0xB: "welfare",
                        0xC: "etc",
                        0xD: "etc",
                        0xE: "etc",
                        0xF: "etc"
                    }[y.get("genre1", 0xF)],
                    "title": y["name"],
                    "fullTitle": y["name"],  # TODO: Support flags such as [字]
                    "detail": y.get("description", ""),
                    "start": y["startAt"],
                    "end": y["endAt"],
                    "seconds": (y["endAt"] - y["startAt"]) / 1000,
                    "description": y.get("description", ""),
                    "extra": {
                        "_": y["extended"]  # TODO
                    } if "extended" in y else {},
                    "channel": {
                        "type": channels[y["channelId"]]["channelType"],
                        "channel": channels[y["channelId"]]["channel"],
                        "name": channels[y["channelId"]]["halfWidthName" if USE_HALF_WIDTH else "name"],
                        "id": to_base_36(y["channelId"]),
                        "sid": channels[y["channelId"]]["serviceId"],
                        "nid": channels[y["channelId"]]["networkId"],
                        "hasLogoData": channels[y["channelId"]]["hasLogoData"],
                        "n": channels[y["channelId"]]["remoteControlKeyId"]
                    },
                    "subTitle": "",  # Unsupported
                    "episode": None,  # Unsupported
                    "flags": []  # Unsupported
                }
                for y in x["programs"]
            ]
        }
        for x in call_epgstation_api(f"/schedules?startAt=0&endAt=100000000000000&isHalfWidth={USE_HALF_WIDTH}&GR=true&BS=true&CS=true&SKY=true")
        
    ])

@app.route("/recording.json", methods=["GET"])
def get_recording():
    # 扱いやすいように id をキーとして辞書を作る
    channels = {
        x["id"]: x
        for x in call_epgstation_api("/channels")
    }

    return jsonify([
        {
            "id": to_base_36(x["programId"]),
            "category": {
                0x0: "news",
                0x1: "sports",
                0x2: "information",
                0x3: "drama",
                0x4: "music",
                0x5: "variety",
                0x6: "cinema",
                0x7: "anime",
                0x8: "documentary",
                0x9: "theater",
                0xA: "hobby",
                0xB: "welfare",
                0xC: "etc",
                0xD: "etc",
                0xE: "etc",
                0xF: "etc"
            }[x["genre1"]],
            "title": x["name"],
            "fullTitle": x["name"],  # TODO: Support flags such as [字]
            "detail": x.get("description", ""),
            "start": x["startAt"],
            "end": x["endAt"],
            "seconds": (x["endAt"] - x["startAt"]) / 1000,
            "description": x.get("description", ""),
            "extra": {
                "_": x["extended"]  # TODO
            } if "extended" in x else {},
            "channel": {
                "type": channels[x["channelId"]]["channelType"],
                "channel": channels[x["channelId"]]["channel"],
                "name": channels[x["channelId"]]["halfWidthName" if USE_HALF_WIDTH else "name"],
                "id": to_base_36(x["channelId"]),
                "sid": channels[x["channelId"]]["serviceId"],
                "nid": channels[x["channelId"]]["networkId"],
                "hasLogoData": channels[x["channelId"]]["hasLogoData"],
                "n": channels[x["channelId"]]["remoteControlKeyId"]
            },
            "subTitle": "",  # Unsupported
            "episode": None,  # Unsupported
            "flags": [],  # Unsupported

            "isManualReserved": "ruleId" not in x,
            "priority": 0,  # Unsupported
            "tuner": {
                "name": "EPGStation",
                "command": "",
                "isScrambling": False
            },  # Unsupported
            "command": "",  # Unsupported
            "pid": 0,  # Unsupported
            "recorded": x["videoFiles"][0]["filename"]
        }
        for x in call_epgstation_api(f"/recording?offset=0&limit=10000&isHalfWidth={USE_HALF_WIDTH}")["records"]
    ])

@app.route("/reserves.json", methods=["GET"])
def get_reserves():
    # 扱いやすいように id をキーとして辞書を作る
    channels = {
        x["id"]: x
        for x in call_epgstation_api("/channels")
    }

    return jsonify([
        {
            "id": to_base_36(x["programId"]),
            "category": {
                0x0: "news",
                0x1: "sports",
                0x2: "information",
                0x3: "drama",
                0x4: "music",
                0x5: "variety",
                0x6: "cinema",
                0x7: "anime",
                0x8: "documentary",
                0x9: "theater",
                0xA: "hobby",
                0xB: "welfare",
                0xC: "etc",
                0xD: "etc",
                0xE: "etc",
                0xF: "etc"
            }[x["genre1"]],
            "title": x["name"],
            "fullTitle": x["name"],  # TODO: Support flags such as [字]
            "detail": x.get("description", ""),
            "start": x["startAt"],
            "end": x["endAt"],
            "seconds": (x["endAt"] - x["startAt"]) / 1000,
            "description": x.get("description", ""),
            "extra": {
                " ": x["extended"]  # TODO
            } if "extended" in x else {},
            "channel": {
                "type": channels[x["channelId"]]["channelType"],
                "channel": channels[x["channelId"]]["channel"],
                "name": channels[x["channelId"]]["halfWidthName" if USE_HALF_WIDTH else "name"],
                "id": to_base_36(x["channelId"]),
                "sid": channels[x["channelId"]]["serviceId"],
                "nid": channels[x["channelId"]]["networkId"],
                "hasLogoData": channels[x["channelId"]]["hasLogoData"],
                "n": channels[x["channelId"]]["remoteControlKeyId"]
            },
            "subTitle": "",  # Unsupported
            "episode": None,  # Unsupported
            "flags": [],  # Unsupported

            "isConflict": x["isConflict"],
            "recordedFormat": ""  # Unsupported
        }
        for x in call_epgstation_api(f"/reserves?offset=0&limit=10000&isHalfWidth={USE_HALF_WIDTH}")["reserves"]
    ])

def to_base_36(value):
    n = 36
    characters = string.digits + string.ascii_lowercase

    result = ""
    tmp = value
    while tmp >= n:
        idx = tmp%n
        result = characters[idx] + result
        tmp = int(tmp / n)
    idx = tmp%n
    result = characters[idx] + result
    return result

if __name__ == "__main__":
    app.run(host=HTTP_HOST, port=HTTP_PORT)
