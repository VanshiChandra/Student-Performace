document.addEventListener("DOMContentLoaded", async () => {
  const ctx = document.getElementById("progressChart");
  if (!ctx) return;

  try {
    const response = await fetch(
      window.location.origin + "/records/chart-data"
    );
        const data = await response.json();

    if (data.error || data.length === 0) return;

    const labels = data.map((_, idx) => `Attempt ${idx + 1}`);
    const subjects = Object.keys(data[0]).filter(k => k !== "username");

    const datasets = subjects.map(subject => ({
      label: subject,
      data: data.map(d => d[subject]),
      fill: false,
      borderColor: `hsl(${Math.random() * 360}, 70%, 50%)`,
      tension: 0.1
    }));

    new Chart(ctx, {
      type: "line",
      data: { labels, datasets },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  } catch (err) {
    console.error("Error loading chart data:", err);
  }
});
