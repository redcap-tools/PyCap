"""REDCap API methods for Project file repository"""

from typing import TYPE_CHECKING, Any, Dict, IO, Literal, Optional, Union, cast

from redcap.methods.base import Base, FileMap, Json
from redcap.request import EmptyJson, FileUpload


class FileRepository(Base):
    """Responsible for all API methods under 'File Repository' in the API Playground"""

    def create_folder_in_repository(
        self,
        name: str,
        folder_id: Optional[int] = None,
        dag_id: Optional[int] = None,
        role_id: Optional[int] = None,
        format_type: Literal["json", "csv", "xml"] = "json",
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Create a New Folder in the File Repository

        Args:
            name:
                The desired name of the folder to be created (max length = 150 characters)
            folder_id:
                The folder_id of a specific folder in the File Repository for which you wish
                to create this sub-folder. If none is provided, the folder will be created in
                the top-level directory of the File Repository.
            dag_id:
                The dag_id of the DAG (Data Access Group) to which you wish to restrict
                access for this folder. If none is provided, the folder will accessible to
                users in all DAGs and users in no DAGs.
            role_id:
                The role_id of the User Role to which you wish to restrict access for this
                folder. If none is provided, the folder will accessible to users in all
                User Roles and users in no User Roles.
            format_type:
                Return the metadata in native objects, csv or xml.
            return_format_type:
                Response format. By default, response will be json-decoded.
        Returns:
            Union[str, List[Dict[str, Any]]]:
                List of all changes made to this project, including data exports,
                data changes, and the creation or deletion of users

        Examples:
            >>> proj.create_folder_in_repository(name="New Folder")
            [{'folder_id': ...}]
        """
        payload: Dict[str, Any] = self._initialize_payload(
            content="fileRepository",
            format_type=format_type,
            return_format_type=return_format_type,
        )

        payload["action"] = "createFolder"
        payload["name"] = name

        if folder_id:
            payload["folder_id"] = folder_id

        if dag_id:
            payload["dag_id"] = dag_id

        if role_id:
            payload["role_id"] = role_id

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="fileRepository",
            format_type=format_type,
        )

    def export_file_repository(
        self,
        folder_id: Optional[int] = None,
        format_type: Literal["json", "csv", "xml"] = "json",
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Export of list of files/folders in the File Repository

        Only exports the top-level of files/folders. To see which files are contained
        within a folder, use the `folder_id` parameter

        Args:
            folder_id:
                The folder_id of a specific folder in the File Repository for which you wish
                to search for files/folders. If none is provided, the search will be conducted
                in the top-level directory of the File Repository.
            format_type:
                Return the metadata in native objects, csv or xml.
            return_format_type:
                Response format. By default, response will be json-decoded.
        Returns:
            Union[str, List[Dict[str, Any]]]:
                List of all changes made to this project, including data exports,
                data changes, and the creation or deletion of users

        Examples:
            >>> proj.export_file_repository()
            [{'folder_id': ..., 'name': 'New Folder'}, ...]
        """
        payload: Dict[str, Any] = self._initialize_payload(
            content="fileRepository",
            format_type=format_type,
            return_format_type=return_format_type,
        )

        payload["action"] = "list"

        if folder_id:
            payload["folder_id"] = folder_id

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="fileRepository",
            format_type=format_type,
        )

    def export_file_from_repository(
        self,
        doc_id: int,
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ) -> FileMap:
        """
        Export the contents of a file stored in the File Repository

        Args:
            doc_id: The doc_id of the file in the File Repository
            return_format_type:
                Response format. By default, response will be json-decoded.

        Returns:
            Content of the file and content-type dictionary

        Examples:
            >>> file_dir = proj.export_file_repository()
            >>> text_file = [file for file in file_dir if file["name"] == "test.txt"].pop()
            >>> proj.export_file_from_repository(doc_id=text_file["doc_id"])
            (b'hello', {'name': 'test.txt', 'charset': 'UTF-8'})
        """
        payload = self._initialize_payload(
            content="fileRepository", return_format_type=return_format_type
        )
        # there's no format field in this call
        payload["action"] = "export"
        payload["doc_id"] = doc_id

        content, headers = cast(
            FileMap, self._call_api(payload=payload, return_type="file_map")
        )
        # REDCap adds some useful things in content-type
        content_map = {}
        if "content-type" in headers:
            splat = [
                key_values.strip() for key_values in headers["content-type"].split(";")
            ]
            key_values = [
                (key_values.split("=")[0], key_values.split("=")[1].replace('"', ""))
                for key_values in splat
                if "=" in key_values
            ]
            content_map = dict(key_values)

        return content, content_map

    def import_file_into_repository(
        self,
        file_name: str,
        file_object: IO,
        folder_id: Optional[int] = None,
    ) -> EmptyJson:
        """
        Import the contents of a file represented by file_object into
        the file repository

        Args:
            file_name: File name visible in REDCap UI
            file_object: File object as returned by `open`
            folder_id:
                The folder_id of a specific folder in the File Repository where
                you wish to store the file. If none is provided, the file will
                be stored in the top-level directory of the File Repository.

        Returns:
            Empty JSON object

        Examples:
            >>> import tempfile
            >>> tmp_file = tempfile.TemporaryFile()
            >>> proj.import_file_into_repository(
            ...     file_name="myupload.txt",
            ...     file_object=tmp_file,
            ... )
            [{}]
        """
        payload: Dict[str, Any] = self._initialize_payload(content="fileRepository")
        payload["action"] = "import"

        if folder_id:
            payload["folder_id"] = folder_id

        file_upload_dict: FileUpload = {"file": (file_name, file_object)}

        return cast(
            EmptyJson,
            self._call_api(
                payload=payload, return_type="empty_json", file=file_upload_dict
            ),
        )
