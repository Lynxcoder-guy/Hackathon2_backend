import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from Auth_funcs.auth_endpoints import router as auth_router
from Auth_funcs.database import get_engine


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("BACKEND_CORS_ORIGINS")
    if configured_origins:
        return [
            origin.strip()
            for origin in configured_origins.split(",")
            if origin.strip()
        ]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


app = FastAPI(title="Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)


@app.get("/")
def check_run():
    return {"message": "Backend Running..."}


def run_terminal_tools():
    while True:
        action = input("Enter 'run' to start the API, 'test' for database tools, or 'exit': ")
        if action == "run":
            import uvicorn

            uvicorn.run(app, host="127.0.0.1", port=8000)
        elif action == "test":
            from terminal_tester import terminal_db_tester

            with Session(get_engine()) as session:
                terminal_db_tester(session)
        elif action == "exit":
            return
        else:
            print("Invalid action. Please enter run, test, or exit.")


if __name__ == "__main__":
    run_terminal_tools()
