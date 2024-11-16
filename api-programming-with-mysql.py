from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://username:password@localhost/books_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False