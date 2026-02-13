from fastapi import FastAPI
from app.routers import auth, products, orders

app = FastAPI(title="Shop API", description="Simple shop API with JWT auth")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {"message": "Shop API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
