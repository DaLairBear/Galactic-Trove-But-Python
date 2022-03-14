import jinja2, hashlib, os, json
from flask import Flask, render_template, request, flash, redirect, session, jsonify, url_for
from database_set_up import connect_to_db, db, Store, Collector, Collections, Inventories, Card, Inventory_row, Cart, Collection_row
from itertools import chain


app = Flask(__name__)
app.secret_key = os.getenv('api_secret_key')
app.jinja_env.undefinded = jinja2.StrictUndefined
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True

# Landing
@app.route("/")
def home():
    """Homepage."""

    return render_template("home.html")

@app.route("/home")
def homealt():
    """Homepage."""

    return render_template("home.html")

# Register Methods for if a Collector or Store
@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_collector_process():
    """Process collector registration."""
    if request.method =='POST':
        option = request.form['register']
        if option == "collector":
            return redirect('/register_collector')
        elif option == "store":
            return redirect('/register_store')
        else:
            return render_template("register.html")
    

# Collector Registration Methods
@app.route('/register_collector', methods=['GET'])
def collector_register_form():
    """Show form for collector signup."""

    return render_template("register_collector.html")

@app.route('/register_collector', methods=['POST'])
def collector_register_process():
    """Process registration."""

    # Get form variables
    first_name = request.form["First Name"]
    last_name = request.form["Last Name"]
    username = request.form["Username"]
    email = request.form["Email"]
    password = request.form["Password"]
    hashpassword = hashlib.sha224(str(password).encode('utf-8')).hexdigest()


    new_collector = Collector(first_name=first_name, last_name=last_name, username=username, email=email, hashpassword=hashpassword)
    db.session.add(new_collector)
    db.session.commit()

    new_collection = Collections(collector_id=new_collector.collector_id, collection_name="Click Here To Name Your Collection")
    db.session.add(new_collection)
    db.session.commit()

    flash(f"Welcome {username} to Galactic Trove.")
    return redirect(f"/collector/{new_collector.collector_id}")



# Store Registration Methods   
@app.route('/register_store', methods=['GET'])
def store_register_form():
    """Show form for user signup."""

    return render_template("register_store.html")

@app.route('/register_store', methods=['POST'])
def store_register_process():
    """Process registration."""

    # Get form variables
    first_name = request.form["First Name"]
    last_name = request.form["Last Name"]
    store_name = request.form["Store Name"]
    email = request.form["Email"]
    password = request.form["Password"]
    hashpassword = hashlib.sha224(str(password).encode('utf-8')).hexdigest()


    new_store = Store(first_name=first_name, last_name=last_name, store_name=store_name, email=email, hashpassword=hashpassword)
    db.session.add(new_store)
    db.session.commit()

    new_inventory = Inventories(store_id=new_store.store_id, inventory_name="Click Here To Name Your Inventory")
    db.session.add(new_inventory)
    db.session.commit()

    flash(f"Welcome {store_name} to Galactic Trove.")
    return redirect(f"/store/{new_store.store_id}")



# Login Methods
@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_form_submit():
    """Login form submit."""

    email = request.form["Email"]
    password = request.form["Password"]
    hashpassword = hashlib.sha224(str(password).encode('utf-8')).hexdigest()

    print(email)
    print(password)
    if request.method =='POST':
        option = request.form['login']

        if option == "collector":
            collector = Collector.query.filter_by(email=email).first()

            if hashpassword != collector.hashpassword:
                flash("Incorrect Password!")
                return redirect("/login")
            session["collector_id"] = collector.collector_id

            flash("Logging In!")
            return redirect(f"/collector/{collector.collector_id}")

        elif option == "store":
            store = Store.query.filter_by(email=email).first()
            if not store:
                flash("No Store account with that email found!")
                return redirect("/login")

            if hashpassword != store.hashpassword:
                flash("Incorrect Password!")
                return redirect("/login")

            session["store_id"] = store.store_id
            print("Logging in Store")
            return redirect(f"/store/{store.store_id}")  

        else:
            return render_template("login.html")



# Logged In Collector and Store Homes
@app.route("/collector/<int:collector_id>", methods=["GET"])
def collector(collector_id):
    """Collector homepage."""

    collector_id = session.get("collector_id")
    return render_template("collector.html", collector_id=collector_id)

@app.route("/store/<int:store_id>", methods=["GET"])
def store(store_id):
    """Store homepage."""

    store_id = session.get("store_id")
    return render_template("store.html", store_id=store_id)



# Logout Collector and Store
@app.route("/collectorlogout", methods=["GET"])
def collectorlogout():
    """Collectors way to logout."""

    del session["collector_id"]
    flash("Logged Out.")
    return redirect("/")

@app.route("/storelogout", methods=["GET"])
def storelogout():
    """Stores way to logout."""

    del session["store_id"]
    flash("Logged Out.")
    return redirect("/")



# Collector Features
@app.route("/collection/<int:collector_id>", methods=["GET"])
def collections(collector_id):
    """Gets collectors collections."""

    collector_id = session.get("collector_id")
    
    results = []
    cards_list =[]
    for card_names in Card.query.with_entities(Card.card_name).order_by('card_name').distinct():
        results.append(card_names)
    for value, in results:
        cards_list.append(value)
    
    collection_ids = []
    collections_in_db = Collections.query.filter_by(collector_id=collector_id).order_by('collection_id').all()


    test = Collections.query.with_entities(Collections.collection_id).filter_by(collector_id=collector_id).all()
    for collection in test:
        for value in collection:
            collection_ids.append(value)


    collection_rows = []
    for ids in collection_ids:
        row = Collection_row.query.with_entities(Collection_row.card_id, Collection_row.quantity, Collection_row.finish).filter_by(collection_id=ids).order_by('item').all()
        if row == []:
            return render_template("collection.html", collector_id=collector_id, collections_in_db=collections_in_db, cards_list=cards_list)
        else:
            collection_rows.append(row)


    card_collection = []
    for collection in collection_rows:
        d = []
        for card in collection:
            card_id = card[0]
            finish = card[2]

            if finish == 'nonfoil':
                cardget = Card.query.with_entities(Card.card_name, Card.set_name, Card.nonfoil_price).filter_by(card_id=card_id).all()
                c = dict(card)
                for a in cardget:
                    b = dict(a)
                    c.update(b)
                    d.append(c)
            elif finish == 'foil':
                cardget = Card.query.with_entities(Card.card_name, Card.set_name, Card.foil_price).filter_by(card_id=card_id).all()
                c = dict(card)
                for a in cardget:
                    b = dict(a)
                    c.update(b)
                    d.append(c)
            elif finish == 'etched':
                cardget = Card.query.with_entities(Card.card_name, Card.set_name, Card.etched_price).filter_by(card_id=card_id).all()
                c = dict(card)
                for a in cardget:
                    b = dict(a)
                    c.update(b)
                    d.append(c)
        card_collection.append(d)
    return render_template("collection.html", collector_id=collector_id, collections_in_db=collections_in_db, cards_list=cards_list, card_collection=card_collection)


@app.route("/updatecollectionname", methods=["POST"])
def updatecollectionname():
    """Updates collection Name """
    name = request.get_json()
    results = json.loads(name)

    collector_id = session.get("collector_id")
    collection_id = results["collection_id"]
    collection_name = results["collectionname"].lstrip()

    collection_to_update = collections.query.filter_by(collection_id=collection_id).first()
    collection_to_update.collection_name = collection_name

    db.session.commit()

    return redirect(f"/collection/{collector_id}")

@app.route("/collection_get_set_autocomplete_list/<card_name>", methods=["GET", "POST"])
def collection_get_set_autocomplete_list(card_name):
    """"Gets Sets based off card entered."""

    card_name_stringed = card_name.replace('%20', ' ')

    results = []
    sets_list =[]
    for set_names in Card.query.with_entities(Card.set_name).filter_by(card_name=card_name_stringed).order_by('set_name'):
        results.append(set_names)
    for value, in results:
        sets_list.append(value)

    return json.dumps(sets_list)

@app.route("/collection_get_finishes_autocomplete_list/<card_name>&<set_name>", methods=["GET", "POST"])
def collection_get_finishes_list(card_name, set_name):
    """Gets Finishes based off card and set entered."""
    card_name_stringed = card_name.replace('%20', ' ')
    set_name_stringed = set_name.replace('%20', ' ')

    results = Card.query.with_entities(Card.finishes).filter_by(card_name=card_name_stringed, set_name=set_name_stringed).first()
    finishes_list = []
    for value in results:
        for element in value:
            finishes_list.append(element)

    return json.dumps(finishes_list)


@app.route("/collection_addnewcard", methods=["POST"])
def collection_add_new_card():
    """collections add card"""
    card = request.get_json()
    results = json.loads(card)
    
    collector_id = session.get("collector_id")
    collection_id = results["collection_id"]
    card_name = results["card_name"]
    set_name = results["set_name"]
    quantity = results["quantity"]
    finish = results["finish"]


    card_id = Card.query.with_entities(Card.card_id).filter_by(card_name=card_name, set_name=set_name)
    new_collection_row = Collection_row(collection_id=collection_id, card_id=card_id, quantity=quantity, finish=finish)
    db.session.add(new_collection_row)
    db.session.commit()

    return redirect(url_for('collector',collector_id=collector_id))

@app.route("/collection_deletecard", methods=["POST"])
def collection_delete_card():
    """Delete card from collection"""
    collector_id = session.get("collector_id")
    card = request.get_json()
    results = json.loads(card)

    collection_id = results["collection_id"]
    card_id = results["card_id"]
    Collection_row.query.filter_by(collection_id=collection_id, card_id=card_id).delete()
    db.session.commit()

    return redirect(url_for('collector',collector_id=collector_id))



# Store Features
# Inventory
@app.route("/inventory/<int:store_id>", methods=["GET"])
def inventories(store_id):
    """Gets Stores Inventories."""

    store_id = session.get("store_id")
    
    results = []
    cards_list =[]
    for card_names in Card.query.with_entities(Card.card_name).order_by('card_name').distinct():
        results.append(card_names)
    for value, in results:
        cards_list.append(value)
    
    inventory_ids = []
    inventories_in_db = Inventories.query.filter_by(store_id=store_id).order_by('inventory_id').all()


    test = Inventories.query.with_entities(Inventories.inventory_id).filter_by(store_id=store_id).all()
    for inventory in test:
        for value in inventory:
            inventory_ids.append(value)


    inventory_rows = []
    for ids in inventory_ids:
        row = Inventory_row.query.with_entities(Inventory_row.card_id, Inventory_row.quantity, Inventory_row.finish).filter_by(inventory_id=ids).order_by('item').all()
        if row == []:
            return render_template("inventory.html", store_id=store_id, inventories_in_db=inventories_in_db, cards_list=cards_list)
        else:
            inventory_rows.append(row)


    card_inventory = []
    for inventory in inventory_rows:
        d = []
        for card in inventory:
            card_id = card[0]
            finish = card[2]

            if finish == 'nonfoil':
                cardget = Card.query.with_entities(Card.card_name, Card.set_name, Card.nonfoil_price).filter_by(card_id=card_id).all()
                c = dict(card)
                for a in cardget:
                    b = dict(a)
                    c.update(b)
                    d.append(c)
            elif finish == 'foil':
                cardget = Card.query.with_entities(Card.card_name, Card.set_name, Card.foil_price).filter_by(card_id=card_id).all()
                c = dict(card)
                for a in cardget:
                    b = dict(a)
                    c.update(b)
                    d.append(c)
            elif finish == 'etched':
                cardget = Card.query.with_entities(Card.card_name, Card.set_name, Card.etched_price).filter_by(card_id=card_id).all()
                c = dict(card)
                for a in cardget:
                    b = dict(a)
                    c.update(b)
                    d.append(c)
        card_inventory.append(d)
    print(card_inventory)
    return render_template("inventory.html", store_id=store_id, inventories_in_db=inventories_in_db, cards_list=cards_list, card_inventory=card_inventory)


@app.route("/updateinventoryname", methods=["POST"])
def updateinventoryname():
    """Updates Inventory Name """
    name = request.get_json()
    results = json.loads(name)

    store_id = session.get("store_id")
    inventory_id = results["inventory_id"]
    inventory_name = results["inventoryname"].lstrip()

    inventory_to_update = Inventories.query.filter_by(inventory_id=inventory_id).first()
    inventory_to_update.inventory_name = inventory_name

    db.session.commit()

    return redirect(f"/inventory/{store_id}")

@app.route("/inventory_get_set_autocomplete_list/<card_name>", methods=["GET", "POST"])
def inventory_get_set_autocomplete_list(card_name):
    """"Gets Sets based off card entered."""

    card_name_stringed = card_name.replace('%20', ' ')

    results = []
    sets_list =[]
    for set_names in Card.query.with_entities(Card.set_name).filter_by(card_name=card_name_stringed).order_by('set_name'):
        results.append(set_names)
    for value, in results:
        sets_list.append(value)

    return json.dumps(sets_list)

@app.route("/inventory_get_finishes_autocomplete_list/<card_name>&<set_name>", methods=["GET", "POST"])
def inventory_get_finishes_list(card_name, set_name):
    """Gets Finishes based off card and set entered."""
    card_name_stringed = card_name.replace('%20', ' ')
    set_name_stringed = set_name.replace('%20', ' ')

    results = Card.query.with_entities(Card.finishes).filter_by(card_name=card_name_stringed, set_name=set_name_stringed).first()
    finishes_list = []
    for value in results:
        for element in value:
            finishes_list.append(element)

    return json.dumps(finishes_list)


@app.route("/inventory_addnewcard", methods=["POST"])
def inventory_add_new_card():
    """Inventories add card"""
    card = request.get_json()
    results = json.loads(card)
    
    store_id = session.get("store_id")
    inventory_id = results["inventory_id"]
    card_name = results["card_name"]
    set_name = results["set_name"]
    quantity = results["quantity"]
    finish = results["finish"]


    card_id = Card.query.with_entities(Card.card_id).filter_by(card_name=card_name, set_name=set_name)
    new_inventory_row = Inventory_row(inventory_id=inventory_id, card_id=card_id, quantity=quantity, finish=finish)
    db.session.add(new_inventory_row)
    db.session.commit()

    return redirect(url_for('store',store_id=store_id))

@app.route("/inventory_deletecard", methods=["POST"])
def inventory_delete_card():
    """Delete card from Inventory"""
    store_id = session.get("store_id")
    card = request.get_json()
    results = json.loads(card)

    inventory_id = results["inventory_id"]
    card_id = results["card_id"]
    Inventory_row.query.filter_by(inventory_id=inventory_id, card_id=card_id).delete()
    db.session.commit()

    return redirect(url_for('store',store_id=store_id))



if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    app.run(host="0.0.0.0")