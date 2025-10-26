from fastapi import FastAPI, Request
import dirtyjson
import re
import os  # <- add this

# -------------------------------
# helper function defined first
# -------------------------------
def clean_json_string(s: str) -> str:
    # replace escaped \r, \n, \t
    s = s.replace("\\r", " ").replace("\\n", " ").replace("\\t", " ")
    # remove trailing commas before } or ]
    s = re.sub(r",\s*(?=[}\]])", "", s)
    # optionally replace smart quotes with normal quotes
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    print("cleaned", s)
    return s

def parser_encoded_clean(raw: str):
    """Try parsing with using a clean version of the data."""
    return parser_encoded(clean_json_string(raw))

def parser_encoded(raw: str):
    print("Processing: ", raw)
    # 1. try parsing directly
    try:
        return dirtyjson.loads(raw)
    except Exception:
        pass

    # 2. unescape if it looks like \"name\": patterns
    if '\\"' in raw or raw.startswith("{\\"):
        try:
            unescaped = raw.encode("utf-8").decode("unicode_escape")
            print("unescaped once:", unescaped)
            return dirtyjson.loads(unescaped)
        except Exception:
            pass

    # 5. give up — return None
    return None    
    
def decode_multiple_strategies(raw: str):
    """Try multiple parsing strategies in order until one works."""
    parsers = [parser_encoded, parser_encoded_clean]

    for parser in parsers:
        result = parser(raw)
        if result is not None:
            print("success", result)
            return result
    
    # fallback: return raw string if all fail
    print("Failed to extract", raw)
    return raw

#variables
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
            parsed = decode_multiple_strategies(raw)   # function called here
            results.append({"valid": True, "json": parsed})
        except Exception as e:
            results.append({"valid": False, "error": str(e), "raw": raw})

    return {"count": len(results), "results": results}


if __name__ == "__main__":
    import uvicorn

    # read PORT from environment, default to 8080
    port = int(os.environ.get("PORT", 8080))
    
    uvicorn.run("application:app", host="0.0.0.0", port=port, reload=True)
