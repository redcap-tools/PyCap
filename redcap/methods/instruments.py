"""REDCap API methods for Project instruments"""
from io import StringIO

from redcap.methods.base import Base


class Instruments(Base):
    """Responsible for all API methods under 'Instruments' in the API Playground"""

    # pylint: disable=redefined-builtin
    def export_instrument_event_mappings(
        self, arms=None, format="json", df_kwargs=None
    ):
        """
        Export the project's form to event mapping

        Parameters
        ----------
        arms : list
            Limit exported form event mappings to these arm numbers
        format : (``'json'``), ``'csv'``, ``'xml'``
            Return the form event mappings in native objects,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        fem : list, str, ``pandas.DataFrame``
            form-event mapping for the project
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self._basepl("formEventMapping", format=ret_format)

        if arms:
            for i, value in enumerate(arms):
                payload[f"arms[{ i }]"] = value

        response, _ = self._call_api(payload, "exp_fem")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError("Unsupported format: '{ format }'")
        if not df_kwargs:
            df_kwargs = {}

        return self.read_csv(StringIO(response), **df_kwargs)

    # pylint: enable=redefined-builtin
