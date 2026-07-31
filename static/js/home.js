// =============================
// Animated Counter
// =============================

const counters = document.querySelectorAll(".counter");

counters.forEach(counter => {

    counter.innerText = "0";

    const updateCounter = () => {

        const target = +counter.getAttribute("data-target");

        const current = +counter.innerText;

        const increment = target / 100;

        if (current < target) {

            counter.innerText = `${Math.ceil(current + increment)}`;

            setTimeout(updateCounter, 20);

        } else {

            counter.innerText = target.toLocaleString();

        }

    };

    updateCounter();

});

// =========================
// LIVE AI SHOWCASE
// =========================

const recipes = [
    {
        ingredient: "Chicken",
        title: "Garlic Chicken Bowl",
        time: "Ready in 25 Minutes"
    },
    {
        ingredient: "Pasta",
        title: "Creamy Garlic Pasta",
        time: "Ready in 20 Minutes"
    },
    {
        ingredient: "Rice",
        title: "Healthy Fried Rice",
        time: "Ready in 18 Minutes"
    },
    {
        ingredient: "Eggs",
        title: "Cheese Omelette",
        time: "Ready in 10 Minutes"
    }
];

// Get elements safely
const ingredientAnimation = document.getElementById("ingredientAnimation");
const recipeTitle = document.getElementById("recipeTitle");
const recipeTime = document.getElementById("recipeTime");

// Only run this animation if the elements exist
if (ingredientAnimation && recipeTitle && recipeTime) {

    let current = 0;

    setInterval(() => {

        current++;

        if (current >= recipes.length) {
            current = 0;
        }

        ingredientAnimation.textContent = recipes[current].ingredient;
        recipeTitle.textContent = recipes[current].title;
        recipeTime.textContent = recipes[current].time;

    }, 3000);

}