# Paper Offline Reader · 论文手机离线精读

[简体中文](README.md) · [English](README.en.md)

把论文 PDF 整理成一个适合手机阅读、可以离线带走的 HTML 文件。

这是一个 Codex skill：由 agent 阅读论文、撰写中文精读并选择原图，再由本地脚本完成排版、图片内嵌和基础校验。脚本本身不调用模型，不负责自动摘要或翻译。

## 阅读效果

- **中文精读**：研究问题、数据与方法、核心公式、主要结果、适用边界和引用信息。
- **原图解读**：保留原始图表，多分面图可分开排列，手机上纵向阅读，点按放大。
- **原文核对**：可将 PDF 的全部页面嵌入，按页展开查看，包括公式和参考文献。
- **手机阅读设置**：章节目录、字号调整、夜间模式、阅读进度条。
- **真正的单文件交付**：CSS、JavaScript 和图片均内嵌，不依赖 CDN、远程字体或阅读服务器。外部引用链接仍需联网。

中文精读默认是结构化导读，不是逐句翻译；完整原文以页图保存，不宣称英文全文已经重排或可以搜索。

## 安装到 Codex

下载此仓库并解压，将包含 `SKILL.md` 的目录命名为 `paper-offline-reader`，放入个人技能目录：

- Windows：`%USERPROFILE%\.codex\skills\paper-offline-reader`
- macOS / Linux：`~/.codex/skills/paper-offline-reader`
- 设置了 `CODEX_HOME` 时：`$CODEX_HOME/skills/paper-offline-reader`

最终应能找到 `paper-offline-reader/SKILL.md`。让 Codex 重新加载技能列表后即可调用。

## 使用

提供论文 PDF，然后向 Codex 发送：

```text
使用 $paper-offline-reader，把这篇论文整理成适合手机阅读的单文件离线网页。
保留中文精读、关键原图和完整原文。
```

也可以提供可访问的全文链接。若网站无法读取全文，技能会说明缺口并请求 PDF，不用摘要冒充全文。

得到 HTML 后，将这个文件保存到手机，用支持本地 HTML 的浏览器打开。手机文件预览器对脚本的支持不同；不支持交互的预览器中，正文及原生折叠内容仍可阅读，完整交互需要浏览器支持。

## 独立使用构建脚本

需要 Python，以及 PyMuPDF、Pillow。若 Codex 环境已提供这些依赖，可直接使用该环境。

```sh
python -m pip install -r requirements.txt
```

本仓库提供了一个**纯文字演示配置**，用于试跑版式，不包含真实论文的研究结论：

```sh
python scripts/build_reader.py --content examples/content.json --no-original --output output/demo.html
```

要制作真实论文阅读页，先按 [内容配置说明](references/content-spec.md) 撰写对应论文的 JSON，再执行：

```sh
python scripts/build_reader.py --content content.json --pdf article.pdf --output output/paper.html
```

脚本会验证图像、页码、裁切坐标、内部链接和外部运行资源。发布或交付前，还应人工核对原文事实，并在手机宽度下检查图表与交互。这些自动检查不等于真实手机断网测试。

已在 Python 3.12 环境进行构建验证；所用依赖版本见下方 `requirements.txt` 的说明。

## 文件结构

```text
paper-offline-reader/
├── SKILL.md                    # 技能入口与工作流程
├── agents/openai.yaml          # Codex 技能名称与默认调用示例
├── assets/reader.html          # 可复用阅读页模板
├── scripts/build_reader.py     # 本地单文件构建器
├── references/content-spec.md  # 内容配置与图表裁切说明
├── examples/content.json       # 无论文内容的演示配置
├── README.en.md                # English documentation
└── requirements.txt            # Python 依赖
```

## 内容与隐私

仓库仅包含技能、通用模板、构建器和演示配置，不包含用户的论文 PDF、阅读成品或本地文件路径。构建器在本地运行，不上传论文；在 Codex 中读取论文时，仍受所使用产品的数据处理规则约束。

生成阅读页时应保留原作者和出处。分享包含完整论文或图表的成品前，应确认相应材料的使用与分发权限。技能默认交付个人离线文件，不会自动公开发布或托管阅读页。
