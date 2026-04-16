async function loadProfile() {
    const res = await fetch("/profile/data");
    const data = await res.json();

    document.getElementById("username").innerText = data.username;
    document.getElementById("full_name").value = data.full_name;
    document.getElementById("birth_date").value = data.birth_date;

    document.getElementById("balance").innerText = data.balance.toFixed(2);
    document.getElementById("spent").innerText = data.total_spent.toFixed(2);
    document.getElementById("discount").innerText = (data.discount * 100);
}

async function saveProfile() {
    const name = document.getElementById("full_name").value;
    const date = document.getElementById("birth_date").value;

    await fetch(`/profile/update?full_name=${name}&birth_date=${date}`, {
        method: "POST"
    });

    alert("Saved");
}

async function addBalance() {
    const amount = document.getElementById("amount").value;

    await fetch(`/balance/add?amount=${amount}`, {
        method: "POST"
    });

    loadProfile();
}

loadProfile();