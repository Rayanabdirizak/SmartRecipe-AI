const container = document.getElementById("historyContainer");
const search = document.getElementById("searchHistory");

let history =
JSON.parse(localStorage.getItem("recipeHistory")) || [];

function displayRecipes(list){

    container.innerHTML = "";

    if(list.length===0){

        container.innerHTML="<h2>No recipes found.</h2>";

        return;
    }

    list.slice().reverse().forEach((item,index)=>{

        container.innerHTML += `

        <div class="ai-card">

            <div class="ai-header">

                <h2>${item.title}</h2>

                <span class="ai-badge">

                    ${item.date}

                </span>

            </div>

            <div class="ai-body">

                <pre class="recipe-output">

${item.recipe}

                </pre>

            </div>

            <div class="ai-footer">

                <button
                class="recipe-btn delete-btn"
                onclick="deleteRecipe(${history.length-1-index})">

                🗑 Delete

                </button>

            </div>

        </div>

        `;

    });

}

displayRecipes(history);

search.addEventListener("keyup",()=>{

    const keyword =
    search.value.toLowerCase();

    const filtered =
    history.filter(item=>

        item.title.toLowerCase().includes(keyword) ||

        item.recipe.toLowerCase().includes(keyword)

    );

    displayRecipes(filtered);

});

function deleteRecipe(index){

    if(confirm("Delete this recipe?")){

        history.splice(index,1);

        localStorage.setItem(

            "recipeHistory",

            JSON.stringify(history)

        );

        displayRecipes(history);

    }

}