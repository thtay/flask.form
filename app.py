from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm

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
    backref = db.backref('subscribers', lazy='dynamic')
        )

    def __repr__(self):
        return '<Design {}>'.format(self.design_id)


class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(20))

    def __repr__(self):
        return '<Tag {}>'.format(self.tag_name)


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        tag_id_list = request.form.getlist('mycheckbox')
        filter_posts = []
        for tag_id in tag_id_list:
            tag = Tag.query.get_or_404(tag_id)
            for post in tag.subscribers:
                filter_posts.append(post)
        tags = Tag.query.all()
        return render_template('index.html', posts=filter_posts, tags=tags, filtered_tags=tag_id_list)
    else:
        posts = Design.query.all()
        tags = Tag.query.all()
        return render_template('index.html', posts=posts, tags=tags)

@app.route('/delete/<int:id>')
def delete(id):
    design_to_delete = Design.query.get_or_404(id)

    for each_tag in design_to_delete.subscriptions:
        # All the tags in that design
        designs_using_tag = []
        for any_design in each_tag.subscribers:
            #Designs that use that tag
            designs_using_tag.append(any_design.design_name)
        if len(designs_using_tag) == 1:
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


@app.route('/update/<int:id>',methods=['GET', 'POST'])
def update(id):
    posts = Design.query.get_or_404(id)
    tag_string = ""
    orignal_tags = set()
    for design_tag in posts.subscriptions:
        tag_string += design_tag.tag_name + ","
        orignal_tags.add(design_tag.tag_name)
    if request.method == 'POST':
        posts.design_content = request.form['content']
        posts.design_name = request.form['name']
        tag_content = request.form['tag_input']
        multi_tags = tag_content.split(',')
        for each_tag in multi_tags:
            #Add new tag
            if each_tag not in orignal_tags:
                #add the tag to the design
                exists = Tag.query.filter_by(tag_name=each_tag).first()
                if exists is not None:
                    # return 'This Tag is Found'
                    posts.subscriptions.append(exists)
                else:
                    #Tag has never been used before
                    new_tag = Tag(tag_name=each_tag)
                    db.session.add(new_tag)
                    posts.subscriptions.append(new_tag)
            #Removed an existing tag
            else:
                ##Tag is already part of deisgn
                orignal_tags.remove(each_tag)
        if len(orignal_tags) > 0:
            for tag_to_delete in orignal_tags:
                tag_id_to_delete = Tag.query.filter_by(tag_name=tag_to_delete).first()
                posts.subscriptions.remove(tag_id_to_delete)
                designs_using_tag = []
                for any_design in tag_id_to_delete.subscribers:
                    designs_using_tag.append(any_design.design_name)
                if len(designs_using_tag) > 0:
                    try:
                        db.session.delete(tag_id_to_delete)
                    except:
                        return 'There was a problem deleting the tag from task'
            #Do nothing
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error updating task'
    else:
        return render_template('update.html', posts=posts, tag_string=tag_string)


@app.route('/search/<int:id>', methods=['GET', 'POST'])
def search(id):
    posts = []
    tag = Tag.query.get_or_404(id)
    for p in tag.subscribers:
        posts.append(p)

    return render_template('index.html', posts=posts)



@app.route('/adddesign', methods=['GET', 'POST'])
def adddesign():
    if request.method == 'POST':
        design_content_input = request.form['design_input']
        tag_content = request.form['tag_input']
        design_info = request.form['design_info']
        new_design = Design(design_name=design_content_input,
                            design_content=design_info)

        multi_tags = tag_content.split(',')
        for each_tag in multi_tags:
            exists = Tag.query.filter_by(tag_name=each_tag).first()
            if exists is not None:
                # return 'This Tag is Found'
                new_design.subscriptions.append(exists)
            else:
                new_tag = Tag(tag_name=each_tag)
                db.session.add(new_tag)
                new_design.subscriptions.append(new_tag)

        try:
            db.session.add(new_design)
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem adding new designs"
    else:
        return render_template('adddesign.html')



if __name__ == "__main__":
    app.run(debug=True)