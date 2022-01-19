"""REDCap API methods for Project info"""
from typing import Dict, List, overload
from typing_extensions import Literal

from redcap.methods.base import Base


class ProjectInfo(Base):
    """Responsible for all API methods under 'Projects' in the API Playground"""

    # pylint: disable=redefined-builtin
    @overload
    def export_project_info(self, format: Literal["json"]) -> List[Dict]:
        ...

    @overload
    def export_project_info(self, format: Literal["csv", "xml"]) -> str:
        ...

    def export_project_info(self, format: Literal["json", "csv", "xml"] = "json"):
        """
        Export Project Information

        Args:
            format: Format of returned data

        Returns:
            Union[str, List[Dict]]: Project information

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

        payload = self._basepl(content="project", format=format)

        return self._call_api(payload, "exp_proj")

    # pylint: enable=redefined-builtin
