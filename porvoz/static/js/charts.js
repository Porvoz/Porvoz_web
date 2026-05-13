/**
 * Charts para Porvoz - utiliza Chart.js
 * Necesita: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
 */

const PorvozCharts = {
  adherenciaChart: null,

  init() {
    this.checkChartJS();
  },

  checkChartJS() {
    if (typeof Chart === "undefined") {
      console.warn("Chart.js no está cargado. Descargando...");
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js";
      script.onload = () => {
        console.log("Chart.js cargado");
      };
      document.head.appendChild(script);
    }
  },

  /**
   * Dibuja gráfico de adherencia por día (últimos 7 días)
   * @param {string} canvasId - ID del canvas element
   * @param {array} labels - días de la semana
   * @param {array} data - array de porcentajes (0-100)
   */
  adherenciaWeekly(canvasId, labels, data) {
    if (typeof Chart === "undefined") return;

    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    this.adherenciaChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Adherencia (%)",
            data: data,
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.1)",
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: "#10b981",
            pointBorderColor: "#fff",
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: (value) => value + "%",
            },
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  },

  /**
   * Dibuja gráfico de donut de resultados de llamadas
   * @param {string} canvasId - ID del canvas element
   * @param {number} confirmadas - cantidad
   * @param {number} noConfirmadas - cantidad
   */
  resultadosLlamadas(canvasId, confirmadas, noConfirmadas) {
    if (typeof Chart === "undefined") return;

    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Confirmadas", "No confirmadas"],
        datasets: [
          {
            data: [confirmadas, noConfirmadas],
            backgroundColor: ["#10b981", "#ef4444"],
            borderColor: "#fff",
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
        },
      },
    });
  },
};

// Inicializar cuando el DOM está listo
document.addEventListener("DOMContentLoaded", () => {
  PorvozCharts.init();
});
