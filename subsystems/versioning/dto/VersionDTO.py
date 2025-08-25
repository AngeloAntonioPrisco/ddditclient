from dataclasses import dataclass
from typing import List

@dataclass
class VersionDTO:
    repositoryName: str
    resourceName: str
    branchName: str
    versionName: str
    username: str # This field must be retrieved from token before sending DTO
    pushedAt: str # When sending DTO this can be null because the real value will be calculated server side
    comment: str
    tags: List[str]
    mesh: str
    material: str


