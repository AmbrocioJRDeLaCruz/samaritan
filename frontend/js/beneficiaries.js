const token = localStorage.getItem("token");

if(!token) {
  window.location.href = "login.html";
}

async function loadBeneficiaries() {
  const response = await fetch("http://127.0.0.1:8000/beneficiaries/", {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  if (response.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "login.html";
    return;
  }

  const beneficiaries = await response.json()

  const list = document.querySelector("#beneficiaries-list");

  list.innerHTML = "";

  beneficiaries.forEach((beneficiary) => {
    const div = document.createElement("div");

    div.innerHTML = `
      <h3>${beneficiary.name}</h3>
      <p>Phone: ${beneficiary.phone ?? "N/A"}</p>
      <p>Location: ${beneficiary.location ?? "N/A"}</p>
      <p>Household size: ${beneficiary.household_size ?? "N/A"}</p>
      <hr>
    `;

    list.appendChild(div);
  });
}

const form = document.querySelector("#beneficiary-form");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = document.querySelector("#name").value;
  const phone = document.querySelector("#phone").value;
  const location = document.querySelector("#location").value;
  const householdSize = document.querySelector("#household_size").value;

  const response = await fetch("http://127.0.0.1:8000/beneficiaries/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      name,
      phone: phone || null,
      location: location || null,
      household_size: householdSize
        ? Number(householdSize)
        : null
    })
  });

  const data = await response.json();

  if (response.ok) {
    document.querySelector("#message").textContent = "Beneficiary created successfully";

    form.reset();

    loadBeneficiaries();
  }else {
    document.querySelector("#message").textContent = data.detail ?? "Something went wrong";
  }
});

loadBeneficiaries();