"""Build figures and offline preview; optionally re-extract whitelisted lab evidence.

python build.py --source-root /path/to/vps  # read original evidence, never mutate it
python build.py                           # rebuild from bundled aggregates
"""
import argparse
import csv
import hashlib
import html
import json
import math
import os
import re
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/embra-article-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import markdown

HERE = Path(__file__).resolve().parent
ASSETS = HERE / 'assets'
DATA = HERE / 'data'
ASSETS.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
RUNS28 = ['20260928T044810Z', '20260928T051000Z', '20260928T072200Z']
RUNS29 = ['20260929T075832Z', '20260929T155607Z']


def extract(root):
    sources = []
    lab = root / 'test/migration_vps_lab/results'

    def record(path):
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        sources.append({'path': str(path.relative_to(root)), 'sha256': digest.hexdigest()})

    def read(path):
        record(path)
        return json.loads(path.read_text())

    rows = []
    total_requests = 0
    for run, phase, label in zip(RUNS28, ['M3_apply', 'M3_apply', 'M4_apply'],
                                  ['M3 trước ngắt', 'M3 chạy tiếp', 'M4 có hai điểm ngắt']):
        d = read(lab / run / 'summary.json')
        total_requests += d['all']['requests']
        assert not d['all']['errors']
        base = d['phases']['baseline']['stats']['p99_ms']
        s = d['phases'][phase]['stats']
        rows.append(dict(run=run, phase=phase, label=label, metric='start_to_end',
                         selection='overlap_apply_window', requests=s['requests'],
                         p99_ms=s['p99_ms'], baseline_p99_ms=base))
    assert total_requests == 1269965
    v = read(lab / RUNS28[-1] / 'final-verification.json')
    keys = ['seed_rows', 'total_rows', 'b3_bad', 'b4_bad', 'app_update_bad',
            'app_insert_missing', 'acknowledged', 'ack_missing', 'passed']
    integrity28 = {k: v[k] for k in keys}
    assert v['acknowledged'] == 846642 and v['ack_missing'] == 0 and v['passed']
    assert v['total_rows'] == 8423321
    audit = read(lab / RUNS28[-1] / 'final-audit.json')
    audit = {k: audit[k] for k in ['batch_gaps', 'batch_receipt_mismatches', 'index_correct', 'passed']}
    ep = lab / RUNS28[-1] / 'primary/M4-executor.jsonl'
    record(ep)
    kills = []
    for line in ep.open():
        e = json.loads(line)
        if e.get('name') in ('kill_before_commit', 'kill_after_commit_before_ack'):
            kills.append({k: e[k] for k in ['name', 'batch', 'last']})
    assert [(x['batch'], x['last']) for x in kills] == [(7, 30000), (13, 65000)]

    # Start-in-window is explicit and consistent for both follow-up runs.
    # No request IDs, endpoints or request bodies are exported.
    for run in RUNS29:
        p = lab / run / 'primary'
        events_path = p / 'events.jsonl'
        record(events_path)
        events = [json.loads(x) for x in events_path.read_text().splitlines()]
        wins = {}
        for phase in ['baseline', 'M3_apply', 'M4_apply']:
            a = next(x['time'] for x in events if x['name'] == phase + '_start')
            b = next(x['time'] for x in events if x['name'] == phase + '_end')
            wins[phase] = (a, b)
        samples = {k: {'start_to_end': [], 'scheduled_to_end': []} for k in wins}
        req = p / 'requests.jsonl'
        record(req)
        with req.open() as stream:
            for line in stream:
                r = json.loads(line)
                for phase, (a, b) in wins.items():
                    if a <= r['start'] < b:
                        assert r['end'] >= r['start']
                        samples[phase]['start_to_end'].append(r['ms'])
                        samples[phase]['scheduled_to_end'].append((r['end'] - r['scheduled']) * 1000)

        def percentile(values):
            values.sort()
            assert values
            return round(values[math.ceil(len(values) * .99) - 1], 3)

        for metric in ['start_to_end', 'scheduled_to_end']:
            baseline = percentile(samples['baseline'][metric])
            for phase in ['M3_apply', 'M4_apply']:
                xs = samples[phase][metric]
                rows.append(dict(run=run, phase=phase, label=phase[:2], metric=metric,
                                 selection='start_in_apply_window', requests=len(xs),
                                 p99_ms=percentile(xs), baseline_p99_ms=baseline))
    final = read(lab / RUNS29[-1] / 'primary/verification.json')
    assert final['acknowledged'] == 509380 and final['ack_missing'] == 0 and final['passed']
    with (DATA / 'latency.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    evidence = dict(extracted_on='2026-10-08', requests_28=total_requests,
                    integrity_28=integrity28, audit_28=audit, kill_checkpoints_28=kills,
                    integrity_final={k: final[k] for k in keys},
                    method='nearest-rank p99; ceil(n * 0.99) - 1 after sorting',
                    sources=sources)
    (DATA / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')


def saveplot(fig, name):
    fig.savefig(ASSETS / (name + '.svg'), bbox_inches='tight')
    fig.savefig(ASSETS / (name + '.png'), dpi=180, bbox_inches='tight')
    plt.close(fig)


def figures():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.fonttype': 'none', 'figure.facecolor': '#faf8f3',
                         'axes.facecolor': '#faf8f3', 'text.color': '#232323',
                         'axes.labelcolor': '#232323', 'axes.spines.top': False,
                         'axes.spines.right': False})
    rows = list(csv.DictReader((DATA / 'latency.csv').open()))
    earlier = [r for r in rows if r['run'] in RUNS28]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.subplots_adjust(left=.25, right=.94, bottom=.2, top=.76)
    for i, r in enumerate(earlier):
        b, v = float(r['baseline_p99_ms']), float(r['p99_ms'])
        ax.plot([b, v], [i, i], color='#cec8bb', linewidth=3, zorder=1)
        ax.scatter(b, i, color='#656962', s=80, zorder=2, label='Baseline cùng lượt' if i == 0 else None)
        ax.scatter(v, i, color='#b45820', s=85, zorder=2, label='Trong pha backfill' if i == 0 else None)
        ax.annotate(f'{b:,.3f}', (b, i), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=9)
        ax.annotate(f'{v:,.3f}', (v, i), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=9)
    ax.set_xscale('log')
    ax.set_xlim(1, 4000)
    ax.set_xticks([1, 10, 100, 1000], labels=['1', '10', '100', '1.000'])
    ax.set_yticks(range(3), [r['label'] for r in earlier])
    ax.set_ylim(2.6, -.6)
    ax.set_xlabel('p99 request SQL (ms) · trục logarithmic')
    ax.grid(axis='x', color='#dfd9cf')
    ax.legend(loc='lower left', bbox_to_anchor=(-.01, 1.08), ncol=2, frameon=False, fontsize=10)
    fig.suptitle('28/9 · Dữ liệu đúng, đuôi latency vẫn tăng', fontsize=17, x=.05, ha='left', y=.98)
    fig.text(.05, .91, 'Đo từ lúc worker bắt đầu request; ba cửa sổ riêng, không phải time series.', fontsize=10)
    fig.text(.05, .025, 'Nguồn: summary từng lượt · Số ghi trên điểm dùng dấu chấm thập phân.', fontsize=9, color='#666')
    saveplot(fig, 'latency-28')

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharey=True)
    fig.subplots_adjust(left=.1, right=.97, top=.73, bottom=.23, wspace=.3)
    for ax, run, title in zip(axes, RUNS29, ['29/9 · lượt 4', 'Đêm 29–30/9 · lượt 7']):
        selected = [r for r in rows if r['run'] == run and r['metric'] == 'scheduled_to_end']
        values = [float(r['p99_ms']) for r in selected]
        bars = ax.bar(['M3', 'M4'], values, color=['#b45820', '#354e56'], width=.52)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, val+75, f'{val:,.1f}', ha='center', fontsize=10)
        ax.axhline(1000, color='#a93932', linestyle='--', linewidth=1.3)
        ax.set_title(title, loc='left', fontsize=12)
        ax.set_ylim(0, 3000)
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#dfd9cf')
    axes[0].set_ylabel('p99 lịch phát → hoàn tất (ms)')
    fig.suptitle('Tính cả thời gian chờ, p99 vẫn vượt một giây', fontsize=16, x=.05, ha='left', y=.98)
    fig.text(.05, .89, 'Đường nét đứt: mục tiêu 1.000 ms của vòng sau.', fontsize=10)
    fig.text(.05, .08, 'Tính lại từ log SQL · nearest-rank · chọn request bắt đầu trong cửa sổ apply.', fontsize=9)
    fig.text(.05, .035, 'Khác cấu hình / bối cảnh tải: không dùng biểu đồ này làm phép so sánh A/B của throttle.', fontsize=9, color='#666')
    saveplot(fig, 'latency-followup')

    fig = plt.figure(figsize=(12, 6.3), facecolor='#232323')
    fig.text(.07, .83, 'EMBRA / ENGINEERING NOTES', color='#deb562', fontsize=17)
    fig.text(.07, .56, 'Backfill 8 triệu dòng', color='#fafafa', fontsize=37, weight='bold')
    fig.text(.07, .36, 'Dữ liệu đúng.\nLatency chưa đạt.', color='#e6e3da', fontsize=27, linespacing=1.4)
    fig.text(.07, .10, 'Ghi chép thử nghiệm · 28–30/09/2026', color='#bcb8ad', fontsize=14)
    saveplot(fig, 'cover')


def svg(text, filename, height=420):
    doc = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 '+str(height)+'" role="img">'
    doc += '<rect width="1100" height="'+str(height)+'" rx="12" fill="#faf8f3"/>'
    doc += '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#59645c"/></marker></defs>'
    doc += '<g font-family="Arial, sans-serif" fill="#232323">'+text+'</g></svg>'
    (ASSETS / filename).write_text(doc)


def txt(x, y, s, size=20, fill='#232323', weight='normal'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}">{html.escape(s)}</text>'


def box(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="#d1cabd"/>'


def arrow(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="#59645c" stroke-width="2" marker-end="url(#arrow)"/>'


def diagrams():
    s = txt(40, 48, 'Lab 28/9 · Generator chạy cùng primary', 29, weight='bold')
    s += box(40, 88, 435, 235) + txt(65, 123, 'PRIMARY · 4 vCPU / 8 GB', 22, weight='bold')
    s += txt(65, 164, 'PostgreSQL 16.15 · bảng orders')
    s += txt(65, 203, 'Generator: 200 tx/s theo lịch', 20, '#b45820')
    s += txt(65, 238, '64 worker · read / update / insert', 18)
    s += txt(65, 285, 'Dùng chung CPU, có thể tranh tài nguyên.', 17, '#656962')
    s += box(680, 88, 375, 115) + txt(702, 123, 'REPLICA · 2 vCPU / 4 GB', 22, weight='bold')
    s += txt(702, 163, 'Replication bất đồng bộ', 19)
    s += arrow(475, 148, 680, 148) + txt(506, 131, 'WAL', 18)
    s += box(680, 248, 375, 75) + txt(702, 279, 'Clone ZFS để diễn tập', 20)
    s += txt(702, 304, 'Chạy migration thử trước khi approve', 16, '#656962')
    s += arrow(865, 203, 865, 246)
    s += txt(40, 368, 'Seed: 8 triệu dòng / 10,35 GiB · ext4 trên zvol · dữ liệu tổng hợp', 19)
    s += txt(40, 400, 'Sơ đồ topology; không thể hiện mọi thành phần backup/approval của lab.', 16, '#656962')
    svg(s, 'topology.svg')
    s = txt(40, 48, 'M4 · Hai điểm ngắt, hai checkpoint khác nhau', 28, weight='bold')
    for y, title, before, middle, end in [
        (100, 'Ngắt trước commit batch 7', 'Dữ liệu + receipt', 'CHƯA COMMIT', 'last_id = 30.000'),
        (275, 'Ngắt sau commit batch 13, trước ACK', 'Dữ liệu + receipt', 'ĐÃ COMMIT', 'last_id = 65.000')]:
        s += txt(40, y, title, 22, weight='bold')
        s += box(40, y+22, 260, 64)+txt(60, y+61, before, 20)
        s += arrow(302, y+54, 384, y+54)
        s += box(386, y+22, 270, 64)+txt(408, y+61, middle, 20, '#b45820')
        s += arrow(658, y+54, 741, y+54)
        s += box(743, y+22, 310, 64)+txt(765, y+61, end, 22, weight='bold')
    s += txt(40, 226, 'Transaction chưa commit → đọc receipt cũ và xử lý lại batch chưa hoàn tất.', 18, '#656962')
    s += txt(40, 402, 'ACK bị mất → đọc receipt đã commit và tiếp tục từ checkpoint mới.', 18, '#656962')
    s += txt(40, 449, 'Sơ đồ cơ chế; không theo tỷ lệ thời gian. Nguồn: M4-executor.jsonl, lượt 28/9.', 16, '#656962')
    svg(s, 'commit-resume.svg', height=475)


STYLE = '''
*{box-sizing:border-box}body{margin:0;background:#faf8f3;color:#262623;font:18px/1.8 system-ui,sans-serif}
.bar{padding:16px 5vw;border-bottom:1px solid #ddd6c8;font-size:13px;letter-spacing:.06em}
.bar a{color:inherit}main{max-width:820px;margin:54px auto 90px;padding:0 28px}h1{font-size:clamp(32px,5vw,48px);line-height:1.2;letter-spacing:-.035em;margin:0 0 28px}
h2{font-size:28px;line-height:1.35;margin-top:54px}p{margin:22px 0}a{color:#8b421b;text-underline-offset:3px}img{display:block;width:100%;height:auto;border:1px solid #e3dccf;border-radius:8px}p:has(>em){font-size:15px;color:#62635b;line-height:1.65}
table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.6}th,td{padding:12px 10px;border-bottom:1px solid #ded7ca;text-align:left}th{background:#f0ece2}.table-scroll{overflow-x:auto}code{font-size:.88em;background:#eee9de;padding:2px 5px;border-radius:4px}pre{overflow:auto;padding:16px;background:#eee9de}hr{border:0;border-top:1px solid #ded7ca;margin:44px 0}strong{font-weight:650}.notice{background:#f0e7d5;padding:14px 18px;font-size:14px;border-left:3px solid #ac6a30;margin-bottom:32px}
@media(max-width:600px){body{font-size:17px}main{margin-top:32px;padding:0 20px}h2{font-size:24px}.table-scroll table{min-width:550px}}
'''


def preview():
    for src, target, title in [('article.md', 'preview.html', 'Backfill 8 triệu dòng'),
                                ('EVIDENCE.md', 'evidence.html', 'Bằng chứng và phương pháp')]:
        content = markdown.markdown((HERE/src).read_text(), extensions=['tables', 'fenced_code'])
        content = content.replace('href="EVIDENCE.md"', 'href="evidence.html"')
        content = content.replace('href="article.md"', 'href="preview.html"')
        content = re.sub(r'<img ([^>]*?)src="([^"]+)"([^>]*?)>', r'<a href="\2" aria-label="Mở hình ở kích thước đầy đủ"><img \1src="\2"\3></a>', content)
        content = content.replace('<table>', '<div class="table-scroll"><table>').replace('</table>', '</table></div>')
        page = '<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        page += '<meta name="robots" content="noindex,nofollow"><title>'+html.escape(title)+' · Embra — bản nháp</title><style>'+STYLE+'</style>'
        page += '<body><div class="bar">EMBRA / ENGINEERING · <a href="preview.html">Bài viết</a> · <a href="evidence.html">Bằng chứng</a></div><main>'
        page += '<div class="notice">Bản đọc thử nội bộ · chưa xuất bản · số liệu lab, không phải cam kết dịch vụ.</div>'
        page += content+'</main></body></html>'
        (HERE/target).write_text(page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path)
    args = parser.parse_args()
    if args.source_root:
        extract(args.source_root.resolve())
    figures()
    diagrams()
    preview()
    print('Built figures, cover and offline previews in', HERE)
