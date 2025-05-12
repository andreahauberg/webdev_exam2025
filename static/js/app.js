// Nvigation
function burgerMenu() {
  const burgerBtn = document.querySelector("#burger_btn");
  const sideMenu = document.querySelector("#side_menu");
  const closeBtn = document.querySelector("#close_btn");

  if (!burgerBtn || !sideMenu || !closeBtn) return;

  burgerBtn.addEventListener("click", () => {
    sideMenu.classList.toggle("open");
  });

  closeBtn.addEventListener("click", () => {
    sideMenu.classList.remove("open");
  });
}




// ###############################################

// input search

const search_results = document.querySelector("#search_results");
const input_search = document.querySelector("#input_search");
let my_timer = null;

// setTimeout - runs only 1 time
// setInterval - runs forever in intervals
function search() {
  clearInterval(my_timer);
  if (input_search.value != "") {
    my_timer = setTimeout(async function () {
      try {
        const search_for = input_search.value;
        const conn = await fetch(`/search?q=${search_for}`);
        const data = await conn.json();
        search_results.innerHTML = "";
        console.log(data);
        data.forEach((item) => {
          const a = `<div class="instant-item" mix-get="/items/${item.item_pk}">
                                <img src="/static/images/${item.item_image}">
                                <a href="/${item.item_name}">${item.item_name}</a>
                                </div>`;
          search_results.insertAdjacentHTML("beforeend", a);
        });
        mix_convert();
        search_results.classList.remove("hidden");
      } catch (err) {
        console.error(err);
      }
    }, 500);
  } else {
    search_results.innerHTML = "";
    search_results.classList.add("hidden");
  }
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
        className: "custom-marker", // Class for custom styling
        html: `<div class="custom-marker">
                  <img src="/static/icons/${item.item_icon}" />
               </div>`, // Custom content inside the div
        iconSize: [32, 32], // size of the icon
        iconAnchor: [16, 16], // point of the icon which will correspond to marker's location
        popupAnchor: [0, -16],
      });

      L.marker([item.item_lat, item.item_lon], { icon: customIcon })
        .addTo(map)
        .bindPopup(item.item_name);
    });
  } catch (err) {
    console.error("Failed to add markers:", err, data);
  }
};

function onMarkerClick(event) {
  alert("Marker clicked at " + event.latlng);
}

// ###############################################