"""REDCap API methods for Project files"""

from typing import TYPE_CHECKING, Dict, Optional, Tuple, Union

from redcap.methods.base import Base

if TYPE_CHECKING:
    from io import TextIOWrapper


class Files(Base):
    """Responsible for all API methods under 'Files' in the API Playground"""

    def _check_file_field(self, field: str) -> bool:
        """Check that field exists and is a file field"""
        is_field = field in self.field_names
        is_file = self._filter_metadata(key="field_type", field_name=field) == "file"
        if not (is_field and is_file):
            msg = f"'{ field }' is not a field or not a 'file' field"
            raise ValueError(msg)

        return True

    def export_file(
        self,
        record: str,
        field: str,
        event: Optional[str] = None,
        return_format: str = "json",
        repeat_instance: Optional[int] = None,
    ) -> Tuple[bytes, Dict]:
        """
        Export the contents of a file stored for a particular record

        Note:
            Unlike other export methods, this only works on a single record.

        Args:
            record: Record ID
            field: Field name containing the file to be exported.
            event: For longitudinal projects, the unique event name
            return_format:
                `'json'`, `'csv'`, `'xml'`
                Format of error message
            repeat_instance:
                (Only for projects with repeating instruments/events)
                The repeat instance number of the repeating event (if longitudinal)
                or the repeating instrument (if classic or longitudinal).

        Returns:
            Content of the file and content-type dictionary
        """
        assert self._check_file_field(field)
        # load up payload
        payload = self._basepl(content="file", format=return_format)
        # there's no format field in this call
        del payload["format"]
        payload["returnFormat"] = return_format
        payload["action"] = "export"
        payload["field"] = field
        payload["record"] = record
        if event:
            payload["event"] = event
        if repeat_instance:
            payload["repeat_instance"] = str(repeat_instance)
        content, headers = self._call_api(payload, "exp_file")
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

    def import_file(
        self,
        record: str,
        field: str,
        file_name: str,
        file_object: "TextIOWrapper",
        event: Optional[str] = None,
        repeat_instance: Optional[Union[int, str]] = None,
        return_format: str = "json",
    ) -> str:
        """
        Import the contents of a file represented by file_object to a
        particular records field

        Args:
            record: Record ID
            field: Field name where the file will go
            file_name: File name visible in REDCap UI
            file_object: File object as returned by `open`
            event: For longitudinal projects, the unique event name
            repeat_instance:
                (Only for projects with repeating instruments/events)
                The repeat instance number of the repeating event (if longitudinal)
                or the repeating instrument (if classic or longitudinal).
            return_format:
                `'json'`, `'csv'`, `'xml'`
                Format of error message

        Returns:
            Response from server as specified by `return_format`
        """
        self._check_file_field(field)
        # load up payload
        payload = self._basepl(content="file", format=return_format)
        # no format in this call
        del payload["format"]
        payload["returnFormat"] = return_format
        payload["action"] = "import"
        payload["field"] = field
        payload["record"] = record
        if event:
            payload["event"] = event
        if repeat_instance:
            payload["repeat_instance"] = repeat_instance
        file_kwargs = {"files": {"file": (file_name, file_object)}}
        return self._call_api(payload, "imp_file", **file_kwargs)[0]

    def delete_file(
        self,
        record: str,
        field: str,
        return_format: str = "json",
        event: Optional[str] = None,
    ) -> Union[str, Dict]:
        """
        Delete a file from REDCap

        Note:
            There is no undo button to this.

        Args:
            record: Record ID
            field: Field name
            return_format:
                `'json'`, `'csv'`, `'xml'`
                Return format for error message
            event: For longitudinal projects, the unique event name

        Returns:
            Response from REDCap after deleting file
        """
        self._check_file_field(field)
        # Load up payload
        payload = self._basepl(content="file", format=return_format)
        del payload["format"]
        payload["returnFormat"] = return_format
        payload["action"] = "delete"
        payload["record"] = record
        payload["field"] = field
        if event:
            payload["event"] = event
        return self._call_api(payload, "del_file")[0]
