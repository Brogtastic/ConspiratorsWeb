from flask import Blueprint, render_template, request, jsonify, redirect, url_for

views = Blueprint(__name__, "views")

test = 'Nothing at all'
name = "Tim"

@views.route("/", methods=['GET', 'POST'])
def home():
    global test
    global name
    if(request.method=='POST'):
        test = request.form.get('test')
    return render_template("index.html", name=name)

@views.route("/profile")
def profile():
    global name
    args = request.args
    name = args.get('name', name)  # If 'name' is not in the query parameters, keep the current name
    return jsonify({'name': name})

@views.route("/json")
def get_json():
    global test
    if(request.form.get('test')):
        test = request.form.get('test')
    return jsonify({'name': 'Brogdog', 'coolness': 10, 'test': test})

@views.route("/data")
def get_data():
    data = request.json
    return jsonify(data)

@views.route("/get-json")
def go_to_home():
    return redirect(url_for("views.get_json"))