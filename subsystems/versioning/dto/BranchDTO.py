from dataclasses import dataclass

@dataclass
class BranchDTO:
    repositoryName: str
    resourceName: str
    branchName: str