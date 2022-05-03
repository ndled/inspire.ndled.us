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
    youtube_id = []
    youtube_names = []
    for folder in os.listdir("./youtube_screen_grab/static/temp/"):
        if os.path.isdir(f"./youtube_screen_grab/static/temp/{folder}"):
            if len(folder) == 11:
                if os.listdir(f"./youtube_screen_grab/static/temp/{folder}"):
                    youtube_id.append(folder)
                    youtube_names.append(
                        os.listdir(f"./youtube_screen_grab/static/temp/{folder}")[
                            0
                        ].split(folder)[0]
                    )
    if request.method == "POST":
        if request.form.get("submit"):
            form_data = request.form
            url, url_id = youtube_url_handler(form_data["new_video"])
            if url_id in youtube_id:
                return redirect(url_for("/.newurl", url_id=url_id))
            elif len(url_id) == 11:
                task = new_video.delay(url, url_id)
                return redirect(url_for("/.taskstatus", task_id=task.id, url_id=url_id))
            flash("Nope! Should be a valid youtube url")
            return render_template("new.html", results=youtube_id, name=youtube_names)
        else:
            flash("need a url")
            return render_template("new.html", results=youtube_id, name=youtube_names)
    else:
        return render_template("new.html", results=youtube_id, name=youtube_names)


@bp.route("/taskstatus/<task_id>_<url_id>", methods=["GET", "POST"])
def taskstatus(task_id, url_id):
    task = new_video.AsyncResult(task_id)
    if task.state != "SUCCESS":
        if os.path.exists(f"./youtube_screen_grab/static/temp/{url_id}"):
            if len(os.listdir(f"./youtube_screen_grab/static/temp/{url_id}")) > 1:
                flash("Finished downloading, but still processing images")
                return redirect(url_for("/.newurl", url_id=url_id))
        return render_template(
            "task.html",
            video_name="In Progress, this can take a while. Press random image to see if it's done",
            status=task.state,
            result_url=url_id,
        )
    else:
        return redirect(url_for("/.newurl", url_id=task.result.split("v=")[-1]))


@bp.route("/<url_id>", methods=["GET", "POST"])
def newurl(url_id):
    if os.path.exists(f"./youtube_screen_grab/static/temp/{url_id}"):
        if len(os.listdir(f"./youtube_screen_grab/static/temp/{url_id}")) > 1:
            image_path = random_image(
                img_dir=f"./youtube_screen_grab/static/temp/{url_id}"
            )
            return render_template(
                "task.html",
                image=f"./static/temp/{url_id}/{image_path}",
                video_name=image_path.split(".mp4")[0],
            )
        else:
            flash("working on it")
            return render_template("task.html")
    else:
        return redirect(url_for("/.new"))
