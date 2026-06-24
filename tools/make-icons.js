const { app, nativeImage } = require("electron");
const fs = require("fs");
const path = require("path");

const iconSvg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round">
    <rect x="58" y="52" width="132" height="148" rx="12" stroke-width="14"/>
    <path d="M86 92h76" stroke-width="12"/>
    <path d="M86 124h76" stroke-width="12"/>
    <path d="M86 156h50" stroke-width="12"/>
    <path d="M156 180l42-42 20 20-42 42-28 8 8-28z" stroke-width="12"/>
    <path d="M192 144l20 20" stroke-width="10"/>
  </g>
</svg>`;

app.whenReady().then(() => {
  fs.mkdirSync("assets", { recursive: true });
  const image = nativeImage.createFromDataURL(
    `data:image/svg+xml;base64,${Buffer.from(iconSvg).toString("base64")}`
  );
  const png = image.toPNG();

  if (!png.length) {
    throw new Error("Failed to render icon SVG");
  }

  fs.writeFileSync(path.join("assets", "icon.png"), png);
  fs.writeFileSync(path.join("assets", "tray.png"), png);
  console.log("icons written");
  app.quit();
});
