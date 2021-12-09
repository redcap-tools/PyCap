"""REDCap API methods for Project metadata"""
from io import StringIO

from redcap.methods.base import Base
from redcap.request import RedcapError


class Metadata(Base):
    """Responsible for all API methods under 'Metadata' in the API Playground"""

    # pylint: disable=redefined-builtin
    def export_metadata(self, fields=None, forms=None, format="json", df_kwargs=None):
        """
        Export the project's metadata

        Parameters
        ----------
        fields : list
            Limit exported metadata to these fields
        forms : list
            Limit exported metadata to these forms
        format : (``'json'``), ``'csv'``, ``'xml'``, ``'df'``
            Return the metadata in native objects, csv or xml.
            ``'df'`` will return a ``pandas.DataFrame``.
        df_kwargs : dict
            Passed to ``pandas.read_csv`` to control construction of
            returned DataFrame.
            by default ``{'index_col': 'field_name'}``

        Returns
        -------
        metadata : list, str, ``pandas.DataFrame``
            metadata sttructure for the project.
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self._basepl("metadata", format=ret_format)
        to_add = [fields, forms]
        str_add = ["fields", "forms"]
        for key, data in zip(str_add, to_add):
            if data:
                for i, value in enumerate(data):
                    payload[f"{key}[{i}]"] = value

        response, _ = self._call_api(payload, "metadata")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{format}'")

        if not df_kwargs:
            df_kwargs = {"index_col": "field_name"}
        return self._read_csv(StringIO(response), **df_kwargs)

    def import_metadata(
        self, to_import, format="json", return_format="json", date_format="YMD"
    ):
        """
        Import metadata (DataDict) into the RedCap Project

        Parameters
        ----------
        to_import : array of dicts, csv/xml string, ``pandas.DataFrame``
            :note:
                If you pass a csv or xml string, you should use the
                ``format`` parameter appropriately.
        format : ('json'),  'xml', 'csv'
            Format of incoming data. By default, to_import will be json-encoded
        return_format : ('json'), 'csv', 'xml'
            Response format. By default, response will be json-decoded.
        date_format : ('YMD'), 'DMY', 'MDY'
            Describes the formatting of dates. By default, date strings
            are formatted as 'YYYY-MM-DD' corresponding to 'YMD'. If date
            strings are formatted as 'MM/DD/YYYY' set this parameter as
            'MDY' and if formatted as 'DD/MM/YYYY' set as 'DMY'. No
            other formattings are allowed.

        Returns
        -------
        response : dict, str
            response from REDCap API, json-decoded if ``return_format`` == ``'json'``
            If successful, the number of imported fields
        """
        payload = self._initialize_import_payload(to_import, format, "metadata")
        payload["returnFormat"] = return_format
        payload["dateFormat"] = date_format
        response = self._call_api(payload, "imp_metadata")[0]
        if "error" in str(response):
            raise RedcapError(str(response))
        return response

    # pylint: enable=redefined-builtin
