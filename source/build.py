import json, base64, html, os
from data import STAGES, STEPS, GHOST, FINDING, FACE_NAMES
HERE = os.path.dirname(os.path.abspath(__file__))
OUT2 = '/home/claude/peeps/out2'
e = html.escape

need = {('mentor','explaining'),('mentee','smile')}
for s in STEPS:
    need.add(('mentor', s['faces'][0])); need.add(('mentee', s['faces'][1]))
need.add(('mentor', GHOST['mentor']['face'])); need.add(('mentee', GHOST['mentee']['face']))
faces = {}
for who, f in sorted(need):
    svg = open(f'{OUT2}/{who}-{f}.svg', 'rb').read()
    faces[f'{who}:{f}'] = 'data:image/svg+xml;base64,' + base64.b64encode(svg).decode()

stages = ''.join(f'<div style="grid-column:span {len(ns)}">{e(name)}</div>' for name, ns in STAGES)

def branch(who):
    g = GHOST[who]; label = 'Mentor' if who == 'mentor' else 'Mentee'
    lis = ''.join(f'<li><div><b>{e(t)}</b><q>{e(q)}</q>' + (f'<p class="pain">{e(p)}</p>' if p else '') + '</div></li>' for t, q, p in g['steps'])
    return (f'<article class="branch only-{who}"><div class="branch-head"><img src="{faces[who+":"+g["face"]]}" alt="{e(g["faceAlt"])}">'
            f'<h3><span class="pill {who}">{label}</span>{e(g["title"])}</h3></div><ol class="seq">{lis}</ol>'
            f'<p class="help"><b>What would help:</b> {e(g["help"])}</p></article>')
branches = branch('mentor') + branch('mentee')

head = '<tr><th scope="col"><span class="sr">Row</span></th>' + ''.join(f'<th scope="col">{s["n"]}. {e(s["title"])}</th>' for s in STEPS) + '</tr>'
def row(label, cells, cls=''):
    return f'<tr class="{cls}"><th scope="row">{label}</th>' + ''.join(cells) + '</tr>'
def wrong_cell(s):
    if not s['wrong']: return '<td><span style="color:var(--muted)">None recorded</span></td>'
    return '<td>' + ''.join(f'<div class="w only-{"mentee" if t=="mentee" else "x"}"><span class="pill {t}">{"Both" if t=="both" else "Mentee"}</span><br>{e(x)}</div>' for t, x in s['wrong']) + '</td>'
rows = [
    row('Mentor thinks', [f'<td>“{e(s["mentor"])}”</td>' for s in STEPS], 'only-mentor'),
    row('Mentee thinks', [f'<td>“{e(s["mentee"])}”</td>' for s in STEPS], 'only-mentee'),
    row('How it feels', [f'<td class="{"br" if s["breaks"] else ""}">{e(s["mood"])}</td>' for s in STEPS]),
    row('What goes wrong', [wrong_cell(s) for s in STEPS]),
    row('Where they hear from us', [f'<td>{e(s["touch"])}</td>' for s in STEPS]),
    row('What would help', [f'<td>{e(s["help"])}</td>' for s in STEPS]),
]
table = f'<table><caption class="sr">The first-year mentorship journey, all eight steps</caption><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'

data = {'stages': STAGES, 'steps': STEPS, 'faces': faces, 'faceNames': FACE_NAMES}
t = open(os.path.join(HERE, 'template.html')).read()
t = (t.replace('{{STAGES}}', stages).replace('{{BRANCHES}}', branches).replace('{{TABLE}}', table)
      .replace('{{F_HEAD}}', e(FINDING['headline'])).replace('{{F_NOTE}}', e(FINDING['note']))
      .replace('{{HMW}}', ''.join(f'<div>{e(h)}</div>' for h in FINDING['hmw']))
      .replace('{{DATA}}', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')))
# remaining face placeholders in static markup are filled by the script from data-face
open(os.path.join(HERE, 'index.html'), 'w').write(t)
print(len(t)//1024, 'KB')
