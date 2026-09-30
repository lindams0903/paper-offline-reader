# Paper Offline Reader

[简体中文](README.md) · [English](README.en.md)

Turn a research paper into a mobile-friendly, self-contained HTML file for offline reading.

This is a **Codex skill**. The agent reads the paper, writes a structured reading guide, and selects source figures. A local Python builder handles layout, image embedding, and basic validation. The builder does not call a model or automatically summarize or translate papers.

## What you get

- **A structured reading guide:** research questions, data and methods, key equations, results, limitations, and citation information. Chinese is the default; request another language when needed.
- **Source figures with explanations:** preserve original charts, optionally separate multi-panel figures for vertical reading, and tap to enlarge.
- **The complete source paper:** optionally embed every PDF page, including equations and references, as expandable page images.
- **Mobile reading controls:** a table of contents, font-size controls, dark mode, and a reading-progress indicator.
- **One offline file:** inline CSS, JavaScript, and images, with no CDN, remote fonts, or reading server required. External citation links still require internet access.

The guide is a structured explanation, not a sentence-by-sentence translation. Source PDF pages are embedded as images; the skill does not claim to provide searchable or reflowed English full text.

## Install in Codex

Download and extract this repository. Name the folder containing `SKILL.md` `paper-offline-reader`, then place it in your personal skills directory:

- Windows: `%USERPROFILE%\.codex\skills\paper-offline-reader`
- macOS / Linux: `~/.codex/skills/paper-offline-reader`
- If `CODEX_HOME` is configured: `$CODEX_HOME/skills/paper-offline-reader`

The resulting path should contain `paper-offline-reader/SKILL.md`. Reload the skills list in Codex before invoking it.

## Use the skill

Provide a paper PDF and ask Codex:

```text
Use $paper-offline-reader to turn this paper into a mobile-friendly,
single-file offline reading page. Include a Chinese reading guide,
key source figures, and the complete original paper.
```

To request an English reading guide, say so explicitly. The supplied interface and configuration example use Chinese; the agent can adapt the wording and template to your requested language.

You can also provide a link to accessible full text. If the full paper cannot be read, the skill should explain the missing source and request a PDF rather than substitute an abstract for the full paper.

Save the resulting HTML file on your phone and open it with a browser that supports local HTML files. File-preview apps vary in JavaScript support. The article body and native expandable sections remain available without script execution; interactive controls need browser support.

## Run the builder separately

The builder requires Python, PyMuPDF, and Pillow. An existing Codex environment that already provides these dependencies can be used directly.

```sh
python -m pip install -r requirements.txt
```

The repository includes a **text-only layout demonstration**, with no real research claims:

```sh
python scripts/build_reader.py --content examples/content.json --no-original --output output/demo.html
```

For a real paper, prepare a JSON manuscript following the [content configuration reference](references/content-spec.md) (currently in Chinese), then run:

```sh
python scripts/build_reader.py --content content.json --pdf article.pdf --output output/paper.html
```

The builder checks images, page numbers, crop coordinates, internal links, and external runtime resources. Before delivering a page, also verify its claims against the paper and inspect its layout and interactions at mobile widths. Automated checks do not constitute a real-device offline test.

The build has been verified with Python 3.12. Dependency versions used for verification are recorded in `requirements.txt`.

## Repository structure

```text
paper-offline-reader/
├── SKILL.md                    # Agent workflow and instructions
├── agents/openai.yaml          # Codex skill metadata and invocation example
├── assets/reader.html          # Reusable reading-page template
├── scripts/build_reader.py     # Local single-file builder
├── references/content-spec.md  # JSON schema and figure-crop guidance
├── examples/content.json       # Text-only demonstration
├── README.md                   # Chinese documentation
├── README.en.md                # English documentation
└── requirements.txt            # Python dependencies
```

## Content and privacy

This repository contains only the skill, generic template, builder, and demonstration configuration. It contains no user PDFs, generated paper readers, or personal local paths. The builder runs locally and does not upload papers. When an agent reads a paper in Codex, the product's applicable data-handling rules still apply.

Preserve original authorship and source information in generated readers. Before distributing a reader containing a complete paper or its figures, confirm the relevant rights to use and share those materials. The skill produces a personal offline file by default; it does not automatically publish or host the resulting reader.
