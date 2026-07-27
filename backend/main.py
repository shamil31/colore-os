from fastapi import FastAPI

app = FastAPI(
    title="Coloré OS",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "project": "Coloré OS",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }