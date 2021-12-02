"""REDCap API methods for Project field names"""
from io import StringIO

from redcap.methods.base import Base


class FieldNames(Base):
    """Responsible for all API methods under 'Field Names' in the API Playground"""

    # pylint: disable=redefined-builtin
    def export_field_names(self, field=None, format="json", df_kwargs=None):
        """
        Export the project's export field names

        Parameters
        ----------
        fields : str
            Limit exported field name to this field (only single field supported).
            When not provided, all fields returned.
        format : (``'json'``), ``'csv'``, ``'xml'``, ``'df'``
            Return the metadata in native objects, csv or xml.
            ``'df'`` will return a ``pandas.DataFrame``.
        df_kwargs : dict
            Passed to ``pandas.read_csv`` to control construction of
            returned DataFrame.
            by default ``{'index_col': 'original_field_name'}``

        Returns
        -------
        metadata : list, str, ``pandas.DataFrame``
            metadata structure for the project.
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"

        payload = self._basepl("exportFieldNames", format=ret_format)

        if field:
            payload["field"] = field

        response, _ = self._call_api(payload, "exp_field_names")
        # pylint: disable=duplicate-code
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{format}'")
        if not df_kwargs:
            df_kwargs = {"index_col": "original_field_name"}
        return self.read_csv(StringIO(response), **df_kwargs)
        # pylint: enable=duplicate-code

    # pylint: enable=redefined-builtin
