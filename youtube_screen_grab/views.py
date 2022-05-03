from flask import render_template
from flask import request
from flask import Blueprint
from flask import url_for
from flask import redirect
from flask import flash

import os
from youtube_screen_grab import celery
from youtube_screen_grab.util import (
    download,
    remove_old,
    video_cut,
    random_image,
    youtube_url_handler,
)

bp = Blueprint("/", __name__)


@celery.task
def new_video(url, url_id):
    if os.path.exists(f"./youtube_screen_grab/static/temp/{url_id}"):
        remove_old(f"./youtube_screen_grab/static/temp/{url_id}")
    else:
        os.makedirs(f"./youtube_screen_grab/static/temp/{url_id}")
    download(url, f"./youtube_screen_grab/static/temp/{url_id}")
    video_path = f"./youtube_screen_grab/static/temp/{url_id}"
    video_cut(video_path, f"./youtube_screen_grab/static/temp/{url_id}")
    return url


@bp.route("/", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        if request.form.get("submit"):
            form_data = request.form
            url, url_id = youtube_url_handler(form_data["new_video"])
            if url_id in os.listdir("./youtube_screen_grab/static/temp/"):
                return redirect(url_for("/.newurl", url_id=url_id))
            elif len(url_id) == 11:
                task = new_video.delay(url, url_id)
                return redirect(url_for("/.taskstatus", task_id=task.id))
            else:
                flash("Nope! Should be a valid youtube url")
    else:
        results = []
        for folder in os.listdir("./youtube_screen_grab/static/temp/"):
            if os.path.isdir(folder):
                print(folder)
                if len(folder) == 11:
                    results.append(folder)
        return render_template("new.html", results=results)


@bp.route("/taskstatus/<task_id>", methods=["GET", "POST"])
def taskstatus(task_id):
    task = new_video.AsyncResult(task_id)
    if task.state != "SUCCESS":
        return render_template(
            "task.html",
            video_name="In Progress, this can take a while. Press random image to see if it's done",
            status=task.state,
        )
    else:
        return redirect(url_for("/.newurl", url_id=task.result.split("v=")[-1]))


@bp.route("/<url_id>", methods=["GET", "POST"])
def newurl(url_id):
    if os.path.exists(f"./youtube_screen_grab/static/temp/{url_id}"):
        image_path = random_image(img_dir=f"./youtube_screen_grab/static/temp/{url_id}")
        return render_template(
            "task.html",
            image=f"./static/temp/{url_id}/{image_path}",
            video_name=image_path.split(".mp4")[0],
        )
    else:
        return redirect(url_for("/.new"))
