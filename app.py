from flask import Flask, render_template, request, session, redirect
from DBcm import UseDatabase
from vsearch import search4letters
from checker import check_logged_in

app = Flask(__name__)
app.secret_key = 'SecretKey'

app.config['dbconfig'] = {
    'host': '10.211.55.11',
    'user': 'ithub',
    'password': 'Pa$$w0rd',
    'database': 'vsearchlogDB'
}

# Для первого варианта проверки авторизации
login = "admin"
password = "admin"


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to search4letters on the web!')


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    title = 'Here are your results'
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                           the_phrase=phrase,
                           the_letters=letters,
                           the_title=title,
                           the_results=results)


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    contents = []

    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select * from log"""
        cursor.execute(_SQL)
        data = cursor.fetchall()

    for row in data:
        contents.append(list(row))

    titles = ('#', 'Date', 'Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents)

    # with open('vsearch.log') as log:
    #     for line in log:
    #         contents.append([])
    #         for item in line.split('|'):
    #             contents[-1].append(escape(item))
    # titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results')
    # return render_template('viewlog.html',
    #                        the_title='View Log',
    #                        the_row_titles=titles,
    #                        the_data=contents)


def log_request(req: 'flask_request', res: str) -> None:
    # print(req.form['phrase'], req.form['letters'], req.remote_addr, str(req.user_agent.browser), res, sep=' ')
    # with open('vsearch.log', 'a') as log:
    #     print(req.form, req.remote_addr, req.user_agent, res, file=log, sep='|')

    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into log 
        (phrase, letters, ip, browser_string, results)
        values 
        (%s, %s, %s, %s, %s)"""

        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              str(req.user_agent),
                              res))


@app.route('/login')
def login_page() -> 'html':
    return render_template('login.html', the_title='Login page')


@app.route('/auth', methods=['POST'])
def do_login() -> 'html':
    ## Первый вариант с использованием одной пары логин-пароль из заданных в коде переменных
    # if request.form['login'] == login and request.form['password'] == password:
    #     session['logged_in'] = True
    #     return redirect('/viewlog')
    # else:
    #     return render_template('login.html', the_title='Login page', tried_to_login=True)

    ## Второй вариант с использованием заранее созданной таблицы creds в базе данных и поиске там пользователей
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = f"""select login, password from creds where login = '{request.form['login']}'"""
        cursor.execute(_SQL)
        creds = cursor.fetchone()
    if creds and request.form['login'] == creds[0] and request.form['password'] == creds[1]:
        session['logged_in'] = True
        return redirect('/viewlog')
    else:
        return render_template('login.html', the_title='Login page', tried_to_login=True)


@app.route('/logout')
@check_logged_in
def do_logout() -> str:
    if 'logged_in' in session:
        session.pop('logged_in')
        return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
