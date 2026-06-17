"use strict";

const { app, BrowserWindow, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");

const outputDir = path.join(__dirname, "..", "assets", "promo");
const outputPath = path.join(outputDir, "real-screenshot.png");

const demoNote = {
  id: "note-1",
  title: "Today",
  height: 230,
  collapsed: false,
  todos: [
    { id: "todo-1", content: "Review launch checklist" },
    { id: "todo-2", content: "Capture real product screenshot" },
    { id: "todo-3", content: "Polish README hero image" },
    { id: "todo-4", content: "Keep notes docked beside the workspace" },
  ],
  done: [{ id: "done-1", content: "Create app icon", doneAt: Date.now() }],
};

app.whenReady().then(async () => {
  fs.mkdirSync(outputDir, { recursive: true });

  ipcMain.handle("note:get", () => demoNote);
  ipcMain.handle("note:update", (_event, note) => note);
  ipcMain.handle("note:toggle", () => demoNote);
  ipcMain.handle("note:resize-by", () => demoNote);

  const win = new BrowserWindow({
    width: 320,
    height: 230,
    show: false,
    frame: false,
    transparent: true,
    webPreferences: {
      preload: path.join(__dirname, "..", "src", "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  await win.loadFile(path.join(__dirname, "..", "src", "index.html"), { query: { id: demoNote.id } });
  await new Promise((resolve) => setTimeout(resolve, 500));

  const image = await win.capturePage();
  fs.writeFileSync(outputPath, image.toPNG());
  console.log(outputPath);
  app.quit();
});
