from qfluentwidgets import MessageBox


class MessageDialog(MessageBox):
    def __init__(
        self,
        title,
        content,
        parent=None,
        yes_text=None,
        cancel_text=None,
        show_cancel=True,
        show_confirm=True,
    ):
        super().__init__(title, content, parent)

        i18n = parent.window().i18n if parent else None

        if i18n:
            self.yesButton.setText(yes_text or i18n.get("confirm"))
            self.cancelButton.setText(cancel_text or i18n.get("cancel"))

        if not show_cancel:
            self.cancelButton.hide()

        if not show_confirm:
            self.yesButton.hide()
