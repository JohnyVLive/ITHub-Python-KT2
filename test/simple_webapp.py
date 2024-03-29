from flask import Flask, session
from checker import check_logged_in

app = Flask(__name__)
app.secret_key = 'SecretKey'

@app.route('/')
def hello():
    return 'Hello from the simple webapp.'


@app.route('/page1')
@check_logged_in
def page1():
    return 'This is page 1.'



@app.route('/page2')
def page2():
    return 'This is page 2.'


@app.route('/page3')
def page3():
    return 'This is page 3.'


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return "You are logged in"

@app.route('/logout')
def do_logout() -> str:
    if 'logged_in' in session:
        session.pop('logged_in')
        return "You are logged out"
    else:
        return "You are NOT logged in"

@app.route('/status')
def check_status() -> str:
    if 'logged_in' in session:
        return "You are currently logged in"
    else:
        return "You are NOT logged in"

if __name__ == '__main__':
    app.run(debug=True)
