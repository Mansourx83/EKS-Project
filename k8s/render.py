import sys, json

account = sys.argv[1]
count   = sys.argv[2]
now     = sys.argv[3]
try:
    buckets = json.loads(sys.argv[4])
except:
    buckets = []

rows = ""
for i, b in enumerate(buckets):
    name = b.get("Name","")
    date = (b.get("Date") or "")[:10]
    rows += f"<tr><td class='num'>{i+1}</td><td><span class='bucket-icon'>🪣</span> <span class='name'>{name}</span></td><td><span class='date-badge'>{date}</span></td><td><span class='region-badge'>us-east-1</span></td><td><span class='status-badge'>&#10003; Active</span></td></tr>"

if not rows:
    rows = "<tr><td colspan='5' class='empty'><div class='empty-icon'>🪣</div><div>No S3 Buckets found</div></td></tr>"

html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta http-equiv='refresh' content='30'>
  <title>S3 Buckets - EKS Lab</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#c9d1d9;min-height:100vh;padding:2rem}}
    .header{{background:linear-gradient(135deg,#1f6feb,#0d419d);border-radius:16px;padding:2rem;text-align:center;margin-bottom:2rem;box-shadow:0 4px 20px rgba(31,111,235,0.3)}}
    .header h1{{font-size:2rem;color:#fff;margin-bottom:.5rem}}
    .header p{{color:#cae8ff;font-size:.9rem}}
    .stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem}}
    .card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1.5rem;text-align:center;transition:transform .2s}}
    .card:hover{{transform:translateY(-2px)}}
    .card .icon{{font-size:2rem;margin-bottom:.5rem}}
    .card .value{{font-size:1.8rem;font-weight:bold;color:#58a6ff}}
    .card .label{{color:#8b949e;font-size:.8rem;margin-top:.3rem}}
    .irsa-badge{{background:#1a2332;border:1px solid #1f6feb;border-radius:8px;padding:.8rem 1.2rem;margin-bottom:1.5rem;font-size:.85rem;color:#79c0ff}}
    .table-container{{background:#161b22;border:1px solid #30363d;border-radius:12px;overflow:hidden}}
    .table-header{{padding:1rem 1.5rem;background:#21262d;border-bottom:1px solid #30363d;font-weight:bold;color:#8b949e;font-size:.85rem}}
    table{{width:100%;border-collapse:collapse}}
    th{{background:#21262d;color:#8b949e;padding:.8rem 1rem;text-align:left;font-size:.8rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em}}
    td{{padding:1rem;border-bottom:1px solid #21262d;font-size:.9rem}}
    tr:last-child td{{border-bottom:none}}
    tr:hover td{{background:#1c2128}}
    td.num{{color:#8b949e;font-size:.8rem;width:40px;text-align:center}}
    .name{{color:#58a6ff;font-weight:600}}
    .date-badge{{background:#1f2d1f;color:#3fb950;padding:.2rem .6rem;border-radius:20px;font-size:.75rem}}
    .region-badge{{background:#1a2332;color:#79c0ff;padding:.2rem .6rem;border-radius:20px;font-size:.75rem}}
    .status-badge{{background:#1f2d1f;color:#3fb950;padding:.2rem .6rem;border-radius:20px;font-size:.75rem}}
    .empty{{text-align:center;padding:3rem;color:#8b949e}}
    .empty-icon{{font-size:3rem;margin-bottom:1rem}}
    .footer{{text-align:center;color:#8b949e;font-size:.75rem;margin-top:1.5rem}}
    .footer span{{background:#161b22;border:1px solid #30363d;padding:.3rem .8rem;border-radius:20px;margin:0 .3rem}}
  </style>
</head>
<body>
  <div class='header'>
    <h1>☁️ Amazon S3 Buckets</h1>
    <p>Live view from inside an EKS Pod using IRSA — no hardcoded credentials</p>
  </div>
  <div class='stats'>
    <div class='card'><div class='icon'>🪣</div><div class='value'>{count}</div><div class='label'>Total Buckets</div></div>
    <div class='card'><div class='icon'>🔐</div><div class='value'>IRSA</div><div class='label'>Auth Method</div></div>
    <div class='card'><div class='icon'>⏱️</div><div class='value'>30s</div><div class='label'>Refresh Rate</div></div>
  </div>
  <div class='irsa-badge'>
    🔐 This Pod fetches data using <strong>IRSA</strong> — no AWS Access Keys in the code! &nbsp;|&nbsp; AWS Account: <strong>{account}</strong>
  </div>
  <div class='table-container'>
    <div class='table-header'>📋 S3 Bucket List</div>
    <table>
      <thead><tr><th>#</th><th>Bucket Name</th><th>Creation Date</th><th>Region</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <div class='footer'>
    <span>🕐 Last updated: {now}</span>
    <span>☸️ EKS Lab</span>
    <span>🔄 Auto-refresh every 30s</span>
  </div>
</body>
</html>"""

with open("/usr/share/nginx/html/index.html","w") as f:
    f.write(html)
print(f"Updated — {count} buckets")
