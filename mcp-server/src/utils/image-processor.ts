/**
 * Image Processor - 图像处理模块
 *
 * 通过 child_process 调用 Python 脚本进行图像处理
 */

import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SCRIPTS_DIR = path.resolve(__dirname, "../../scripts");

// 日志工具
function log(level: "INFO" | "WARN" | "ERROR", message: string, data?: unknown): void {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] [image-processor] ${message}`;
  console.error(logMessage);
  if (data !== undefined) {
    console.error(JSON.stringify(data, null, 2));
  }
}

// 运行 Python 脚本的通用函数
function runPythonScript(
  scriptName: string,
  args: string[]
): Promise<{ status: string; [key: string]: unknown }> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(SCRIPTS_DIR, scriptName);
    log("INFO", `启动 Python 脚本: ${scriptPath}`, args);

    const process = spawn("python", [scriptPath, ...args], {
      cwd: SCRIPTS_DIR,
    });

    let stdout = "";
    let stderr = "";

    process.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    process.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    process.on("close", (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout.trim());
          log("INFO", `脚本执行成功: ${scriptName}`, result);
          resolve(result);
        } catch {
          // 如果输出不是 JSON，返回原始输出
          resolve({ status: "success", output: stdout.trim() });
        }
      } else {
        log("ERROR", `脚本执行失败: ${scriptName}`, { code, stderr });
        reject(new Error(`脚本执行失败 (code ${code}): ${stderr}`));
      }
    });

    process.on("error", (error) => {
      log("ERROR", `进程启动失败: ${scriptName}`, error);
      reject(error);
    });
  });
}

// ============================================================
// 图像处理函数
// ============================================================

export interface OptimizeClarityOptions {
  dpi?: number;
}

export async function optimizeClarity(
  inputPath: string,
  outputPath: string,
  options: OptimizeClarityOptions = {}
): Promise<{ status: string; input: string; output: string; dpi: number }> {
  log("INFO", "optimizeClarity 调用", { inputPath, outputPath, options });

  // 验证输入文件存在
  if (!fs.existsSync(inputPath)) {
    throw new Error(`输入文件不存在: ${inputPath}`);
  }

  // 确保输出目录存在
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const args = [inputPath, outputPath];
  if (options.dpi) {
    args.push("--dpi", options.dpi.toString());
  }

  const result = await runPythonScript("optimize-clarity.py", args) as {
    status: string;
    input: string;
    output: string;
    dpi?: number;
  };

  return {
    status: result.status,
    input: result.input || inputPath,
    output: result.output || outputPath,
    dpi: result.dpi || options.dpi || 300,
  };
}

export interface RemoveBackgroundOptions {
  threshold?: number;
}

export async function removeBackground(
  inputPath: string,
  outputPath: string,
  options: RemoveBackgroundOptions = {}
): Promise<{ status: string; input: string; output: string; threshold: number }> {
  log("INFO", "removeBackground 调用", { inputPath, outputPath, options });

  // 验证输入文件存在
  if (!fs.existsSync(inputPath)) {
    throw new Error(`输入文件不存在: ${inputPath}`);
  }

  // 确保输出目录存在
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const args = [inputPath, outputPath];
  if (options.threshold !== undefined) {
    args.push("--threshold", options.threshold.toString());
  }

  const result = await runPythonScript("remove-background.py", args) as {
    status: string;
    input: string;
    output: string;
    threshold?: number;
  };

  return {
    status: result.status,
    input: result.input || inputPath,
    output: result.output || outputPath,
    threshold: result.threshold || options.threshold || 15,
  };
}