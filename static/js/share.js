document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[name^="is_shared_"]').forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked) {
        const id = cb.name.split('_')[2];
        const sel = document.querySelector(`select[name="share_with_${id}[]"]`);
        if (sel && sel.selectedOptions.length === 0) {
          alert('You marked this document public but have not picked any users.');
        }
      }
    });
  });
});
