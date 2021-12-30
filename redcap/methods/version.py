"""REDCap API methods for Project REDCap version"""

import warnings

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
        """
        payload = self._basepl("version")
        redcap_version = self._call_api(payload, "version")[0].decode("utf-8")
        resp: Optional[semantic_version.Version] = None
        if "error" in redcap_version:
            warnings.warn("Version information not available for this REDCap instance")
        if semantic_version.validate(redcap_version):
            resp = semantic_version.Version(redcap_version)

        return resp
