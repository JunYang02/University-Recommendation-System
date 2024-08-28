// home navigation
const hamburgerIcon = document.querySelector('.hamburger-icon');
const navbarMenu = document.querySelector('.menu-bar');

hamburgerIcon.addEventListener('click', () => {
  navbarMenu.classList.toggle('active');
});

const navLinks = document.querySelectorAll('.menu-bar a');

navLinks.forEach(link => {
  link.addEventListener('click', () => {
    // Close the navbar
    navbarMenu.classList.remove('active');

    // Optionally, you can also scroll to the target section
    const targetId = link.getAttribute('href');
    const targetSection = document.querySelector(targetId);
    if (targetSection) {
      targetSection.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

const myCarouselElement = document.querySelector('#myCarousel')
const carousel = new bootstrap.Carousel(myCarouselElement, {
  interval: 2000, // Adjust the interval (in milliseconds) to control the automatic sliding speed
  pause: 'hover' // Pause the carousel when hovering over it
});
