from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@localhost/books_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year
        }

with app.app_context():
    db.create_all()

@app.route("/api/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify({"success": True, "data": [book.to_dict() for book in books], "total": len(books)}), HTTPStatus.OK

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    
    if book is None:
        return jsonify(
            {
                "success": False, 
                "error": "Book not found"
            }
        ), HTTPStatus.NOT_FOUND
    
    return jsonify(
        {
            "success": True, 
            "data": book.to_dict(),
        }
    ), HTTPStatus.OK

@app.route("/api/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return jsonify(
            {
                "success": False,
                "error": "Content-type must be application/json"
            }
        ), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    
    required_fields = ["title", "author", "year"]
    for field in required_fields:
        if field not in data:
            return jsonify(
                { 
                    "success": False,
                    "error": f"Missing required field: {field}",
                }
            ), HTTPStatus.BAD_REQUEST
        
    new_book = Book(
        title=data['title'],
        author=data['author'],
        year=data['year']
    )
    
    db.session.add(new_book)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": new_book.to_dict(),
        }
    ), HTTPStatus.CREATED

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get(book_id)

    if book is None:
        return jsonify(
            {
                "success": False,
                "error": "Book not found"
            }
        ), HTTPStatus.NOT_FOUND

    data = request.get_json()

    if not data:
        return jsonify(
            {
                "success": False,
                "error": "No data provided for update"
            }
        ), HTTPStatus.BAD_REQUEST
    
    allowed_keys = {"title", "author", "year"}
    for key in data:
        if key in allowed_keys:
            setattr(book, key, data[key])

    if "year" in data and (not isinstance(data["year"], int) or data["year"] <= 0):
        return jsonify(
            {
                "success": False,
                "error": "Invalid value for 'year'"
            }
        ), HTTPStatus.BAD_REQUEST

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": book.to_dict()
        }
    ), HTTPStatus.OK

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    
    if book is None:
        return jsonify(
            {
                "success": False,
                "error": "Book not found"
            }
        ), HTTPStatus.NOT_FOUND

    db.session.delete(book)
    db.session.commit()
    
    return jsonify(
        {
            "success": True,
            "message": f"Book with id {book_id} deleted successfully",
            "deleted_book": book.to_dict()  
        }
    ), HTTPStatus.OK

@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "success": False,
            "error": "Resource not found"
        }
    ), HTTPStatus.NOT_FOUND

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify(
        {
            "success": False,
            "error": "Internal Server Error"
        }
    ), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(debug=True)
