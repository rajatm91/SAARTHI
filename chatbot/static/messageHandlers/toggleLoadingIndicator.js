let dotsInterval;

export function toggleLoadingIndicator(show) {
  const loadingIndicator = document.getElementById("loading-indicator");
  const dots = document.getElementById("dots");

  if (show) {
    loadingIndicator.style.display = "block";

    let dotsCount = 0;
    dotsInterval = setInterval(() => {
      dotsCount = (dotsCount + 1) % 4;
      dots.textContent = ".".repeat(dotsCount);
    }, 500);
  } else {
    loadingIndicator.style.display = "none";

    clearInterval(dotsInterval);
  }
}