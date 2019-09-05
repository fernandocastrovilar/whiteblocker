import logging
import os
import whiteblocker_api
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from threading import Thread


# Create the application instance
app = Flask(__name__)
logging.basicConfig(filename="api.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)


@app.route('/')
def root():
    return redirect('/home')


@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = "Invalid Credentials. Please, try again."
            flash(error)
            return render_template('login.html')
        else:
            session['logged_in'] = True
            return redirect('/home')
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/home')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='static/favicon.ico')


@app.route('/list')
def list_whiteblocker():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')


@app.route('/manual')
def manual_whiteblocker():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')


@app.route('/help')
def help_whiteblocker():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect("https://github.com/fernandocastrovilar/whiteblocker", code=302)


if __name__ == "__main__":
    try:
        app.secret_key = os.urandom(12)
        #check = check_system()
        #if check == "ko":
        #	raise Exception("Iptables is not installed")
        Thread(target=whiteblocker_api.main()).start()
        Thread(target=app.run(host="0.0.0.0", debug=True)).start()
    except KeyboardInterrupt:
        print("^C received, shutting down the web server")
        logging.error("^C received, shutting down the web server")
        exit("Exit")
    except Exception as e:
        print(e)
        logging.error(e)

