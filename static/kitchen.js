const form = document.querySelector("#kitchen-form");
const loadingNode = document.querySelector("#sim-loading");
const clockNode = document.querySelector("#sim-clock");
const metricsRoot = document.querySelector("#metrics-root");
const stationRoot = document.querySelector("#station-root");
const roomRoot = document.querySelector("#room-root");
const completedRoot = document.querySelector("#completed-root");
const tablesRoot = document.querySelector("#tables-root");
const playToggleButton = document.querySelector("#play-toggle");
const speedSelect = document.querySelector("#playback-speed");
const addOrderButton = document.querySelector("#add-order-button");
const resetKitchenButton = document.querySelector("#reset-kitchen-button");
const chefMinusButton = document.querySelector("#chef-minus");
const chefPlusButton = document.querySelector("#chef-plus");
const chefLiveBadge = document.querySelector("#chef-live-badge");

const STATION_LABELS = {
  cold: "冷菜台",
  hot: "热菜灶",
  soup: "炖煮炉",
  steam: "蒸箱",
};

const COURSE_BIAS = {
  appetizer: 6.0,
  soup: 5.0,
  seafood: 4.2,
  poultry: 3.8,
  meat: 3.6,
  vegetable: 2.8,
  staple: 2.0,
  dessert: 1.0,
};

const state = {
  minute: 0,
  timer: null,
  intervalMs: Number(speedSelect.value),
  playing: true,
  nextTableNumber: 1,
  tables: [],
  tasks: [],
  runningTasks: [],
  stationRefs: new Map(),
  roomRefs: new Map(),
  tableRefs: new Map(),
  completedSignature: "",
  config: null,
  startTime: "18:00",
};

function collectConfig() {
  const formData = new FormData(form);
  return {
    start_time: formData.get("start_time") || "18:00",
    chefs: Number(formData.get("chefs")),
    cold_stations: Number(formData.get("cold_stations")),
    hot_stations: Number(formData.get("hot_stations")),
    soup_stations: Number(formData.get("soup_stations")),
    steamers: Number(formData.get("steamers")),
  };
}

function createSlots(config) {
  return {
    hot: Array.from({ length: config.hot_stations }, (_, index) => ({
      slotId: `hot-${index + 1}`,
      station: "hot",
      busyUntil: 0,
      currentTaskId: null,
      disabled: false,
    })),
    cold: Array.from({ length: config.cold_stations }, (_, index) => ({
      slotId: `cold-${index + 1}`,
      station: "cold",
      busyUntil: 0,
      currentTaskId: null,
      disabled: false,
    })),
    soup: Array.from({ length: config.soup_stations }, (_, index) => ({
      slotId: `soup-${index + 1}`,
      station: "soup",
      busyUntil: 0,
      currentTaskId: null,
      disabled: false,
    })),
    steam: Array.from({ length: config.steamers }, (_, index) => ({
      slotId: `steam-${index + 1}`,
      station: "steam",
      busyUntil: 0,
      currentTaskId: null,
      disabled: false,
    })),
  };
}

function resetKitchen() {
  stopClock();
  state.minute = 0;
  state.nextTableNumber = 1;
  state.tables = [];
  state.tasks = [];
  state.runningTasks = [];
  state.config = collectConfig();
  state.startTime = state.config.start_time;
  state.stationSlots = createSlots(state.config);
  state.stationRefs.clear();
  state.roomRefs.clear();
  state.tableRefs.clear();
  state.completedSignature = "";
  renderMetrics();
  renderStations();
  renderRoom();
  renderCompletedRecords();
  renderTables();
  renderEvents();
  updateBoard();
  setPlaybackState(true);
}

function formatClock(startTime, minuteOffset) {
  const [hours, minutes] = startTime.split(":").map(Number);
  const total = hours * 60 + minutes + minuteOffset;
  const normalized = ((total % (24 * 60)) + 24 * 60) % (24 * 60);
  const hh = String(Math.floor(normalized / 60)).padStart(2, "0");
  const mm = String(normalized % 60).padStart(2, "0");
  return `${hh}:${mm}`;
}

function stopClock() {
  if (state.timer) {
    clearInterval(state.timer);
    state.timer = null;
  }
}

function startClock() {
  stopClock();
  if (!state.playing) return;
  state.timer = setInterval(() => {
    tickMinute();
  }, state.intervalMs);
}

function setPlaybackState(playing) {
  state.playing = playing;
  playToggleButton.textContent = playing ? "暂停" : "继续";
  if (playing) {
    startClock();
  } else {
    stopClock();
  }
}

function tickMinute() {
  state.minute += 1;
  finishTasksForMinute();
  scheduleForMinute();
  updateBoard();
}

function createMetricCard(label, value, hint) {
  const article = document.createElement("article");
  article.className = "metric-card";
  article.innerHTML = `
    <span>${label}</span>
    <strong>${value}</strong>
    <small>${hint}</small>
  `;
  return article;
}

function getDynamicMetrics() {
  const activeTables = state.tables.filter((table) => table.arrival_minute <= state.minute && !table.completed);
  const firstWaits = state.tables
    .filter((table) => table.first_served_at !== null)
    .map((table) => table.first_served_at - table.arrival_minute);

  const currentLongestWait = activeTables.reduce((maxWait, table) => {
    const anchor = table.last_served_at ?? table.arrival_minute;
    return Math.max(maxWait, state.minute - anchor);
  }, 0);

  const stationBusy = Object.values(state.stationSlots)
    .flat()
    .filter((slot) => slot.busyUntil > state.minute).length;

  return {
    averageFirstWait: firstWaits.length > 0 ? Math.round(firstWaits.reduce((sum, value) => sum + value, 0) / firstWaits.length) : 0,
    longestWait: currentLongestWait,
    activeTables: activeTables.length,
    busyStations: stationBusy,
  };
}

function renderMetrics() {
  const metrics = getDynamicMetrics();
  metricsRoot.innerHTML = "";
  metricsRoot.append(
    createMetricCard("平均首道等待", `${metrics.averageFirstWait} 分钟`, "越短说明第一口更快来到桌上"),
    createMetricCard("当前最长等待", `${metrics.longestWait} 分钟`, "重点看有没有哪桌被晾太久"),
    createMetricCard("活跃桌数", `${metrics.activeTables} 桌`, "当前正在经历出餐过程的桌数"),
    createMetricCard("忙碌工位", `${metrics.busyStations} 个`, "越满说明厨房正在高负荷运转"),
  );
}

function updateChefLiveBadge() {
  if (!chefLiveBadge || !state.config) return;
  const busyChefs = getCurrentChefLoad();
  chefLiveBadge.textContent = `当前 ${state.config.chefs} 名厨师 · 忙碌 ${busyChefs} 名`;
}

function renderStations() {
  stationRoot.innerHTML = "";
  state.stationRefs.clear();

  Object.entries(state.stationSlots).forEach(([stationKey, slots]) => {
    const group = document.createElement("section");
    group.className = `station-group station-${stationKey}`;
    group.innerHTML = `
      <div class="station-group-header">
        <h4>${STATION_LABELS[stationKey]}</h4>
        <span class="mini-pill">${slots.length} 个工位</span>
      </div>
      <div class="station-slots"></div>
    `;
    const slotList = group.querySelector(".station-slots");
    slots.forEach((slot) => {
      const article = document.createElement("article");
      article.className = "station-slot";
      article.innerHTML = `
        <div class="slot-top">
          <span class="slot-badge">${slot.slotId}</span>
          <span class="status-pill">空闲</span>
        </div>
        <div class="slot-main">
          <p class="slot-dish">等待接单</p>
          <p class="slot-meta">当前没有菜在这个工位上</p>
        </div>
        <div class="slot-actions">
          <button class="ghost-button slot-action" type="button" data-slot-id="${slot.slotId}">停用工位</button>
        </div>
        <div class="progress-track"><div class="progress-fill"></div></div>
      `;
      article.querySelector(".slot-action")?.addEventListener("click", () => {
        toggleSlotAvailability(slot.slotId);
      });
      state.stationRefs.set(slot.slotId, article);
      slotList.appendChild(article);
    });
    stationRoot.appendChild(group);
  });
}

function renderRoom() {
  roomRoot.innerHTML = "";
  state.roomRefs.clear();

  const activeTables = state.tables.filter((table) => !table.archived);
  if (activeTables.length === 0) {
    roomRoot.innerHTML = `<div class="room-empty">当前前场没有等待中的桌台，新的席面进入后会出现在这里。</div>`;
    return;
  }

  activeTables.forEach((table) => {
    const plateMarkup = Array.from({ length: table.courses_total }, () => '<span class="plate waiting"></span>').join("");
    const roomTable = document.createElement("article");
    roomTable.className = "room-table";
    roomTable.innerHTML = `
      <div class="room-table-top">
        <strong>${table.table_name}</strong>
        <span class="mini-pill">${table.diners} 位</span>
      </div>
      <div class="room-disc">
        <div class="room-center" data-role="count">${table.served_count}/${table.courses_total}</div>
        <div class="plate-ring" data-role="plates">${plateMarkup}</div>
      </div>
      <div class="room-note" data-role="note">刚刚入单，等待第一道菜</div>
      <div class="room-course-block">
        <div class="room-course-title">桌上菜品</div>
        <div class="room-course-list" data-role="served-list">
          <span class="room-course-chip muted">尚未上菜</span>
        </div>
      </div>
      <div class="room-course-block">
        <div class="room-course-title">当前制作</div>
        <div class="room-course-list" data-role="cooking-list">
          <span class="room-course-chip muted">暂时没有</span>
        </div>
      </div>
      <div class="room-actions">
        <button class="ghost-button room-action" type="button" data-action="rush" data-table-id="${table.table_id}">催菜优先</button>
        <button class="ghost-button room-action" type="button" data-action="add-dish" data-table-id="${table.table_id}">加一道菜</button>
        <button class="ghost-button room-action" type="button" data-action="refire" data-table-id="${table.table_id}">退上一道重做</button>
        <button class="ghost-button room-action" type="button" data-action="archive" data-table-id="${table.table_id}">确认离场</button>
      </div>
    `;
    roomTable.querySelectorAll(".room-action").forEach((button) => {
      button.addEventListener("click", async () => {
        const action = button.dataset.action;
        const tableId = button.dataset.tableId;
        if (!tableId) return;
        if (action === "rush") {
          markTableRush(tableId);
        } else if (action === "add-dish") {
          await addDishToTable(tableId);
        } else if (action === "refire") {
          refireLastServedDish(tableId);
        } else if (action === "archive") {
          archiveTable(tableId);
        }
      });
    });
    state.roomRefs.set(table.table_id, roomTable);
    roomRoot.appendChild(roomTable);
  });
}

function renderCompletedRecords() {
  const completedTables = state.tables
    .filter((table) => table.archived)
    .sort((left, right) => (right.archived_at ?? 0) - (left.archived_at ?? 0));
  const signature = completedTables.map((table) => `${table.table_id}:${table.archived_at ?? 0}`).join("|");
  if (signature === state.completedSignature) {
    return;
  }

  state.completedSignature = signature;
  if (completedTables.length === 0) {
    completedRoot.innerHTML = `<div class="completed-empty">完整出齐的桌台会沉到这里，方便前场只关注还在进行中的席面。</div>`;
    return;
  }

  completedRoot.innerHTML = completedTables
    .map(
      (table) => `
        <article class="completed-item">
          <div class="completed-top">
            <strong>${table.table_name}</strong>
            <span class="mini-pill">${formatClock(state.startTime, table.archived_at ?? state.minute)} 离场归档</span>
          </div>
          <div class="completed-tags">
            <span class="mini-pill">${table.diners} 位</span>
            <span class="mini-pill">共 ${table.courses_total} 道菜</span>
          </div>
          <div class="completed-dishes">
            ${table.courses
              .filter((course) => course.status === "served")
              .map((course) => `<span class="completed-dish-chip">${course.name}</span>`)
              .join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function renderTables() {
  tablesRoot.innerHTML = "";
  state.tableRefs.clear();

  state.tables.filter((table) => !table.archived).forEach((table) => {
    const card = document.createElement("article");
    card.className = "table-card";
    card.dataset.tableId = table.table_id;
    card.innerHTML = `
      <div class="table-top">
        <div>
          <h4>${table.table_name}</h4>
          <p class="table-summary">${table.menu_title}</p>
        </div>
        <span class="status-pill waiting" data-role="status">等待首道</span>
      </div>
      <div class="table-meta-row">
        <div class="table-tag-row">
          <span class="mini-pill">${table.diners} 位</span>
          <span class="mini-pill">${table.occasion}</span>
          <span class="mini-pill">${table.budget}</span>
          <span class="mini-pill">入单 ${formatClock(state.startTime, table.arrival_minute)}</span>
        </div>
        <div class="table-summary" data-role="summary">刚刚进入后厨，等待排程</div>
      </div>
      <div class="table-progress"><div class="table-progress-fill" data-role="progress"></div></div>
      <div class="dish-list"></div>
    `;

    const dishList = card.querySelector(".dish-list");
    table.courses.forEach((course) => {
      const dish = document.createElement("div");
      dish.className = "dish-chip";
      dish.dataset.taskId = course.task_id;
      dish.innerHTML = `
        <strong>${course.name}</strong>
        <small>${course.course_label} · ${course.station_label} · ${course.duration} 分钟</small>
      `;
      dishList.appendChild(dish);
    });

    state.tableRefs.set(table.table_id, card);
    tablesRoot.appendChild(card);
  });
}

function renderEvents() {
  return;
}

function findTask(taskId) {
  return state.tasks.find((task) => task.task_id === taskId);
}

function findSlotById(slotId) {
  return Object.values(state.stationSlots)
    .flat()
    .find((slot) => slot.slotId === slotId);
}

function recalculateTableProgress(table) {
  const servedCourses = table.courses
    .filter((course) => course.status === "served" && typeof course.end_minute === "number")
    .sort((left, right) => left.end_minute - right.end_minute);

  table.served_count = servedCourses.length;
  table.first_served_at = servedCourses.length ? servedCourses[0].end_minute : null;
  table.last_served_at = servedCourses.length ? servedCourses[servedCourses.length - 1].end_minute : null;
  table.completed = table.served_count >= table.courses_total;
  table.completed_at = table.completed ? table.last_served_at : null;
  table.served_times = servedCourses.map((course) => course.end_minute);
}

function requeueTask(task, options = {}) {
  const table = state.tables.find((item) => item.table_id === task.table_id);
  if (!table) return;

  if (task.status === "cooking") {
    table.running_count = Math.max(0, table.running_count - 1);
    state.runningTasks = state.runningTasks.filter((item) => item.task_id !== task.task_id);
    const currentSlot = task.slot_id ? findSlotById(task.slot_id) : null;
    if (currentSlot) {
      currentSlot.currentTaskId = null;
      currentSlot.busyUntil = state.minute;
    }
  }

  task.status = "queued";
  task.start_minute = null;
  task.end_minute = null;
  task.slot_id = null;
  task.priority_boost = options.priorityBoost ?? 0;
  task.earliest_start = Math.max(state.minute + (options.delayMinutes ?? 0), task.arrival_minute);

  recalculateTableProgress(table);
  table.priority_boost = Math.max(table.priority_boost || 0, options.tableBoost ?? 0);
}

function finishTasksForMinute() {
  const done = state.runningTasks.filter((task) => task.end_minute <= state.minute);
  let roomNeedsRefresh = false;
  done.forEach((task) => {
    const table = state.tables.find((item) => item.table_id === task.table_id);
    if (!table) return;

    task.status = "served";
    table.running_count = Math.max(0, table.running_count - 1);
    table.served_count += 1;
    table.last_served_at = task.end_minute;
    table.served_times.push(task.end_minute);
    if (table.first_served_at === null) {
      table.first_served_at = task.end_minute;
    }
    if (table.served_count >= table.courses_total) {
      table.completed = true;
      table.completed_at = task.end_minute;
      roomNeedsRefresh = true;
    }
    table.priority_boost = 0;

    const slot = state.stationSlots[task.station].find((item) => item.slotId === task.slot_id);
    if (slot) {
      slot.currentTaskId = null;
    }
  });

  state.runningTasks = state.runningTasks.filter((task) => task.end_minute > state.minute);
  if (roomNeedsRefresh) {
    renderRoom();
  }
}

function getCurrentChefLoad() {
  return state.runningTasks.reduce((sum, task) => sum + task.chef_need, 0);
}

function selectFreeSlot(stationKey) {
  return state.stationSlots[stationKey].find((slot) => !slot.disabled && slot.busyUntil <= state.minute) || null;
}

function computePriority(task, table, minServedCount) {
  const waitAnchor = table.last_served_at ?? table.arrival_minute;
  const waitSinceLast = state.minute - waitAnchor;
  const targetTime = task.arrival_minute + task.target_offset;
  const lateness = state.minute - targetTime;
  const servedGap = table.served_count - minServedCount;
  const firstRoundBonus = table.served_count === 0 ? 14 : 0;
  const runningPenalty = table.running_count * 3.2;
  return (
    lateness * 1.8 +
    waitSinceLast * 1.25 +
    firstRoundBonus +
    COURSE_BIAS[task.course] -
    servedGap * 12.0 -
    runningPenalty -
    task.duration * 0.08 +
    (table.priority_boost || 0) +
    (task.priority_boost || 0)
  );
}

function scheduleForMinute() {
  while (true) {
    const currentChefLoad = getCurrentChefLoad();
    const chefsAvailable = state.config.chefs - currentChefLoad;
    const activeTables = state.tables.filter((table) => table.arrival_minute <= state.minute && !table.completed);
    const minServedCount = activeTables.reduce((minValue, table) => Math.min(minValue, table.served_count), Infinity);
    const baseServed = Number.isFinite(minServedCount) ? minServedCount : 0;

    const candidates = [];
    state.tasks.forEach((task) => {
      if (task.status !== "queued") return;
      if (state.minute < task.arrival_minute || state.minute < task.earliest_start) return;
      if (task.chef_need > chefsAvailable) return;

      const table = state.tables.find((item) => item.table_id === task.table_id);
      if (!table || table.running_count >= 2) return;

      const slot = selectFreeSlot(task.station);
      if (!slot) return;

      candidates.push({
        priority: computePriority(task, table, baseServed),
        task,
        table,
        slot,
      });
    });

    if (candidates.length === 0) return;

    candidates.sort((left, right) => {
      if (right.priority !== left.priority) return right.priority - left.priority;
      return right.task.duration - left.task.duration;
    });

    const chosen = candidates[0];
    const { task, table, slot } = chosen;
    task.status = "cooking";
    task.start_minute = state.minute;
    task.end_minute = state.minute + task.duration;
    task.slot_id = slot.slotId;
    slot.busyUntil = task.end_minute;
    slot.currentTaskId = task.task_id;
    table.running_count += 1;
    state.runningTasks.push(task);
  }
}

function ensureTableVisuals() {
  renderRoom();
  renderCompletedRecords();
  renderTables();
}

function updateStations() {
  state.stationRefs.forEach((node, slotId) => {
    const slot = findSlotById(slotId);
    const statusNode = node.querySelector(".status-pill");
    const dishNode = node.querySelector(".slot-dish");
    const metaNode = node.querySelector(".slot-meta");
    const fillNode = node.querySelector(".progress-fill");
    const actionButton = node.querySelector(".slot-action");
    const task = slot?.currentTaskId ? findTask(slot.currentTaskId) : null;

    if (!slot) {
      return;
    }

    if (slot.disabled) {
      node.classList.remove("active");
      node.classList.add("unavailable");
      statusNode.textContent = "停用中";
      statusNode.className = "status-pill done";
      dishNode.textContent = "工位已暂停";
      metaNode.textContent = "当前不再接收新任务，恢复后才能重新分配。";
      fillNode.style.width = "0%";
      if (actionButton) {
        actionButton.textContent = "恢复工位";
      }
      return;
    }

    node.classList.remove("unavailable");
    if (!task || task.status !== "cooking") {
      node.classList.remove("active");
      statusNode.textContent = "空闲";
      statusNode.className = "status-pill";
      dishNode.textContent = "等待接单";
      metaNode.textContent = "当前没有菜在这个工位上";
      fillNode.style.width = "0%";
      if (actionButton) {
        actionButton.textContent = "停用工位";
      }
      return;
    }

    const progress = ((state.minute - task.start_minute) / Math.max(1, task.duration)) * 100;
    node.classList.add("active");
    statusNode.textContent = task.table_name;
    statusNode.className = "status-pill cooking";
    dishNode.textContent = task.name;
    metaNode.textContent = `${task.course_label} · ${task.chef_need} 位厨师 · 预计 ${formatClock(state.startTime, task.end_minute)} 出菜`;
    fillNode.style.width = `${Math.max(6, Math.min(100, progress))}%`;
    if (actionButton) {
      actionButton.textContent = "停用工位";
    }
  });
}

function updateRoom() {
  state.tables.forEach((table) => {
    if (table.archived) return;
    const node = state.roomRefs.get(table.table_id);
    if (!node) return;
    const countNode = node.querySelector('[data-role="count"]');
    const platesNode = node.querySelector('[data-role="plates"]');
    const noteNode = node.querySelector('[data-role="note"]');
    const servedListNode = node.querySelector('[data-role="served-list"]');
    const cookingListNode = node.querySelector('[data-role="cooking-list"]');
    const rushButton = node.querySelector('[data-action="rush"]');
    const addDishButton = node.querySelector('[data-action="add-dish"]');
    const refireButton = node.querySelector('[data-action="refire"]');
    const archiveButton = node.querySelector('[data-action="archive"]');
    const plateNodes = [...platesNode.querySelectorAll(".plate")];

    countNode.textContent = `${table.served_count}/${table.courses_total}`;
    const cookingCourses = table.courses.filter((course) => course.status === "cooking");
    const servedCourses = table.courses.filter((course) => course.status === "served");
    const cookingIndexes = new Set(cookingCourses.map((course) => course.dish_index));
    plateNodes.forEach((plateNode, index) => {
      let nextClass = "plate waiting";
      if (index < table.served_count) nextClass = "plate served";
      else if (cookingIndexes.has(index)) nextClass = "plate cooking";
      if (plateNode.className !== nextClass) {
        plateNode.className = nextClass;
      }
    });

    const servedSignature = servedCourses.map((course) => course.name).join("|");
    if (servedListNode.dataset.signature !== servedSignature) {
      servedListNode.dataset.signature = servedSignature;
      servedListNode.innerHTML = servedCourses.length
        ? servedCourses
            .slice(-4)
            .map((course) => `<span class="room-course-chip served">${course.name}</span>`)
            .join("")
        : `<span class="room-course-chip muted">尚未上菜</span>`;
    }

    const cookingSignature = cookingCourses.map((course) => course.name).join("|");
    if (cookingListNode.dataset.signature !== cookingSignature) {
      cookingListNode.dataset.signature = cookingSignature;
      cookingListNode.innerHTML = cookingCourses.length
        ? cookingCourses
            .map((course) => `<span class="room-course-chip cooking">${course.name}</span>`)
            .join("")
        : `<span class="room-course-chip muted">暂时没有</span>`;
    }

    if (table.completed) {
      node.classList.add("done");
      noteNode.textContent = "这一桌已经完整出齐，等待确认离场";
    } else {
      node.classList.remove("done");
      if (table.running_count > 0) {
        noteNode.textContent = "这一桌正在连续出餐";
      } else {
        const waitAnchor = table.last_served_at ?? table.arrival_minute;
        const waitMinutes = Math.max(0, state.minute - waitAnchor);
        noteNode.textContent = table.served_count === 0 ? `已等待 ${waitMinutes} 分钟，首道待出` : `距上一道已过 ${waitMinutes} 分钟`;
      }
    }

    if (rushButton) {
      rushButton.textContent = table.priority_boost > 0 ? "催菜已标记" : "催菜优先";
      rushButton.disabled = table.completed;
    }
    if (addDishButton) {
      addDishButton.disabled = table.archived;
    }
    if (refireButton) {
      refireButton.disabled = servedCourses.length === 0 || table.archived;
    }
    if (archiveButton) {
      archiveButton.disabled = !table.completed;
      archiveButton.textContent = table.completed ? "确认离场" : "完成后离场";
    }
  });
}

function updateTables() {
  state.tables.forEach((table) => {
    if (table.archived) return;
    const node = state.tableRefs.get(table.table_id);
    if (!node) return;

    const statusNode = node.querySelector('[data-role="status"]');
    const summaryNode = node.querySelector('[data-role="summary"]');
    const progressNode = node.querySelector('[data-role="progress"]');
    const dishes = [...node.querySelectorAll(".dish-chip")];

    progressNode.style.width = `${(table.served_count / table.courses_total) * 100}%`;

    if (table.completed) {
      statusNode.textContent = "待离场";
      statusNode.className = "status-pill done";
      summaryNode.textContent = `本桌已全部出齐，共 ${table.courses_total} 道菜，等待人工确认离场`;
    } else if (table.running_count > 0) {
      statusNode.textContent = "出餐中";
      statusNode.className = "status-pill cooking";
      const cookingNames = table.courses.filter((course) => course.status === "cooking").map((course) => course.name);
      summaryNode.textContent = `当前正在处理：${cookingNames.join("、")}`;
    } else {
      statusNode.textContent = table.served_count === 0 ? "等待首道" : "等待下一道";
      statusNode.className = "status-pill waiting";
      const waitAnchor = table.last_served_at ?? table.arrival_minute;
      summaryNode.textContent = `距离上一道已过 ${Math.max(0, state.minute - waitAnchor)} 分钟，当前已上 ${table.served_count}/${table.courses_total} 道`;
    }

    dishes.forEach((dishNode) => {
      const task = findTask(dishNode.dataset.taskId);
      dishNode.classList.remove("queued", "cooking", "served");
      dishNode.classList.add(task.status);
    });
  });
}

function updateBoard() {
  clockNode.textContent = formatClock(state.startTime, state.minute);
  updateChefLiveBadge();
  renderMetrics();
  updateStations();
  updateRoom();
  renderCompletedRecords();
  updateTables();
  renderEvents();
}

async function fetchOrder(payload) {
  const response = await fetch("/api/kitchen-order", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("新桌菜单生成失败，请稍后重试。");
  }

  return response.json();
}

async function fetchExtraDish(payload) {
  const response = await fetch("/api/kitchen-extra-dish", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("追加菜品失败，请稍后重试。");
  }

  return response.json();
}

function normalizeIncomingOrder(order) {
  return {
    ...order,
    courses_total: order.courses.length,
    served_count: 0,
    running_count: 0,
    last_served_at: null,
    first_served_at: null,
    completed_at: null,
    served_times: [],
    completed: false,
    archived: false,
    archived_at: null,
    priority_boost: 0,
    courses: order.courses.map((course, index) => ({
      ...course,
      dish_index: index,
      status: "queued",
      arrival_minute: order.arrival_minute,
      table_id: order.table_id,
      table_name: order.table_name,
      start_minute: null,
      end_minute: null,
      slot_id: null,
      priority_boost: 0,
    })),
  };
}

function markTableRush(tableId) {
  const table = state.tables.find((item) => item.table_id === tableId);
  if (!table || table.archived || table.completed) return;
  table.priority_boost = 24;
  updateBoard();
}

function refireLastServedDish(tableId) {
  const table = state.tables.find((item) => item.table_id === tableId);
  if (!table || table.archived) return;

  const lastServedDish = table.courses
    .filter((course) => course.status === "served" && typeof course.end_minute === "number")
    .sort((left, right) => right.end_minute - left.end_minute)[0];

  if (!lastServedDish) return;

  requeueTask(lastServedDish, {
    delayMinutes: 1,
    priorityBoost: 26,
    tableBoost: 18,
  });
  scheduleForMinute();
  updateBoard();
}

function toggleSlotAvailability(slotId) {
  const slot = findSlotById(slotId);
  if (!slot) return;

  if (slot.disabled) {
    slot.disabled = false;
    slot.busyUntil = state.minute;
    scheduleForMinute();
    updateBoard();
    return;
  }

  const task = slot.currentTaskId ? findTask(slot.currentTaskId) : null;
  if (task && task.status === "cooking") {
    requeueTask(task, {
      delayMinutes: 2,
      priorityBoost: 18,
      tableBoost: 10,
    });
  }
  slot.disabled = true;
  slot.currentTaskId = null;
  slot.busyUntil = state.minute;
  updateBoard();
}

function adjustChefCount(delta) {
  if (!state.config) return;
  const nextChefCount = Math.max(1, Math.min(10, state.config.chefs + delta));
  if (nextChefCount === state.config.chefs) return;
  state.config.chefs = nextChefCount;
  const chefInput = form.querySelector('input[name="chefs"]');
  if (chefInput) {
    chefInput.value = String(nextChefCount);
  }
  scheduleForMinute();
  updateBoard();
}

function archiveTable(tableId) {
  const table = state.tables.find((item) => item.table_id === tableId);
  if (!table || !table.completed || table.archived) return;
  table.archived = true;
  table.archived_at = state.minute;
  renderRoom();
  renderCompletedRecords();
  renderTables();
  updateBoard();
}

async function addDishToTable(tableId) {
  const table = state.tables.find((item) => item.table_id === tableId);
  if (!table || table.archived) return;

  loadingNode.classList.remove("hidden");
  try {
    const dish = await fetchExtraDish({
      table_id: table.table_id,
      table_name: table.table_name,
      arrival_minute: state.minute,
      dish_index: table.courses.length,
      existing_dishes: table.courses.map((course) => course.name),
      existing_course_meta: table.courses.map((course) => ({ course: course.course })),
      request_profile: table.request_profile,
    });

    table.completed = false;
    table.completed_at = null;
    table.archived = false;
    table.priority_boost = 16;
    const normalizedDish = {
      ...dish,
      start_minute: null,
      end_minute: null,
      slot_id: null,
      priority_boost: 10,
    };
    table.courses.push(normalizedDish);
    table.courses_total += 1;
    state.tasks.push(normalizedDish);
    ensureTableVisuals();
    scheduleForMinute();
    updateBoard();
  } catch (error) {
    console.error(error);
  } finally {
    loadingNode.classList.add("hidden");
  }
}

async function addRandomOrder() {
  loadingNode.classList.remove("hidden");
  addOrderButton.disabled = true;

  try {
    const order = await fetchOrder({
      table_number: state.nextTableNumber,
      arrival_minute: state.minute,
      seed_hint: `${state.nextTableNumber}-${state.minute}`,
    });
    const normalized = normalizeIncomingOrder(order);
    state.tables.push(normalized);
    state.tasks.push(...normalized.courses);
    state.nextTableNumber += 1;
    ensureTableVisuals();
    scheduleForMinute();
    updateBoard();
  } catch (error) {
    console.error(error);
  } finally {
    loadingNode.classList.add("hidden");
    addOrderButton.disabled = false;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  resetKitchen();
});

playToggleButton.addEventListener("click", () => {
  setPlaybackState(!state.playing);
});

speedSelect.addEventListener("change", () => {
  state.intervalMs = Number(speedSelect.value);
  if (state.playing) {
    startClock();
  }
});

addOrderButton.addEventListener("click", async () => {
  await addRandomOrder();
});

resetKitchenButton.addEventListener("click", () => {
  resetKitchen();
});

chefMinusButton?.addEventListener("click", () => {
  adjustChefCount(-1);
});

chefPlusButton?.addEventListener("click", () => {
  adjustChefCount(1);
});

resetKitchen();
