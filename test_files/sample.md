# MarkAny HTML 转换测试

这是一份用于测试HTML转换功能的示例页面。包含标题、段落和列表。

## 功能特点

* 支持多种格式互转
* 保持原始排版格式
* 支持中英文混排

## 技术栈

1. Python 后端处理
2. Electron 桌面应用框架
3. Vue.js 前端界面

## 数据示例

| 格式 | 扩展名 | 支持状态 |
| --- | --- | --- |
| PDF | .pdf | 已支持 |
| Word | .docx | 已支持 |
| Excel | .xlsx | 已支持 |

## 代码示例

```
def convert(file_path, target_format):
    converter = get_converter(file_path)
    return converter.to_markdown(file_path, output_dir)
```

更多内容请参考[项目文档](https://example.com)。