// profile.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form[action$="profile"]');
  form.addEventListener('submit', (e) => {
    const pwd = form.password.value;
    if (pwd && pwd.length < 6) {
      e.preventDefault();
      alert('Password must be at least 6 characters long.');
    }
  });
});
