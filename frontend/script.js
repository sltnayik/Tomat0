const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyzeBtn");
const hasil = document.getElementById("hasil");
const akurasi = document.getElementById("akurasi");
const spinner = document.getElementById("spinner");

let selectedFile = null;
let chart = null;

// Preview Gambar
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) {
    selectedFile = file;
    preview.src = URL.createObjectURL(file);
    preview.classList.remove("hidden");
  }
});

// Warna khusus tiap kelas
const classColors = {
  Hawar: "#ef4444",
  Karat: "#f59e0b",
  "Bercak Daun": "#10b981",
  Sehat: "#3b82f6",
  Unknown: "#6b7280",
};

// Kirim ke backend
analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Pilih gambar terlebih dahulu!");
    return;
  }

  // Tampilkan spinner
  spinner.style.display = "block";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    hasil.textContent = data.label;
    akurasi.textContent = data.accuracy;

    updateChart(data.probabilities);
  } catch (error) {
    alert("Gagal menghubungi server!");
    console.error(error);
  }

  spinner.style.display = "none";
});

// Update Chart
function updateChart(probabilities) {
  const ctx = document.getElementById("chartCanvas").getContext("2d");

  const labels = Object.keys(probabilities);
  const values = Object.values(probabilities);

  const bgColors = labels.map((label) => classColors[label] || "#006effff");

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Probabilitas (%)",
          data: values.map((v) => v * 100),
          backgroundColor: bgColors,
        },
      ],
    },
    options: {
      animation: {
        duration: 1200,
        easing: "easeOutExpo",
        delay: (ctx) => ctx.dataIndex * 200, // animasi bar satu-per-satu
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}
