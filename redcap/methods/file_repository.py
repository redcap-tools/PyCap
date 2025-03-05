"""REDCap API methods for Project file repository"""

from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class FileRepository(Base):
    """Responsible for all API methods under 'File Repository' in the API Playground"""

    def create_folder(
        self,
        name: str,
        folder_id: Optional[int] = None,
        dag_id: Optional[int] = None,
        role_id: Optional[int] = None,
        format_type: Literal["json", "csv", "xml"] = "json",
        return_format_type: Optional[Literal["json", "csv", "xml"]] = None,
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
            >>> proj.create_folder(name="New Folder")
            [{"folder_id": ..., "name": "New Folder"}]
        """
        payload: Dict[str, Any] = self._initialize_payload(
            content="fileRepository", format_type=format_type
        )

        payload["action"] = "createFolder"
        payload["name"] = name

        if folder_id:
            payload["folder_id"] = folder_id

        if dag_id:
            payload["dag_id"] = dag_id

        if role_id:
            payload["role_id"] = role_id

        if return_format_type:
            payload["returnFormat"] = return_format_type

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="fileRepository",
            format_type=format_type,
        )
