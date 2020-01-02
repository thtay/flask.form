from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import SelectField



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

subs = db.Table('subs',
    db.Column('design_id', db.Integer, db.ForeignKey('design.design_id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id'))
)

class Design (db.Model):
    design_id = db.Column(db.Integer, primary_key=True)
    design_name = db.Column(db.String(40))
    design_content = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default= datetime.utcnow)
    subscriptions = db.relationship('Tag', 
        secondary=subs, 
        backref = db.backref('subscribers', lazy = 'dynamic')
        )

    def __repr__(self):
        return '<Design {}>'.format(self.design_id)

class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(20))

    def __repr__(self):
        return '<Tag {}>'.format(self.tag_name)


@app.route("/", methods=['POST','GET'])
def index():

    if request.method == 'POST':
        design_content_input = request.form['design_input']
        tag_content = request.form['tag_input']
        design_info = request.form['design_info']
        new_design = Design(design_name=design_content_input, 
                            design_content=design_info)

        #exists = db.session.query(Tag.tag_id).filter_by(tag_name=tag_content).scalar() is not None
        exists = Tag.query.filter_by(tag_name=tag_content).first()
        if exists is not None: 
            #return 'This Tag is Found'
            new_tag = exists
        else:
            new_tag = Tag(tag_name = tag_content)   

        try:
            db.session.add(new_design)
            db.session.add(new_tag)  
            new_design.subscriptions.append(new_tag)
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem adding new designs"
    else:
        posts = Design.query.all()
        tags = Tag.query.all()
        return render_template("index.html", posts=posts, tags=tags)

@app.route('/delete/<int:id>')
def delete(id):
    design_to_delete = Design.query.get_or_404(id)

    for each_tag in design_to_delete.subscriptions:
        designs_using_tag = []
        for any_design in each_tag.subscribers:
            designs_using_tag.append(any_design.design_name)

        if len(designs_using_tag) == 1:
            tag_to_delete = each_tag
            try:
                db.session.delete(each_tag)
            except:
                return 'There was a problem deleting the tag from task'

    try:
        db.session.delete(design_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    posts = Design.query.get_or_404(id)
    if request.method == 'POST':
        posts.design_content = request.form['content']
        posts.design_name = request.form['name']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error updating task'
    else:
        return render_template('update.html', posts = posts)


@app.route('/search/<int:id>', methods=['GET','POST'])
def search(id):
    posts = []
    tag = Tag.query.get_or_404(id)
    for p in tag.subscribers:
        posts.append(p)

    return render_template('search.html', posts = posts)


@app.route('/tagdelete/<int:id>')
def tagdelete(id):
    tag_to_delete = Tag.query.get_or_404(id)

    try:
        db.session.delete(tag_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that tag'


if __name__ == "__main__":
    app.run(debug=True)