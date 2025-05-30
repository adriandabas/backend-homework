import json
import requests
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

##### Usual flask initialization #####
app = Flask(__name__)


##### Database declaration #####
db_name = 'notes.db'   # filename where to store stuff (sqlite is file-based)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name      # how do we connect to the database ? here we say it's by looking in a file named notes.db
db = SQLAlchemy(app)    # this variable, db, will be used for all SQLAlchemy commands

# Define a table in the database
class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)    # les colonnes de notre table
    title = db.Column(db.String)
    content = db.Column(db.String)
    done = db.Column(db.Boolean, default=False)

with app.app_context():     # actually create the database (i.e. tables)
    db.create_all()


##### Creating new endpoints #####
@app.route('/')
def hello_world():
    # redirect to /front/notes
    return redirect('/front/notes')

"""
http :5001/api/notes title="courses" content="acheter du lait" done=True
http :5001/api/notes title="devoirs" content="lire le cours de MMC" done=0
http :5001/api/notes title="dentiste" content="mercredi 14h"
"""    
@app.route('/api/notes', methods=['POST'])  # création des lignes de notre table
def create_note():
    # we expect the user to send a json object with the 3 fields (title, content, done)
    try:
        parameters = json.loads(request.data)
        title = parameters['title']
        content = parameters['content']
        done = parameters.get('done', None)  # attention : renvoie une chaîne de caractère
        
        if done == None:
            new_note = Note(title=title, content=content)   # création d'un objet de type Notes, done=False par défaut
        else :
            # j'ai des problèmes de conversion 
            # on prend l'objet donné par l'utilisateur, on le convertit en string, on le met en minuscules 
            # et on renvoie True si il appartient à la liste
            to_bool = lambda x: str(x).lower() in ['true', '1']
            new_note = Note(title=title, content=content, done=to_bool(done))  
        
        print("Note created successfully")
        db.session.add(new_note)
        db.session.commit() # comme sur git
        return parameters
    except Exception as exc:
        return dict(error=f"{type(exc)}: {exc}"), 422
    
"""
http :5001/api/notes
"""
@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return [dict(id=note.id, title=note.title, content=note.content, done=note.done) for note in notes]

"""
http :5001/api/notes/<id>/done
"""
@app.route('/api/notes/<id>/done', methods=['POST'])
def new_status(id):
    try: 
        note = Note.query.get(id)   # on récupère la note par son id
        
        data = request.get_json()   
        new_status = data.get('done')   # on récupère le nouveau statut
        
        note.done = bool(new_status)    # on met à jour l'état de la note
        db.session.commit()             # comme sur git !
        return data
    except Exception as exc:    # on utilise try et except pour ne pas faire crasher l'api si une des commandes au-dessus n'est pas réalisable (id n'existe pas, etc)
        return dict(error=f"{type(exc)}: {exc}"), 422  

# Frontend
"""
http://localhost:5001/front/notes
"""
@app.route('/front/notes')
def front_notes():
    # this endpoint will call the 'api/notes' endpoint
    # which will retrieve all notes from the DB
    # and pass that list to the new Jinja2 template
    # that will create one custom HTML element per note
    # and return the full HTML page to the browser
    url = request.url_root + '/api/notes'
    req = requests.get(url) #
    if not (200 <= req.status_code < 300):
        return dict(error=f"could not request notes list", url=url,
                    status=req.status_code, text=req.text)
    notes = req.json()
    return render_template('notes.html.j2', notes=notes)  # permet d'accéder à la variable notes dans le template/html