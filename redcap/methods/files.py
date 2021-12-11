"""REDCap API methods for Project files"""

from redcap.methods.base import Base


class Files(Base):
    """Responsible for all API methods under 'Files' in the API Playground"""

    def _check_file_field(self, field):
        """Check that field exists and is a file field"""
        is_field = field in self.field_names
        is_file = self._filter_metadata(key="field_type", field_name=field) == "file"
        if not (is_field and is_file):
            msg = f"'{ field }' is not a field or not a 'file' field"
            raise ValueError(msg)

        return True

    def export_file(
        self, record, field, event=None, return_format="json", repeat_instance=None
    ):
        """
        Export the contents of a file stored for a particular record

        Notes
        -----
        Unlike other export methods, this works on a single record.

        Parameters
        ----------
        record : str
            record ID
        field : str
            field name containing the file to be exported.
        event: str
            for longitudinal projects, specify the unique event here
        return_format: ('json'), 'csv', 'xml'
            format of error message
        repeat_instance: (None),str,int

        Returns
        -------
        content : bytes
            content of the file
        content_map : dict
            content-type dictionary
        """
        self._check_file_field(field)
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
        record,
        field,
        fname,
        fobj,
        event=None,
        repeat_instance=None,
        return_format="json",
    ):
        """
        Import the contents of a file represented by fobj to a
        particular records field

        Parameters
        ----------
        record : str
            record ID
        field : str
            field name where the file will go
        fname : str
            file name visible in REDCap UI
        fobj : file object
            file object as returned by `open`
        event : str
            for longitudinal projects, specify the unique event here
        repeat_instance : int
            (only for projects with repeating instruments/events)
            The repeat instance number of the repeating event (if longitudinal)
            or the repeating instrument (if classic or longitudinal).
        return_format : ('json'), 'csv', 'xml'
            format of error message

        Returns
        -------
        response :
            response from server as specified by ``return_format``
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
        file_kwargs = {"files": {"file": (fname, fobj)}}
        return self._call_api(payload, "imp_file", **file_kwargs)[0]

    def delete_file(self, record, field, return_format="json", event=None):
        """
        Delete a file from REDCap

        Notes
        -----
        There is no undo button to this.

        Parameters
        ----------
        record : str
            record ID
        field : str
            field name
        return_format : (``'json'``), ``'csv'``, ``'xml'``
            return format for error message
        event : str
            If longitudinal project, event to delete file from

        Returns
        -------
        response : dict, str
            response from REDCap after deleting file
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
