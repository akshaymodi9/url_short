import sqlite3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import datetime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String())
    tiny_url = db.Column(db.String())
    created_timestamp = db.Column(db.DateTime)

    def __init__(self, original_url, tiny_url, created_timestamp):
        self.original_url = original_url
        self.tiny_url = tiny_url
        self.created_timestamp = created_timestamp


class UrlSchema(ma.Schema):
    class Meta:
        fields = ('original_url', 'tiny_url')


url_schema = UrlSchema()

''' 4424637687969321678 '''

@app.route('/<url>', methods=['GET'])
def get_url(url):
    result = db.session.query(Urls).filter(Urls.tiny_url == url).first()

    if result is None:
        return jsonify({"msg": "Url not found in database"})

    return url_schema.jsonify(result)


@app.route('/', methods=["POST"])
def add_url():
    original_url = request.json['original_url']

    url_present = db.session.query(Urls).filter(Urls.original_url == original_url).first()

    if url_present is not None:
        return url_schema.jsonify(url_present)

    tiny_url = hash(original_url)

    hash_present = db.session.query(Urls).filter(Urls.tiny_url == tiny_url).first()

    if hash_present is not None:
        tiny_url = hash(tiny_url)

    new_url = Urls(original_url, tiny_url, datetime.datetime.now())

    db.session.add(new_url)
    db.session.commit()

    return url_schema.jsonify(new_url)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
