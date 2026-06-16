import sys, json

account = sys.argv[1]
count   = sys.argv[2]
now     = sys.argv[3]
try:
    buckets_data = json.loads(sys.argv[4])
except:
    buckets_data = []

# جيب محتوى كل bucket
bucket_sections = ""
for i, b in enumerate(buckets_data):
    name = b.get("Name","")
    date = (b.get("Date") or "")[:10]

    # جيب objects جوه الـ bucket
    import subprocess, json as j
    try:
        result = subprocess.run(
            ["aws", "s3api", "list-objects-v2", "--bucket", name, "--query", "Contents[].{Key:Key,Size:Size}", "--output", "json"],
            capture_output=True, text=True, timeout=10
        )
        objects = j.loads(result.stdout) if result.stdout.strip() and result.stdout.strip() != "None" else []
    except:
        objects = []

    obj_rows = ""
    for obj in (objects or []):
        key  = obj.get("Key","")
        size = obj.get("Size", 0)
        size_str = f"{size/1024:.1f} KB" if size < 1048576 else f"{size/1048576:.1f} MB"
        obj_rows += f"<tr><td class='obj-icon'>📄</td><td class='obj-name'>{key}</td><td class='obj-size'>{size_str}</td></tr>"

    if not obj_rows:
        obj_rows = "<tr><td colspan='3' class='empty-obj'>No objects in this bucket</td></tr>"

    bucket_sections += f"""
    <div class='bucket-card'>
      <div class='bucket-card-header'>
        <span class='bucket-card-icon'>🪣</span>
        <span class='bucket-card-name'>{name}</span>
        <span class='bucket-card-date'>Created: {date}</span>
        <span class='region-badge'>us-east-1</span>
        <span class='obj-count'>{len(objects or [])} objects</span>
      </div>
      <table class='obj-table'>
        <thead>
          <tr><th></th><th>Object Name</th><th>Size</th></tr>
        </thead>
        <tbody>{obj_rows}</tbody>
      </table>
    </div>"""

if not bucket_sections:
    bucket_sections = "<div class='no-buckets'>🪣 No S3 Buckets found in this account</div>"

html = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta http-equiv='refresh' content='30'>
  <title>S3 Buckets - EKS Lab</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#c9d1d9;min-height:100vh;padding:2rem}}

    /* HEADER */
    .header{{background:linear-gradient(135deg,#1f6feb,#0d419d);border-radius:16px;padding:2rem;text-align:center;margin-bottom:2rem;box-shadow:0 4px 20px rgba(31,111,235,0.3)}}
    .header h1{{font-size:2rem;color:#fff;margin-bottom:.5rem}}
    .header p{{color:#cae8ff;font-size:.9rem}}

    /* STATS */
    .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}}
    .card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:1.2rem;text-align:center;transition:transform .2s}}
    .card:hover{{transform:translateY(-2px)}}
    .card .icon{{font-size:1.8rem;margin-bottom:.4rem}}
    .card .value{{font-size:1.6rem;font-weight:bold;color:#58a6ff}}
    .card .label{{color:#8b949e;font-size:.75rem;margin-top:.2rem}}

    /* IRSA BADGE */
    .irsa-badge{{background:#1a2332;border:1px solid #1f6feb;border-radius:8px;padding:.8rem 1.2rem;margin-bottom:1.5rem;font-size:.85rem;color:#79c0ff;display:flex;align-items:center;gap:.5rem}}

    /* BUCKET CARDS */
    .buckets-title{{color:#8b949e;font-size:.85rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:1rem}}
    .bucket-card{{background:#161b22;border:1px solid #30363d;border-radius:12px;margin-bottom:1.5rem;overflow:hidden;transition:border-color .2s}}
    .bucket-card:hover{{border-color:#1f6feb}}
    .bucket-card-header{{background:#21262d;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap}}
    .bucket-card-icon{{font-size:1.3rem}}
    .bucket-card-name{{color:#58a6ff;font-weight:700;font-size:1rem;flex:1}}
    .bucket-card-date{{color:#8b949e;font-size:.8rem}}
    .region-badge{{background:#1a2332;color:#79c0ff;padding:.2rem .6rem;border-radius:20px;font-size:.75rem}}
    .obj-count{{background:#1f2d1f;color:#3fb950;padding:.2rem .6rem;border-radius:20px;font-size:.75rem}}

    /* OBJECTS TABLE */
    .obj-table{{width:100%;border-collapse:collapse}}
    .obj-table th{{background:#161b22;color:#8b949e;padding:.6rem 1rem;text-align:left;font-size:.75rem;font-weight:600;text-transform:uppercase}}
    .obj-table td{{padding:.7rem 1rem;border-bottom:1px solid #21262d;font-size:.85rem}}
    .obj-table tr:last-child td{{border-bottom:none}}
    .obj-table tr:hover td{{background:#1c2128}}
    .obj-icon{{width:30px;text-align:center}}
    .obj-name{{color:#c9d1d9}}
    .obj-size{{color:#8b949e;font-size:.8rem}}
    .empty-obj{{text-align:center;padding:1rem;color:#8b949e;font-size:.85rem}}
    .no-buckets{{text-align:center;padding:3rem;color:#8b949e;font-size:1rem}}

    /* FOOTER */
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
    <div class='card'><div class='icon'>☸️</div><div class='value'>EKS</div><div class='label'>Platform</div></div>
    <div class='card'><div class='icon'>⏱️</div><div class='value'>30s</div><div class='label'>Refresh Rate</div></div>
  </div>

  <div class='irsa-badge'>
    🔐 This Pod fetches data using <strong>&nbsp;IRSA&nbsp;</strong> — no AWS Access Keys in the code!
    &nbsp;|&nbsp; AWS Account: <strong>{account}</strong>
  </div>

  <div class='buckets-title'>📋 S3 Buckets & Contents</div>
  {bucket_sections}

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
