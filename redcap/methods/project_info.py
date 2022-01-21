"""REDCap API methods for Project info"""
from typing import overload
from typing_extensions import Literal

from redcap.methods.base import Base, Json


class ProjectInfo(Base):
    """Responsible for all API methods under 'Projects' in the API Playground"""

    @overload
    def export_project_info(self, format_type: Literal["json"]) -> Json:
        ...

    @overload
    def export_project_info(self, format_type: Literal["csv", "xml"]) -> str:
        ...

    def export_project_info(self, format_type: Literal["json", "csv", "xml"] = "json"):
        """
        Export Project Information

        Args:
            format_type: Format of returned data

        Returns:
            Union[str, List[Dict[str, Any]]]: Project information

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
        return_type = self._lookup_return_type(format_type)

        return self._call_api(payload, return_type)
