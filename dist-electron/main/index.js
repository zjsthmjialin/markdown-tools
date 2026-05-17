"use strict";
const electron = require("electron");
const path = require("path");
const child_process = require("child_process");
const http = require("http");
let pythonProcess = null;
function waitForPythonService(maxRetries = 30, interval = 1e3) {
  return new Promise((resolve) => {
    let retries = 0;
    const check = () => {
      http.get("http://127.0.0.1:8765/", (res) => {
        res.resume();
        resolve();
      }).on("error", () => {
        retries++;
        if (retries >= maxRetries) {
          console.error("[Python] Service failed to start after", maxRetries, "retries");
          resolve();
        } else {
          setTimeout(check, interval);
        }
      });
    };
    check();
  });
}
async function startPythonService() {
  var _a, _b;
  const isDev2 = process.env.NODE_ENV === "development";
  const resourcesPath = isDev2 ? path.join(__dirname, "../../src/python") : path.join(process.resourcesPath, "python");
  const pythonScript = path.join(resourcesPath, "main.py");
  console.log("[Python] Starting service...");
  console.log("[Python] Script path:", pythonScript);
  pythonProcess = child_process.spawn("python", [pythonScript], {
    stdio: ["pipe", "pipe", "pipe"],
    cwd: resourcesPath
  });
  (_a = pythonProcess.stdout) == null ? void 0 : _a.on("data", (data) => {
    console.log("[Python]", data.toString().trim());
  });
  (_b = pythonProcess.stderr) == null ? void 0 : _b.on("data", (data) => {
    console.error("[Python Error]", data.toString().trim());
  });
  pythonProcess.on("error", (err) => {
    console.error("Failed to start Python service:", err);
    pythonProcess = null;
  });
  pythonProcess.on("exit", (code) => {
    console.error("[Python] Process exited with code", code);
    pythonProcess = null;
  });
  await waitForPythonService();
  console.log("[Python] Service ready");
}
async function callPythonService(data) {
  return new Promise((resolve) => {
    let resolved = false;
    const postData = JSON.stringify(data);
    const options = {
      hostname: "127.0.0.1",
      port: 8765,
      path: "/",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(postData)
      }
    };
    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        req.destroy();
        resolve({ success: false, error: "请求超时" });
      }
    }, 3e5);
    const req = http.request(options, (res) => {
      let data2 = "";
      res.on("data", (chunk) => {
        data2 += chunk;
      });
      res.on("end", () => {
        if (!resolved) {
          resolved = true;
          clearTimeout(timeout);
          try {
            const result = JSON.parse(data2);
            resolve(result);
          } catch (e) {
            resolve({ success: false, error: "Invalid response from Python service" });
          }
        }
      });
    });
    req.on("error", (e) => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        resolve({ success: false, error: `连接Python服务失败: ${e.message}` });
      }
    });
    req.write(postData);
    req.end();
  });
}
function setupIpcHandlers() {
  electron.ipcMain.handle("select-directory", async () => {
    const result = await electron.dialog.showOpenDialog({
      properties: ["openDirectory"]
    });
    return result.filePaths[0] || null;
  });
  electron.ipcMain.handle("convert-file", async (_event, filePath, sourceFormat, targetFormat, outputDir) => {
    console.log(`Converting: ${filePath} (${sourceFormat} -> ${targetFormat})`);
    if (outputDir) console.log(`Output dir: ${outputDir}`);
    try {
      const result = await callPythonService({
        filePath,
        sourceFormat,
        targetFormat,
        outputDir
      });
      console.log(`Result: success=${result.success}, error=${result.error || "none"}`);
      return result;
    } catch (error) {
      console.error(`Convert error:`, error);
      return { success: false, error: String(error) };
    }
  });
}
function stopPythonService() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
    console.log("Python service stopped");
  }
}
let win = null;
const isDev = process.env.NODE_ENV === "development";
electron.app.whenReady().then(async () => {
  const primaryDisplay = electron.screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;
  win = new electron.BrowserWindow({
    width: 900,
    height: 700,
    minWidth: 700,
    minHeight: 500,
    x: Math.floor((width - 900) / 2),
    y: Math.floor((height - 700) / 2),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "../preload/preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  setupIpcHandlers();
  await startPythonService();
  if (isDev) {
    win.loadURL("http://localhost:5173");
    win.webContents.openDevTools();
    win.show();
  } else {
    win.loadFile(path.join(__dirname, "../../dist/index.html"));
  }
  win.webContents.on("did-finish-load", () => {
    win == null ? void 0 : win.show();
  });
  win.on("closed", () => {
    win = null;
  });
});
electron.app.on("window-all-closed", () => {
  stopPythonService();
  electron.app.quit();
});
electron.app.on("activate", () => {
  if (win === null) {
    electron.app.whenReady();
  }
});
