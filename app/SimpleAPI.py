#!/usr/bin/env python3

from mysql.connector import connect, Error
import flask
import json

app = flask.Flask(__name__)

# disables JSON pretty-printing in flask.jsonify
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

DB_HOST = "mysqldb"
DB_NAME = "themes"
DB_TABLE = "themes"
DB_USER = "user"
DB_PASSWORD = "petyak00"


@app.route('/initdb')
def db_init():
    # весь код роботи з базою даних обертати в блок  try ... except, також треба закривати 
    # всі з'єднання до бази за допомогою диспетчера контекста with ... as ...
    mydb = connect(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASSWORD
    )
    cursor = mydb.cursor()
    # додати код ініціалізації користувача з перевіркою на існування
    cursor.execute("DROP DATABASE IF EXISTS " + DB_NAME)
    cursor.execute("CREATE DATABASE " + DB_NAME)
    cursor.close()

    mydb = connect(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME
    )
    cursor = mydb.cursor()

    cursor.execute("DROP TABLE IF EXISTS " + DB_TABLE)
    cursor.execute("CREATE TABLE " + DB_TABLE + " (id SERIAL PRIMARY KEY, title TEXT, url TEXT)")
    cursor.close()

    return resp(200, {"status": "init database done"})


def db_conn():
    try:
        connection = connect(
            host = "localhost",
            user = "user",
            password = "password",
        )
        print(connection)
        return connection
    except Error as e:
        print(e)


def to_json(data):
    return json.dumps(data) + "\n"


def resp(code, data):
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


def theme_validate():
    errors = []
    json = flask.request.get_json()
    if json is None:
        errors.append(
            "No JSON sent. Did you forget to set Content-Type header" +
            " to application/json?")
        return (None, errors)

    for field_name in ['title', 'url']:
        if type(json.get(field_name)) is not str:
            errors.append(
                "Field '{}' is missing or is not a string".format(
          field_name))

    return (json, errors)


def affected_num_to_code(cnt):
    code = 200
    if cnt == 0:
        code = 404
    return code


@app.route('/')
def root():
    return flask.redirect('/api/1.0/themes')

# e.g. failed to parse json
@app.errorhandler(400)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(404)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(405)
def page_not_found(e):
    return resp(405, {})


@app.route('/api/1.0/themes', methods=['GET'])
def get_themes():
    with db_conn() as db:
        tuples = db.query("SELECT id, title, url FROM themes")
        themes = []
        for (id, title, url) in tuples:
            themes.append({"id": id, "title": title, "url": url})
        return resp(200, {"themes": themes})


@app.route('/api/1.0/themes', methods=['POST'])
def post_theme():
    (json, errors) = theme_validate()
    if errors:  # list is not empty
        return resp(400, {"errors": errors})

    with db_conn() as db:
        insert = db.prepare(
            "INSERT INTO themes (title, url) VALUES ($1, $2) " +
            "RETURNING id")
        [(theme_id,)] = insert(json['title'], json['url'])
        return resp(200, {"theme_id": theme_id})


@app.route('/api/1.0/themes/<int:theme_id>', methods=['PUT'])
def put_theme(theme_id):
    (json, errors) = theme_validate()
    if errors:  # list is not empty
        return resp(400, {"errors": errors})

    with db_conn() as db:
        update = db.prepare(
            "UPDATE themes SET title = $2, url = $3 WHERE id = $1")
        (_, cnt) = update(theme_id, json['title'], json['url'])
        return resp(affected_num_to_code(cnt), {})


@app.route('/api/1.0/themes/<int:theme_id>', methods=['DELETE'])
def delete_theme(theme_id):
    with db_conn() as db:
        delete = db.prepare("DELETE FROM themes WHERE id = $1")
        (_, cnt) = delete(theme_id)
        return resp(affected_num_to_code(cnt), {})

if __name__ == '__main__':
    app.debug = True  # enables auto reload during development
    app.run(host ='0.0.0.0')