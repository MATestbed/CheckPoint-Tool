import os

from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__)
ALLOWED_EXTENSIONS = {"png"}


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/get_folders", methods=["POST"])
def get_folders():
    path = request.form.get("path")

    print("Received path:", path)
    if os.path.exists(path):
        folders = [
            folder
            for folder in os.listdir(path)
            if os.path.isdir(os.path.join(path, folder))
        ]
        return jsonify(folders)
    print("error")
    return jsonify([])


@app.route("/get_images", methods=["POST"])
def get_images_list():
    path = request.form.get("path")
    if os.path.exists(path):
        images_list = os.listdir(path)
        images_list = [
            img
            for img in images_list
            if img.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS and "drawed" in img
        ]
        # 排序按顺序返回
        # [:-7]为了适应0_drawed.png这种格式的图片
        images_list.sort(key=lambda x: int((x.split(".")[0])[:-7]))
        images = [
            os.path.join(path, img)
            for img in images_list
            if img.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS
        ]
        print("\n".join(images))
        return jsonify(images)
    return jsonify([])


@app.route("/image")
def load_single_image():
    path = request.args.get("path")
    if not path:
        return "No image path provided", 400
    if not os.path.exists(path) or not os.path.isfile(path):
        return "Image not found", 404
    return send_from_directory(os.path.dirname(path), os.path.basename(path))


@app.route("/get_instruction", methods=["POST"])
def get_instruction():
    folder_path = request.form.get("folder_path")
    try:
        with open(folder_path + "/instruction.txt", "r") as file:
            content = file.read()
        return content
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_annotation", methods=["POST"])
def get_annotation():
    annotation_path = request.form.get("annotation_path")
    try:
        if os.path.exists(annotation_path):
            with open(annotation_path, "r") as file:
                annotation = file.read()
                return annotation
        else:
            return "", 204  # No content for this path
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/save_annotations", methods=["POST"])
def save_annotations():
    data = request.get_json()
    task_folder_path = data["currentFolderPath"]
    annotations = data[
        "annotations"
    ]  # This should be a list of annotations corresponding to images
    select_images_list = data["selectedImages"]

    # 对select_images_list中的元素进行排序
    # [:-7]为了适应0_drawed.png这种格式的图片
    select_images_list.sort(key=lambda x: int((x.split(".")[0])[:-7]))

    # selected_images = "::".join(select_images_list)
    # checkpoint = Checkpoint.query.filter_by(user_id=current_user.id, task_folder_path=task_folder_path).first()
    # if checkpoint:
    #     checkpoint.selected_image_list = selected_images
    # else:
    #     checkpoint = Checkpoint(user_id=current_user.id, task_folder_path=task_folder_path, selected_image_list=selected_images)
    #     db.session.add(checkpoint)
    # db.session.commit()

    # 删除task_folder_path下的所有.text文件
    for filename in os.listdir(task_folder_path):
        if filename.endswith(".text"):
            os.remove(os.path.join(task_folder_path, filename))

    print(f"len: {len(annotations)}")
    print(annotations)
    print(f"len: {len(select_images_list)}")
    print(select_images_list)

    # Assuming `selectedImages` contains the image file names
    for filename in select_images_list:
        image_path = os.path.join(task_folder_path, filename)
        annotation_path = (
            image_path + ".text"
        )  # This is where you will save the annotation text

        # [:-7]为了适应0_drawed.png这种格式的图片
        index = (filename.split(".")[0])[:-7]
        annotation = annotations[int(index)]

        print(f"filename: {filename}")
        print(f"annotation: {annotation}")

        # Save the annotation to a .text file
        try:
            with open(annotation_path, "w") as file:
                file.write(annotation)
        except Exception as e:
            print(f"Failed to save annotation for {filename}: {str(e)}")
            return (
                jsonify(
                    {"error": f"Failed to save annotation for {filename}: {str(e)}"}
                ),
                500,
            )

    return jsonify({"message": "Annotations saved successfully"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8890)
