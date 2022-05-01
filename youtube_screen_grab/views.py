from flask import render_template
from flask import request
from flask import Blueprint
import os

from youtube_screen_grab.util import download, remove_old, video_cut, random_image

bp = Blueprint("/new", __name__)


@bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        if request.form.get("submit"):
            form_data = request.form
            url = form_data["new_video"]
            if os.path.exists("./youtube_screen_grab/static/temp/"):
                remove_old("./youtube_screen_grab/static/temp/")
            else:
                os.makedirs("./youtube_screen_grab/static/temp/")
            download(url, "./youtube_screen_grab/static/temp")
            video_path = "./youtube_screen_grab/static/temp/"
            video_cut(video_path, "./youtube_screen_grab/static/temp")
            image_path = random_image("./youtube_screen_grab/static/temp")
            return render_template("new.html", image=f"static/temp/{image_path}")
        if request.form["random_image"]:
            image_path = random_image(img_dir="./youtube_screen_grab/static/temp")
            return render_template("new.html", image=f"static/temp/{image_path}")
    else:
        return render_template("new.html")
