from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from starlette.background import BackgroundTask
from starlette.responses import FileResponse
from starlette.templating import _TemplateResponse  # noqa

from apps.accounts.managers import AccountManager, Exporter, Uploader
from apps.accounts.schemas import AccountCreateModel, AccountUpdateModel, ExportModel
from apps.accounts.utils import (
    create_accounts,
    create_new_account,
    get_encoding_by_user_agent,
    search_account_by_name,
    update_account,
)
from apps.auth.utils import login_require
from core.ctx_proc import render_template
from core.settings import settings

app_name = "accounts"
router = APIRouter()


@router.get(
    path=settings.search_url,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
@router.get(
    path=settings.home_url,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def home(
    request: Request,
) -> _TemplateResponse:
    return render_template(f"{app_name}/account-home.html", request)


@router.post(
    settings.search_url,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def accounts_search(
    request: Request,
    search: Annotated[str, Form()],
) -> _TemplateResponse:
    user = request.user

    if user and user.is_active:
        accounts = await search_account_by_name(user, name=search)
    else:
        accounts = None

    context = {
        "SEARCH_RESULT": True,
        "accounts": accounts,
    }

    return render_template(
        f"{app_name}/account-home.html",
        request,
        context=context,
    )


@router.post(
    f"/{app_name}/create",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(login_require)],
)
async def accounts_create(request: Request, account_create: AccountCreateModel):
    await create_new_account(request.user.id, account_create)


@router.patch(
    f"/{app_name}/update",
    dependencies=[Depends(login_require)],
)
async def accounts_change(
    request: Request,
    account_update: AccountUpdateModel,
):
    await update_account(request.user.id, account_update)


@router.post(
    f"/{app_name}/upload",
    dependencies=[Depends(login_require)],
    status_code=status.HTTP_201_CREATED,
)
async def accounts_import(
    request: Request,
    file: UploadFile,
):
    uploader = Uploader(
        request.user,
        encoding=get_encoding_by_user_agent(request),
    )
    accounts = await uploader.extract_accounts_from_uploaded_file(file)

    if accounts:
        await create_accounts(accounts)

    return {"created_accounts": len(accounts)}


@router.post(
    f"/{app_name}/export",
    dependencies=[Depends(login_require)],
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
)
async def accounts_export(request: Request, export_model: ExportModel):
    exporter = Exporter(
        request.user,
        export_model,
        encoding=get_encoding_by_user_agent(request),
    )
    delete_task = BackgroundTask(func=exporter.delete)

    await exporter.make_export()

    return FileResponse(
        path=exporter.path,
        filename=exporter.file_name,
        media_type="multipart/form-data",
        background=delete_task,
    )


@router.delete(
    f"/{app_name}/delete/" + "{account_id}",
    dependencies=[Depends(login_require)],
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def accounts_delete(request: Request, account_id: int):
    account_manager = AccountManager()
    await account_manager.delete(request.user, [account_id])
