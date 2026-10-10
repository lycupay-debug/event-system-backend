const fs = require("node:fs");
const path = require("node:path");

const source = path.resolve(__dirname, "../nodes/LarkBitable/larkBitable.svg");
const destination = path.resolve(__dirname, "../dist/nodes/LarkBitable/larkBitable.svg");
fs.mkdirSync(path.dirname(destination), { recursive: true });
fs.copyFileSync(source, destination);
