// Add ingredients to shopping list

function addToShoppingList() {

    const ingredients = [
        "Flour",
        "Tomato Sauce",
        "Mozzarella Cheese",
        "Oregano",
        "Olive Oil",
        "Fresh Basil"
    ];

    let shopping = JSON.parse(localStorage.getItem("shopping")) || [];

    ingredients.forEach(item => {

        if (!shopping.includes(item)) {

            shopping.push(item);

        }

    });

    localStorage.setItem("shopping", JSON.stringify(shopping));

    alert("Ingredients added to Shopping List 🛒");

}

function clearShopping(){

    localStorage.removeItem("shopping");

    location.reload();

}