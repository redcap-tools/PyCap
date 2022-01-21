"""REDCap API methods for Project REDCap version"""

from typing import Optional

import semantic_version  # type: ignore

from redcap.methods.base import Base


class Version(Base):
    """Responsible for all API methods under 'REDCap' in the API Playground"""

    def export_version(self) -> Optional[semantic_version.Version]:
        """
        Get the REDCap version

        Returns:
            REDCap version running on the url provided

        Examples:
            >>> import semantic_version
            >>> redcap_version = proj.export_version()
            >>> assert redcap_version >= semantic_version.Version("12.0.1")
        """
        payload = self._initialize_payload("version")
        resp = None

        redcap_version = self._call_api(payload, return_type="str")

        if semantic_version.validate(redcap_version):
            resp = semantic_version.Version(redcap_version)

        return resp
