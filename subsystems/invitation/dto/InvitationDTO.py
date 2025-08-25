from dataclasses import dataclass

@dataclass
class InvitationDTO:
    toUsername: str
    repositoryName: str