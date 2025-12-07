
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const hamburgerIcon = document.querySelector('.hamburger-icon');

    // Mobile menu toggle
    mobileMenuButton?.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
        hamburgerIcon?.classList.toggle('open');
    });

    // Close mobile menu when a nav link is clicked
    mobileMenu?.addEventListener('click', (event) => {
        if (event.target.tagName === 'A') {
            mobileMenu.classList.add('hidden');
            hamburgerIcon?.classList.remove('open');
        }
    });
});



   