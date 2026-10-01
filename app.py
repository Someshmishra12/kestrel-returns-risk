"""Kestrel returns-risk service. No external API / key needed. Run: uvicorn app:app --port 8000"""
import joblib, numpy as np, pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from feats import build
B = joblib.load("model.joblib"); M, COLS, CATS = B["model"], B["cols"], B["cats"]
CUST = pd.read_csv("customers.csv"); PROD = pd.read_csv("products.csv")
CALL_THRESHOLD = 0.15           # call before dispatch above this risk (see MEMO)
RET, CALL, PREV = 1150, 45, 0.35
app = FastAPI(title="Kestrel returns risk")

class Order(BaseModel):
    order_id: str = "NEW"
    order_placed_at: str
    customer_id: str
    sku: str
    sales_channel: str
    payment_mode: str
    discount_pct: float
    qty: int = 1
    order_value_inr: float
    promised_delivery_days: int
    delivery_pincode: int
    is_gift: str = "N"
    customer_prior_orders: int = 0
    customer_prior_returns: int = 0
    delivery_note: str | None = None
    # last_service_event_type / pickup_scheduled_at are accepted-and-ignored: they do not exist at dispatch.
    last_service_event_type: str | None = None
    pickup_scheduled_at: str | None = None
    source: str = "crm"

def _prep(df):
    X, m = build(df, CUST, PROD)
    for c in CATS: X[c] = pd.Categorical(X[c].astype(str), categories=B["cat_levels"][c])
    return X[COLS], m

def _p(X): return float(M.predict_proba(X)[0, 1])

TEXT = {  # feature -> (neutral baseline value, sentence)
 "prior_returns": "Customer has returned {v:.0f} earlier order(s)",
 "prior_ret_rate": "Customer's past return rate is high ({v:.0%})",
 "payment_mode": "Payment is {v} (cash-on-delivery orders return most)",
 "family": "Product family ({v}) has a higher return rate",
 "promised_days": "Long promised delivery ({v:.0f} days)",
 "discount_pct": "Heavy discount ({v:.0f}%)",
 "is_gift": "Order is a gift",
 "shield": "Kestrel Shield member (free returns)",
 "sales_channel": "Sold via {v}",
 "order_value": "Order value Rs {v:,.0f}",
 "list_price": "Product list price Rs {v:,.0f}",
 "tenure_days": "Customer account age ({v:.0f} days)",
 "prior_orders": "Customer has {v:.0f} earlier order(s)",
}
def reasons(X):
    base = M.predict_proba(X)[0, 1]; lo = lambda p: np.log(p/(1-p)); out = []
    for c in COLS:
        Z = X.copy()
        if c in CATS: Z[c] = pd.Categorical([B["cat_levels"][c][0]], categories=B["cat_levels"][c])
        else: Z[c] = B["med"][c]
        d = lo(base) - lo(M.predict_proba(Z)[0, 1])
        out.append((c, d))
    out.sort(key=lambda t: -abs(t[1]))
    res = []
    for c, d in out[:4]:
        if abs(d) < 0.08 or c not in TEXT: continue
        v = X[c].iloc[0]; v = v if c in CATS else float(v)
        res.append({"factor": c, "effect": "raises risk" if d > 0 else "lowers risk",
                    "strength": round(abs(d), 2), "text": TEXT[c].format(v=v)})
    return res

@app.post("/predict")
def predict(o: Order):
    if o.customer_id not in set(CUST.customer_id): raise HTTPException(422, "unknown customer_id")
    if o.sku not in set(PROD.sku): raise HTTPException(422, "unknown sku")
    try:
        df = pd.DataFrame([o.model_dump()]); df["order_placed_at"] = pd.to_datetime(df.order_placed_at)
        X, m = _prep(df)
    except Exception as e: raise HTTPException(422, f"bad input: {e}")
    p = _p(X); shield = bool(X.shield.iloc[0])
    gain = PREV*p*RET - CALL
    if p < CALL_THRESHOLD: action, why = "ship", "Risk is low; a confirmation call costs more than it is expected to save."
    else: action, why = "call_before_dispatch", f"Expected saving from a confirmation call is about Rs {gain:,.0f} after the Rs {CALL} call cost."
    if shield: why += " Shield member: do NOT hold; call only."
    return {"order_id": o.order_id, "return_probability": round(p, 4), "score": round(p, 4),
            "recommended_action": action, "hold_recommended": False,
            "expected_net_saving_inr": round(max(gain, 0), 0), "explanation": why,
            "reasons": reasons(X), "model_note": "Typical accuracy: ~89%. About 3 in 10 flagged orders really return; roughly 4 in 10 returns are never flagged."}

@app.get("/health")
def health(): return {"ok": True}
@app.get("/")
def home(): return FileResponse("static/index.html")
