from dataclasses import dataclass, field

from src.interfaces.models.subject import Subject


@dataclass
class SharedSubjects:
    leader_target_map_id: Subject[int] = field(init=False, default_factory=Subject)
    full_pods: Subject = field(init=False, default_factory=Subject)

    def disconnect_originator(self, originator: object):
        self.leader_target_map_id.disconnect_originator(originator)
        self.full_pods.disconnect_originator(originator)
