"""REDCap API methods for Project users"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, overload

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class DataAccessGroups(Base):
    """Responsible for all API methods under 'Data Access Groups' in the API Playground"""

    @overload
    def export_dags(self, format_type: Literal["json"], df_kwargs: None) -> Json:
        ...

    @overload
    def export_dags(self, format_type: Literal["csv", "xml"], df_kwargs: None) -> str:
        ...

    @overload
    def export_dags(
        self, format_type: Literal["df"], df_kwargs: Optional[Dict[str, Any]]
    ) -> "pd.DataFrame":
        ...

    def export_dags(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the DAGs of the Project

        Args:
            format_type:
                Response return format
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]: List of DAGs

        Examples:
            >>> proj.export_dags()
            [{'data_access_group_name': 'Test DAG', 'unique_group_name': 'test_dag'}]
        """
        payload = self._initialize_payload(content="dag", format_type=format_type)
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="dag",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    @overload
    def import_dags(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ) -> int:
        ...

    @overload
    def import_dags(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["csv", "xml"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ) -> str:
        ...

    def import_dags(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ):
        """
        Import DAGs into the REDCap Project

        Note:
            DAGs can be renamed by simply changing the group name (data_access_group_name).
            DAGs can be created by providing group name value while unique group name should
            be set to blank.

        Args:
            to_import: array of dicts, csv/xml string, `pandas.DataFrame`
                Note:
                    If you pass a csv or xml string, you should use the
                    `import format` parameter appropriately.
            return_format_type:
                Response format. By default, response will be json-decoded.
            import_format:
                Format of incoming data. By default, to_import will be json-encoded

        Returns:
            Union[int, str]: Number of DAGs added or updated

        Examples:
            Create a new data access group
            >>> new_dag = [{"data_access_group_name": "New DAG", "unique_group_name": ""}]
            >>> proj.import_dags(new_dag)
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="dag",
        )
        payload["action"] = "import"

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = self._call_api(payload, return_type)

        return response

    @overload
    def delete_dags(self, dags: List[str], return_format_type: Literal["json"]) -> int:
        ...

    @overload
    def delete_dags(
        self, dags: List[str], return_format_type: Literal["csv", "xml"]
    ) -> str:
        ...

    def delete_dags(
        self,
        dags: List[str],
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Delete dags from the project.

        Args:
            dags: List of usernames to delete from the project
            return_format_type:
                Response format. By default, response will be json-decoded.

        Returns:
            Union[int, str]: Number of dags deleted

        Examples:
            Create a new data access group
            >>> new_dag = [{"data_access_group_name": "New DAG", "unique_group_name": ""}]
            >>> proj.import_dags(new_dag)
            1

            We know that 'New DAG' will automatically be assigned 'new_dag' as it's
            unique group name
            >>> proj.delete_dags(["new_dag"])
            1
        """
        payload = self._initialize_payload(
            content="dag", return_format_type=return_format_type
        )
        payload["action"] = "delete"
        # Turn list of dags into dict, and append to payload
        dags_dict = {f"dags[{ idx }]": dag for idx, dag in enumerate(dags)}
        payload.update(dags_dict)

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="delete"
        )
        response = self._call_api(payload, return_type)
        return response
