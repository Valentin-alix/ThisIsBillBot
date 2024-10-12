from dataclasses import dataclass

from protos.game.multi_account_pb2 import PartyLeaveEvent, PartyNewMemberEvent, PartyJoinEvent, PartyMemberRemoveEvent
from src.core.frames.frame import Frame


@dataclass
class PartyFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(PartyLeaveEvent, self.on_party_leave_event, originator=self)
        self.event_manager.on(PartyNewMemberEvent, self.on_party_new_member_event, originator=self)
        self.event_manager.on(PartyJoinEvent, self.on_party_join_event, originator=self)
        self.event_manager.on(PartyMemberRemoveEvent, self.on_party_member_remove_event, originator=self)

    def on_party_leave_event(self, msg: PartyLeaveEvent):
        self.game_state.party.party_id = None
        self.game_state.party.party_member_by_id.clear()

    def on_party_new_member_event(self, msg: PartyNewMemberEvent):
        self.game_state.party.party_id = msg.party_id
        self.game_state.party.party_member_by_id[msg.member.id] = msg.member

    def on_party_join_event(self, msg: PartyJoinEvent):
        self.game_state.party.party_id = msg.party_id
        self.game_state.party.party_member_by_id = {member.id:member for member in msg.members}

    def on_party_member_remove_event(self, msg: PartyMemberRemoveEvent):
        del self.game_state.party.party_member_by_id[msg.leaving_player_id]