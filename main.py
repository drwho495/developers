from flask import Flask, redirect, url_for, render_template, request, session, flash
import pymongo
import dns
import base64
 
def get_base64_encoded_image(img_file):
	return base64.b64encode(img_file.read()).decode('utf-8')

client = pymongo.MongoClient("mongodb+srv://root:spooky123@cluster0.4uuqg.mongodb.net/test?retryWrites=true&w=majority")
mydb = client.dev
col = mydb.users

app = Flask(
				__name__,
				template_folder='templates',
				static_folder='static'
)

app.secret_key = "fasdfudhFSDUfD01110011 01100101 01100011 01110010 01100101 01110100SghdsugdfhdfgushusdhufsdFDSfhudsfhudsfhudshufsdhuf"

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/admin', methods = ["POST", "GET"])
def admin():
	if "user" in session:
		if session["user"] == "admin":
			if request.method == "POST":
				delId = request.form["id"]

				col2 = mydb.projects

				print(int(delId))

				col2.delete_one({"id": int(delId)})

				return render_template("admin.html")
			else:
				return render_template("admin.html")

@app.route('/project/<theid>')
def project(theid):
	col2 = mydb.projects

	projs = col2.find({},{'_id': False})

	json = None

	for proj in projs:
		print(theid)

		try:
			if proj["id"] and str(theid) == str(proj["id"]):

				json = proj
				break
		except:
			print("Deleted...")

	if "user" in session: 
		newvalues = { "$set": { "views": json["views"] + 1 } }
		print(json["views"] + 1)
		col2.update(json, newvalues)
	else:
		print("User not signed up!")
	return render_template("projects.html", content = [json, ""])

@app.route('/login', methods = ["POST", "GET"])
def login():
	if request.method == "POST":
		global username
		global password
		if request.form["username"] == "":
			flash("No username!")

			return render_template("login.html")
		if request.form["password"] == "":
			flash("No password!")

			return render_template("login.html")
		username = request.form["username"]
		password = request.form["password"]
		
		exists = False

		usersRaw = col.find({},{'_id': False})
		users = list(usersRaw)

		rlUsername = None
		rlPassword = None

		for x in users:
			print(x["username"])
			if(x["username"].lower() == username.lower()):
				exists = True
				rlUsername = x["username"]
				rlPassword = x["password"]
				break
		
		print(exists)

		if(exists == True and rlPassword.lower() == password.lower()):
			session["user"] = username			

			return redirect("user")
		else:
			flash("Username wrong!")

			return redirect("login")
	else:
		return render_template("login.html")


@app.route('/signup', methods = ["POST", "GET"])
def signup():
	if request.method == "POST":
		global username
		global password
		if request.form["username"] == "":
			flash("No username!")

			return render_template("signup.html")
		if request.form["password"] == "":
			flash("No password!")

			return render_template("signup.html")
		username = request.form["username"]
		password = request.form["password"]
		
		exists = False

		usersRaw = col.find({},{'_id': False})
		users = list(usersRaw)

		for x in users:
			if(x["username"].lower() == username.lower()):
				exists = True
				break
		
		if(exists == True):
			flash("User already exists!")

			return render_template("signup.html")
		else:
			col.insert_one({"username": username, "password": password})

			session["user"] = username
			return redirect("user")
	else:
		return render_template("signup.html")

@app.route('/user')
def user():
	if("user" in session):
		userProj = {}
		col2 = mydb.projects

		projRaw = col2.find({},{'_id': False})

		for project in list(projRaw):
			print(project["id"])

			if project["user"] == session["user"]:
				userProj[project["name"]] = project["id"]
	else:
		return redirect("/login")

	return render_template("user.html", content = {"user": session["user"], "projects": userProj})

@app.route('/create', methods = ["POST", "GET"])
def create():
	if request.method == "POST" and "user" in session:
		col2 = mydb.projects

		mainId = int(col2.find({}).sort("id", -1)[0]["id"])
		print(mainId + 1)
		idNum = mainId + 1 
		with open("null.jpg", "rb") as img_file:
			bse64_img = "data:image/jpeg;base64," + get_base64_encoded_image(img_file)

		if request.files:
			img = request.files["img"]

			bse64 = get_base64_encoded_image(img)
			bse64_img = "data:image/jpeg;base64," + bse64

		projName = request.form["projName"]
		desc = request.form["desc"]
		short_desc = request.form["short_desc"]
		language = request.form["language"]
		user = session["user"]
		website = request.form["site"]

		col2.insert_one({"name": projName, "website": website, "img": bse64_img, "descripton": desc, "short_desc": short_desc, "language": language, "user": user, "views": 0, "id": idNum})

		return redirect("/user")
	else:
		if "user" in session:
			return render_template("create.html")
		else:
			return redirect("/signup")
		
		
@app.route('/edit/<editId>', methods = ["POST", "GET"])
def edit(editId):
	if request.method == "POST" and "user" in session:
		col2 = mydb.projects

		proj = None

		for x in col2.find():
			if str(x["id"]) == str(editId) and x["user"] == session["user"]:
				proj = x
				break

		if proj == None:
			return "Doesnt exist!"

		projName = request.form["projName"]
		desc = request.form["desc"]
		short_desc = request.form["short_desc"]
		language = request.form["language"]
		user = session["user"]
		website = request.form["site"]

		newvalues = { "$set": {"name": projName, "website": website, "descripton": desc, "short_desc": short_desc, "language": language, "user": user} }
		
		col2.update_one(proj, newvalues)

		return redirect("/user")
	else:
		if "user" in session:
			col2 = mydb.projects

			proj = None

			for x in list(col2.find({},{'_id': False})):
				if str(x["id"]) == str(editId) and x["user"] == session["user"]:
					proj = x
					print("Exists!")
					break
			
			if proj != None:
				return render_template("edit.html", content = proj)
			else:
				return "404"
		else:
			return redirect("/signup")

@app.route('/projects')
def projects():
	col2 = mydb.projects
	popularRaw = col2.find({},{'_id': False}).limit(5).sort("views", -1)

	popular = list(popularRaw)

	newestRaw = col2.find({},{'_id': False}).limit(5).sort('date', -1)

	newest = list(newestRaw)
	
	return render_template("projects.html", content = {"popular": popular, "newest": newest})

@app.route('/popular')
def popular():
	col2 = mydb.projects
	projects = col2.find({},{'_id': False}).sort("views", -1)

	projArr = list(projects)

	return render_template("popular.html", content = projArr)

@app.route('/newest')
def newest():
	col2 = mydb.projects
	projects = col2.find({},{'_id': False}).sort("date", -1)

	projArr = list(projects)

	return render_template("popular.html", content = projArr)


app.run(host='0.0.0.0', port = 8080)
