from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests, os


db = SQLAlchemy()


class Store(db.Model):
    store_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    store_name = db.Column(db.String(18), nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    hashpassword = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<First_name %r, Last_name %r, Store_name %r, email %r>' % (self.first_name,
                                                                           self.last_name,
                                                                           self.store_name,
                                                                           self.email)


class Collector(db.Model):
    collector_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    username = db.Column(db.String(18), nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    hashpassword = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<First_name %r, Last_name %r, Username %r, email %r>' % (self.first_name,
                                                                         self.last_name,
                                                                         self.username,
                                                                         self.email)


class Collections(db.Model):
    collection_id = db.Column(db.Integer, primary_key=True)
    collector_id = db.Column(db.Integer, db.ForeignKey('collector.collector_id'), nullable=False)
    collection_name = db.Column(db.String(40))

    def __repr__(self):
        return '<Collection_name %r>' % self.collection_name


class Inventories(db.Model):
    inventory_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)
    inventory_name = db.Column(db.String(40))

    def __repr__(self):
        return '<Inventory_name %r>' % self.inventory_name


class Card(db.Model):
    card_id = db.Column(db.Integer, primary_key=True)
    card_name = db.Column(db.String(300))
    nonfoil_price = db.Column(db.Float)
    foil_price = db.Column(db.Float)
    etched_price = db.Column(db.Float)
    set_name = db.Column(db.String(120))
    set_code = db.Column(db.String(10))
    finishes = db.Column(db.ARRAY(db.String(100)))
    

    def __repr__(self):
        return '<Card_name %r, Nonfoil_price %r, Foil_price %r, Etched_price %r, Set_name %r, Set_code %r, Finishes %r>' % (self.card_name, 
                                                                                                                            self.nonfoil_price, 
                                                                                                                            self.foil_price, 
                                                                                                                            self.etched_price, 
                                                                                                                            self.set_name,
                                                                                                                            self.set_code,
                                                                                                                            self.finishes)


class Inventory_row(db.Model):
    item = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.inventory_id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.card_id'), nullable=False)
    quantity = db.Column(db.Integer)
    finish = db.Column(db.String(10))

    def __repr__(self):
        return '<Quantity %r>' % self.quantity


class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)
    item = db.Column(db.Integer, db.ForeignKey('inventory_row.item'), nullable=False)
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return '<Quantity %r>' % self.quantity


class Collection_row(db.Model):
    item = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.collection_id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.card_id'), nullable=False)
    quantity = db.Column(db.Integer)
    finish = db.Column(db.String(10))

    def __repr__(self):
        return '<Quantity %r>' % self.quantity


def carddata():
    response = requests.get("https://api.scryfall.com/bulk-data")
    file_response = response.json()['data']
    data = file_response[2]['download_uri']
    cards = requests.get(data)
    card_data = cards.json()

    for x in card_data:
        label = Card(card_name=x['name'], nonfoil_price=x['prices']['usd'], foil_price=x['prices']['usd_foil'], etched_price=x['prices']['usd_etched'], set_name=x['set_name'], set_code=x['set'], finishes=x['finishes'])
        db.session.add(label)
        db.session.commit()



def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('sqlalchemy_database_uri')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('sqlalchemy_database_uri')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)
    print("Connected to DB.")