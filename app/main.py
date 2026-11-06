from fastapi import FastAPI

app = FastAPI(title="Second brain API")


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get("/version")
def verion() -> dict[str, str]:
	return {"version": "0.0.1"}

