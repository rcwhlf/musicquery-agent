// 将 logo-icon.svg 栅格化为多种尺寸 PNG
const sharp = require("sharp");
const fs = require("fs");

const svg = fs.readFileSync("E:/musicquery-agent/logo/logo-icon.svg");
const out = "E:/musicquery-agent/logo";

(async () => {
  for (const size of [1024, 512, 256, 128]) {
    await sharp(svg, { density: 72 * (size / 512) * 2 })
      .resize(size, size)
      .png()
      .toFile(`${out}/logo-icon-${size}.png`);
  }
  console.log("ICONS_DONE");
})();
