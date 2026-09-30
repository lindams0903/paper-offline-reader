# 内容配置与构建说明

`build_reader.py` 接受 UTF-8 JSON。全文理解、中文写作和原图选择由使用技能的 agent 完成，脚本负责渲染和内嵌。配置使用当前论文的事实，不复制之前示例中的论断。

## 命令

```text
python <skill>/scripts/build_reader.py --content content.json --pdf article.pdf --output output/论文_手机离线阅读.html
```

纯网页来源或明确不要原文页时传 `--no-original`。没有 PDF 时仍可生成纯文字页；需要图片的纯网页内容应先通过可用工具合法保存为本地图片文件，再使用 `path` 图源。缺失依赖时查看工作区自带运行环境；主要依赖为 PyMuPDF (`fitz`) 和 Pillow。

## 配置字段

```json
{
  "title": "适合阅读的中文题名",
  "original_title": "Original paper title",
  "authors": ["First Author", "Second Author"],
  "publication": "期刊、年份、卷期与文章号",
  "doi": "10.xxxx/example",
  "brand": "论文 · 离线精读",
  "eyebrow": "PAPER READER",
  "description": "本文的具体主题与导读范围",
  "lead_html": "一句话点明论文的主要贡献。",
  "scope_html": "依据完整论文整理的中文导读，非逐句译文。",
  "sections": [
    {
      "id": "findings",
      "title": "核心结果",
      "html": "<p>基于原文的结果说明。</p>{{figure:result}}<p class=\"loc\">见<a href=\"#page-2\">原文第 2 页</a>。</p>"
    }
  ],
  "figures": {
    "result": {
      "page": 2,
      "rect": [0.1, 0.1, 0.9, 0.45],
      "label": "图 1 · 原图标题",
      "caption": "说明横纵轴、图例与应关注的结果。"
    }
  },
  "page_labels": {"1": "题名与摘要", "2": "方法与结果"},
  "footer": "出处、原作者和许可标注；整理者的说明及整理日期。"
}
```

上例只说明配置形状，不是可用于论文的事实。`title`、`sections` 必填。DOI 可省略，若填写必须使用当前论文的真实 DOI。`sections` 必须有至少一个章节，ID 使用小写字母、数字和短横线，不能与页面控件 ID 重复。

`page` 是从 1 起算的 PDF 页码；`rect` 是相对该页可见尺寸的归一化裁切 `[left, top, right, bottom]`，各值在 0–1 内，省略则整页。先观察源页面，再确定裁切。不要套用前一篇 PDF 的坐标。`scale` 默认为 3，可调 1–4。

本地图片图源使用 `path` 替代 `page` 和 `rect`，相对路径相对于配置文件。PDF 图源与文件图源只能选一个。图片仍应来自本文或明确注明的来源；不得发明图表内容。

在 `html` 中写 `{{figure:KEY}}` 插入图；可用 `<div class="fig-grid">…</div>` 将多个原图分面组成桌面网格、手机单列。`fig-grid two` 为桌面两列。其余已有样式：

- `note`：必要的解释或限制；`loc`：原文定位；`small`：辅助文本。
- `formula`：公式容器，支持横向滚动；`table-wrap`：表格局部滚动；`table-wrap compact`：窄表格。
- `findings` 与 `finding`，内部 `key`：核心结论块。
- `glossary`：`dl` 术语表；`reference`：引用信息块。

`*_html` 和章节 `html` 是 agent 撰写的可信内容片段，禁止直接塞入未经检查的网页源代码。脚本拒绝活动嵌入、事件处理属性及外部运行资源；外部普通引用链接可以保留，但离线时不会打开。正文中不必加入多余功能或装饰。

## 输出与检查

默认输出包含全部 PDF 原文页和图表放大控件，原文锚点为 `#page-N`。`--no-original` 时不生成这些锚点，也不要在正文写指向它们的链接。

脚本发现无效页码、越界裁切、重复 ID、失效内部锚点、缺失图源或外部资源时失败，不覆盖已有输出。图片默认 WebP，字体为系统字体。样式与逻辑都内嵌，阅读偏好按文档隔离保存；本地存储不可用不影响阅读。

可在输出目录用现有的本地静态服务器预览。按技能要求检查真实交互与手机宽度，不使用截图伪装成经过验证的交互页面。
