import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from auth import Auth
from account import AccountDB, AccountManager
from database import TaskDB
from task_manager import TaskManager

app = FastAPI()
auth = Auth()  # Create an instance of Auth
account_manager = AccountManager()  # Add account manager instance
task_manager = TaskManager()

# Mount static files with absolute path
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Configure templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/")
def read_root():
    return RedirectResponse(url="/task")


@app.get("/task")
async def get_task(request: Request):
    tasks = task_manager.get_tasks()
    spider_sleep_time = task_manager.get_spider_sleep_time()
    return templates.TemplateResponse(
        "task.html",
        {"request": request, "tasks": tasks, "spider_sleep_time": spider_sleep_time},
    )


@app.post("/create_task")
async def create_task(request: Request):
    form_data = await request.form()
    date = form_data.get("date")

    if not date:
        return {"error": "Date is required"}

    await task_manager.create_task(date)  # type: ignore
    return RedirectResponse(url="/task", status_code=303)


@app.post("/start_task/{task_id}")
async def start_task(task_id: int):
    await task_manager.start_task(task_id)
    return RedirectResponse(url="/task", status_code=303)


@app.post("/stop_task/{task_id}")
async def stop_task(task_id: int):
    await task_manager.stop_task(task_id)
    return RedirectResponse(url="/task", status_code=303)


@app.get("/download/{task_id}")
async def download_file(task_id: int):
    task = task_manager.session.query(TaskDB).get(task_id)
    if task and task.data_file_path and os.path.exists(task.data_file_path):
        return FileResponse(
            task.data_file_path, filename=os.path.basename(task.data_file_path)
        )
    return {"error": "File not found"}


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


@app.get("/account")
def get_accounts(request: Request):
    return templates.TemplateResponse(
        "account.html", {"request": request, "accounts": account_manager.get_accounts()}
    )


@app.post("/account")
async def add_account(request: Request):
    form_data = await request.form()
    username = str(form_data.get("username"))
    password = str(form_data.get("password"))

    success = account_manager.add_account(username, password)
    message = "Account added successfully" if success else "Username already exists"

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "accounts": account_manager.get_accounts(),
            "message": message,
        },
    )


@app.post("/account/delete")
async def delete_account(request: Request):
    form_data = await request.form()
    username = str(form_data.get("username"))

    success = account_manager.delete_account(username)
    message = "Account deleted successfully" if success else "Failed to delete account"

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "accounts": account_manager.get_accounts(),
            "message": message,
        },
    )


@app.post("/account/toggle_active")
async def toggle_active(request: Request):
    form_data = await request.form()
    username = str(form_data.get("username"))
    current_status = form_data.get("current_status") == "True"

    success = await account_manager.set_active_status(username, not current_status)
    message = (
        "Active status toggled successfully"
        if success
        else "Failed to toggle active status"
    )

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "accounts": account_manager.get_accounts(),
            "message": message,
        },
    )


@app.post("/account/login")
async def login_account(request: Request):
    form_data = await request.form()
    username = str(form_data.get("username"))

    account = (
        account_manager.session.query(AccountDB).filter_by(username=username).first()
    )
    if account:
        success = await account_manager.login(account)
        message = (
            "Account logged in successfully" if success else "Failed to login account"
        )
    else:
        message = "Account not found"

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "accounts": account_manager.get_accounts(),
            "message": message,
        },
    )


@app.post("/update_sleep_time")
async def update_sleep_time(request: Request):
    form_data = await request.form()
    sleep_time = int(str(form_data.get("sleep_time", 10)))
    await task_manager.update_sleep_time(sleep_time)
    return RedirectResponse(url="/task", status_code=303)


@app.on_event("shutdown")
async def shutdown_event():
    await account_manager.cleanup()
