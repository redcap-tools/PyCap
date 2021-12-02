"""The Base class for all REDCap methods"""
import warnings
import semantic_version

from redcap.request import RCRequest, RedcapError, RequestException

# pylint: disable=too-many-instance-attributes


class Base:
    """Base attributes and methods for the REDCap API"""

    def __init__(self, url, token, name="", verify_ssl=True, lazy=False):
        """
        Parameters
        ----------
        url : str
            API URL to your REDCap server
        token : str
            API token to your project
        name : str, optional
            name for project
        verify_ssl : boolean, str
            Verify SSL, default True. Can pass path to CA_BUNDLE.
        """

        self.token = token
        self.name = name
        self.url = url
        self.verify = verify_ssl
        self.metadata = None
        self.redcap_version = None
        self.field_names = None
        # We'll use the first field as the default id for each row
        self.def_field = None
        self.field_labels = None
        self.forms = None
        self.events = None
        self.arm_nums = None
        self.arm_names = None
        self.configured = False

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
        try:
            self.redcap_version = self._rcv()
        except Exception as general_fail:
            raise RedcapError(
                "Determination of REDCap version failed"
            ) from general_fail
        self.field_names = self.filter_metadata("field_name")
        # we'll use the first field as the default id for each row
        self.def_field = self.field_names[0]
        self.field_labels = self.filter_metadata("field_label")
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
        self.configured = True

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
    def _rcv(self):
        payload = self._basepl("version")
        rcv = self._call_api(payload, "version")[0].decode("utf-8")
        resp = None
        if "error" in rcv:
            warnings.warn("Version information not available for this REDCap instance")
            resp = ""
        if semantic_version.validate(rcv):
            resp = semantic_version.Version(rcv)

        return resp

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
