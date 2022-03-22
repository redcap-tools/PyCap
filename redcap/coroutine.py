import asyncio
from collections import namedtuple
from optparse import Values
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, overload

from typing_extensions import Literal, TypedDict
from xmlrpc.client import DateTime

from aiohttp import ClientResponseError, ClientResponse, ClientSession

from mergedeep import merge, Strategy

from copy import copy

from datetime import date, datetime

from dict2xml import dict2xml

from uuid import uuid4

import pandas as pd

import itertools

import asyncio

import tqdm

from io import StringIO

from tqdm.contrib.logging import logging_redirect_tqdm

import logging

import json

from request import FileUpload, Json, EmptyJson

RedcapError = ClientResponseError

__author__ = "Shane Buckley <tshanebuckley@gmail.com>"

class _RCCorutine:

    """
    Private class wrapping the request response for a single call to the
    redcap api along with some metadata. Contains the responses along with their 
    headers and some metadata.
    """

    def __init__(
        self,
        url: str,
        payload: Dict,
        fmt: Optional[Literal["json", "csv", "xml"]],
        verify_ssl: Union[bool, str],
        def_field: str,
        return_headers: bool,
        file: Optional[FileUpload],
        sleep_time: int,
        chunks: int,
    ):
        """Constructor"""
        self.creation_time = datetime.now()
        self._id = self._get_id(__name__, date_time=self.creation_time)
        self.logger = logging.getLogger(self._id)
        self.content = dict()
        self.header = dict()
        self.payload = payload
        self.url = url
        self.fmt = fmt
        self.verify_ssl = verify_ssl
        self.def_field = def_field
        self.return_headers = return_headers
        self.file = file
        self.response = dict()
        self.errors = dict()
        self.error_payloads = dict()
        self.records = None
        self.sleep_time = sleep_time
        self.chunks = chunks
        self.chunked = False

    def _get_id(
        self,
        name: str,
        date_time: DateTime = None,
    ) -> str:
        """Method to get a unique id."""
        id = str(uuid4())
        if date_time == None:
            dt = datetime.now()
        else:
            dt = date_time
        dt = date_time
        return "{id}_{dt}_{name}"

    # method to get the records for a project asynchronously
    async def _get_records(
        self,
    ) -> List[str]:
        # determine if the payload is exporting records
        has_records = self.payload['content'] in [
            'record',
            'file',
            'log',
            'participantList'
        ]
        records = [payload[key] for key in payload.keys if 'record' in key]
        # if the payload has defined records
        if len(records) > 0:
            return records
        # if the payload does not have defined records
        elif has_records:
            # generate the simple payload
            payload = {
                'token': self.payload['token'],
                'content': 'record',
                'format': 'json',
                'type': 'flat',
                'csvDelimiter': '',
                'fields[0]': self.def_field,
                'rawOrLabel': 'raw',
                'rawOrLabelHeaders': 'raw',
                'exportCheckboxLabel': 'false',
                'exportSurveyFields': 'false',
                'exportDataAccessGroups': 'false',
                'returnFormat': 'json',
            }
            # run a basic request to fetch these ids
            async with ClientSession() as session:
                async with session.post(self.url, data=payload) as response:
                    resp_dict = await response.json()
                    #print(response)
            # get the ids only from the response
            records = set([x[self.def_field] for x in resp_dict])
            # return the resultant list
            return records
        else:
            return []

    @staticmethod
    def _chunks(
        self,
        lst: List,
        n: int
    ) -> List:
        """Yield successive n-sized chunks from lst."""
        for i in range(0, n):
            yield lst[i::n]

    @staticmethod
    def _merge_chunk(
        self,
        chunk_as_list_of_dicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Runs the deep merge over a chunk to create a single dictionary."""
        chunk_as_dict = dict()
        merge(chunk_as_dict, *chunk_as_list_of_dicts, strategy=Strategy.TYPESAFE_ADDITIVE)
        for key in chunk_as_dict.keys():
            if isinstance(chunk_as_dict[key], list):
                chunk_as_dict[key] = list(set(chunk_as_dict[key]))
        return chunk_as_dict

    @staticmethod
    def _get_payloads(
        self,
        extended_by: str = 'record',
    ) -> Dict[str, Json]:
        """Gets all possible payloads and then chunks them"""

        # create a copy of the overall payload
        pload = copy(self.payload)
        # we want to handle the payload as json
        pload['format'] = 'json'
        pload['returnFormat'] = 'json'
        # get the set of criteria to not extend by
        try:
            not_extended_by = set(pload.keys()) - set(extended_by)
            # get the criteria not being extended by while removing them from the selection_criteria
            not_extended_by = {key: pload.pop(key) for key in not_extended_by}
        except:
            not_extended_by = set()
        # if not_extended_by is empty, then set it to None
        if len(not_extended_by) == 0:
            not_extended_by = None
        # converts the dict into lists with tags identifying the criteria: from criteria: value to <criteria>_value
        criteria_list = [[key + '_' + item for item in pload[key]] for key in pload.keys()]
        # gets all permutations to get all individual calls
        extended_call_list_of_tuples = list(itertools.product(*criteria_list))
        # method to convert the resultant list of tuples into a list of dicts
        def crit_tuple_to_dict(this_tuple, extend_to_dicts=None):
            # get the list of key
            keys = {x.split('_')[0] for x in this_tuple}
            # initialize the dicts
            this_dict = {this_key: [] for this_key in keys}
            # fill the list of dicts
            for item in this_tuple:
                # get the key
                key = item.split('_')[0]
                # get the value
                value = item.replace(key + '_', '', 1)
                # add the value
                this_dict[key].append(value)
            # if there were fields the calls were not extended by
            if extend_to_dicts != None:
                this_dict.update(not_extended_by)
            # return the list of dicts
            return this_dict
        # convert the list of lists back into a list of dicts
        extended_call_list_of_dicts = [crit_tuple_to_dict(this_tuple=x, extend_to_dicts=not_extended_by) for x in extended_call_list_of_tuples]
        # method to re-combine the max-width jobs split into n chunks
        def condense_to_chunks(all_api_calls, num_chunks):
            # chunk the api_calls list
            chunked_calls_unmerged = list(self._chunks(lst=all_api_calls, n=num_chunks))
            # merge the chunks idividual calls
            chunked_calls_merged = [self._merge_chunk(x) for x in chunked_calls_unmerged]
            # return the api calls
            return chunked_calls_merged
        # chunk the calls
        final_call_list = condense_to_chunks(all_api_calls=extended_call_list_of_dicts, num_chunks=self.chunks)
        # drop any empty api_calls
        final_call_list = [x for x in final_call_list if x != {}]
        print(final_call_list)
        print(len(final_call_list))
        # convert the list to a dictionaries, assigning ids to each payload
        final_call_dict = {self._get_id("RCCoroutine"): x for x in final_call_list}
        # return the list of api requests
        return final_call_dict

    @overload
    @staticmethod
    async def _get_content(
        self,
        response: ClientResponse,
        format_type: None,
        return_empty_json: Literal[True],
        return_bytes: Literal[False],
    ) -> EmptyJson:
        ...

    @overload
    @staticmethod
    async def _get_content(
        self,
        response: ClientResponse,
        format_type: None,
        return_empty_json: Literal[False],
        return_bytes: Literal[True],
    ) -> bytes:
        ...

    @overload
    @staticmethod
    async def _get_content(
        self,
        response: ClientResponse,
        format_type: Literal["json"],
        return_empty_json: Literal[False],
        return_bytes: Literal[False],
    ) -> Union[Json, Dict[str, str]]:
        """This should return json, but might also return an error dict"""
        ...

    @overload
    @staticmethod
    async def _get_content(
        self,
        response: ClientResponse,
        format_type: Literal["csv", "xml"],
        return_empty_json: Literal[False],
        return_bytes: Literal[False],
    ) -> str:
        ...

    @staticmethod
    async def _get_content(
        self,
        response: ClientResponse,
        format_type: Optional[Literal["json", "csv", "xml"]],
        return_empty_json: bool,
        return_bytes: bool,
    ):
        """Abstraction for grabbing content from a returned response"""
        # extract the content from the payloads
        streamed_content = await self.response.json()
        # get if any payload had errors
        self.has_errors()
        # check if any payloads had errors
        if len(self.errors.keys()) > 0:
            # build the error string
            error_str = "Request {self._id} had did not complete.\n"
            for e in self.errors.keys():
                error_str + "Coroutine {e} from request {self._id} had the following errors:\n"
                error_str + "\nFrom using the payload:"
                error_str + self.error_payloads[e]
            # log the error
            self.logger.error(error_str)
            # raise an exception, use the content of the first response with an error
            raise RedcapError(self.content.values()[0], message=error_str)

        # if the payloads were extended
        if self.chunked:
            # recombine the payloads
            content = self._recombine_content()
        # otherwise, unlist the single content item and do original PyCap check
        else:
            response = self.response[0]
            # return them to their correct return type
            
            if return_bytes:
                return response.content

            if return_empty_json:
                return [{}]

            if format_type == "json":
                return response.json()

        # don't do anything to csv/xml strings
        return response.text

    @staticmethod
    def _has_errors(
        self,
        content: Dict[str, ClientResponse]
    ):
        """Determines if any requests had errors."""
        if len(content.keys()) > 1:
            def has_error(content):
                bad_request = False
                try:
                    bad_request = "error" in content.text
                    bad_request |= 200 == content.status
                except AttributeError:
                    # we're not dealing with an error dict
                    bad_request = True
                return bad_request
            # add a loop here to run the above method and set self.errors and self.error_payloads
            #for response in self.
        # original method
        else:
            if self.fmt == "json":
                try:
                    bad_request = "error" in content.keys()
                except AttributeError:
                    # we're not dealing with an error dict
                    bad_request = False
            elif self.fmt == "csv":
                bad_request = content.lower().startswith("error:")
            # xml is the default returnFormat for error messages
            elif self.fmt == "xml" or self.fmt is None:
                bad_request = "<error>" in str(content).lower()

        if bad_request:
            raise RedcapError(content)

    @staticmethod
    async def run(
        self,
    ) -> Union[Tuple[Dict[str, Any]], Dict[str, Any]]:

        # get if the request has records
        self.records = self._get_records()
        # if the payloads need extended (chunk > 1 and has records)
        if ( (len(self.records) > 0) and (self.chunks > 0) ):
            # extend by records to get a list of payloads
            payloads = self._get_payloads()
            self.chunked = True
        # otherwise, add to a dictionary
        else:
            payloads = {self._get_id("RCCoroutine"), self.payload}
        # execute the payload(s)
        await self._run_request(payloads) #TODO: add method
        
        # get the content from the responses
        await self._get_content()

        # check for errors
        self._has_errors(self.content)

        # run the response through _return_data to clean it up
        # let self.content be the dictionary of content and the result of this be the final content
        content = await self._return_data()

        if self.return_headers:
                return content, self.headers
        else:
            return content

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

    @overload
    async def _return_data(
        self,
        response: Json,
        content: Literal[
            "exportFieldNames",
            "formEventMapping",
            "metadata",
            "participantList",
            "project",
            "record",
            "report",
            "user",
        ],
        format_type: Literal["json"],
        df_kwargs: None,
        record_type: Literal["flat", "eav"] = "flat",
        chunked: bool = False,
    ) -> Json:
        ...

    @overload
    async def _return_data(
        self,
        response: str,
        content: Literal[
            "exportFieldNames",
            "formEventMapping",
            "metadata",
            "participantList",
            "project",
            "record",
            "report",
            "user",
        ],
        format_type: Literal["csv", "xml"],
        df_kwargs: None,
        record_type: Literal["flat", "eav"] = "flat",
        chunked: bool = False,
    ) -> str:
        ...

    @overload
    async def _return_data(
        self,
        response: str,
        content: Literal[
            "exportFieldNames",
            "formEventMapping",
            "metadata",
            "participantList",
            "project",
            "record",
            "report",
            "user",
        ],
        format_type: Literal["df"],
        df_kwargs: Optional[Dict[str, Any]],
        record_type: Literal["flat", "eav"] = "flat",
        chunked: bool = False,
    ) -> "pd.DataFrame":
        ...

    async def _return_data(
        self,
        response: Union[Json, str],
        content: Literal[
            "exportFieldNames",
            "formEventMapping",
            "metadata",
            "participantList",
            "project",
            "record",
            "report",
            "user",
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

        # original method
        if self.records != []:
            if format_type != "df":
                return response

            if not df_kwargs:
                if (
                    content in ["formEventMapping", "participantList", "project", "user"]
                    or record_type == "eav"
                ):
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

            buf = StringIO(response) # make this async
            dataframe = self._read_csv(buf, **df_kwargs)
            buf.close()

            return dataframe
        # recombine the response if it was chunked
        #else:
