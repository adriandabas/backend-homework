document.addEventListener(
  "DOMContentLoaded",
  // once the page is loaded
  () => {
    console.log("DOMContentLoaded")

    // Connexion du client à SocketIo
    const socket = io();
    // Réception de l'évènement côté client
    socket.on('note-updated', function(data) {
        console.log('Note updated event received:', data);
        const checkbox = document.querySelector(`input[data-id="${data.id}"]`);
        if (checkbox) {
            checkbox.checked = data.done;
        }
    })

    document.querySelectorAll(".note>form>input")
      // on every input element inside the form inside the note class
      .forEach((element) => {
        // how to react on its change event
        element.addEventListener("change", (event) => {
          const done = element.checked
          const id = element.dataset.id
          // ask the API to update the note
          fetch(`/api/notes/${id}/done`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ done }),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.ok) {
                console.log("ok")
              } else {
                console.log(data.status, data)
              }
            })
        })
      })
  },
)

