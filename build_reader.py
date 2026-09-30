"""Build a self-contained paper reader from an agent-authored JSON manuscript."""
import argparse
import base64
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re

from PIL import Image


def esc(value):
    return html.escape(str(value), quote=True)


class Audit(HTMLParser):
    def __init__(self, fragment=False):
        super().__init__()
        self.fragment = fragment
        self.ids = []
        self.targets = []
        self.images = 0

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {'iframe', 'object', 'embed', 'base', 'form', 'audio', 'video', 'source'}:
            raise ValueError(f'Unsupported embedded/active content: {tag}')
        if self.fragment and tag in {'script', 'style', 'link', 'meta', 'html', 'body', 'head'}:
            raise ValueError(f'Unsupported manuscript element: {tag}')
        if any(k.startswith('on') or k in {'srcdoc', 'srcset', 'style'} for k in a) and self.fragment:
            raise ValueError('Manuscript must not contain event handlers, srcset, srcdoc or inline styles')
        if 'id' in a:
            self.ids.append(a['id'])
        href = a.get('href', '')
        if href.startswith('#'):
            self.targets.append(href[1:])
        if href and not href.startswith(('#', 'https://', 'http://', 'mailto:', 'data:image/')):
            raise ValueError(f'Unsupported link scheme: {href[:80]}')
        if tag == 'script' and 'src' in a:
            raise ValueError('External scripts are not allowed')
        if tag == 'link' and not href.startswith('data:image/'):
            raise ValueError('External linked resources are not allowed')
        if tag == 'meta' and 'http-equiv' in a:
            raise ValueError('HTTP-equiv metadata is not supported')
        if tag == 'img' and a.get('src'):
            src = a['src']
            if not src.startswith('data:image/webp;base64,'):
                raise ValueError('All images must be embedded WebP resources')
            Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1], validate=True))).verify()
            self.images += 1


def webp(image):
    image = image.convert('RGB')
    stream = io.BytesIO()
    image.save(stream, format='WEBP', quality=88, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(stream.getvalue()).decode('ascii'), image.size


def pdf_image(doc, number, rect=None, scale=2.25):
    if isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= len(doc):
        raise ValueError(f'Invalid PDF page: {number}')
    scale = float(scale)
    if not 1 <= scale <= 4:
        raise ValueError('Image scale must be between 1 and 4')
    import fitz
    page = doc[number - 1]
    clip = page.rect
    if rect is not None:
        if len(rect) != 4:
            raise ValueError('Crop rect must contain four normalized values')
        left, top, right, bottom = map(float, rect)
        if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
            raise ValueError(f'Invalid normalized crop: {rect}')
        clip = fitz.Rect(page.rect.x0 + left * page.rect.width,
                         page.rect.y0 + top * page.rect.height,
                         page.rect.x0 + right * page.rect.width,
                         page.rect.y0 + bottom * page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
    return webp(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))


def image_button(src, size, label):
    width, height = size
    return (f'<button class="image-open" aria-label="放大：{esc(label)}">'
            f'<img src="{src}" width="{width}" height="{height}" loading="lazy" '
            f'alt="{esc(label)}"></button>')


def build(config, config_dir, doc=None, include_original=True):
    if not config.get('title') or not config.get('sections'):
        raise ValueError('title and a nonempty sections array are required')
    include_original = bool(include_original and doc is not None)
    figures = config.get('figures', {})
    figure_cache = {}

    def render_figure(match):
        key = match.group(1)
        if key in figure_cache:
            return figure_cache[key]
        spec = figures[key]
        if ('path' in spec) == ('page' in spec):
            raise ValueError(f'Figure {key}: choose either path or page')
        if 'path' in spec:
            with Image.open(config_dir / spec['path']) as im:
                src, size = webp(im)
        else:
            if doc is None:
                raise ValueError(f'Figure {key} needs a PDF')
            src, size = pdf_image(doc, spec['page'], spec.get('rect'), spec.get('scale', 3))
        label = spec.get('label', key)
        caption = spec.get('caption', '')
        link = (f' <a href="#page-{spec["page"]}">原文第 {spec["page"]} 页</a>'
                if include_original and 'page' in spec else '')
        markup = (f'<figure>{image_button(src, size, label)}<figcaption><b>{esc(label)}</b> '
                  f'{esc(caption)}{link}</figcaption></figure>')
        figure_cache[key] = markup
        return markup

    def fragment(value):
        value = re.sub(r'\{\{figure:([A-Za-z0-9_-]+)\}\}', render_figure, str(value))
        audit = Audit(fragment=True)
        audit.feed(value)
        audit.close()
        return value

    metadata = []
    authors = config.get('authors', [])
    if authors:
        metadata.append(esc(' · '.join(authors)))
    if config.get('publication'):
        metadata.append(esc(config['publication']))
    if config.get('doi'):
        doi = config['doi']
        if not re.fullmatch(r'10\.[0-9]{4,9}/[^\s<>"\x00-\x1f]+', doi):
            raise ValueError('DOI must be an identifier such as 10.1234/article.1')
        from urllib.parse import quote
        metadata.append(f'DOI：<a href="https://doi.org/{quote(doi, safe="/().:;-")}">{esc(doi)}</a>')
    main = [f'<p class="eyebrow">{esc(config.get("eyebrow", "PAPER READER"))}</p>',
            f'<h1>{esc(config["title"])}</h1>']
    if config.get('original_title'):
        main.append(f'<p class="en-title">{esc(config["original_title"])}</p>')
    main.append('<p class="meta">' + '<br>'.join(metadata) + '</p>')
    tags = ['中文精读版', '单文件离线']
    if figures:
        tags.append('原图解读')
    if include_original:
        tags.append(f'完整 {len(doc)} 页原文')
    main.append('<div class="chips">' + ''.join(f'<span class="chip">{esc(t)}</span>' for t in tags) + '</div>')
    if config.get('lead_html'):
        main.append(f'<div class="lead">{fragment(config["lead_html"])}</div>')
    scope = config.get('scope_html', '中文内容为结构化导读，非逐句译文。外部引用链接需要联网，其余阅读内容均在本文件内。')
    main.append(f'<div class="small">{fragment(scope)}</div>')
    nav, sections = [], []
    for index, section in enumerate(config['sections'], 1):
        sid = section['id']
        if not re.fullmatch(r'[a-z][a-z0-9-]*', sid):
            raise ValueError(f'Invalid section ID: {sid}')
        title = esc(section['title'])
        nav.append(f'<li><a href="#{sid}">{title}</a></li>')
        sections.append(f'<section id="{sid}"><span class="section-no">{index:02d} / READ</span>'
                        f'<h2>{title}</h2>{fragment(section["html"])}</section>')
    if include_original:
        nav.append(f'<li><a href="#original">完整原文 · {len(doc)} 页</a></li>')
    main.append('<details class="toc" id="toc"><summary>阅读目录</summary><ol>' + ''.join(nav) + '</ol></details>')
    main.extend(sections)
    if include_original:
        main.append(f'<section id="original"><span class="section-no">FULL PAPER</span><h2>完整原文 · {len(doc)} 页</h2>'
                    '<p>按页展开，点按页面放大；放大后可上下、左右拖动。全部原文页图已嵌入，无需连接原网站。</p>')
        for number in range(1, len(doc) + 1):
            src, size = pdf_image(doc, number)
            label = config.get('page_labels', {}).get(str(number), '')
            summary = f'第 {number:02d} 页' + (f' · {label}' if label else '')
            main.append(f'<details class="source-page" id="page-{number}"><summary>{esc(summary)}</summary>'
                        f'{image_button(src, size, f"原文第 {number} 页")}</details>')
        main.append('</section>')
    main.append(f'<p class="footer">{esc(config.get("footer", ""))}</p><a class="jump" href="#top">回到开头</a>')
    shell = (Path(__file__).resolve().parents[1] / 'assets' / 'reader.html').read_text(encoding='utf-8')
    document_id = hashlib.sha256((config.get('doi') or config['title']).encode('utf-8')).hexdigest()[:16]
    replacements = {'MAIN': ''.join(main), 'TITLE': esc(config['title'] + '｜离线精读'),
                    'DESCRIPTION': esc(config.get('description', config['title'])),
                    'BRAND': esc(config.get('brand', '论文 · 离线精读')), 'DOCUMENT_ID': document_id}
    output = re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: replacements[m.group(1)], shell)
    audit = Audit()
    audit.feed(output)
    audit.close()
    if len(audit.ids) != len(set(audit.ids)):
        raise ValueError('Duplicate HTML IDs; choose unique section IDs')
    missing = set(audit.targets) - set(audit.ids)
    if missing:
        raise ValueError(f'Broken internal links: {sorted(missing)}')
    if '{{figure:' in output or re.search(r'\{\{[A-Z_]+\}\}', output):
        raise ValueError('Unresolved content markers')
    return output, audit.images


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content', required=True, type=Path)
    parser.add_argument('--pdf', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--no-original', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.content.read_text(encoding='utf-8-sig'))
    if args.pdf:
        import fitz
        with fitz.open(args.pdf) as doc:
            output, images = build(config, args.content.resolve().parent, doc, not args.no_original)
    else:
        output, images = build(config, args.content.resolve().parent, include_original=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding='utf-8')
    print(f'Created: {args.output.resolve()}')
    print(f'Embedded images: {images}; size: {args.output.stat().st_size / 1048576:.2f} MiB')
    print('PASS: embedded images decode; internal links resolve; no external runtime resources.')


if __name__ == '__main__':
    main()
