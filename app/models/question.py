"""
question.py
-----------
WHAT: The question bank used ONLY by the Before/After Cyber Safety
      Assessment (Part H) — separate from Challenge (used by the game,
      see app/models/challenge.py). See challenge.py's docstring for why
      these are kept as two separate table pairs.
WHERE: app/models/question.py
"""

from app.extensions import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # phishing, url, password, scam, general
    text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    options = db.relationship(
        "QuestionOption", back_populates="question", order_by="QuestionOption.order_index",
        cascade="all, delete-orphan",
    )

    def correct_option(self):
        return next((o for o in self.options if o.is_correct), None)

    def __repr__(self):
        return f"<Question {self.id} [{self.category}]>"


class QuestionOption(db.Model):
    __tablename__ = "question_options"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    question = db.relationship("Question", back_populates="options")

    def __repr__(self):
        return f"<QuestionOption {self.id} correct={self.is_correct}>"
