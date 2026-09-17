const form = document.querySelector("#register-form");

if (form){
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.querySelector("#name").value;
    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;

    const response = await fetch("http://127.0.0.1:8000/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name,
        email,
        password
      })
    });

    const data = await response.json();

    if (response.ok){
      document.querySelector("#message").textContent = "Account created successfully"
    } else {
      document.querySelector("#message").textContent = data.detail;
    }

  });
}

const loginForm = document.querySelector("#login-form")

if (loginForm){
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.querySelector("#email").value;
    const password = document.querySelector("#password").value;

    const response = await fetch("http://127.0.0.1:8000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email,
        password
      })
    });

    const data = await response.json();

    if (response.ok){
      localStorage.setItem("token", data.access_token);

      window.location.href = "dashboard.html";
    } else {
      document.querySelector("#message").textContent = data.detail
    }

  });
}