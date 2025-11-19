from jinja2 import Template

HTML_TPL = """
<!doctype html><html><head><meta charset="utf-8">
<title>{{ title }}</title>
<style>
body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;
max-width:900px;margin:40px auto;padding:0 16px;line-height:1.6}
h1{font-size:28px} h2{font-size:20px;margin-top:28px}
table{border-collapse:collapse} td,th{border:1px solid #ddd;padding:6px 8px}
.figure{margin:12px 0}
.badge{display:inline-block;background:#eef;border:1px solid #dde;padding:2px 8px;border-radius:12px;margin-right:6px}
</style></head><body>
<h1>{{ title }}</h1>
<h2>摘要</h2>
<div>{{ summary | safe }}</div>
<h2>指標</h2>
{% if metrics %}<table><tbody>
{% for k,v in metrics.items() %}<tr><th>{{k}}</th><td>{{v}}</td></tr>{% endfor %}
</tbody></table>{% else %}<p>無</p>{% endif %}
<h2>圖表</h2>
{% if figures %}{% for f in figures %}
<div class="figure"><img src="{{ f }}" style="max-width:100%"></div>
{% endfor %}{% else %}<p>無</p>{% endif %}
</body></html>
"""

def render_html_report(html_path: str, title: str, summary: str, metrics: dict, figures: list[str]):
    tpl = Template(HTML_TPL)
    html = tpl.render(title=title, summary=summary, metrics=metrics, figures=figures)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
