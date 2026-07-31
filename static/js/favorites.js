// Save Recipe

function addToFavorites(recipe){

    let favorites = JSON.parse(localStorage.getItem("favorites")) || [];

    if(!favorites.includes(recipe)){

        favorites.push(recipe);

        localStorage.setItem("favorites", JSON.stringify(favorites));

        alert(recipe + " added to favorites ❤️");

    }else{

        alert("Recipe already exists ❤️");

    }

}