"""REDCap API methods for Project info"""
from redcap.methods.base import Base


class ProjectInfo(Base):
    """Responsible for all API methods under 'Projects' in the API Playground"""

    # pylint: disable=redefined-builtin
    def export_project_info(self, format="json"):
        """
        Export Project Information

        Parameters
        ----------
        format: (json, xml, csv), json by default
            Format of returned data
        """

        payload = self._basepl(content="project", format=format)

        return self._call_api(payload, "exp_proj")[0]

    # pylint: enable=redefined-builtin
