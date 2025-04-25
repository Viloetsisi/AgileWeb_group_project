// auth.js

$(document).ready(function () {
  // handle Signup form submission
  $("#signup-form").submit(function (e) {
    e.preventDefault(); // stop default form submit action

    // get form values
    const username = $("#username").val();
    const email = $("#email").val();
    const password = $("#password").val();
    const confirm_password = $("#confirm_password").val();

    // simple frontend password confirmation check
    if (password !== confirm_password) {
      alert("Passwords do not match.");
      return;
    }

    const formData = { username, email, password };

    // AJAX call to backend
    $.ajax({
      url: "/signup",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(formData),

      success: function (response) {
        alert(response.message);
        window.location.href = "/login";
      },

      error: function (xhr) {
        const message =
          xhr.responseJSON.message || "An error occurred. Please try again.";
        alert(`Error: ${message}`);
      },
    });
  });
});
