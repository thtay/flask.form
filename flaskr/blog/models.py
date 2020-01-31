from flaskr import db
from datetime import datetime


subs = db.Table('subs',
    db.Column('design_id', db.Integer, db.ForeignKey('design.design_id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id'))
)


class Design (db.Model):
    design_id = db.Column(db.Integer, primary_key=True)
    design_name = db.Column(db.String(40))
    design_content = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
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
