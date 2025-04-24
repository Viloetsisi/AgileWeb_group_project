// upload.js
document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('data_file');
  const label = document.querySelector('label[for="data_file"]');
  fileInput.addEventListener('change', () => {
    const fileName = fileInput.files[0]?.name || 'Select a file';
    label.textContent = fileName;
  });
});
