async function generateRecipe() {

    const ingredients = document.getElementById("ingredients").value.trim();
    const result = document.getElementById("recipeResult");

    if (!ingredients) {
        alert("Please enter some ingredients.");
        return;
    }

   result.innerHTML = `
<div class="loading-card">

    <div class="loader"></div>

    <h2>🤖 Gemini AI is cooking...</h2>

    <p>Please wait a few seconds.</p>

</div>
`;

    const formData = new FormData();
    formData.append("ingredients", ingredients);

    try {

        const response = await fetch("/generate-recipe", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {

            result.innerHTML = `
                <div class="recipe-card">
                    <div class="recipe-content">
                        <h2>❌ AI Error</h2>
                        <p>${data.error}</p>
                    </div>
                </div>
            `;

            return;
        }

     result.innerHTML = `
<div class="ai-card">

    <div class="ai-header">

        <h2>🤖 AI Generated Recipe</h2>

        <span class="ai-badge">

            Powered by Gemini

        </span>

    </div>

    <div class="ai-body">

        <pre
        id="typingText"
        class="recipe-output"></pre>

    </div>

    <div class="ai-footer">

    <button class="recipe-btn" onclick="window.print()">
        🖨 Print Recipe
    </button>

    <button class="recipe-btn" onclick="saveAIRecipe()">
        ❤️ Save Recipe
    </button>

    <button class="recipe-btn" onclick="addAIShoppingList()">
        🛒 Shopping List
    </button>

    <button class="recipe-btn" onclick="downloadPDF()">
        📄 Download PDF
    </button>

    <button class="recipe-btn" onclick="analyzeNutrition()">
        📊 Analyze Nutrition
    </button>

</div>
</div>
`;

typeWriter(
    data.recipe,
    document.getElementById("typingText")
);

// ===============================
// Save Recipe History
// ===============================

let history =
JSON.parse(localStorage.getItem("recipeHistory")) || [];

history.push({

    title: ingredients,

    recipe: data.recipe,

    date: new Date().toLocaleString()

});

localStorage.setItem(

    "recipeHistory",

    JSON.stringify(history)

);


    } catch (err) {

        console.error(err);

        result.innerHTML = `
            <div class="recipe-card">
                <div class="recipe-content">
                    <h2>❌ Network Error</h2>
                    <p>${err.message}</p>
                </div>
            </div>
        `;
    }

}


// ===============================
// Save AI Recipe
// ===============================

function saveAIRecipe(){

    const recipe =
        document.querySelector(".recipe-output").innerText;

    let favorites =
        JSON.parse(localStorage.getItem("favorites")) || [];

    if(!favorites.includes(recipe)){

        favorites.push(recipe);

        localStorage.setItem(
            "favorites",
            JSON.stringify(favorites)
        );

        alert("❤️ AI Recipe saved!");

    }else{

        alert("Recipe already saved.");

    }

}


// =====================================
// AI Shopping List
// =====================================

function addAIShoppingList(){

    const recipe =
        document.querySelector(".recipe-output").innerText;

    const lines = recipe.split("\n");

    let shopping =
        JSON.parse(localStorage.getItem("shopping")) || [];

    let readingIngredients = false;

    lines.forEach(line=>{

        line = line.trim();

        if(line.includes("Ingredients")){

            readingIngredients = true;
            return;

        }

        if(line.includes("Instructions")){

            readingIngredients = false;

        }

        if(readingIngredients){

            if(line.length>2){

                shopping.push(line);

            }

        }

    });

    shopping = [...new Set(shopping)];

    localStorage.setItem(
        "shopping",
        JSON.stringify(shopping)
    );

    alert("🛒 Ingredients added!");
}



// =====================================
// AI Typing Animation
// =====================================

function typeWriter(text, element) {

    let i = 0;

    element.innerHTML = "";

    const timer = setInterval(() => {

        element.innerHTML += text.charAt(i);

        i++;

        element.scrollTop = element.scrollHeight;

        if (i >= text.length) {

            clearInterval(timer);

        }

    }, 15);

}

// ===============================
// Download Recipe PDF
// ===============================

async function downloadPDF(){

    const recipe =
        document.querySelector(".recipe-output").innerText;

    const formData = new FormData();

    formData.append("recipe", recipe);

    const response = await fetch("/download-pdf",{

        method:"POST",

        body:formData

    });

    const data = await response.json();

    window.open(data.url,"_blank");

}


// =======================================
// AI Nutrition Analysis
// =======================================

async function analyzeNutrition(){

    const recipe =
        document.querySelector(".recipe-output").innerText;

    const result =
        document.getElementById("recipeResult");

    const formData = new FormData();

    formData.append("recipe", recipe);

    result.innerHTML += `
        <div class="loading-card">

            <div class="loader"></div>

            <h2>📊 Analyzing Nutrition...</h2>

        </div>
    `;

    try{

        const response = await fetch("/analyze-nutrition",{

            method:"POST",

            body:formData

        });

        const data = await response.json();

        if(!response.ok){

            alert(data.error);

            return;

        }

        result.innerHTML += `

        <div class="ai-card">

            <div class="ai-header">

                <h2>🍎 Nutrition Analysis</h2>

            </div>

            <div class="ai-body">

                <pre class="recipe-output">

${data.nutrition}

                </pre>

            </div>

        </div>

        `;

    }

    catch(err){

        alert(err.message);

    }

}