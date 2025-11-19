import os, uuid, json
import pandas as pd
from backend.methods.base import METHODS_REGISTRY
from backend.services.reports import render_html_report

def run_method(method_id: str, file_path: str, roles: dict, params: dict):
    if method_id not in METHODS_REGISTRY:
        raise ValueError(f"Unknown method_id: {method_id}")
    df = pd.read_csv(file_path)
    run_id = str(uuid.uuid4())[:8]
    out_dir = f"backend/storage/runs/{run_id}"
    os.makedirs(out_dir, exist_ok=True)

    method = METHODS_REGISTRY[method_id]()
    result = method.run(df, roles, params, out_dir=out_dir)

    html_path = os.path.join(out_dir, "report.html")
    render_html_report(
        html_path=html_path,
        title=method.name,
        summary=result.get("summary_md",""),
        metrics=result.get("metrics",{}),
        figures=result.get("figures",[])
    )

    payload = {
        "run_id": run_id,
        "method_id": method_id,
        "metrics": result.get("metrics",{}),
        "figures": result.get("figures",[]),
        "summary": result.get("summary_md",""),
        "report_html_path": html_path,
        "file_path": file_path
    }
    with open(os.path.join(out_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload
