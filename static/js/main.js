const galeria = document.getElementById("galeria");
const modal = document.getElementById("modal");
const modalImg = document.getElementById("modal-img");
const cerrar = document.querySelector(".cerrar");

let indice = 0;
const porCarga = 18;

function cargarImagenes() {
  for (let i = 0; i < porCarga; i++) {
    if (indice >= IMAGENES.length) return;

    const nombreImagen = IMAGENES[indice]; 

    const card = document.createElement("div");
    card.className = "card";

    const img = document.createElement("img");
    img.src = `/static/uploads/${nombreImagen}`;
    img.loading = "lazy";

    img.addEventListener("click", () => {

      document
        .querySelectorAll("#galeria img.active")
        .forEach(i => i.classList.remove("active"));

      img.classList.add("active");

      modalImg.src = img.src;
      modal.classList.add("mostrar");

      fetch("/imagen-abierta", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          imagen: nombreImagen
        })
      }).catch(() => {});
    });

    card.appendChild(img);
    galeria.appendChild(card);
    indice++;
  }
}

cerrar.addEventListener("click", () => {
  modal.classList.remove("mostrar");
});

modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.classList.remove("mostrar");
  }
});

window.addEventListener("scroll", () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 150) {
    cargarImagenes();
  }
});

document.getElementById("enviar").addEventListener("click", () => {
  window.location.href = "/add_photo";
});


cargarImagenes();
