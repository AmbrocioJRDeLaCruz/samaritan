const token = localStorage.getItem("token")

if (!token){
  window.location.href = "login.html";
}

async function loadUser(){
  const response = await fetch("http://localhost:3000/auth/me", {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  if (!response.ok){
    localStorage.removeItem("token");
    window.location.href = "login.html";
    return;
  }

  const user = await response.json();

  document.querySelector("#welcome").textContent = `Welcome, ${user.name}`;
}

document.querySelector("#logout").addEventListener("click", () => {
  localStorage.removeItem("token");
  window.location.href = "login.html";
});

loadUser();