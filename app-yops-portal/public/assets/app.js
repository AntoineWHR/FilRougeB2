const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const revealElements = document.querySelectorAll(".reveal");

for (const element of revealElements) {
  const children = element.querySelectorAll(":scope > *");
  children.forEach((child, index) => {
    child.classList.add("stagger-child");
    child.style.setProperty("--i", index);
  });
}

const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        const counters = entry.target.querySelectorAll("[data-count]");
        for (const counter of counters) animateCount(counter);
        observer.unobserve(entry.target);
      }
    }
  },
  { threshold: 0.12 }
);

for (const element of revealElements) {
  observer.observe(element);
}

function animateCount(node) {
  const target = parseFloat(node.dataset.count);
  if (isNaN(target)) return;
  const suffix = node.dataset.suffix || "";
  if (reduced) {
    node.textContent = formatValue(target) + suffix;
    return;
  }
  const duration = 1100;
  const start = performance.now();
  const tick = (now) => {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    node.textContent = formatValue(target * eased) + suffix;
    if (t < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function formatValue(value) {
  return Number.isInteger(value) ? Math.round(value).toString() : value.toFixed(1);
}

const searchInputs = document.querySelectorAll("[data-search-target]");
for (const input of searchInputs) {
  const targetSelector = input.dataset.searchTarget;
  input.addEventListener("input", () => {
    const term = input.value.trim().toLowerCase();
    const rows = document.querySelectorAll(targetSelector);
    for (const row of rows) {
      const text = row.textContent.toLowerCase();
      row.style.display = !term || text.includes(term) ? "" : "none";
    }
  });
}

const spotlightTargets = document.querySelectorAll(
  ".service-strip article, .price-card, .report-card, .panel, .quick-action, .timeline-item, .activity-item"
);
for (const card of spotlightTargets) {
  card.addEventListener("pointermove", (event) => {
    const rect = card.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    card.style.setProperty("--spot-x", `${x}%`);
    card.style.setProperty("--spot-y", `${y}%`);
  });
  card.addEventListener("pointerleave", () => {
    card.style.removeProperty("--spot-x");
    card.style.removeProperty("--spot-y");
  });
}
