from flask import Flask,render_template,request,redirect,url_for,abort,flash
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5  #pip install bootstrap-flask
from flask_sqlalchemy import SQLAlchemy
import os


app=Flask(__name__)
app.config["SECRET_KEY"]=os.environ.get("FLASK_KEY")

bootstrap=Bootstrap5(app)

db=SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DB_URI","sqlite:///todolist.db")
db.init_app(app)


class Task(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    task_name=db.Column(db.String,nullable=False)
    status=db.Column(db.Boolean,nullable=False,default=False)


with app.app_context():
    db.create_all()


class AddTaskForm(FlaskForm):
    task=StringField("",validators=[DataRequired()])
    submit=SubmitField("Add Task")


@app.route('/',methods=["GET","POST"])
def home():
    result=db.session.execute(db.select(Task))
    all_tasks=list(result.scalars())

    add_form=AddTaskForm()

    if add_form.validate_on_submit():
        new_task=Task(task_name=add_form.task.data,status=bool(request.form.get("status")))
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("index.html",form=add_form, all_tasks=all_tasks)


@app.route("/delete-task/<int:task_id>")
def delete_task(task_id):
    #index=request.args.get("task_id") - this is needed only if u don't want to pass a template varaible
    task=db.session.execute(db.select(Task).where(Task.id==task_id)).scalar()

    if not task:
        return abort(404)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('home'))


@app.route("/update-task/<int:task_id>",methods=["GET","POST"])
def update_task(task_id):
    if request.method=="POST":
        status=request.form.get("status")

        task=db.session.execute(db.select(Task).where(Task.id==task_id)).scalar()
        task.status=bool(status)
        db.session.commit()

        result = db.session.execute(db.select(Task).where(Task.status == 1))
        all_done = list(result.scalars())
        data = db.session.execute(db.select(Task))
        row_data = list(data.scalars())

        if len(all_done) == len(row_data):
            if len(row_data)>1:
                flash("Congats! You've completed all your tasks.")
            else:
                flash("Congats! You've completed the task.")

            for row in row_data:
                db.session.delete(row)
                db.session.commit()
            return redirect(url_for('home',all_rows=row_data))

        return redirect(url_for('home',all_rows=row_data))

    return render_template("index.html")


if __name__=="__main__":
    app.run(debug=False)