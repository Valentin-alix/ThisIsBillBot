from ankama_launcher_emulator.controller.paysafecard_pool import PaysafecardPoolController
from qfluentwidgets import BodyLabel

from src.gui.pages.settings.settings_panel import SettingsPanel


class PaymentSettingsPanel(SettingsPanel):
    def __init__(self) -> None:
        super().__init__(
            "Add a 16-digit Paysafecard code. Existing codes are kept and duplicates are ignored."
        )
        self.selection = self.overview(["Ordre d’utilisation", "Code Paysafecard"])
        self.bind_deletion(self.selection, PaysafecardPoolController().remove_pin)
        self.pin = self.line("Code Paysafecard")
        self.count = BodyLabel("", self)
        self.form.addRow(BodyLabel("Saved codes", self), self.count)
        self.save_button.setText("Add code")

    def reload(self) -> None:
        def render(pins: list[str]) -> None:
            self.count.setText(str(len(pins)))
            self.selection.set_rows([
                (pin, (str(index), " ".join(pin[start:start + 4] for start in range(0, len(pin), 4))))
                for index, pin in enumerate(pins, 1)
            ])
            self.pin.clear()

        self.perform(PaysafecardPoolController().load, render)

    def save(self) -> None:
        pin = self.pin.text()
        self.perform(lambda: PaysafecardPoolController().add_pins([pin]), lambda _: self.reload())
