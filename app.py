# HookEcho - Minimal Webhook Echo Tester
# Signature: Mourad.Soltani

"""
Minimal webhook echo tester for solo developers.
Generates unique endpoints to inspect incoming HTTP requests.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uuid
import time
from typing import Dict, List, Any
import uvicorn

app = FastAPI(title="HookEcho", description="Minimal webhook echo tester by Mourad.Soltani")

# In-memory store for requests (production would use Redis/DB)
endpoints: Dict[str, List[Dict[str, Any]]] = {}

@app.get("/health")
async def health():
    """Health check endpoint. Must pass for tests."""
    return {"status": "healthy", "service": "hookecho", "signature": "Mourad.Soltani"}

@app.post("/create")
async def create_endpoint():
    """Create a unique webhook endpoint."""
    endpoint_id = str(uuid.uuid4())[:8]
    endpoints[endpoint_id] = []
    return {
        "endpoint_id": endpoint_id,
        "url": f"/hook/{endpoint_id}",
        "full_url_hint": "Use your deployed base + /hook/{id}"
    }

@app.api_route("/hook/{endpoint_id}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def hook(endpoint_id: str, request: Request):
    """Catch-all for webhook requests."""
    if endpoint_id not in endpoints:
        return JSONResponse(status_code=404, content={"error": "Endpoint not found. Create one first."})
    
    body = await request.body()
    try:
        body_json = await request.json()
    except Exception:
        body_json = None
    
    entry = {
        "timestamp": time.time(),
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "body_raw": body.decode("utf-8", errors="replace")[:10000],  # limit size
        "body_json": body_json,
        "client": request.client.host if request.client else None
    }
    endpoints[endpoint_id].append(entry)
    # Keep only last 50
    if len(endpoints[endpoint_id]) > 50:
        endpoints[endpoint_id] = endpoints[endpoint_id][-50:]
    
    return {"received": True, "endpoint_id": endpoint_id, "requests_count": len(endpoints[endpoint_id])}

@app.get("/inspect/{endpoint_id}")
async def inspect(endpoint_id: str):
    """Get all captured requests for an endpoint."""
    if endpoint_id not in endpoints:
        return JSONResponse(status_code=404, content={"error": "Endpoint not found"})
    return {
        "endpoint_id": endpoint_id,
        "requests": endpoints[endpoint_id],
        "count": len(endpoints[endpoint_id])
    }

@app.get("/", response_class=HTMLResponse)
async def home():
    """Simple UI to create and inspect."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HookEcho - Mourad.Soltani</title>
        <style>
            body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            button { padding: 10px 20px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
            pre { background: #f5f5f5; padding: 15px; overflow: auto; border-radius: 4px; }
            input { padding: 8px; width: 300px; margin-right: 10px; }
        </style>
    </head>
    <body>
        <h1>HookEcho</h1>
        <p>Minimal webhook echo tester by <strong>Mourad.Soltani</strong></p>
        <button onclick="create()">Create New Endpoint</button>
        <div id="result"></div>
        <hr>
        <h3>Inspect Endpoint</h3>
        <input id="eid" placeholder="Endpoint ID" />
        <button onclick="inspect()">Inspect</button>
        <pre id="inspect"></pre>
        <script>
            async function create() {
                const res = await fetch('/create', {method: 'POST'});
                const data = await res.json();
                document.getElementById('result').innerHTML = 
                    `<p>Created: <strong>${data.endpoint_id}</strong><br>URL: ${data.url}</p>
                     <p>Send any HTTP request to <code>/hook/${data.endpoint_id}</code></p>`;
            }
            async function inspect() {
                const id = document.getElementById('eid').value;
                const res = await fetch('/inspect/' + id);
                const data = await res.json();
                document.getElementById('inspect').textContent = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
