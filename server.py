from flask import Flask, jsonify, send_file, render_template_string
import os
import json

# Tên thư mục chứa video
VIDEO_FOLDER = "video"
CONFIG_FILE = "config_media.json"

# Khởi tạo Flask app
app = Flask(__name__)


# Hàm tạo hoặc cập nhật config_media.json
def update_config():
    videos = [
        f
        for f in os.listdir(VIDEO_FOLDER)
        if os.path.isfile(os.path.join(VIDEO_FOLDER, f))
    ]
    config_data = []

    for idx, video in enumerate(videos, start=1):
        video_path = os.path.join(VIDEO_FOLDER, video)
        config_data.append({"id": str(idx), "video_path": video_path})

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)


# Route để lấy danh sách các video
@app.route("/video", methods=["GET"])
def list_videos():
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)

        video_links = {item["id"]: f"/video/{item['id']}" for item in config_data}

        # Tạo HTML để hiển thị danh sách video
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Video List</title>
        </head>
        <body>
            <h1>Available Videos</h1>
            <ul>
            {% for id, link in video_links.items() %}
                <li><a href="{{ link }}">Video {{ id }}</a></li>
            {% endfor %}
            </ul>
        </body>
        </html>
        """

        return render_template_string(html_template, video_links=video_links)
    except FileNotFoundError:
        return jsonify({"error": "No videos found or config file missing."}), 404


# Route để phát video dựa trên ID
@app.route("/video/<video_id>", methods=["GET"])
def serve_video(video_id):
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)

        video_item = next(
            (item for item in config_data if item["id"] == video_id), None
        )
        if video_item:
            return send_file(video_item["video_path"])
        else:
            return jsonify({"error": "Video not found."}), 404
    except FileNotFoundError:
        return jsonify({"error": "Config file missing."}), 404


if __name__ == "__main__":
    # Tạo thư mục video nếu chưa tồn tại
    if not os.path.exists(VIDEO_FOLDER):
        os.makedirs(VIDEO_FOLDER)

    # Cập nhật tệp config_media.json
    update_config()

    # Chạy server
    app.run(host="0.0.0.0", port=5000, debug=True)
