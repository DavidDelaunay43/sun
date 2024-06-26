class WindowManager:
    dialog_instances = {}

    @classmethod
    def show_dialog(cls, dialog_class):
        if dialog_class not in cls.dialog_instances:
            cls.dialog_instances[dialog_class] = dialog_class()

        dialog_instance = cls.dialog_instances[dialog_class]

        if dialog_instance.isHidden() or not dialog_instance.isVisible():
            dialog_instance.show()
        else:
            dialog_instance.raise_()
            dialog_instance.activateWindow()
