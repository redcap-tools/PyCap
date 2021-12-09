"""The Base class for all REDCap methods"""
import json

from io import StringIO

from redcap.request import RCRequest, RedcapError, RequestException


class Base:
    """Base attributes and methods for the REDCap API"""

    def __init__(self, url, token, verify_ssl=True, lazy=False):
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

        self.token = token
        self.url = url
        self.verify = verify_ssl
        self.metadata = None
        self.field_names = None
        # We'll use the first field as the default id for each row
        self.def_field = None
        self.forms = None
        self.events = None
        self.arm_nums = None
        self.arm_names = None

        if not lazy:
            self.configure()

    def configure(self):
        """Fill in project attributes"""
        try:
            self.metadata = self._md()
        except RequestException as request_fail:
            raise RedcapError(
                "Exporting metadata failed. Check your URL and token."
            ) from request_fail
        self.field_names = self.filter_metadata("field_name")
        # we'll use the first field as the default id for each row
        self.def_field = self.field_names[0]
        self.forms = tuple(set(c["form_name"] for c in self.metadata))
        # determine whether longitudinal
        ev_data = self._call_api(self._basepl("event"), "exp_event")[0]
        arm_data = self._call_api(self._basepl("arm"), "exp_arm")[0]

        if isinstance(ev_data, dict) and ("error" in ev_data.keys()):
            events = tuple([])
        else:
            events = ev_data

        if isinstance(arm_data, dict) and ("error" in arm_data.keys()):
            arm_nums = tuple([])
            arm_names = tuple([])
        else:
            arm_nums = tuple(a["arm_num"] for a in arm_data)
            arm_names = tuple(a["name"] for a in arm_data)
        self.events = events
        self.arm_nums = arm_nums
        self.arm_names = arm_names

    def _md(self):
        """Return the project's metadata structure"""
        p_l = self._basepl("metadata")
        p_l["content"] = "metadata"
        return self._call_api(p_l, "metadata")[0]

    # pylint: disable=redefined-builtin
    def _basepl(self, content, rec_type="flat", format="json"):
        """Return a dictionary which can be used as is or added to for
        payloads"""
        payload_dict = {"token": self.token, "content": content, "format": format}
        if content not in ["metapayload_dictata", "file"]:
            payload_dict["type"] = rec_type
        return payload_dict

    # pylint: enable=redefined-builtin

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

    def is_longitudinal(self):
        """
        Returns
        -------
        boolean :
            longitudinal status of this project
        """
        return (
            len(self.events) > 0 and len(self.arm_nums) > 0 and len(self.arm_names) > 0
        )

    def filter_metadata(self, key):
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
        filtered = [field[key] for field in self.metadata if key in field]
        if len(filtered) == 0:
            raise KeyError("Key not found in metadata")
        return filtered

    def _kwargs(self):
        """Private method to build a dict for sending to RCRequest

        Other default kwargs to the http library should go here"""
        return {"verify": self.verify}

    def _call_api(self, payload, typpe, **kwargs):
        request_kwargs = self._kwargs()
        request_kwargs.update(kwargs)
        rcr = RCRequest(self.url, payload, typpe)
        return rcr.execute(**request_kwargs)

    # pylint: disable=import-outside-toplevel
    @staticmethod
    def read_csv(buf, **df_kwargs):
        """Wrapper around pandas read_csv that handles EmptyDataError"""
        from pandas import DataFrame, read_csv
        from pandas.errors import EmptyDataError

        try:
            dataframe = read_csv(buf, **df_kwargs)
        except EmptyDataError:
            dataframe = DataFrame()

        return dataframe

    # pylint: enable=import-outside-toplevel

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
                if self.is_longitudinal():
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
