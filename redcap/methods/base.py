"""The Base class for all REDCap methods"""
from __future__ import annotations

import json

from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    cast,
    overload,
    Tuple,
    TYPE_CHECKING,
    Union,
)

from io import StringIO

from redcap.request import (
    _ContentConfig,
    _RCRequest,
    RedcapError,
    FileUpload,
    Json,
)

if TYPE_CHECKING:
    import pandas as pd

# We're designing class to be lazy by default, and not hit the API unless
# explicitly requested by the user

# return_type type aliases
FileMap = Tuple[bytes, dict]


class Base:
    """Base attributes and methods for the REDCap API"""

    def __init__(
        self,
        url: str,
        token: str,
        verify_ssl: Union[bool, str] = True,
        **request_kwargs,
    ):
        """Initialize a Project, validate url and token"""
        self._validate_url_and_token(url, token)
        self._url = url
        self._token = token
        self.verify_ssl = verify_ssl

        self._validate_request_kwargs(**request_kwargs)
        self._request_kwargs = request_kwargs

        # attributes which require API calls
        self._metadata: Optional[Json] = None
        self._forms: Optional[List[str]] = None
        self._field_names: Optional[List[str]] = None
        self._def_field: Optional[str] = None
        self._is_longitudinal: Optional[bool] = None

    @property
    def url(self) -> str:
        """API URL to a REDCap server"""
        return self._url

    @property
    def token(self) -> str:
        """API token to a project"""
        return self._token

    @property
    def metadata(self) -> Json:
        """Project metadata in JSON format"""
        if self._metadata is None:
            payload = self._initialize_payload("metadata", format_type="json")
            self._metadata = cast(Json, self._call_api(payload, return_type="json"))

        return self._metadata

    @property
    def forms(self) -> List[str]:
        """Project form names"""
        if self._forms is None:
            self._forms = list(set(self._filter_metadata(key="form_name")))

        return self._forms

    @property
    def field_names(self) -> List[str]:
        """Project field names

        Note:
            These are survey field names, not export field names
        """
        if self._field_names is None:
            self._field_names = self._filter_metadata(key="field_name")

        return self._field_names

    @property
    def def_field(self) -> str:
        """The 'record_id' field equivalent for a project"""
        if self._def_field is None:
            self._def_field = self.field_names[0]

        return self._def_field

    @property
    def is_longitudinal(self) -> bool:
        """Whether or not this project is longitudinal"""
        if self._is_longitudinal is None:
            try:
                payload = self._initialize_payload(
                    content="formEventMapping", format_type="json"
                )
                self._call_api(payload, return_type="json")
                self._is_longitudinal = True
            except RedcapError:
                # we should only get a error back if there were no events defined
                # for the project
                self._is_longitudinal = False

        return self._is_longitudinal

    @staticmethod
    def _validate_url_and_token(url: str, token: str) -> None:
        """Run basic validation on user supplied url and token"""
        assert url, "Error! REDCap URL is missing"
        assert token, "Error! REDCap token is missing"
        url_actual_last_5 = url[-5:]
        url_expected_last_5 = "/api/"

        assert url_actual_last_5 == url_expected_last_5, (
            f"Incorrect url format '{ url }', url must end with",
            f"{ url_expected_last_5 }",
        )

        actual_token_len = len(token)
        expected_token_len = 32

        assert actual_token_len == expected_token_len, (
            f"Incorrect token format '{ token }', token must must be",
            f"{ expected_token_len } characters long",
        )

    @staticmethod
    def _validate_request_kwargs(**request_kwargs):
        """Run basic validation on user supplied kwargs for requests"""
        # list of kwargs hardcoded in _RCRequest.execute(...) and self._call_api(...)
        hardcoded_kwargs = [
            "url",
            "data",
            "verify, verify_ssl",
            "return_headers",
            "files",
            "file",
        ]
        unallowed_kwargs = [
            kwarg for kwarg in request_kwargs if kwarg in hardcoded_kwargs
        ]
        assert (
            len(unallowed_kwargs) == 0
        ), f"Not allowed to define {unallowed_kwargs} when initiating object"

    # pylint: disable=import-outside-toplevel
    @staticmethod
    def _read_csv(buf: StringIO, **df_kwargs) -> "pd.DataFrame":
        """Wrapper around pandas read_csv that handles EmptyDataError"""
        import pandas as pd
        from pandas.errors import EmptyDataError

        try:
            dataframe = pd.read_csv(buf, **df_kwargs)
        except EmptyDataError:
            dataframe = pd.DataFrame()

        return dataframe

    # pylint: enable=import-outside-toplevel
    @staticmethod
    def _lookup_return_type(
        format_type: Literal["json", "csv", "xml", "df"],
        request_type: Literal["export", "import", "delete"],
        import_records_format: Optional[
            Literal["count", "ids", "auto_ids", "nothing"]
        ] = None,
    ) -> Literal["json", "str", "int", "count_dict", "ids_list", "empty_json"]:
        """Look up a common return types based on format

        Non-standard return types will need to be passed directly
        to _call_api() via the return_type parameter.

        Args:
            format_type: The provided format for the API call
            request_type:
                The type of API request. Exports behave very differently
                from imports/deletes
            import_records_format:
                Format options from the import_records method. We
                need to use custom logic, because that method has
                different possible return types compared to all other
                methods
        """
        if format_type in ["csv", "xml", "df"]:
            return "str"

        if format_type == "json":
            if request_type == "export":
                return "json"
            if request_type in ["import", "delete"] and not import_records_format:
                return "int"
            if import_records_format in ["count", "auto_ids"]:
                return "count_dict"
            if import_records_format == "ids":
                return "ids_list"
            if import_records_format == "nothing":
                return "empty_json"

        raise ValueError(f"Invalid format_type: { format_type }")

    @overload
    def _filter_metadata(
        self,
        key: str,
        field_name: None = None,
    ) -> list:
        ...

    @overload
    def _filter_metadata(self, key: str, field_name: str) -> str:
        ...

    def _filter_metadata(self, key: str, field_name: Optional[str] = None):
        """Safely filter project metadata based off requested column and field_name"""
        res: Union[list, str]

        if field_name:
            try:
                res = str(
                    [
                        row[key]
                        for row in self.metadata
                        if row["field_name"] == field_name
                    ][0]
                )
            except IndexError:  # pragma: no cover
                print(f"{ key } not in metadata field: { field_name }")
                return ""
        else:
            res = [row[key] for row in self.metadata]

        return res

    def _initialize_payload(
        self,
        content: str,
        format_type: Optional[Literal["json", "csv", "xml", "df"]] = None,
        return_format_type: Optional[Literal["json", "csv", "xml"]] = None,
        record_type: Literal["flat", "eav"] = "flat",
    ) -> Dict[str, str]:
        """Create the default dictionary for payloads

        This can be used as is for simple API requests or added to
        for more complex API requests.

        Args:
            content:
                The 'content' parameter documented in the REDCap API.
                e.g. 'record', 'metadata', 'file', 'event', etc.
            format_type: Format of the data returned for export methods
            return_format_type: Format of the data returned for import/delete methods
            record_type: The type of records being exported/imported
        """
        payload = {"token": self.token, "content": content}

        if format_type:
            if format_type == "df":
                payload["format"] = "csv"
            else:
                payload["format"] = format_type

        if return_format_type:
            payload["returnFormat"] = return_format_type

        if content == "record":
            payload["type"] = record_type

        return payload

    def _initialize_import_payload(
        self,
        to_import: Union[List[dict], str, "pd.DataFrame"],
        import_format: Literal["json", "csv", "xml", "df"],
        return_format_type: Literal["json", "csv", "xml"],
        content: str,
    ) -> Dict[str, Any]:
        """Standardize the data to be imported and add it to the payload

        Args:
            to_import: array of dicts, csv/xml string, ``pandas.DataFrame``
            import_format: Format of incoming data
            return_format_type: Format of outgoing (returned) data
            content: The kind of data that are imported

        Returns:
            payload: The initialized payload dictionary and updated format
        """

        payload = self._initialize_payload(
            content=content, return_format_type=return_format_type
        )
        if import_format == "df":
            to_import = cast("pd.DataFrame", to_import)

            buf = StringIO()
            has_named_index = to_import.index.name is not None
            to_import.to_csv(buf, index=has_named_index)
            payload["data"] = buf.getvalue()
            buf.close()
            import_format = "csv"
        elif import_format == "json":
            payload["data"] = json.dumps(to_import, separators=(",", ":"))
        else:
            # don't do anything to csv/xml
            to_import = cast("str", to_import)
            payload["data"] = to_import

        payload["format"] = import_format
        return payload

    def _return_data(
        self,
        response: Union[Json, str],
        content: Literal[
            "dag",
            "exportFieldNames",
            "formEventMapping",
            "log",
            "metadata",
            "participantList",
            "project",
            "record",
            "report",
            "user",
            "userDagMapping",
            "userRole",
            "userRoleMapping",
            "repeatingFormsEvents",
        ],
        format_type: Literal["json", "csv", "xml", "df"],
        df_kwargs: Optional[Dict[str, Any]] = None,
        record_type: Literal["flat", "eav"] = "flat",
    ):
        """Handle returning data for export methods

        This mostly just stores the logic for the default
        `df_kwargs` value for export methods, when returning
        a dataframe.

        Args:
            response: Output from _call_api
            content:
                The 'content' parameter for the API call.
                Same one used in _initialize_payload
            format_type:
                The format of the response.
                Same one used in _initialize_payload
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. Different defaults exist for
                different content
            record_type:
                Database output structure type.
                Used only for records content
        """
        if format_type != "df":
            return response

        if not df_kwargs:
            if record_type == "eav":
                df_kwargs = {}
            elif content == "exportFieldNames":
                df_kwargs = {"index_col": "original_field_name"}
            elif content == "metadata":
                df_kwargs = {"index_col": "field_name"}
            elif content in ["report", "record"]:
                if self.is_longitudinal:
                    df_kwargs = {"index_col": [self.def_field, "redcap_event_name"]}
                else:
                    df_kwargs = {"index_col": self.def_field}
            # catchall for other endpoints
            else:
                df_kwargs = {}

        response = cast(str, response)

        buf = StringIO(response)
        dataframe = self._read_csv(buf, **df_kwargs)
        buf.close()

        return dataframe

    def _call_api(
        self,
        payload: Dict[str, Any],
        return_type: Literal[
            "file_map", "json", "empty_json", "count_dict", "ids_list", "str", "int"
        ],
        file: Optional[FileUpload] = None,
    ) -> Union[
        FileMap, Json, Dict[str, int], List[dict], List[str], int, str, Literal["1"]
    ]:
        """Make a POST Requst to the REDCap API

        Args:
            payload: Payload to send in POST request
            return_type:
                The data type of the return value. Used
                primarily for static typing, and developer
                understanding of the REDCap API
            file:
                File data to send with file-related API requests
        """
        config = _ContentConfig(
            return_empty_json=return_type == "empty_json",
            return_bytes=return_type == "file_map",
        )

        return_headers = return_type == "file_map"

        rcr = _RCRequest(url=self.url, payload=payload, config=config)
        return rcr.execute(
            verify_ssl=self.verify_ssl,
            return_headers=return_headers,
            file=file,
            **self._request_kwargs,
        )
