"""The Base class for all REDCap methods"""
import json

from typing import List, Optional, Tuple, Union

from io import StringIO

from redcap.request import RCRequest, RedcapError, RequestException

# We're designing class to be lazy by default, and not hit the API unless
# explicitly requested by the user
# pylint: disable=attribute-defined-outside-init,too-many-instance-attributes


class Base:
    """Base attributes and methods for the REDCap API"""

    def __init__(self, url: str, token: str, verify_ssl: Union[bool, str] = True):
        """
        Parameters
        ----------
        url : str
            API URL to your REDCap server
        token : str
            API token to your project
        verify_ssl : boolean, str
            Verify SSL, default True. Can pass path to CA_BUNDLE.
        """
        self._validate_url_and_token(url, token)
        self._url = url
        self._token = token
        self.verify_ssl = verify_ssl

    @property
    def url(self) -> str:
        """Project url, with validation"""
        return self._url

    @property
    def token(self) -> str:
        """Project token, with validation"""
        return self._token

    @property
    def metadata(self) -> List[dict]:
        """Project metadata in JSON format"""
        try:
            return self._metadata
        except AttributeError:
            self._metadata = self._intialize_metadata()
            return self._metadata
        except RequestException as request_fail:
            raise RedcapError(
                "Exporting metadata failed. Check your URL and token."
            ) from request_fail

    @property
    def field_names(self) -> List[str]:
        """Project field names. Note these are survey field names, not export field names"""
        try:
            return self._field_names
        except AttributeError:
            self._field_names = self.filter_metadata("field_name")
            return self._field_names

    @property
    def def_field(self) -> str:
        """The 'record_id' field equivalent for a project"""
        try:
            return self._def_field
        except AttributeError:
            self._def_field = self.field_names[0]
            return self.def_field

    @property
    def events(self) -> Optional[str]:
        """Events for a longitudinal project"""
        try:
            return self._events
        except AttributeError:
            events = self._call_api(self._basepl("event"), "exp_event")[0]
            # we should only get a dict back if there were no events defined
            # for the project
            if isinstance(events, dict) and "error" in events.keys():
                self._events = None
            # otherwise, we should get JSON
            else:
                self._events = events

            return self._events

    @property
    def is_longitudinal(self) -> bool:
        """The longitudinal status of this project"""
        try:
            return self._is_longitudinal
        except AttributeError:
            if self.events:
                self._is_longitudinal = True
            else:
                self._is_longitudinal = False

            return self._is_longitudinal

    @staticmethod
    def _validate_url_and_token(url: str, token: str) -> None:
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

    # pylint: disable=import-outside-toplevel
    @staticmethod
    def _read_csv(buf, **df_kwargs):
        """Wrapper around pandas read_csv that handles EmptyDataError"""
        from pandas import DataFrame, read_csv
        from pandas.errors import EmptyDataError

        try:
            dataframe = read_csv(buf, **df_kwargs)
        except EmptyDataError:
            dataframe = DataFrame()

        return dataframe

    # pylint: enable=import-outside-toplevel
    def _meta_metadata(self, field, key):
        """Return the value for key for the field in the metadata"""
        metadata_field = ""
        try:
            metadata_field = str(
                [f[key] for f in self.metadata if f["field_name"] == field][0]
            )
        except IndexError:
            print(f"{ key } not in metadata field:{ field }")
            return metadata_field
        else:
            return metadata_field

    def filter_metadata(self, key: str) -> Tuple[str, ...]:
        """
        Return a list of values for the metadata key from each field
        of the project's metadata.

        Parameters
        ----------
        key: str
            A known key in the metadata structure

        Returns
        -------
        filtered :
            attribute list from each field
        """
        # pylint: disable=consider-using-generator
        filtered = tuple([field[key] for field in self.metadata if key in field])
        # pylint: enable=consider-using-generator
        if len(filtered) == 0:
            raise KeyError("Key not found in metadata")
        return filtered

    def _kwargs(self):
        """Private method to build a dict for sending to RCRequest

        Other default kwargs to the http library should go here"""
        return {"verify": self.verify_ssl}

    def _call_api(self, payload, typpe, **kwargs):
        request_kwargs = self._kwargs()
        request_kwargs.update(kwargs)
        rcr = RCRequest(self.url, payload, typpe)
        return rcr.execute(**request_kwargs)

    # pylint: disable=redefined-builtin
    def _basepl(self, content, rec_type="flat", format="json"):
        """Return a dictionary which can be used as is or added to for
        payloads"""
        payload_dict = {"token": self.token, "content": content, "format": format}
        if content not in ["metapayload_dictata", "file"]:
            payload_dict["type"] = rec_type
        return payload_dict

    # pylint: enable=redefined-builtin

    def _intialize_metadata(self):
        """Return the project's metadata structure"""
        p_l = self._basepl("metadata")
        p_l["content"] = "metadata"
        return self._call_api(p_l, "metadata")[0]

    # pylint: disable=redefined-builtin
    def _initialize_import_payload(self, to_import, format, data_type):
        """
        Standardize the data to be imported and add it to the payload

        Parameters
        ----------
        to_import : array of dicts, csv/xml string, ``pandas.DataFrame``
            :note:
                If you pass a csv or xml string, you should use the
                ``format`` parameter appropriately.
        format : ('json'),  'xml', 'csv'
            Format of incoming data. By default, to_import will be json-encoded
        data_type: 'record', 'metadata'
            The kind of data that are imported

        Returns
        -------
        payload : (dict, str)
            The initialized payload dictionary and updated format
        """

        payload = self._basepl(data_type)
        # pylint: disable=comparison-with-callable
        if hasattr(to_import, "to_csv"):
            # We'll assume it's a df
            buf = StringIO()
            if data_type == "record":
                if self.is_longitudinal:
                    csv_kwargs = {"index_label": [self.def_field, "redcap_event_name"]}
                else:
                    csv_kwargs = {"index_label": self.def_field}
            elif data_type == "metadata":
                csv_kwargs = {"index": False}
            to_import.to_csv(buf, **csv_kwargs)
            payload["data"] = buf.getvalue()
            buf.close()
            format = "csv"
        elif format == "json":
            payload["data"] = json.dumps(to_import, separators=(",", ":"))
        else:
            # don't do anything to csv/xml
            payload["data"] = to_import
        # pylint: enable=comparison-with-callable

        payload["format"] = format
        return payload

    # pylint: enable=redefined-builtin
