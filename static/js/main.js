document.addEventListener("DOMContentLoaded", () => {
  const nav = document.querySelector(".nav-links");
  const menuBtn = document.querySelector(".menu-btn");
  const testimonialGrid = document.getElementById("testimonial-grid");
  const toggleCommentsBtn = document.getElementById("toggle-comments");
  const commentList = document.getElementById("comment-list");
  const likeBtn = document.getElementById("like-btn");
  const unlikeBtn = document.getElementById("unlike-btn");

  if (menuBtn && nav) {
    menuBtn.addEventListener("click", () => nav.classList.toggle("open"));
    nav.addEventListener("click", () => nav.classList.remove("open"));
  }

  const testimonialPool = [
    { name: "Mike Johnson", country: "USA", text: "Just received my Tesla Model 3 2024!! I paid the delivery fee and within 9 days the car was at my door." },
    { name: "Sarah Williams", country: "UK", text: "I received my Tesla Model Y 2025 after paying the delivery fee. It was delivered right to my address." },
    { name: "Carlos Mendez", country: "Mexico", text: "From Mexico! I received my Tesla Model 3 2024 after paying the delivery fee." },
    { name: "Priya Sharma", country: "India", text: "From India, I got my Tesla Model Y 2025 after the payment chat on WhatsApp." },
    { name: "James Okafor", country: "Nigeria", text: "Nigeria represent! Tesla Model 3 delivered to my doorstep." },
    { name: "Emma Brown", country: "Canada", text: "Tesla delivery confirmed and the process was smooth." },
    { name: "Aisha Bello", country: "Ghana", text: "My delivery details were verified through WhatsApp quickly." }
  ];

  function avatarLetters(name) {
    return name.split(" ").slice(0, 2).map((n) => n[0]).join("").toUpperCase();
  }

  function relativeTime(createdAt) {
    const diffMin = Math.floor((Date.now() - createdAt) / 60000);
    if (diffMin <= 0) return "just now";
    if (diffMin === 1) return "1 min ago";
    return `${diffMin} min ago`;
  }

  function createTestimonialCard(item) {
    const card = document.createElement("article");
    card.className = "testimony-card pop-in";
    card.dataset.createdAt = String(item.createdAt);

    card.innerHTML = `
      <div class="avatar">${avatarLetters(item.name)}</div>
      <div class="testimony-body">
        <div class="meta">
          <strong>${item.name}</strong>
          <span>${item.country}</span>
          <span class="time-label">${relativeTime(item.createdAt)}</span>
        </div>
        <p>${item.text}</p>
      </div>
    `;

    return card;
  }

  function updateTestimonialTimes() {
    if (!testimonialGrid) return;
    testimonialGrid.querySelectorAll(".time-label").forEach((el) => {
      const card = el.closest(".testimony-card");
      const createdAt = Number(card?.dataset.createdAt || Date.now());
      el.textContent = relativeTime(createdAt);
    });
  }

  function seedTestimonials() {
    if (!testimonialGrid) return;
    testimonialGrid.innerHTML = "";
    const now = Date.now();
    const seedAges = [10, 8, 6, 4];

    testimonialPool.slice(0, 4).forEach((item, index) => {
      testimonialGrid.appendChild(
        createTestimonialCard({
          ...item,
          createdAt: now - seedAges[index] * 60000
        })
      );
    });

    updateTestimonialTimes();
  }

  function addNewTestimonial() {
    if (!testimonialGrid) return;

    const random = testimonialPool[Math.floor(Math.random() * testimonialPool.length)];
    const fresh = {
      ...random,
      createdAt: Date.now(),
      text: `${random.name.split(" ")[0]} says their Tesla delivery is being processed now.`
    };

    testimonialGrid.prepend(createTestimonialCard(fresh));

    while (testimonialGrid.children.length > 6) {
      testimonialGrid.removeChild(testimonialGrid.lastElementChild);
    }

    updateTestimonialTimes();
  }

  if (toggleCommentsBtn && commentList) {
    toggleCommentsBtn.addEventListener("click", async () => {
      const isCollapsed = commentList.classList.contains("collapsed");
      commentList.classList.toggle("collapsed", !isCollapsed);
      commentList.classList.toggle("expanded", isCollapsed);

      if (isCollapsed && !commentList.dataset.loaded) {
        try {
          const res = await fetch("/static/data/comments.json");
          const allComments = await res.json();

          const html = allComments.slice(5).map((comment) => `
            <div class="yt-comment${comment.pinned ? " pinned" : ""}">
              <div class="comment-avatar">${comment.initials}</div>
              <div class="comment-body">
                <div class="comment-meta">
                  <strong>${comment.name}</strong>
                  <span>${comment.time}</span>
                  ${comment.pinned ? '<span class="pinned-label">📌 Pinned</span>' : ""}
                </div>
                <p>${comment.text}</p>
                <div class="comment-actions">
                  <span>${comment.likes}</span>
                  <span>Reply</span>
                </div>
              </div>
            </div>
          `).join("");

          commentList.insertAdjacentHTML("beforeend", html);
          commentList.dataset.loaded = "true";
        } catch (err) {
          console.error("Failed to load comments:", err);
        }
      }

      toggleCommentsBtn.innerHTML = isCollapsed
        ? "Hide comments"
        : '<span id="more-count">70,842</span> more comments';
    });
  }

  if (likeBtn && unlikeBtn) {
    likeBtn.addEventListener("click", () => {
      likeBtn.classList.toggle("active");
      unlikeBtn.classList.remove("unliked");
    });

    unlikeBtn.addEventListener("click", () => {
      unlikeBtn.classList.toggle("unliked");
      likeBtn.classList.remove("active");
    });
  }

  seedTestimonials();
  setInterval(addNewTestimonial, 5000);
  setInterval(updateTestimonialTimes, 1000);
});

document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("toggle-comments");
  const commentList = document.getElementById("comment-list");

  if (!toggleBtn || !commentList) return;

  toggleBtn.addEventListener("click", function () {
    const hidden = commentList.classList.toggle("expanded");
    toggleBtn.innerHTML = hidden
      ? 'Hide comments'
      : 'View <span id="more-count">70,842</span> more comments';
  });
});