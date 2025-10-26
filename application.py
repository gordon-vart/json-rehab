from fastapi import FastAPI, Request
import dirtyjson
import re
import os  # <- add this

# -------------------------------
# helper function defined first
# -------------------------------
def decode_dirty_json(input_str):
    try:
        first_pass = dirtyjson.loads(input_str)
    except Exception:
        first_pass = input_str
    if isinstance(first_pass, str):
        try:
            second_pass = dirtyjson.loads(first_pass)
            return second_pass
        except Exception:
            return first_pass
    else:
        return first_pass
    
app = FastAPI()
json_pattern = re.compile(r"\{[\s\S]*?\}")

# -------------------------------
# route handler uses the function
# -------------------------------
@app.post("/extract")
async def extract_json(request: Request):
    text = await request.body()
    text = text.decode("utf-8")
    text = text.replace("\\r", " ").replace("\\n", " ")

    matches = json_pattern.findall(text)
    results = []

    for raw in matches:
        try:
            parsed = decode_dirty_json(raw)   # function called here
            results.append({"valid": True, "json": parsed})
        except Exception as e:
            results.append({"valid": False, "error": str(e), "raw": raw})

    return {"count": len(results), "results": results}


if __name__ == "__main__":
    import uvicorn

    # read PORT from environment, default to 8080
    port = int(os.environ.get("PORT", 8080))
    
    uvicorn.run("application:app", host="0.0.0.0", port=port, reload=True)
