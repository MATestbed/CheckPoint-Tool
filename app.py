from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/jxq/mobile-agent/checkpoint_tools/instance/data.db'
ALLOWED_EXTENSIONS = {'png'}

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    password = db.Column(db.String(50), nullable=False)

# class Checkpoint(db.Model):
#     __tablename__ = 'checkpoints'

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.String(50), nullable=False)
#     task_folder_path = db.Column(db.String(120), nullable=False)
#     selected_image_list = db.Column(db.String(2000))

#     __table_args__ = (db.UniqueConstraint('user_id', 'task_folder_path', name='_user_task_uc'),)

#     def __init__(self, user_id, task_folder_path, selected_image_list):
#         self.user_id = user_id
#         self.task_folder_path = task_folder_path
#         self.selected_image_list = selected_image_list

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@app.route('/get_folders', methods=['POST'])
@login_required
def get_folders():
    path = request.form.get('path')

    print("Received path:", path)
    if os.path.exists(path):
        folders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
        return jsonify(folders)
    print("error")
    return jsonify([])


@app.route('/get_images', methods=['POST'])
@login_required
def get_images_list():
    path = request.form.get('path')
    if os.path.exists(path):
        images_list = os.listdir(path) 
        images_list = [img for img in images_list if img.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS and "drawed" in img]
        # 排序按顺序返回
        # [:-7]为了适应0_drawed.png这种格式的图片
        images_list.sort(key=lambda x:int((x.split('.')[0])[:-7]))
        images = [os.path.join(path, img) for img in images_list if img.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS]
        print("\n".join(images))
        return jsonify(images)
    return jsonify([])

@app.route('/image')
@login_required
def load_single_image():
    path = request.args.get('path')
    if not path:
        return "No image path provided", 400
    if not os.path.exists(path) or not os.path.isfile(path):
        return "Image not found", 404
    return send_from_directory(os.path.dirname(path), os.path.basename(path))


@app.route('/get_instruction', methods=['POST'])
def get_instruction():
    folder_path = request.form.get('folder_path')
    try:
        with open(folder_path + "/instruction.txt", 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/get_annotation', methods=['POST'])
@login_required
def get_annotation():
    annotation_path = request.form.get('annotation_path')
    try:
        if os.path.exists(annotation_path):
            with open(annotation_path, 'r') as file:
                annotation = file.read()
                return annotation
        else:
            return '', 204  # No content for this path
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

@app.route('/save_annotations', methods=['POST'])
@login_required
def save_annotations():
    data = request.get_json()
    task_folder_path = data['currentFolderPath']
    annotations = data['annotations']  # This should be a list of annotations corresponding to images
    select_images_list = data['selectedImages']

    # 对select_images_list中的元素进行排序
    # [:-7]为了适应0_drawed.png这种格式的图片
    select_images_list.sort(key=lambda x:int((x.split('.')[0])[:-7]))
    
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
        annotation_path = image_path + '.text'  # This is where you will save the annotation text
        
        # [:-7]为了适应0_drawed.png这种格式的图片
        index = (filename.split('.')[0])[:-7]
        annotation = annotations[int(index)]

        print(f"filename: {filename}")
        print(f"annotation: {annotation}")

        # Save the annotation to a .text file
        try:
            with open(annotation_path, 'w') as file:
                file.write(annotation)
        except Exception as e:
            print(f"Failed to save annotation for {filename}: {str(e)}")
            return jsonify({"error": f"Failed to save annotation for {filename}: {str(e)}"}), 500
    

    return jsonify({"message": "Annotations saved successfully"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(debug=True, port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
