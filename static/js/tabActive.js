document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".tab-btn");
  const contents = document.querySelectorAll(".tab-content");
  const pageId = document.querySelector("main").id;
  const storageKey = `activeTab_${pageId}`;

  function activateTab(tabId) {
    tabs.forEach(t => t.classList.remove("active"));
    contents.forEach(c => c.classList.remove("active"));

    const tab = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const content = document.getElementById(tabId);
    if (tab && content) {
      tab.classList.add("active");
      content.classList.add("active");
    }
  }

  const savedTab = sessionStorage.getItem(storageKey);
  if (savedTab) {
    activateTab(savedTab);
  } else {
    activateTab(tabs[0].getAttribute("data-tab"));
  }

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const selected = tab.getAttribute("data-tab");
      activateTab(selected);
      sessionStorage.setItem(storageKey, selected);
    });
  });
});