const form = document.querySelector("#menu-form");
const loadingState = document.querySelector("#loading-state");
const emptyState = document.querySelector("#empty-state");
const resultRoot = document.querySelector("#result-root");
const template = document.querySelector("#result-template");

function collectFormData(formElement) {
  const formData = new FormData(formElement);
  return {
    diners: Number(formData.get("diners") || 4),
    occasion: formData.get("occasion"),
    budget: formData.get("budget"),
    surprise: formData.get("surprise"),
    preferences: formData.getAll("preferences"),
    restrictions: formData.getAll("restrictions"),
    notes: formData.get("notes")?.toString().trim() || "",
  };
}

function createPill(text, className = "request-pill") {
  const span = document.createElement("span");
  span.className = className;
  span.textContent = text;
  return span;
}

function renderResult(data) {
  const fragment = template.content.cloneNode(true);

  fragment.querySelector(".menu-title").textContent = data.title;
  fragment.querySelector(".menu-subtitle").textContent = data.subtitle;
  fragment.querySelector(".estimated-total").textContent = `¥${data.estimated_total}`;
  fragment.querySelector(".per-person").textContent = `人均约 ¥${data.per_person}`;
  fragment.querySelector(".menu-summary").textContent = data.summary;

  const summaryNode = fragment.querySelector(".request-summary");
  summaryNode.append(
    createPill(`${data.request.diners} 位用餐`),
    createPill(data.request.occasion),
    createPill(data.request.budget)
  );

  const highlightStrip = fragment.querySelector(".highlight-strip");
  data.highlights.forEach((item) => {
    highlightStrip.appendChild(createPill(item, "highlight-pill"));
  });

  const courseGrid = fragment.querySelector(".course-grid");
  data.courses.forEach((course) => {
    const article = document.createElement("article");
    article.className = "course-card";
    article.innerHTML = `
      <div class="course-meta">
        <span class="course-label">${course.course_label}</span>
        <span class="course-price">¥${course.price}</span>
      </div>
      <h4 class="course-name">${course.name}</h4>
      <p class="course-copy">${course.description}</p>
      <p class="course-note"><strong>为什么推荐：</strong>${course.reason}</p>
      <p class="course-note"><strong>上桌表达：</strong>${course.presentation}</p>
    `;
    courseGrid.appendChild(article);
  });

  const notesNode = fragment.querySelector(".chef-notes");
  data.chef_notes.forEach((note) => {
    const item = document.createElement("li");
    item.textContent = note;
    notesNode.appendChild(item);
  });

  const requestTagsNode = fragment.querySelector(".request-tags");
  data.request.preferences.forEach((item) => requestTagsNode.appendChild(createPill(item)));
  data.request.restrictions.forEach((item) => requestTagsNode.appendChild(createPill(item)));

  resultRoot.innerHTML = "";
  resultRoot.appendChild(fragment);
}

async function generateMenu(payload) {
  const response = await fetch("/api/generate-menu", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("菜单生成失败，请稍后重试。");
  }

  return response.json();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  loadingState.classList.remove("hidden");
  emptyState.classList.add("hidden");
  resultRoot.classList.add("hidden");

  try {
    const payload = collectFormData(form);
    const result = await generateMenu(payload);
    renderResult(result);
    resultRoot.classList.remove("hidden");
  } catch (error) {
    emptyState.innerHTML = `<p>${error.message}</p>`;
    emptyState.classList.remove("hidden");
  } finally {
    loadingState.classList.add("hidden");
  }
});

form.dispatchEvent(new Event("submit"));
