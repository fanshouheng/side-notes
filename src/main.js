"use strict";

const { app, BrowserWindow, Menu, Tray, ipcMain, screen, nativeImage, shell } = require("electron");
const fs = require("fs");
const path = require("path");

const NOTE_COUNT = 3;
const WINDOW_WIDTH = 320;
const DEFAULT_HEIGHT = 150;
const DEFAULT_BACKGROUND_OPACITY = 0.6;
const COLLAPSED_WIDTH = 24;
const GAP = 10;
const TOP = 30;
const MIN_HEIGHT = 72;
const ICON_PATH = path.join(__dirname, "..", "assets", "icon.png");
const TRAY_ICON_PATH = path.join(__dirname, "..", "assets", "tray.png");
const GITHUB_URL = "https://github.com/fanshouheng/side-notes";
const GITHUB_ISSUE_URL = `${GITHUB_URL}/issues/new`;

let tray = null;
let notes = [];
let settings = { desktopMode: false };
let storePath = "";
let isPositioning = false;

function makeDefaultNote(index) {
  return {
    id: `note-${index + 1}`,
    title: `便签 ${index + 1}`,
    height: DEFAULT_HEIGHT,
    backgroundOpacity: DEFAULT_BACKGROUND_OPACITY,
    collapsed: false,
    todos: [],
    done: [],
  };
}

function clampBackgroundOpacity(value) {
  const opacity = Number(value);
  if (!Number.isFinite(opacity)) return DEFAULT_BACKGROUND_OPACITY;
  return Math.min(Math.max(opacity, 0.2), 0.9);
}

function sanitizeNote(note, index) {
  const fallback = makeDefaultNote(index);
  return {
    ...fallback,
    ...note,
    id: fallback.id,
    title: typeof note.title === "string" && note.title.trim() ? note.title : fallback.title,
    height: Math.max(Number(note.height) || DEFAULT_HEIGHT, MIN_HEIGHT),
    backgroundOpacity: clampBackgroundOpacity(note.backgroundOpacity),
    collapsed: Boolean(note.collapsed),
    todos: Array.isArray(note.todos) ? note.todos : [],
    done: Array.isArray(note.done) ? note.done : [],
  };
}

function loadStore() {
  storePath = path.join(app.getPath("userData"), "notes.json");
  let stored = {};

  try {
    stored = JSON.parse(fs.readFileSync(storePath, "utf8"));
  } catch {
    stored = {};
  }

  const groups = Array.isArray(stored.groups) ? stored.groups : [];
  settings = {
    desktopMode: Boolean(stored.settings && stored.settings.desktopMode),
  };
  notes = Array.from({ length: NOTE_COUNT }, (_, index) => sanitizeNote(groups[index] || {}, index));
}

function saveStore() {
  const groups = notes.map(({ window, ...note }) => note);
  fs.mkdirSync(path.dirname(storePath), { recursive: true });
  fs.writeFileSync(storePath, JSON.stringify({ settings, groups }, null, 2), "utf8");
}

function publicNote(note) {
  const { window, ...data } = note;
  return data;
}

function getWorkArea() {
  const point = screen.getCursorScreenPoint();
  return screen.getDisplayNearestPoint(point).workArea;
}

function positionWindows() {
  if (isPositioning) return;
  isPositioning = true;

  const workArea = getWorkArea();
  let y = workArea.y + TOP;

  for (const note of notes) {
    if (note.window && !note.window.isDestroyed()) {
      const visibleWidth = note.collapsed ? COLLAPSED_WIDTH : WINDOW_WIDTH;
      const x = workArea.x + workArea.width - visibleWidth;
      note.window.setBounds({
        x,
        y,
        width: visibleWidth,
        height: Math.max(note.height, MIN_HEIGHT),
      });
    }
    y += Math.max(note.height, MIN_HEIGHT) + GAP;
  }

  isPositioning = false;
}

function applyDesktopMode() {
  for (const note of notes) {
    if (!note.window || note.window.isDestroyed()) continue;
    note.window.setAlwaysOnTop(!settings.desktopMode);
  }
}

function createNoteWindow(note) {
  const win = new BrowserWindow({
    width: WINDOW_WIDTH,
    height: Math.max(note.height, MIN_HEIGHT),
    minWidth: COLLAPSED_WIDTH,
    minHeight: MIN_HEIGHT,
    frame: false,
    transparent: true,
    resizable: true,
    alwaysOnTop: !settings.desktopMode,
    skipTaskbar: true,
    title: note.title,
    icon: ICON_PATH,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  note.window = win;
  win.loadFile(path.join(__dirname, "index.html"), { query: { id: note.id } });

  win.on("resize", () => {
    if (isPositioning) return;
    if (note.collapsed) return;
    const [, height] = win.getSize();
    note.height = Math.max(height, MIN_HEIGHT);
    saveStore();
    positionWindows();
  });

  win.on("move", () => {
    if (!isPositioning) positionWindows();
  });
}

function findNoteByWindow(webContents) {
  return notes.find((note) => note.window && note.window.webContents === webContents);
}

function setAllVisible(visible) {
  for (const note of notes) {
    if (!note.window || note.window.isDestroyed()) continue;
    if (visible) note.window.show();
    else note.window.hide();
  }
  if (visible) positionWindows();
}

function setAllCollapsed(collapsed) {
  for (const note of notes) {
    note.collapsed = collapsed;
  }
  saveStore();
  positionWindows();
}

function setDesktopMode(desktopMode) {
  settings.desktopMode = desktopMode;
  applyDesktopMode();
  if (desktopMode) setAllVisible(true);
  saveStore();
  updateTrayMenu();
}

function openExternalUrl(url) {
  shell.openExternal(url).catch((error) => console.error(`Failed to open ${url}`, error));
}

function updateTrayMenu() {
  if (!tray) return;
  const loginSettings = app.getLoginItemSettings();

  tray.setContextMenu(
    Menu.buildFromTemplate([
      { label: "显示全部便签", click: () => setAllVisible(true) },
      { label: "隐藏全部便签", click: () => setAllVisible(false) },
      { label: "全部展开", click: () => setAllCollapsed(false) },
      { label: "全部缩进", click: () => setAllCollapsed(true) },
      {
        label: "只显示在桌面",
        type: "checkbox",
        checked: settings.desktopMode,
        click: (menuItem) => setDesktopMode(menuItem.checked),
      },
      { type: "separator" },
      { label: "关于", click: () => openExternalUrl(GITHUB_URL) },
      { label: "问题反馈", click: () => openExternalUrl(GITHUB_ISSUE_URL) },
      { type: "separator" },
      {
        label: "开机启动",
        type: "checkbox",
        checked: loginSettings.openAtLogin,
        click: (menuItem) => {
          app.setLoginItemSettings({ openAtLogin: menuItem.checked });
          updateTrayMenu();
        },
      },
      { type: "separator" },
      { label: "退出", click: () => app.quit() },
    ])
  );
}

function createTray() {
  const icon = nativeImage.createFromPath(TRAY_ICON_PATH);
  tray = new Tray(icon);
  tray.setToolTip("右侧便签");
  tray.on("click", () => setAllVisible(true));
  updateTrayMenu();
}

function registerIpc() {
  ipcMain.handle("note:get", (_event, id) => {
    const note = notes.find((item) => item.id === id);
    return note ? publicNote(note) : null;
  });

  ipcMain.handle("note:update", (event, payload) => {
    const note = notes.find((item) => item.id === payload.id);
    if (!note) return null;

    note.title = typeof payload.title === "string" && payload.title.trim() ? payload.title.trim() : note.title;
    note.backgroundOpacity = clampBackgroundOpacity(payload.backgroundOpacity);
    note.todos = Array.isArray(payload.todos) ? payload.todos : note.todos;
    note.done = Array.isArray(payload.done) ? payload.done : note.done;

    const sourceNote = findNoteByWindow(event.sender);
    if (sourceNote && sourceNote.window) sourceNote.window.setTitle(note.title);

    saveStore();
    positionWindows();
    return publicNote(note);
  });

  ipcMain.handle("note:toggle", (event) => {
    const note = findNoteByWindow(event.sender);
    if (!note) return null;

    note.collapsed = !note.collapsed;
    saveStore();
    positionWindows();
    return publicNote(note);
  });

  ipcMain.handle("note:resize-by", (event, deltaY) => {
    const note = findNoteByWindow(event.sender);
    if (!note || !note.window || note.window.isDestroyed()) return null;

    note.collapsed = false;
    note.height = Math.max(note.height + Number(deltaY || 0), MIN_HEIGHT);
    saveStore();
    positionWindows();
    return publicNote(note);
  });
}

app.whenReady().then(() => {
  Menu.setApplicationMenu(null);
  loadStore();
  registerIpc();
  notes.forEach(createNoteWindow);
  createTray();
  positionWindows();

  screen.on("display-metrics-changed", positionWindows);
  screen.on("display-added", positionWindows);
  screen.on("display-removed", positionWindows);
});

app.on("window-all-closed", (event) => {
  event.preventDefault();
});
