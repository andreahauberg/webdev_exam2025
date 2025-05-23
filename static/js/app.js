
// ###############################################

// input search

const search_results = document.querySelector("#search_results");
const input_search = document.querySelector("#input_search");
let my_timer = null;

// setTimeout - runs only 1 time
// setInterval - runs forever in intervals
let previous_input_length = 0;

function search() {
  clearInterval(my_timer);
  const current_value = input_search.value;

  // Only search if input is not empty AND length increased (not decreased)
  if (current_value !== "" && current_value.length > previous_input_length) {
    my_timer = setTimeout(async function () {
      try {
        const search_for = current_value;
        const conn = await fetch(`/search?q=${search_for}`);
        const data = await conn.json();

        if (data.error) {
          search_results.innerHTML = `<div class="search-message error">${data.error}</div>`;
        } else {
          search_results.innerHTML = "";
          data.results.forEach((item) => {
            const a = `
             <div class="instant-item">
  <img src="/static/uploads/${item.item_image}">
  <div class="search-name" mix-get="/items/${item.item_pk}">${item.item_name}</div>
</div>

            `;
            search_results.insertAdjacentHTML("beforeend", a);
          });
          mix_convert();
          search_results.classList.remove("hidden");
        }
      } catch (err) {
        console.error(err);
      }
    }, 500);
  } else {
    search_results.innerHTML = "";
    search_results.classList.add("hidden");
  }

  previous_input_length = current_value.length;
}


addEventListener("click", function (event) {
  if (!search_results.contains(event.target)) {
    search_results.classList.add("hidden");
  }
  if (input_search.contains(event.target)) {
    search_results.classList.remove("hidden");
  }
});


// ###############################################

// Map
window.add_markers_to_map = function (data) {
  try {
    if (typeof data === "string") {
      data = JSON.parse(data);
    }

    console.log("Adding markers:", data);

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

      L.marker([item.item_lat, item.item_lon], { icon: customIcon })
        .addTo(map)
        .bindPopup(item.item_name);
    });

    // Re-run mix_convert to activate new mix-get handlers
    mix_convert();
  } catch (err) {
    console.error("Failed to add markers:", err, data);
  }
};

