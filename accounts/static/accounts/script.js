const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
// Switch to register form
registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});
// Switch to login form
loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});
// Close messages after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const closeButtons = document.querySelectorAll('.close-message');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            button.closest('.messages-container > div').remove();
        });
    });

    setTimeout(() => {
        const messagesContainer = document.querySelector('.messages-container');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
    }, 5000);
});