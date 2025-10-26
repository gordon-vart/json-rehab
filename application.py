from fastapi import FastAPI, Request
import dirtyjson
import re
import os  # <- add this

app = FastAPI()
json_pattern = re.compile(r"\{[\s\S]*?\}")

@app.post("/extract")
async def extract_json(request: Request):
    text = await request.body()
    text = text.decode("utf-8")

    matches = json_pattern.findall(text)
    results = []

    for raw in matches:
        try:
            parsed = dirtyjson.loads(raw)
            results.append({"valid": True, "json": parsed})
        except Exception as e:
            results.append({"valid": False, "error": str(e), "raw": raw})

    return {"count": len(results), "results": results}


if __name__ == "__main__":
    import uvicorn

    # read PORT from environment, default to 8080
    port = int(os.environ.get("PORT", 8080))
    
    uvicorn.run("application:app", host="0.0.0.0", port=port, reload=True)
