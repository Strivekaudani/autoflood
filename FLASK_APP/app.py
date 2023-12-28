import requests
from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_mail import Mail, Message

from passlib.hash import sha256_crypt

engine = create_engine("*******************************")
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '****************@gmail.com'
app.config['MAIL_PASSWORD'] = '*********************'

mail = Mail(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        try:
            name = request.form.get("name")
            surname = request.form.get("surname")
            email = request.form.get("email")
            current_city = request.form.get("current_city")
            password = request.form.get("password")
            confirm = request.form.get("confirm")
            security_question = request.form.get("question")
            security_answer = request.form.get("answer")
            secure_password = sha256_crypt.encrypt(str(password))

            name.capitalize()
            surname.capitalize()
            current_city.capitalize()
            password.capitalize()
            confirm.capitalize()
            security_answer.capitalize()

            emaill = db.execute("SELECT email FROM users WHERE email = :email", {"email":email}).fetchone()

            if password == confirm:
                if emaill is None:
                    db.execute("INSERT INTO users(name, surname, email, hpassword, city)VALUES(:name, :surname, :email, :hpassword, :city)",
                                {"name":name, "surname":surname, "email":email, "hpassword":secure_password, "city":current_city})
                    db.execute("INSERT INTO passwords(email, password, question, answer)VALUES(:email, :password, :question, :answer)",
                                {"email":email, "password":password, "question":security_question, "answer":security_answer})
                    db.commit()
                else:
                    messagess = "Email address already exists"
                    return render_template("error.html", messagess = messagess)
                return redirect(url_for('signin'))
            else:
                messagess = "Password does not match"
                return render_template("error.html", messagess = messagess)

        except ConnectionError as e:
            messagess = "Connection Error. Check your internet connection and try again."
            return render_template("error.html", messagess = messagess)
        except Exception as e:
            messagess = "Sorry, something went wrong. Please try again."
            return render_template("error.html", messagess = messagess)

    return render_template("signup.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/welcome", methods = ["GET", "POST"])
def welcome():
    if request.method == "POST":
        try:
            emails = request.form.get("username")
            passwords = request.form.get("pword")
            passwords.capitalize()
            email_data = db.execute("SELECT email FROM users WHERE email = :email", {"email":emails}).fetchone()
            password_data = db.execute("SELECT hpassword FROM users WHERE email = :email", {"email":emails}).fetchone()

            if email_data is None:
                messagess = "E-mail address not found"
                return render_template("error.html", messagess = messagess)
            else:
                for pass_data in password_data:
                    if sha256_crypt.verify(passwords, pass_data):
                        city_db = db.execute("SELECT city FROM users WHERE email = :email", {"email":emails}).fetchone()
                        name_db = db.execute("SELECT name FROM users WHERE email = :email", {"email":emails}).fetchone()
                        nm = name_db[0]

                        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=82147e9cb4f92562561d007947eaffc2&units=metric'
                        city = city_db[0]
                        r = requests.get(url.format(city)).json()
                        weather = {
                            'city': city,
                            'temperature': r['main']['temp'],
                            'humidity': r['main']['humidity'],
                            'description': r['weather'][0]['description'],
                            'icon': r['weather'][0]['icon'],
                            'country': r['sys']['country']
                        }
                        return render_template("welcome.html", weather = weather, nm = nm)
                    else:
                         messagess = "Incorrect Password"
                         return render_template("error.html", messagess = messagess)

        except ConnectionError as e:
            messagess = "Connection Error. Check your internet connection and try again."
            return render_template("error.html", messagess = messagess)
        except Exception as e:
            messagess = "Sorry, something went wrong. Please try again."
            return render_template("error.html", messagess = messagess)

    return render_template("welcome.html", weather = weather, nm = nm)

@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route("/recover", methods = ["GET", "POST"])
def recover():
    if request.method == "POST":
        try:
            emai = request.form.get("username")
            quest_db = db.execute("SELECT question FROM passwords WHERE email = :email", {"email":emai}).fetchone()

            if quest_db is None:
                messagess = "E-mail Address Not Found"
                return render_template("error.html", messagess = messagess)
            else:
                quest = quest_db[0]

        except ConnectionError as e:
            messagess = "Connection Error. Check your internet connection and try again."
            return render_template("error.html", messagess = messagess)
        except Exception as e:
            messagess = "Sorry, something went wrong. Please try again."
            return render_template("error.html", messagess = messagess)

    return render_template("recover.html", quest = quest)

@app.route("/password", methods = ["GET", "POST"])
def password():
    if request.method == "POST":
        try:
            ans = request.form.get("answers")
            ans.capitalize()
            e_mail = request.form.get("mail")
            answer_db = db.execute("SELECT answer FROM passwords WHERE email = :email", {"email":e_mail}).fetchone()
            ans_wer = answer_db[0]

            if ans == ans_wer:
                passs = db.execute("SELECT password FROM passwords WHERE answer = :answer", {"answer":ans}).fetchone()
                paass = passs[0]

                nom_db = db.execute("SELECT name FROM users WHERE email = :email" , {"email":e_mail}).fetchone()
                nom = nom_db[0]
                surnom_db = db.execute("SELECT surname FROM users WHERE email = :email" , {"email":e_mail}).fetchone()
                surnom = surnom_db[0]

                msg = Message('Password for AutoFlood', sender = 'autofloodapp@gmail.com', recipients = [e_mail])
                msg.body = "Hie " + nom + " " + surnom + "! The password for your AutoFlood account is " + paass + " \n\nRegards, \n\nThe AutoFlood Team"
                mail.send(msg)
            else:
                messagess = "Answer is Incorrect"
                return render_template("error.html", messagess = messagess)

        except ConnectionError as e:
            messagess = "Connection Error. Check your internet connection and try again."
            return render_template("error.html", messagess = messagess)
        except Exception as e:
            messagess = "Sorry, something went wrong. Please try again."
            return render_template("error.html", messagess = messagess)

    return render_template("password.html", e_mail = e_mail)



if __name__ == "__main__":
    app.run(debug = True)
    app.secret_key = "autofloodapp"
