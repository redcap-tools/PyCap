"""REDCap API methods for Project field names"""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Logging(Base):
    """Responsible for all API methods under 'Logging' in the API Playground"""

    # pylint: disable=too-many-locals

    def export_logging(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        return_format_type: Optional[Literal["json", "csv", "xml"]] = None,
        log_type: Optional[
            Literal[
                "export",
                "manage",
                "user",
                "record",
                "record_add",
                "record_edit",
                "record_delete",
                "lock_record",
                "page_view",
            ]
        ] = None,
        user: Optional[str] = None,
        record: Optional[str] = None,
        dag: Optional[str] = None,
        begin_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the project's logs

        Args:
            format_type:
                Return the metadata in native objects, csv or xml.
                `'df'` will return a `pandas.DataFrame`
            return_format_type:
                Response format. By default, response will be json-decoded.
            log_type:
                Filter by specific event types
            user:
                Filter by events created by a certain user
            record:
                Filter by events created for a certain record
            dag:
                Filter by events created by a certain data access group (group ID)
            begin_time:
                Filter by events created after a given timestamp
            end_time:
                Filter by events created before a given timestamp
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame.
        Returns:
            Union[str, List[Dict[str, Any]], "pd.DataFrame"]:
                List of all changes made to this project, including data exports,
                data changes, and the creation or deletion of users

        Examples:
            >>> proj.export_logging()
            [{'timestamp': ..., 'username': ..., 'action': 'Manage/Design ',
            'details': 'Create project ...'}, ...]
        """
        payload: Dict[str, Any] = self._initialize_payload(
            content="log", format_type=format_type
        )
        optional_args = [
            ("returnFormat", return_format_type),
            ("logtype", log_type),
            ("user", user),
            ("record", record),
            ("dag", dag),
            ("beginTime", begin_time),
            ("endTime", end_time),
        ]

        for arg in optional_args:
            arg_name, arg_value = arg
            if arg_value:
                if arg_name in ["beginTime", "endTime"]:
                    arg_value = cast(datetime, arg_value)
                    arg_value = arg_value.strftime("%Y-%m-%d %H:%M:%S")

                payload[arg_name] = arg_value

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="log",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )
        # pylint: enable=too-many-locals
