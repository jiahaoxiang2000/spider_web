from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from auth import Auth

app = FastAPI()
auth = Auth()  # Create an instance of Auth

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/")
def read_root():
    return RedirectResponse(url="/task")


@app.get("/task")
def get_task(request: Request):
    return templates.TemplateResponse("task.html", {"request": request, "tasks": []})


@app.get("/change_authority")
def get_change_authority(request: Request):
    return templates.TemplateResponse("change_authority.html", {"request": request})


@app.post("/change_authority")
async def post_change_authority(request: Request):
    form_data = await request.form()
    username = str(form_data.get("username", ""))
    action = form_data.get("action")

    if not username:
        return templates.TemplateResponse(
            "change_authority.html",
            {"request": request, "result": "Username cannot be empty"},
        )

    result = None
    if action == "upgrade":
        success = await auth.upgrade_authority(username)
        result = (
            f"Successfully upgraded authority for user: {username}"
            if success
            else "Failed to upgrade authority"
        )
    elif action == "downgrade":
        success = await auth.downgrade_authority(username)
        result = (
            f"Successfully downgraded authority for user: {username}"
            if success
            else "Failed to downgrade authority"
        )

    return templates.TemplateResponse(
        "change_authority.html", {"request": request, "result": result}
    )
