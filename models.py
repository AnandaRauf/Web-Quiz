from pony.orm import Database, Required, Set

db = Database()

class Admin(db.Entity):
    name = Required(str)
    email = Required(str)
    password = Required(str)

class User(db.Entity):
    name = Required(str)
    email = Required(str)
    password = Required(str)
    points = Required(int, default=0)
    answers = Set('Answer')

class Question(db.Entity):
    text = Required(str)
    answers = Set('Answer')

class Answer(db.Entity):
    user = Required(User)
    question = Required(Question)
    text = Required(str)
