from app import create_app
app = create_app()
import os

print(os.getenv("DATABASE_URL"))

@app.get("/")
def ping():
    return {"ok": True, "msg": "alive"}

if __name__ == "__main__":
    app.run()


