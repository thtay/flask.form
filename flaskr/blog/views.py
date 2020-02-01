from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr import db
from flaskr.blog.models import Design, Tag

bp: Blueprint = Blueprint("blog", __name__)


@bp.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        tag_id_list = request.form.getlist('mycheckbox')
        filter_posts = set()
        filter_tags = []
        for tag_id in tag_id_list:
            tag = Tag.query.get_or_404(tag_id)
            filter_tags.append(tag)
            for post in tag.subscribers:
                filter_posts.add(post)
        tags = Tag.query.all()
        return render_template("blog/index.html", posts=filter_posts, tags=tags, filtered_tags=filter_tags)
    else:
        posts = Design.query.all()
        tags = Tag.query.all()
        return render_template("blog/index.html", posts=posts, tags=tags)


@bp.route('/delete/<int:id>')
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
        return redirect(url_for("blog.index"))
    except:
        return 'There was a problem deleting that task'


@bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Design.query.get_or_404(id)
    tag_string = ""
    orignal_tags = set()
    for design_tag in post.subscriptions:
        tag_string += design_tag.tag_name + ","
        orignal_tags.add(design_tag.tag_name)
    if request.method == 'POST':
        post.design_content = request.form['content']
        post.design_name = request.form['name']
        tag_content = request.form['tag_input']

        multi_tags = tag_content.split(',')
        for each_tag in multi_tags:
            #Add new tag
            if each_tag not in orignal_tags:
                #add the tag to the design
                exists = Tag.query.filter_by(tag_name=each_tag).first()
                if exists is not None:
                    # return 'This Tag is Found'
                    post.subscriptions.append(exists)
                else:
                    #Tag has never been used before
                    new_tag = Tag(tag_name=each_tag)
                    db.session.add(new_tag)
                    post.subscriptions.append(new_tag)
            #Removed an existing tag
            else:
                ##Tag is already part of deisgn
                orignal_tags.remove(each_tag)
        if len(orignal_tags) > 0:
            for tag_to_delete in orignal_tags:
                tag_id_to_delete = Tag.query.filter_by(tag_name=tag_to_delete).first()
                post.subscriptions.remove(tag_id_to_delete)
                designs_using_tag = []
                for any_design in tag_id_to_delete.subscribers:
                    designs_using_tag.append(any_design.design_name)
                if len(designs_using_tag) > 0:
                    db.session.delete(tag_id_to_delete)
            #Do nothing
        try:
            db.session.commit()
            return redirect(url_for("blog.index"))
        except:
            return 'There was an error updating task'
    else:
        return render_template("blog/update.html", post=post, tag_string=tag_string)


@bp.route('/search/<int:id>', methods=['GET', 'POST'])
def search(id):
    posts = []
    tag = Tag.query.get_or_404(id)
    for p in tag.subscribers:
        posts.append(p)

    return render_template("blog/index.html", posts=posts)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        design_content_input = request.form['design_input']
        tag_content = request.form['tag_input']
        design_info = request.form['design_info']
        new_design = Design(design_name=design_content_input,
                            design_content=design_info)
        if tag_content != "":
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
            return redirect(url_for('blog.index'))
        except:
            return "There was a problem adding new designs"
    else:
        return render_template("blog/create.html")
