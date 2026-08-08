/**
 * MarkAny Document Processing MCP Server
 *
 * 基于 Model Context Protocol 的文档处理服务
 * 支持 PDF 格式转换、页面调整、去水印、调清晰度、去底色等功能
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import {
  optimizeClarity,
  removeBackground,
  OptimizeClarityOptions,
  RemoveBackgroundOptions,
} from "./utils/image-processor.js";

// ============================================================
// 类型定义
// ============================================================

interface PdfConvertParams {
  inputPath: string;
  targetFormat: "md" | "txt" | "html";
  outputPath?: string;
}

interface PdfResizeParams {
  inputPath: string;
  width: number;
  height: number;
}

interface RemoveWatermarkParams {
  inputPath: string;
  region: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  outputPath?: string;
}

interface OptimizeClarityParams {
  inputPath: string;
  outputPath: string;
  dpi?: number;
}

interface RemoveBackgroundParams {
  inputPath: string;
  outputPath: string;
  threshold?: number;
}

// ============================================================
// 日志工具
// ============================================================

function log(level: "INFO" | "WARN" | "ERROR", message: string, data?: unknown): void {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] ${message}`;
  console.error(logMessage);
  if (data !== undefined) {
    console.error(JSON.stringify(data, null, 2));
  }
}

// ============================================================
// 工具定义
// ============================================================

const TOOLS: Tool[] = [
  {
    name: "pdf-convert",
    description: "将 PDF 文档转换为指定格式（Markdown、TXT、HTML）",
    inputSchema: {
      type: "object",
      properties: {
        inputPath: {
          type: "string",
          description: "输入 PDF 文件的完整路径",
        },
        targetFormat: {
          type: "string",
          enum: ["md", "txt", "html"],
          description: "目标转换格式",
        },
        outputPath: {
          type: "string",
          description: "输出文件路径（可选）",
        },
      },
      required: ["inputPath", "targetFormat"],
    },
  },
  {
    name: "pdf-resize",
    description: "调整 PDF 页面尺寸",
    inputSchema: {
      type: "object",
      properties: {
        inputPath: {
          type: "string",
          description: "输入 PDF 文件的完整路径",
        },
        width: {
          type: "number",
          description: "目标宽度",
        },
        height: {
          type: "number",
          description: "目标高度",
        },
      },
      required: ["inputPath", "width", "height"],
    },
  },
  {
    name: "remove-watermark",
    description: "去除 PDF 指定区域的水印或不需要的内容",
    inputSchema: {
      type: "object",
      properties: {
        inputPath: {
          type: "string",
          description: "输入 PDF 文件的完整路径",
        },
        region: {
          type: "object",
          description: "要去除的区域坐标",
          properties: {
            x: { type: "number", description: "左上角 X 坐标" },
            y: { type: "number", description: "左上角 Y 坐标" },
            width: { type: "number", description: "区域宽度" },
            height: { type: "number", description: "区域高度" },
          },
          required: ["x", "y", "width", "height"],
        },
        outputPath: {
          type: "string",
          description: "输出文件路径（可选）",
        },
      },
      required: ["inputPath", "region"],
    },
  },
  {
    name: "optimize-clarity",
    description: "调清晰度 - 自适应图像增强，提升扫描件文字清晰度（灰度 + 去噪 + CLAHE + 自适应二值化）",
    inputSchema: {
      type: "object",
      properties: {
        inputPath: {
          type: "string",
          description: "输入图像或 PDF 文件的完整路径",
        },
        outputPath: {
          type: "string",
          description: "输出图像文件路径",
        },
        dpi: {
          type: "number",
          description: "渲染 DPI (默认: 300)",
        },
      },
      required: ["inputPath", "outputPath"],
    },
  },
  {
    name: "remove-background",
    description: "去底色 - 去除文档背景颜色，自动检测并去除不均匀或带色的背景",
    inputSchema: {
      type: "object",
      properties: {
        inputPath: {
          type: "string",
          description: "输入图像或 PDF 文件的完整路径",
        },
        outputPath: {
          type: "string",
          description: "输出图像文件路径",
        },
        threshold: {
          type: "number",
          description: "背景检测阈值，0-255，越低越严格 (默认: 15)",
        },
      },
      required: ["inputPath", "outputPath"],
    },
  },
];

// ============================================================
// 工具处理器
// ============================================================

async function handlePdfConvert(params: PdfConvertParams): Promise<{ content: string }> {
  log("INFO", "执行 pdf-convert", params);

  try {
    const result = {
      status: "pending",
      message: `PDF 转换功能预留待实现: ${params.inputPath} -> ${params.targetFormat}`,
    };

    log("INFO", "pdf-convert 完成", result);
    return { content: JSON.stringify(result) };
  } catch (error) {
    log("ERROR", "pdf-convert 失败", error);
    throw new Error(`PDF 转换失败: ${error}`);
  }
}

async function handlePdfResize(params: PdfResizeParams): Promise<{ content: string }> {
  log("INFO", "执行 pdf-resize", params);

  try {
    const result = {
      status: "pending",
      message: `PDF 页面调整功能预留待实现: ${params.inputPath} -> ${params.width}x${params.height}`,
    };

    log("INFO", "pdf-resize 完成", result);
    return { content: JSON.stringify(result) };
  } catch (error) {
    log("ERROR", "pdf-resize 失败", error);
    throw new Error(`PDF 页面调整失败: ${error}`);
  }
}

async function handleRemoveWatermark(params: RemoveWatermarkParams): Promise<{ content: string }> {
  log("INFO", "执行 remove-watermark", params);

  try {
    const result = {
      status: "pending",
      message: `去水印功能预留待实现: ${params.inputPath} 区域 ${JSON.stringify(params.region)}`,
    };

    log("INFO", "remove-watermark 完成", result);
    return { content: JSON.stringify(result) };
  } catch (error) {
    log("ERROR", "remove-watermark 失败", error);
    throw new Error(`去水印失败: ${error}`);
  }
}

async function handleOptimizeClarity(params: OptimizeClarityParams): Promise<{ content: string }> {
  log("INFO", "执行 optimize-clarity", params);

  try {
    const options: OptimizeClarityOptions = {};
    if (params.dpi) {
      options.dpi = params.dpi;
    }

    const result = await optimizeClarity(params.inputPath, params.outputPath, options);

    log("INFO", "optimize-clarity 完成", result);
    return { content: JSON.stringify(result) };
  } catch (error) {
    log("ERROR", "optimize-clarity 失败", error);
    throw new Error(`调清晰度失败: ${error}`);
  }
}

async function handleRemoveBackground(params: RemoveBackgroundParams): Promise<{ content: string }> {
  log("INFO", "执行 remove-background", params);

  try {
    const options: RemoveBackgroundOptions = {};
    if (params.threshold !== undefined) {
      options.threshold = params.threshold;
    }

    const result = await removeBackground(params.inputPath, params.outputPath, options);

    log("INFO", "remove-background 完成", result);
    return { content: JSON.stringify(result) };
  } catch (error) {
    log("ERROR", "remove-background 失败", error);
    throw new Error(`去底色失败: ${error}`);
  }
}

// ============================================================
// MCP 服务器主类
// ============================================================

class MarkAnyServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: "markany-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
    log("INFO", "MarkAny MCP Server 初始化完成");
  }

  private setupHandlers(): void {
    // 处理工具列表请求
    this.server.setRequestHandler(ListToolsRequestSchema, () => {
      log("INFO", "收到工具列表请求");
      return { tools: TOOLS };
    });

    // 处理工具调用请求
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      log("INFO", `收到工具调用请求: ${name}`, args);

      try {
        switch (name) {
          case "pdf-convert":
            return await handlePdfConvert(args as unknown as PdfConvertParams);
          case "pdf-resize":
            return await handlePdfResize(args as unknown as PdfResizeParams);
          case "remove-watermark":
            return await handleRemoveWatermark(args as unknown as RemoveWatermarkParams);
          case "optimize-clarity":
            return await handleOptimizeClarity(args as unknown as OptimizeClarityParams);
          case "remove-background":
            return await handleRemoveBackground(args as unknown as RemoveBackgroundParams);
          default:
            throw new Error(`未知工具: ${name}`);
        }
      } catch (error) {
        log("ERROR", `工具调用失败: ${name}`, error);
        throw error;
      }
    });
  }

  async start(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    log("INFO", "MarkAny MCP Server 已连接到 stdio 传输层");
  }
}

// ============================================================
// 启动服务器
// ============================================================

const server = new MarkAnyServer();
server.start().catch((error) => {
  log("ERROR", "服务器启动失败", error);
  process.exit(1);
});