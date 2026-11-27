import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from Auth_funcs.auth_endpoints import router as auth_router
from Auth_funcs.database import get_engine

from Pre_Checkup.pre_checkup_endpoints import router as pre_checkup_router
from Post_Checkup.post_checkup_endpoints import router as post_checkup_router
from Weekly_Condition_logs.wcl_endpoints import router as wcl_router
from Health_Stats.health_stats_endpoints import router as health_stats_router

def get_cors_origins() -> tuple[list[str], str | None]:
    configured_origins = os.getenv("BACKEND_CORS_ORIGINS")
    if configured_origins:
        return (
            [
                origin.strip()
                for origin in configured_origins.split(",")
                if origin.strip()
            ],
            None,
        )
    return (
        [],
        r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    )


api = FastAPI(title="Backend API")
cors_origins, cors_origin_regex = get_cors_origins()

api.include_router(auth_router)
api.include_router(post_checkup_router)
api.include_router(pre_checkup_router)
api.include_router(wcl_router)
api.include_router(health_stats_router)


@api.get("/")
def check_run():
    return {"message": "Backend Running..."}


app = CORSMiddleware(
    app=api,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
