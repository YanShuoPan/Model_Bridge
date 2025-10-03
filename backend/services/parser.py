import pandas as pd
import io, os, re, json
from datetime import datetime

def _infer_y_type(df: pd.DataFrame, roles: dict) -> str:
    y = roles.get("y")
    if y is None or y not in df.columns: return "unknown"
    s = df[y].dropna()
    if set(s.unique()).issubset({0,1}): return "binary"
    if pd.api.types.is_integer_dtype(s) and s.nunique() < 15: return "count"
    return "continuous"

def _simple_task_from_question(q: str) -> str:
    ql = q.lower()
    if any(k in ql for k in ["ate","因果","treatment","處理","政策","實驗"]):
        return "causal"
    if any(k in ql for k in ["survival","存活","time to event","風險"]):
        return "survival"
    if any(k in ql for k in ["分類","classif","0/1","機率"]):
        return "classification"
    if any(k in ql for k in ["預測","regression","迴歸"]):
        return "prediction"
    return "prediction"

def _guess_roles(df: pd.DataFrame):
    cols = list(df.columns)
    guess = {"y": None, "treatment": None, "time": None, "id": None}
    for c in cols:
        if re.fullmatch(r"(y|label|target|outcome)", c, re.I):
            guess["y"] = c; break
    for c in cols:
        if re.fullmatch(r"(t|treat|treatment|w|z)", c, re.I):
            if set(df[c].dropna().unique()).issubset({0,1}):
                guess["treatment"] = c; break
    for c in cols:
        if re.search(r"(time|duration|survival|t_?end)", c, re.I):
            guess["time"] = c; break
    for c in cols:
        if re.fullmatch(r"(id|subject|unit|pid)", c, re.I):
            guess["id"] = c; break
    return guess

def parse_question_and_csv(question, file):
    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))
    roles = _guess_roles(df)
    task = _simple_task_from_question(question)
    y_type = _infer_y_type(df, roles)
    up_dir = "backend/storage/uploads"
    os.makedirs(up_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(up_dir, f"{ts}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)
    head = df.head(5).to_dict(orient="records")
    schema = {c: str(df[c].dtype) for c in df.columns}
    return {
        "question": question,
        "task": task,
        "y_type": y_type,
        "roles": roles,
        "file_path": file_path,
        "preview": {"n_rows": len(df), "n_cols": df.shape[1], "schema": schema, "head": head}
    }
