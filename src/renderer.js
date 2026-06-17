"use strict";

const params = new URLSearchParams(window.location.search);
const noteId = params.get("id");

let note;
let editingId = null;
let activeView = "todo";

const dockTab = document.getElementById("dockTab");
const titleInput = document.getElementById("titleInput");
const opacityInput = document.getElementById("opacityInput");
const todoTab = document.getElementById("todoTab");
const doneTab = document.getElementById("doneTab");
const todoView = document.getElementById("todoView");
const doneView = document.getElementById("doneView");
const todoList = document.getElementById("todoList");
const doneList = document.getElementById("doneList");
const addArea = document.getElementById("addArea");
const resizeEdge = document.querySelector(".resize-edge");

function uid() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function save() {
  return window.sideNotes.updateNote(note);
}

function render() {
  titleInput.value = note.title;
  opacityInput.value = note.backgroundOpacity;
  document.documentElement.style.setProperty("--note-bg-opacity", note.backgroundOpacity);
  dockTab.textContent = note.title;
  todoTab.classList.toggle("active", activeView === "todo");
  doneTab.classList.toggle("active", activeView === "done");
  todoView.classList.toggle("active", activeView === "todo");
  doneView.classList.toggle("active", activeView === "done");
  renderTodos();
  renderDone();
}

function renderTodos() {
  todoList.innerHTML = "";
  note.todos.forEach((todo, index) => {
    const row = document.createElement("div");
    row.className = "todo";

    if (editingId === todo.id) {
      const input = document.createElement("input");
      input.className = "todo-input";
      input.value = todo.content;
      input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") commitEdit(todo, input.value);
        if (event.key === "Escape") {
          editingId = null;
          render();
        }
      });
      input.addEventListener("blur", () => commitEdit(todo, input.value));
      row.append(input);
      requestAnimationFrame(() => input.focus());
    } else {
      const text = document.createElement("div");
      text.className = "todo-text";
      text.textContent = `${index + 1}. ${todo.content}`;
      text.addEventListener("click", () => {
        editingId = todo.id;
        render();
      });
      text.addEventListener("dblclick", () => completeTodo(todo.id));
      row.append(text);
    }

    const remove = document.createElement("button");
    remove.className = "action";
    remove.type = "button";
    remove.textContent = "x";
    remove.addEventListener("click", () => removeTodo(todo.id));
    row.append(remove);

    todoList.append(row);
  });
}

function renderDone() {
  doneList.innerHTML = "";
  note.done.forEach((done, index) => {
    const row = document.createElement("div");
    row.className = "done";
    const text = document.createElement("div");
    text.className = "done-text";
    text.textContent = `${index + 1}. ${done.content}`;
    row.append(text);

    const restore = document.createElement("button");
    restore.className = "action";
    restore.type = "button";
    restore.textContent = "<";
    restore.addEventListener("click", () => restoreDone(done.id));
    row.append(restore);

    const remove = document.createElement("button");
    remove.className = "action";
    remove.type = "button";
    remove.textContent = "x";
    remove.addEventListener("click", () => removeDone(done.id));
    row.append(remove);
    doneList.append(row);
  });
}

function addTodo() {
  const todo = { id: uid(), content: "" };
  note.todos.push(todo);
  editingId = todo.id;
  render();
}

function commitEdit(todo, value) {
  todo.content = value.trim();
  note.todos = note.todos.filter((item) => item.content);
  editingId = null;
  save();
  render();
}

function completeTodo(id) {
  const todo = note.todos.find((item) => item.id === id);
  if (!todo) return;
  note.todos = note.todos.filter((item) => item.id !== id);
  note.done.unshift({ ...todo, doneAt: Date.now() });
  save();
  render();
}

function removeTodo(id) {
  note.todos = note.todos.filter((item) => item.id !== id);
  save();
  render();
}

function restoreDone(id) {
  const done = note.done.find((item) => item.id === id);
  if (!done) return;
  note.done = note.done.filter((item) => item.id !== id);
  note.todos.push({ id: done.id, content: done.content });
  save();
  render();
}

function removeDone(id) {
  note.done = note.done.filter((item) => item.id !== id);
  save();
  render();
}

dockTab.addEventListener("click", () => window.sideNotes.toggle());
addArea.addEventListener("click", addTodo);
todoTab.addEventListener("click", () => {
  activeView = "todo";
  render();
});
doneTab.addEventListener("click", () => {
  activeView = "done";
  render();
});
titleInput.addEventListener("change", () => {
  note.title = titleInput.value.trim() || note.title;
  save();
  render();
});
titleInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") titleInput.blur();
});

opacityInput.addEventListener("input", () => {
  note.backgroundOpacity = Number(opacityInput.value);
  document.documentElement.style.setProperty("--note-bg-opacity", note.backgroundOpacity);
  save();
});

resizeEdge.addEventListener("mousedown", (event) => {
  event.preventDefault();
  let lastY = event.screenY;

  function onMove(moveEvent) {
    const deltaY = moveEvent.screenY - lastY;
    lastY = moveEvent.screenY;
    window.sideNotes.resizeBy(deltaY);
  }

  function onUp() {
    window.removeEventListener("mousemove", onMove);
    window.removeEventListener("mouseup", onUp);
  }

  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", onUp);
});

window.sideNotes.getNote(noteId).then((loaded) => {
  note = loaded;
  render();
});
