# TODO: Переделать работу на менеджера
from datetime import datetime
from json import dumps, loads
from logging import getLogger
from pathlib import Path

from fastapi import UploadFile

from apps.accounts.db.models import Account
from apps.accounts.db.utils import get_acc_db
from apps.accounts.schemas import AccountStatus, ExportModel, ExportType
from apps.accounts.utils import search_accounts_by_ids
from apps.auth.db.models import User
from core.settings import settings
from exceptions import APIError, NotFoundError

logger = getLogger(__name__)


class AccountManager:
    async def delete(
        self,
        user: User,
        accounts_ids: list[int] | tuple[int],
        soft_delete: bool = True,
    ) -> None:
        true_accs = await search_accounts_by_ids(user, accounts_ids)

        if not true_accs:
            raise NotFoundError("Accounts not found")

        async with get_acc_db() as acc_db:
            true_accs_ids = [acc.id for acc in true_accs]

            if soft_delete:
                list_of_update_dict = [
                    {"id": acc_id, "status": AccountStatus.deleted}
                    for acc_id in true_accs_ids
                ]

                return await acc_db.update(list_of_update_dict)

            return await acc_db.delete([acc_db.__table__.id.in_(true_accs_ids)])


class AccountsFileManger:
    temp_dir = settings.temp_dir

    def __init__(
        self,
        user: User,
        encoding: str = settings.base_encoding,
    ) -> None:
        self.encoding = encoding
        self.user = user

        self.path: Path | None = None

    def delete(self) -> None:
        if self.path:
            self.path.unlink(missing_ok=True)
            self.path = None


class Exporter(AccountsFileManger):
    fieldnames = ("name", "data")
    default_indent = 4

    def __init__(
        self,
        user: User,
        export_model: ExportModel,
        encoding: str = settings.base_encoding,
    ) -> None:
        super().__init__(user, encoding)
        self.type = export_model.export_type
        self.accounts_ids = export_model.accounts_ids
        self.file_name = f"Accounts.{self.type}"
        self.path = self.temp_dir / f"{datetime.now().timestamp()}.{self.type}"

    def create_json(self, data: list[Account], indent: int = default_indent) -> None:
        dump_data = []

        for acc in data:
            dump_data.append(
                {fieldname: getattr(acc, fieldname) for fieldname in self.fieldnames}
            )

        with self.path.open(mode="w", encoding=self.encoding) as file:
            file.write(dumps(dump_data, indent=indent))

    def create_text(self, data: list[Account], indent: int = default_indent) -> None:
        with self.path.open(mode="w", encoding=self.encoding) as file:
            for acc in data:
                file.write(f"Name: {acc.name}\n")

                for key, value in acc.data.items():  # type: str, str
                    file.write(f"{" " * indent}{key.capitalize()}:\n")
                    file.write(f"{" " * indent * 2}{value}\n")

    async def make_export(self) -> None:
        accounts = await search_accounts_by_ids(self.user, self.accounts_ids)

        if self.type is ExportType.json:
            self.create_json(accounts)
        elif self.type is ExportType.txt:
            self.create_text(accounts)


class Uploader(AccountsFileManger):
    temp_dir = settings.temp_dir

    async def __write_uploaded_file(self, uploaded_file: UploadFile) -> None:
        data = await uploaded_file.read()

        self.path = self.temp_dir / uploaded_file.filename

        with self.path.open(mode="wb", encoding=self.encoding) as file:
            file.write(data)

    def __parse_txt_accounts(self) -> list[Account]:
        accounts = []

        with self.path.open(mode="r", encoding=self.encoding) as file:
            name = None

            data = {}
            data_item_name = None

            for line in file.readlines():
                if line == "\n":
                    continue

                if line[:5] == "Name:":
                    if name:
                        accounts.append(
                            Account(name=name, data=data, user_id=self.user.id)
                        )

                    name = line[5:].strip()

                    data = {}
                    data_item_name = None

                    continue

                line = line.strip()

                if data_item_name is None:
                    data_item_name = line.strip(":")

                else:
                    data[data_item_name] = line

                    data_item_name = None

            accounts.append(Account(name=name, data=data, user_id=self.user.id))

        return accounts

    def __parse_json_accounts(self) -> list[Account]:
        accounts = []

        with self.path.open(mode="r", encoding=settings.base_encoding) as file:
            for account_dict in loads(file.read()):  # type: dict
                accounts.append(Account(**account_dict, user_id=self.user.id))

        return accounts

    def __get_file_type(self, filename: str) -> str:
        spited_filename = filename.split(".")

        if len(spited_filename) < 1:
            raise APIError("Не определить формат файла", locations=["upload"])

        file_type = spited_filename[-1]

        if file_type not in ExportType:
            raise APIError(
                f"Неподдерживаемый формат файла: '{file_type if file_type else None}'",
                locations=["upload"],
            )
        return file_type

    async def extract_accounts_from_uploaded_file(
        self,
        uploaded_file: UploadFile,
    ) -> list[Account]:
        file_type = self.__get_file_type(uploaded_file.filename)

        await self.__write_uploaded_file(uploaded_file)

        try:
            if file_type == ExportType.txt:
                accounts = self.__parse_txt_accounts()
            else:
                accounts = self.__parse_json_accounts()

        except Exception as ex:
            logger.warning("File error: %s", ex)

            raise APIError("Ошибка распознавания файла", locations=["upload"])

        finally:
            self.delete()

        return accounts
