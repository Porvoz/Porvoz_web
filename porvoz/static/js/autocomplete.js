/**
 * Autocomplete utility para campos de búsqueda
 * Uso: Autocomplete.init('input-id', ['opción1', 'opción2', ...])
 */

const Autocomplete = {
  init(inputId, options = []) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Crear contenedor de sugerencias
    const dropdown = document.createElement("div");
    dropdown.className =
      "absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-20 max-h-64 overflow-y-auto hidden";
    dropdown.id = `${inputId}-dropdown`;
    input.parentElement.style.position = "relative";
    input.parentElement.appendChild(dropdown);

    let filteredOptions = [];
    let selectedIndex = -1;

    function showSuggestions(query) {
      const lowerQuery = query.toLowerCase().trim();
      if (!lowerQuery) {
        dropdown.classList.add("hidden");
        return;
      }

      filteredOptions = options.filter((opt) =>
        opt.toLowerCase().includes(lowerQuery)
      );

      if (filteredOptions.length === 0) {
        dropdown.classList.add("hidden");
        return;
      }

      dropdown.innerHTML = filteredOptions
        .map(
          (opt, idx) =>
            `<div class="px-4 py-2.5 cursor-pointer hover:bg-slate-100 transition-colors text-sm" data-index="${idx}">
              ${highlightMatch(opt, lowerQuery)}
            </div>`
        )
        .join("");

      dropdown.classList.remove("hidden");
      selectedIndex = -1;

      // Click handlers
      dropdown.querySelectorAll("[data-index]").forEach((item) => {
        item.addEventListener("click", () => {
          input.value = filteredOptions[parseInt(item.dataset.index)];
          dropdown.classList.add("hidden");
          input.focus();
        });
      });
    }

    function highlightMatch(text, query) {
      const regex = new RegExp(`(${query})`, "gi");
      return text.replace(
        regex,
        '<span class="font-semibold text-emerald-600">$1</span>'
      );
    }

    // Event listeners
    input.addEventListener("input", (e) => {
      showSuggestions(e.target.value);
    });

    input.addEventListener("keydown", (e) => {
      const items = dropdown.querySelectorAll("[data-index]");

      if (e.key === "ArrowDown") {
        e.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
        items[selectedIndex]?.scrollIntoView({ block: "nearest" });
        items[selectedIndex]?.classList.add("bg-slate-100");
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, -1);
        if (selectedIndex >= 0) {
          items[selectedIndex]?.scrollIntoView({ block: "nearest" });
          items[selectedIndex]?.classList.add("bg-slate-100");
        }
      } else if (e.key === "Enter" && selectedIndex >= 0) {
        e.preventDefault();
        input.value = filteredOptions[selectedIndex];
        dropdown.classList.add("hidden");
      } else if (e.key === "Escape") {
        dropdown.classList.add("hidden");
      }
    });

    // Cerrar al hacer click fuera
    document.addEventListener("click", (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add("hidden");
      }
    });
  },
};
