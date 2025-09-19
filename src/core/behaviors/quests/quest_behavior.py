from dataclasses import dataclass, field

from src.core.behaviors.recovery import RecoverableBehavior
from src.core.behaviors.quests.quest_script_behavior import QuestScriptBehavior
from src.core.engine.quests.quest_criterion import get_required_finished_quest_ids
from src.core.engine.quests.quest_script import QuestCooldown, QuestScript
from src.core.engine.quests.scripts import QUEST_SCRIPTS
from src.services.human_timings import HumanTimingsService


@dataclass
class QuestBehavior(RecoverableBehavior):
    quest_script_behavior: QuestScriptBehavior

    _pending_scripts: list[QuestScript] = field(init=False, default_factory=list[QuestScript])
    _activity_performed: bool = field(init=False, default=False)

    @property
    def activity_performed(self) -> bool:
        return self._activity_performed

    def run(self, scripts: list[QuestScript] | None = None) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(lambda: self.start_quests(scripts=scripts))

    def start_quests(self, scripts: list[QuestScript] | None = None) -> None:
        self._activity_performed = False
        self._pending_scripts = list(QUEST_SCRIPTS if scripts is None else scripts)
        self._run_next_script()

    def _run_next_script(self) -> None:
        """Eligibility is re-checked here, not up front: a script can unlock the next one."""
        while self._pending_scripts:
            script = self._pending_scripts.pop(0)
            if self._is_runnable(script):
                self._activity_performed = True
                return self.quest_script_behavior.start(
                    script=script,
                    callback=self._on_quest_script_finished,
                    parent=self,
                )
        self.finish()

    def _is_runnable(self, script: QuestScript) -> bool:
        if self.game_state.player.level < script.level_min:
            return False
        if script.quest_id is None:
            return True

        missing = [
            required_quest_id
            for required_quest_id in get_required_finished_quest_ids(script.quest_id)
            if not self.game_state.quest.is_finished(required_quest_id)
        ]
        if missing:
            self.logger.info(f"Skipping '{script.name}': quest(s) {missing} not finished yet")
            return False

        if script.cooldown is QuestCooldown.NONE and self.game_state.quest.is_finished(script.quest_id):
            self.logger.info(f"Skipping '{script.name}': done once and not repeatable")
            return False
        return True

    def _on_quest_script_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            self.logger.warning(f"Quest script finished with '{error_code}', moving to the next one")
        self.run_timer(HumanTimingsService().get_timing_long_action(), self._run_next_script)
