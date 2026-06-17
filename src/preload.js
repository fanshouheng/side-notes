"use strict";

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("sideNotes", {
  getNote: (id) => ipcRenderer.invoke("note:get", id),
  updateNote: (note) => ipcRenderer.invoke("note:update", note),
  toggle: () => ipcRenderer.invoke("note:toggle"),
  resizeBy: (deltaY) => ipcRenderer.invoke("note:resize-by", deltaY),
});
