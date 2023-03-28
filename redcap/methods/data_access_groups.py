"""REDCap API methods for Project data access groups"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class DataAccessGroups(Base):
    """Responsible for all API methods under 'Data Access Groups' in the API Playground"""

    def export_dags(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        # pylint: disable=line-too-long
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
            [{'data_access_group_name': 'Test DAG', 'unique_group_name': 'test_dag', 'data_access_group_id': ...}]
        """
        # pylint:enable=line-too-long
        payload = self._initialize_payload(content="dag", format_type=format_type)
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="dag",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

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
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response

    def delete_dags(
        self,
        dags: List[str],
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Delete dags from the project.

        Args:
            dags: List of dags to delete from the project
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
        response = cast(Union[Json, str], self._call_api(payload, return_type))
        return response

    def switch_dag(
        self,
        dag: str,
    ) -> Literal["1"]:
        """
        Allows the current API user to switch (assign/reassign/unassign)
        their current Data Access Group assignment.

        The current user must have been assigned to multiple DAGs via the
        DAG Switcher page in the project

        Args:
            dag: The unique group name of the Data Access Group to which you wish to switch

        Returns:
            "1" if the user successfully switched DAGs

        Examples:
            >>> proj.switch_dag("test_dag") # doctest: +SKIP
            '1'
        """
        # API docs say that "1" is the only valid value
        payload = self._initialize_payload(content="dag", return_format_type="csv")
        payload["action"] = "switch"
        payload["dag"] = dag

        response = cast(Literal["1"], self._call_api(payload, return_type="str"))
        return response

    def export_user_dag_assignment(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the User-DAG assignment of the Project

        Args:
            format_type:
                Response return format
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]:
                List of User-DAGs assignments

        Examples:
            >>> proj.export_user_dag_assignment()
            [{'username': ..., 'redcap_data_access_group': ''}]
        """
        payload = self._initialize_payload(
            content="userDagMapping", format_type=format_type
        )
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="userDagMapping",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    def import_user_dag_assignment(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ):
        """
        Import User-DAG assignments into the REDCap Project

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
            Union[int, str]:
                Number of User-DAGs assignments added or updated

        Examples:
            Create a new user
            >>> new_user = "pandeharris@gmail.com"
            >>> proj.import_users([{"username": new_user}])
            1

            Add that user to a DAG
            >>> dag_mapping = [
            ...     {"username": new_user, "redcap_data_access_group": "test_dag"}
            ... ]
            >>> proj.import_user_dag_assignment(dag_mapping)
            1

            New user-DAG mapping
            >>> proj.export_user_dag_assignment()
            [{'username': 'pandeharris@gmail.com', 'redcap_data_access_group': 'test_dag'},
            {'username': ..., 'redcap_data_access_group': ''}]

            Remove the user
            >>> proj.delete_users([new_user])
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="userDagMapping",
        )
        payload["action"] = "import"

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response
