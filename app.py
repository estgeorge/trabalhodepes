# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = 'asdkjv99jkkHGks34'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/areadocliente')
def areadocliente():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    return 'Logged in as ' + username + '<br>' + \
        "<b><a href = '/logout'>click here to log out</a></b>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Senha inválida. Tente novamente.'
        else:
            session['username'] = request.form['username']
            return redirect(url_for('areadocliente'))
    return render_template('login.html', error=error)


def logged_in():
    if 'username' not in session:
        return redirect(url_for('login'))


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
