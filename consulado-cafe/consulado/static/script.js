let menuIcon  = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');

// Cambia el boton del navbar para el responsive.
menuIcon.onclick = () => {
    menuIcon.classList.toggle('bx-x-circle')
    navbar.classList.toggle('active');
}

// Verifica si el enlace fue clickeado y activa la descarga
document.getElementById('downloadLink').addEventListener('click', function() {
    alert("El archivo PDF está siendo descargado.");
});
