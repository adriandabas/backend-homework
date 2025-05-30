# Trick that can help you populate your DB with some notes
# Start by running 'source aliases.sh'
# Now you shell knows about the functions defined in the file
# So you can run the commandes 'create-notes' and 'list-notes'

function list-notes() {
    http :5001/api/notes
}

function create-notes() {
    http :5001/api/notes title="courses" content="acheter du lait" done=True
    http :5001/api/notes title="devoirs" content="lire le cours de MMC" done=0
    http :5001/api/notes title="dentiste" content="mercredi 14h"
}
