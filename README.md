# PriceWise — Smart Product Price Comparison & Decision Lab

A Python + FastAPI product comparison prototype with a 100+ product demo catalog.

## Signature features
- **Decision Lab / Budget Matchmaker:** enter a budget and get matching products ranked by a transparent demo value score. Shows budget left and best effective offer.
- **Deal DNA score:** heuristic 0–100 offer score using price, rating, discount and free-delivery bonus. It is a demo indicator, not a guarantee of product quality.
- **Hidden Cost Radar:** displays discount savings, delivery charges and effective price so sticker price alone does not mislead.
- **Buy-Style Match:** shows four easy-to-understand winners for each product: lowest final cost, free delivery, biggest discount and highest store rating.
- 12 fictional sample-store offers per product, search, categories, pagination, wishlist, price alerts, trend estimation and external online search.
- Product catalog is seeded into SQLite on startup; new catalog entries are added to an existing database as well.

## Important data note
Store offers and price history are demonstration data, not live prices. Online Search opens an external shopping search. Live pricing would require authorized retailer APIs or permitted feeds.

## Run on Windows (VS Code PowerShell)
1. Extract the ZIP.
2. Open the project root folder (the one containing `requirements.txt`, `backend`, and `frontend`) in VS Code.
3. Terminal → New Terminal.
4. Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

5. Open http://127.0.0.1:8000
6. API docs: http://127.0.0.1:8000/docs

If the `.venv` already exists, skip the first command. Keep the terminal open while using the website.
