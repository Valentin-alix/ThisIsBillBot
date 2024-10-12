from dataclasses import dataclass


@dataclass
class InternalSubjects:
    def disconnect_originator(self, originator: object): ...
