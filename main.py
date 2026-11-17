#!/usr/bin/env python3
import sys, json
def main():
    cash, qty, entry, ema, n, held = 1000000000, 0, 0, None, 0, 0
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        m = json.loads(raw)
        typ = m.get("type")
        if typ == "done":
            break
        if typ != "batch":
            continue
        seq = m["seq"]
        acc = m.get("account", {})
        cash = int(acc.get("cash_quote_units", cash))
        ps = acc.get("positions") or []
        qty = int(ps[0]["qty"]) if ps else qty
        bb = m.get("bars") or []
        orders = []
        c = int(bb[0]["c"]) if bb else 0
        if bb:
            n += 1
            ema = c if ema is None else ema + ((2.0 / 65.0) * (c - ema))
        if bb and qty == 0 and n > 64 and c < ema * 0.995 and cash >= 1000000:
            orders = [{"side": "buy", "client_id": "b" + str(seq), "symbol": "CBBTC",
                       "notional_quote_units": str(cash), "max_slippage_bps": 300}]
            entry = c
        elif bb and qty > 0 and (c > entry * 1.01 or c < entry * 0.98 or held > 720):
            orders = [{"side": "sell", "client_id": "s" + str(seq), "symbol": "CBBTC",
                       "qty": str(qty), "max_slippage_bps": 1000}]
        held = held + 1 if qty > 0 else 0
        sys.stdout.write(json.dumps({"type": "reply", "seq": seq, "orders": orders}, separators=(",", ":")) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
