async function loadProducts() {
    const res = await fetch("/products");
    const products = await res.json();

    const container = document.getElementById("products");
    container.innerHTML = "";

    products.forEach(p => {
        const div = document.createElement("div");

        div.innerHTML = `
            <h3>${p.name}</h3>
            <img src="${p.image}" width="150"/>
            <p>$${p.price}</p>

            <button onclick="add(${p.id})">+</button>
            <button onclick="decrease(${p.id})">-</button>

            <button onclick="showDetails('${p.name}', '${p.description}')">
                View
            </button>

            <hr>
        `;

        container.appendChild(div);
    });
}

function showDetails(name, desc) {
    alert(name + "\n\n" + desc);
}

// ➕ добавить
async function add(id) {
    await fetch(`/cart/add/${id}`, { method: "POST" });
    loadCart();
}

// ➖ уменьшить
async function decrease(id) {
    await fetch(`/cart/decrease/${id}`, { method: "POST" });
    loadCart();
}

// 🛒 загрузка корзины
async function loadCart() {
    const res = await fetch("/cart");
    const items = await res.json();

    const container = document.getElementById("cart");
    container.innerHTML = "";

    items.forEach(i => {
        const div = document.createElement("div");

        div.innerHTML = `
            ${i.name} | ${i.quantity} x $${i.price}
        `;

        container.appendChild(div);
    });
}

async function checkout() {
    const res = await fetch("/cart/checkout", {
        method: "POST"
    });

    const data = await res.json();

    if (res.ok) {
        alert(
            `Success!
Discount: ${data.discount * 100}%
Balance: ${data.balance}`
        );
        loadCart();
    } else {
        alert(data.detail);
    }
}

loadProducts();
loadCart();