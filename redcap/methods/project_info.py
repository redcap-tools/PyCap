"""REDCap API methods for Project info"""
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class ProjectInfo(Base):
    """Responsible for all API methods under 'Projects' in the API Playground"""

    def export_project_info(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export Project Information

        Args:
            format_type: Format of returned data
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[str, List[Dict[str, Any]], pandas.DataFrame]: Project information

        Examples:
            >>> proj.export_project_info()
            {'project_id': ...
            ...
            'in_production': 0,
            'project_language': 'English',
            'purpose': 0,
            'purpose_other': '',
            ...
            'project_grant_number': '',
            'project_pi_firstname': '',
            'project_pi_lastname': '',
            ...
             'bypass_branching_erase_field_prompt': 0}
        """

        payload = self._initialize_payload(content="project", format_type=format_type)
        return_type = self._lookup_return_type(format_type, request_type="export")

        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="project",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )
