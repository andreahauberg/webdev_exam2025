let originalItemsHTML = "";
let originalItemHTML = "";
const currentMarkers = [];
const originalMarkers = [];

// ###############################################
const search_results = document.querySelector("#search_results");
const input_search = document.querySelector("#input_search");
let my_timer = null;
let previous_input_length = 0;

window.addEventListener("DOMContentLoaded", () => {
  const itemsContainer = document.querySelector("#items");
  const itemContainer = document.querySelector("#item");

  originalItemsHTML = itemsContainer.innerHTML;
  originalItemHTML = itemContainer.innerHTML;

  // Gem originale markører (kopiér dem fra currentMarkers)
  originalMarkers.push(...currentMarkers);
});

// ###############################################
function search() {
  clearTimeout(my_timer);
  const current_value = input_search.value;

  if (current_value !== "") {
    my_timer = setTimeout(async function () {
      try {
        const conn = await fetch(
          `/search?q=${encodeURIComponent(current_value)}`
        );
        const data = await conn.json();

        if (data.error) {
          search_results.innerHTML = `<div class="search-message error">${data.error}</div>`;
          search_results.classList.remove("hidden");
        } else {
          search_results.innerHTML = "";
          data.results.forEach((item) => {
            const resultHTML = `
              <div class="instant-item">
                <img src="/static/uploads/${item.item_image}">
                <div class="search-name" mix-get="/items/${item.item_pk}">${item.item_name}</div>
              </div>`;
            search_results.insertAdjacentHTML("beforeend", resultHTML);
            
          });
          search_results.classList.remove("hidden");

          document.querySelector("#items").innerHTML = data.html_items;

          add_markers_to_map(data.results);
          document.querySelector("#button_more_items")?.classList.add("hidden");

          mix_convert();
        }
      } catch (err) {
        console.error("Search failed:", err);
      }
    }, 500);
  } else {
    search_results.innerHTML = "";
    search_results.classList.add("hidden");

    document.querySelector("#items").innerHTML = originalItemsHTML;
    document.querySelector("#item").innerHTML = originalItemHTML;

    currentMarkers.forEach((m) => map.removeLayer(m));
    currentMarkers.length = 0;

    originalMarkers.forEach((marker) => {
      marker.addTo(map);
      currentMarkers.push(marker);
    });
    document.querySelector("#button_more_items")?.classList.remove("hidden");

    mix_convert();
  }

  previous_input_length = current_value.length;
}

// ###############################################
window.add_markers_to_map = function (data) {
  try {
    if (typeof data === "string") {
      data = JSON.parse(data);
    }

    currentMarkers.forEach((marker) => map.removeLayer(marker));
    currentMarkers.length = 0;

    data.forEach((item) => {
      var customIcon = L.divIcon({
        className: "custom-marker",
        html: `<div class="custom-marker">
                 <img mix-get="/items/${item.item_pk}" src="/static/icons/${item.item_icon}" />
               </div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
      });

      const marker = L.marker([item.item_lat, item.item_lon], {
        icon: customIcon,
      })
        .addTo(map)
        .bindPopup(item.item_name);

      currentMarkers.push(marker);
    });

    mix_convert();
  } catch (err) {
    console.error("Failed to add markers:", err, data);
  }
};



search_results.addEventListener("click", function (event) {

  if (event.target.closest("[mix-get]")) {
    search_results.innerHTML = "";
    search_results.classList.add("hidden");
  }
});

document.addEventListener("click", function (event) {
  const clickedInsideInput = input_search.contains(event.target);
  const clickedInsideResults = search_results.contains(event.target);

  if (!clickedInsideInput && !clickedInsideResults) {
    search_results.innerHTML = "";
    search_results.classList.add("hidden");
  }
});


