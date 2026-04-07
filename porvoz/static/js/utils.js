/**
 * Utilidades globales para Porvoz
 * - Toasts (notificaciones flotantes)
 * - Loading states
 * - Keyboard shortcuts
 * - Theme toggle
 */

// ============================================================================
// TOASTS - Notificaciones flotantes
// ============================================================================

const Toast = {
  container: null,

  init() {
    if (this.container) return;
    this.container = document.createElement("div");
    this.container.id = "toast-container";
    this.container.className =
      "fixed bottom-4 right-4 z-50 space-y-3 pointer-events-none";
    document.body.appendChild(this.container);
  },

  show(message, type = "info", duration = 4000) {
    this.init();

    const colorMap = {
      success: "bg-emerald-500 text-white",
      error: "bg-red-500 text-white",
      warning: "bg-amber-500 text-white",
      info: "bg-blue-500 text-white",
    };

    const iconMap = {
      success: "bi-check-circle-fill",
      error: "bi-x-circle-fill",
      warning: "bi-exclamation-triangle-fill",
      info: "bi-info-circle-fill",
    };

    const toast = document.createElement("div");
    toast.className = `${colorMap[type] || colorMap.info} rounded-xl shadow-lg px-5 py-3.5 flex items-center gap-3 text-sm font-medium animate-slideInUp pointer-events-auto`;
    toast.innerHTML = `
      <i class="bi ${iconMap[type] || iconMap.info}"></i>
      <span>${escapeHtml(message)}</span>
      <button class="ml-2 hover:opacity-80 transition-opacity" data-close>
        <i class="bi bi-x-lg text-sm"></i>
      </button>
    `;

    toast.querySelector("[data-close]").addEventListener("click", () => {
      toast.remove();
    });

    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        toast.remove();
      }, duration);
    }

    return toast;
  },
};

// ============================================================================
// LOADING STATES - Spinners en botones
// ============================================================================

const Loading = {
  setLoading(button, isLoading = true) {
    if (!button) return;

    const originalHTML = button.dataset.originalHtml;

    if (isLoading) {
      button.dataset.originalHtml = button.innerHTML;
      button.disabled = true;
      button.innerHTML = `
        <span class="inline-flex items-center gap-2">
          <i class="bi bi-arrow-repeat animate-spin"></i>
          <span>${button.dataset.loadingText || "Procesando..."}</span>
        </span>
      `;
      button.classList.add("opacity-75", "cursor-not-allowed");
    } else {
      button.innerHTML = originalHTML || button.dataset.originalHtml;
      button.disabled = false;
      button.classList.remove("opacity-75", "cursor-not-allowed");
    }
  },

  prevent(form) {
    const submitBtn = form.querySelector('[type="submit"]');
    if (!submitBtn) return;

    form.addEventListener("submit", function (e) {
      if (submitBtn.disabled) {
        e.preventDefault();
        return;
      }
      Loading.setLoading(submitBtn, true);
    });
  },
};

// ============================================================================
// THEME - Tema oscuro/claro
// ============================================================================

const Theme = {
  init() {
    const savedTheme = localStorage.getItem("theme") || "light";
    this.set(savedTheme);
  },

  set(theme) {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  },

  toggle() {
    const current = localStorage.getItem("theme") || "light";
    const newTheme = current === "light" ? "dark" : "light";
    this.set(newTheme);
    return newTheme;
  },
};

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

const Shortcuts = {
  init() {
    document.addEventListener("keydown", (e) => {
      // Ignorar si está escribiendo en un input
      if (
        e.target.matches("input:not([type=checkbox]):not([type=radio])") ||
        e.target.matches("textarea")
      ) {
        return;
      }

      // ?  → mostrar shortcuts
      if (e.key === "?") {
        e.preventDefault();
        this.showHelp();
      }

      // n  → notificaciones
      if (e.key === "n" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        window.location.href = document.querySelector(
          'a[href*="/notificaciones/"]'
        )?.href;
      }

      // p  → pacientes
      if (e.key === "p" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        window.location.href = document.querySelector(
          'a[href*="/pacientes/"]'
        )?.href;
      }

      // l  → llamadas
      if (e.key === "l" && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        window.location.href = document.querySelector(
          'a[href*="/llamadas/"]'
        )?.href;
      }
    });
  },

  showHelp() {
    const help = `
      <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 animate-fadeIn">
        <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 animate-slideUp">
          <h2 class="text-xl font-bold mb-4 flex items-center justify-between">
            Atajos de teclado
            <button class="text-slate-400 hover:text-slate-600" onclick="this.closest('.fixed').remove()">
              <i class="bi bi-x-lg"></i>
            </button>
          </h2>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <kbd class="bg-slate-100 px-2 py-1 rounded font-mono">?</kbd>
              <span class="text-slate-600">Mostrar atajos</span>
            </div>
            <div class="flex justify-between">
              <kbd class="bg-slate-100 px-2 py-1 rounded font-mono">N</kbd>
              <span class="text-slate-600">Notificaciones</span>
            </div>
            <div class="flex justify-between">
              <kbd class="bg-slate-100 px-2 py-1 rounded font-mono">P</kbd>
              <span class="text-slate-600">Pacientes</span>
            </div>
            <div class="flex justify-between">
              <kbd class="bg-slate-100 px-2 py-1 rounded font-mono">L</kbd>
              <span class="text-slate-600">Llamadas</span>
            </div>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML("beforeend", help);
  },
};

// ============================================================================
// HELPERS
// ============================================================================

function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}

// ============================================================================
// INIT
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  Theme.init();
  Shortcuts.init();
  // Convert Django messages to toasts
  document.querySelectorAll(".messages > li").forEach((msg) => {
    const text = msg.textContent.trim();
    const type = msg.className.includes("error")
      ? "error"
      : msg.className.includes("success")
        ? "success"
        : "info";
    Toast.show(text, type);
    msg.style.display = "none";
  });
});
