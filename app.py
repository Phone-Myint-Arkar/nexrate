from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Get latest rates ──
def get_rates(base="USD"):
    res = requests.get(f"https://api.frankfurter.app/latest?from={base}")
    data = res.json()
    rates = data["rates"]
    rates[base] = 1.0
    return rates

# ── Get historical rates ──
def get_historical(base="USD", target="THB", days=28):
    end = datetime.today()
    start = end - timedelta(days=days)

    url = f"https://api.frankfurter.app/{start.date()}..{end.date()}?from={base}&to={target}"
    res = requests.get(url)
    data = res.json()["rates"]

    rates = [v[target] for k, v in sorted(data.items())]
    return rates

# ── Weighted Moving Average ──
def weighted_ma(rates):
    n = len(rates)
    weights = list(range(1, n+1))  # [1,2,3,...]

    weighted_sum = sum(r * w for r, w in zip(rates, weights))
    total_weight = sum(weights)

    return weighted_sum / total_weight

# ── Prediction logic ──
def predict_rate(rates, alpha=0.3):
    n = len(rates)

    # not enough data
    if n < 3:
        return None

    # ── Weighted Moving Average ──
    weights = list(range(1, n + 1))  # [1,2,3,...,n]
    weighted_sum = sum(r * w for r, w in zip(rates, weights))
    total_weight = sum(weights)

    wma = weighted_sum / total_weight

    # ── Momentum (recent change) ──
    momentum = rates[-1] - rates[-2]

    # ── Final Prediction ──
    prediction = wma + (alpha * momentum)

    return round(prediction, 4)

# ── Routes ──
@app.route("/api/rates")
def rates():
    base = request.args.get("base", "USD")
    data = get_rates(base)

    return jsonify({
        "rates": data,
        "currencies": sorted(data.keys())
    })
    
@app.route("/api/predict")
def predict():
    base = request.args.get("from", "USD")
    target = request.args.get("to", "THB")

    history = get_historical(base, target)
    prediction = predict_rate(history)

    return jsonify({
        "history": history,
        "prediction": prediction
    })

@app.route("/api/convert")
def convert_api():
    try:
        amount = float(request.args.get("amount", 1))
        from_cur = request.args.get("from", "USD")
        to_cur = request.args.get("to", "THB")

        rates = get_rates(from_cur)

        if to_cur not in rates:
            return jsonify({"success": False, "error": "Invalid currency"}), 400

        result = amount * rates[to_cur]

        return jsonify({
            "success": True,
            "result": round(result, 2)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)