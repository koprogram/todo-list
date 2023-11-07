from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)  # New field for the description
    deadline = db.Column(db.DateTime, default=datetime.utcnow)  # New field for the deadline
    complete = db.Column(db.Boolean)

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    description = request.form.get('description')
    deadline = request.form.get('deadline')  # Expecting a string in YYYY-MM-DD format
    deadline_date = datetime.strptime(deadline, '%Y-%m-%d') if deadline else None
    new_task = Task(title=title, description=description, deadline=deadline_date, complete=False)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        deadline = request.form['deadline']
        task.deadline = datetime.strptime(deadline, '%Y-%m-%d') if deadline else None
        task.complete = 'complete' in request.form
        db.session.commit()
        return redirect(url_for('index'))
    elif 'complete' in request.args:
        task.complete = True
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)



@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.filter_by(id=task_id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():  # Push an application context
        db.create_all()
    app.run(debug=True)
