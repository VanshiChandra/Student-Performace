document.addEventListener("DOMContentLoaded", () => {
  const trendCtx = document.getElementById("progressChart");
  const subjectCtx = document.getElementById("subjectProgressChart");
  const avgCtx = document.getElementById("subjectAverageChart");

  if (!trendCtx && !subjectCtx && !avgCtx) return;

  fetch("/records/chart-data")
    .then((res) => res.json())
    .then((data) => {
      if (!data || data.length === 0) return;

      // -------- Trend Chart (Overall Percentage) --------
      if (trendCtx) {
        const labels = data.map((_, i) => `Attempt ${i + 1}`);
        const percentages = data.map((r) => r.percentage);

        new Chart(trendCtx, {
          type: "line",
          data: {
            labels,
            datasets: [
              {
                label: "Overall % Progress",
                data: percentages,
                borderColor: "blue",
                backgroundColor: "rgba(0,0,255,0.2)",
                tension: 0.3,
                fill: true,
              },
            ],
          },
        });
      }

      // -------- Subject Progress (Line Chart per Subject) --------
      if (subjectCtx) {
        const labels = data.map((_, i) => `Attempt ${i + 1}`);
        const subjects = Object.keys(data[0].scores);

        const datasets = subjects.map((subj, idx) => {
          const color = `hsl(${(idx * 60) % 360}, 70%, 50%)`;
          return {
            label: subj,
            data: data.map((r) => r.scores[subj] || 0),
            borderColor: color,
            backgroundColor: color,
            tension: 0.3,
            fill: false,
          };
        });

        new Chart(subjectCtx, {
          type: "line",
          data: { labels, datasets },
        });
      }

      // -------- Subject Averages (Bar Chart) --------
      if (avgCtx) {
        const subjects = Object.keys(data[0].scores);
        const averages = subjects.map((subj) => {
          const sum = data.reduce((acc, r) => acc + (r.scores[subj] || 0), 0);
          return (sum / data.length).toFixed(2);
        });

        new Chart(avgCtx, {
          type: "bar",
          data: {
            labels: subjects,
            datasets: [
              {
                label: "Average Score",
                data: averages,
                backgroundColor: subjects.map(
                  (_, idx) => `hsl(${(idx * 60) % 360}, 70%, 60%)`
                ),
              },
            ],
          },
        });
      }
    })
    .catch((err) => console.error("Chart load error:", err));
});
