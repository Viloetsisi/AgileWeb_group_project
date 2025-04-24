// main.js
document.addEventListener('DOMContentLoaded', () => {
  // Enable Bootstrap tooltips
  const tooltipTriggerList = Array.from(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

  // Auto-collapse mobile nav on link click
  const nav = document.getElementById('navMenu');
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      if (nav.classList.contains('show')) {
        new bootstrap.Collapse(nav).hide();
      }
    });
  });
});
