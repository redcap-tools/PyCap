"""REDCap API methods for Project reports"""
from io import StringIO

from redcap.methods.base import Base


class Reports(Base):
    """Responsible for all API methods under 'Reports' in the API Playground"""

    # pylint: disable=redefined-builtin
    # pylint: disable=too-many-locals
    def export_report(
        self,
        format="json",
        report_id=None,
        raw_or_label="raw",
        raw_or_label_headers="raw",
        export_checkbox_labels="false",
        decimal_character=None,
        df_kwargs=None,
    ):
        """
        Export a report of the Project

        Notes
        -----


        Parameters
        ----------
        report_id : the report ID number provided next to the report name
            on the report list page
        format :  (``'json'``), ``'csv'``, ``'xml'``, ``'df'``
            Format of returned data. ``'json'`` returns json-decoded
            objects while ``'csv'`` and ``'xml'`` return other formats.
            ``'df'`` will attempt to return a ``pandas.DataFrame``.
        raw_or_label : raw [default], label - export the raw coded values or
            labels for the options of multiple choice fields
        raw_or_label_headers : raw [default], label - (for 'csv' format 'flat'
            type only) for the CSV headers, export the variable/field names
            (raw) or the field labels (label)
        export_checkbox_labels : true, false [default] - specifies the format of
            checkbox field values specifically when exporting the data as labels
            (i.e., when rawOrLabel=label). When exporting labels, by default
            (without providing the exportCheckboxLabel flag or if
            exportCheckboxLabel=false), all checkboxes will either have a value
            'Checked' if they are checked or 'Unchecked' if not checked.
            But if exportCheckboxLabel is set to true, it will instead export
            the checkbox value as the checkbox option's label (e.g., 'Choice 1')
            if checked or it will be blank/empty (no value) if not checked.
            If rawOrLabel=false, then the exportCheckboxLabel flag is ignored.
        decimal_character : If specified, force all numbers into same decimal
            format. You may choose to force all data values containing a
            decimal to have the same decimal character, which will be applied
            to all calc fields and number-validated text fields. Options
            include comma ',' or dot/full stop '.', but if left blank/null,
            then it will export numbers using the fields' native decimal format.
            Simply provide the value of either ',' or '.' for this parameter.

        Returns
        -------
        Per Redcap API:
        Data from the project in the format and type specified
        Ordered by the record (primary key of project) and then by event id
        """

        ret_format = format
        if format == "df":
            ret_format = "csv"

        payload = self._basepl(content="report", format=ret_format)
        keys_to_add = (
            report_id,
            raw_or_label,
            raw_or_label_headers,
            export_checkbox_labels,
            decimal_character,
        )
        str_keys = (
            "report_id",
            "rawOrLabel",
            "rawOrLabelHeaders",
            "exportCheckboxLabel",
            "decimalCharacter",
        )
        for key, data in zip(str_keys, keys_to_add):
            if data:
                payload[key] = data
        response, _ = self._call_api(payload, "exp_report")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{ format }'")

        if not df_kwargs:
            if self.is_longitudinal:
                df_kwargs = {"index_col": [self.def_field, "redcap_event_name"]}
            else:
                df_kwargs = {"index_col": self.def_field}
        buf = StringIO(response)
        dataframe = self._read_csv(buf, **df_kwargs)
        buf.close()

        return dataframe

    # pylint: enable=too-many-locals
    # pylint: enable=redefined-builtin
