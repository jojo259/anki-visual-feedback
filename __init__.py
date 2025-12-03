from aqt import mw
from aqt.gui_hooks import reviewer_did_answer_card
from aqt.qt import *
from aqt.utils import showInfo

def get_config():
    return mw.addonManager.getConfig(__name__)

def flash_feedback(reviewer, card, ease):
    config = get_config()
    if not config:
        return

    ease_str = str(ease)
    colors = config.get("colors", {})
    if ease_str not in colors:
        return

    color = colors[ease_str]
    duration = config.get("animation_duration", 0.3)
    size = config.get("feedback_size", 30)
    opacity = config.get("opacity", 1.0)

    try:
        size = int(size)
    except ValueError:
        size = 30

    js = f"""
    (function() {{
        let overlay = document.getElementById('visual-feedback-overlay');
        if (!overlay) {{
            overlay = document.createElement('div');
            overlay.id = 'visual-feedback-overlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.pointerEvents = 'none';
            overlay.style.zIndex = '9999';
            document.body.appendChild(overlay);
        }}
        
        overlay.style.transition = 'none';
        overlay.style.opacity = '{opacity}';
        overlay.style.boxShadow = 'inset 0 0 {size}px {size/2}px {color}';
        
        void overlay.offsetWidth;
        
        overlay.style.transition = 'box-shadow {duration}s ease-out';
        overlay.style.boxShadow = 'inset 0 0 0 0 transparent';
    }})();
    """
    
    mw.reviewer.web.eval(js)

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visual Feedback Settings")
        self.config = get_config()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.init_ui()

    def init_ui(self):
        duration_group = QGroupBox("Animation Length")
        duration_layout = QVBoxLayout()
        
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setMinimum(1)
        self.duration_slider.setMaximum(10)
        self.duration_slider.setSingleStep(1)
        current_duration = self.config.get("animation_duration", 0.3)
        self.duration_slider.setValue(int(current_duration * 10))
        
        self.duration_label = QLabel(f"{current_duration}s")
        self.duration_slider.valueChanged.connect(
            lambda v: self.duration_label.setText(f"{v/10}s")
        )
        
        duration_layout.addWidget(self.duration_label)
        duration_layout.addWidget(self.duration_slider)
        duration_group.setLayout(duration_layout)
        self.layout.addWidget(duration_group)

        opacity_group = QGroupBox("Opacity")
        opacity_layout = QVBoxLayout()
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(1)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setSingleStep(1)
        current_opacity = self.config.get("opacity", 1.0)
        self.opacity_slider.setValue(int(current_opacity * 100))
        
        self.opacity_label = QLabel(f"{int(current_opacity * 100)}%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        opacity_layout.addWidget(self.opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_group.setLayout(opacity_layout)
        self.layout.addWidget(opacity_group)

        size_group = QGroupBox("Feedback Size (pixels)")
        size_layout = QVBoxLayout()
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setSingleStep(1)
        
        current_size = self.config.get("feedback_size", 30)
        self.size_slider.setValue(max(1, int(current_size / 10)))
        
        self.size_label = QLabel(f"{self.size_slider.value() * 10}px")
        self.size_slider.valueChanged.connect(
            lambda v: self.size_label.setText(f"{v * 10}px")
        )
        
        size_layout.addWidget(self.size_label)
        size_layout.addWidget(self.size_slider)
        size_group.setLayout(size_layout)
        self.layout.addWidget(size_group)

        colors_group = QGroupBox("Colors (CSS)")
        colors_layout = QFormLayout()
        
        self.color_inputs = {}
        labels = {
            "1": "Again",
            "2": "Hard",
            "3": "Good",
            "4": "Easy"
        }
        
        current_colors = self.config.get("colors", {})
        
        for key, label in labels.items():
            line_edit = QLineEdit(current_colors.get(key, ""))
            self.color_inputs[key] = line_edit
            colors_layout.addRow(label, line_edit)
            
        colors_group.setLayout(colors_layout)
        self.layout.addWidget(colors_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def accept(self):
        new_config = {
            "animation_duration": self.duration_slider.value() / 10.0,
            "feedback_size": self.size_slider.value() * 10,
            "opacity": self.opacity_slider.value() / 100.0,
            "colors": {
                k: v.text() for k, v in self.color_inputs.items()
            }
        }
        mw.addonManager.writeConfig(__name__, new_config)
        super().accept()

def on_config():
    dialog = ConfigDialog(mw)
    dialog.exec()

mw.addonManager.setConfigAction(__name__, on_config)
reviewer_did_answer_card.append(flash_feedback)
