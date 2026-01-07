from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton
from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QPixmap, QWheelEvent, QMouseEvent
import os


class MachineInfoWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._original_pixmap: QPixmap = None
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 5.0
        self._zoom_step = 0.05
        self._last_pan_point = QPoint()
        self._panning = False
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(False)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setScaledContents(False)
        self._image_label.setMouseTracking(True)
        self._image_label.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self._image_label.installEventFilter(self)
        
        self._scroll_area.setWidget(self._image_label)
        self._scroll_area.installEventFilter(self)
        self._scroll_area.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        
        self.grabGesture(Qt.GestureType.PinchGesture)
        self.grabGesture(Qt.GestureType.PanGesture)
        
        main_layout.addWidget(self._scroll_area)
        
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(5, 0, 0, 0)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setMinimumSize(40, 40)
        zoom_in_btn.setMaximumSize(40, 40)
        zoom_in_btn.clicked.connect(self._zoom_in)
        controls_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setMinimumSize(40, 40)
        zoom_out_btn.setMaximumSize(40, 40)
        zoom_out_btn.clicked.connect(self._zoom_out)
        controls_layout.addWidget(zoom_out_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.setMinimumSize(40, 40)
        reset_btn.setMaximumSize(40, 40)
        reset_btn.clicked.connect(self._reset_zoom)
        controls_layout.addWidget(reset_btn)
        
        controls_layout.addStretch()
        
        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        controls_widget.setMaximumWidth(50)
        main_layout.addWidget(controls_widget)
        
        self._load_image()
    
    def showEvent(self, event: QEvent) -> None:
        super().showEvent(event)
        if self._original_pixmap and not self._original_pixmap.isNull():
            self._reset_zoom()
    
    def eventFilter(self, obj, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            delta = event.angleDelta().y()
            if abs(delta) > 0:
                zoom_delta = delta / 120.0 * self._zoom_step
                old_zoom = self._zoom_factor
                self._zoom_factor = max(self._min_zoom, min(self._max_zoom, self._zoom_factor + zoom_delta))
                if self._zoom_factor != old_zoom:
                    self._update_image()
            return True
        elif event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
            if event.button() == Qt.MouseButton.LeftButton:
                self._last_pan_point = event.pos()
                self._panning = True
                return True
        elif event.type() == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
            if self._panning and event.buttons() & Qt.MouseButton.LeftButton:
                delta = event.pos() - self._last_pan_point
                h_bar = self._scroll_area.horizontalScrollBar()
                v_bar = self._scroll_area.verticalScrollBar()
                h_bar.setValue(h_bar.value() - delta.x())
                v_bar.setValue(v_bar.value() - delta.y())
                self._last_pan_point = event.pos()
                return True
        elif event.type() == QEvent.Type.MouseButtonRelease and isinstance(event, QMouseEvent):
            if event.button() == Qt.MouseButton.LeftButton:
                self._panning = False
                return True
        return super().eventFilter(obj, event)
    
    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Gesture:
            try:
                from PyQt6.QtWidgets import QGestureEvent
                gesture_event = QGestureEvent(event)
                pinch = gesture_event.gesture(Qt.GestureType.PinchGesture)
                if pinch:
                    scale_factor = pinch.scaleFactor()
                    if scale_factor != 1.0:
                        new_zoom = self._zoom_factor * scale_factor
                        self._zoom_factor = max(self._min_zoom, min(self._max_zoom, new_zoom))
                        self._update_image()
                        pinch.setScaleFactor(1.0)
                    return True
                pan = gesture_event.gesture(Qt.GestureType.PanGesture)
                if pan:
                    delta = pan.delta()
                    h_bar = self._scroll_area.horizontalScrollBar()
                    v_bar = self._scroll_area.verticalScrollBar()
                    h_bar.setValue(h_bar.value() - int(delta.x()))
                    v_bar.setValue(v_bar.value() - int(delta.y()))
                    return True
            except ImportError:
                pass
        return super().event(event)
    
    def _load_image(self) -> None:
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))
        image_path = os.path.join(project_root, "image.png")
        
        if os.path.exists(image_path):
            self._original_pixmap = QPixmap(image_path)
            if not self._original_pixmap.isNull():
                self._reset_zoom()
    
    def _update_image(self) -> None:
        if self._original_pixmap is None or self._original_pixmap.isNull():
            return
        
        scaled_pixmap = self._original_pixmap.scaled(
            int(self._original_pixmap.width() * self._zoom_factor),
            int(self._original_pixmap.height() * self._zoom_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._image_label.setPixmap(scaled_pixmap)
        self._image_label.adjustSize()
    
    def _zoom_in(self) -> None:
        if self._zoom_factor < self._max_zoom:
            self._zoom_factor = min(self._zoom_factor + self._zoom_step, self._max_zoom)
            self._update_image()
    
    def _zoom_out(self) -> None:
        if self._zoom_factor > self._min_zoom:
            self._zoom_factor = max(self._zoom_factor - self._zoom_step, self._min_zoom)
            self._update_image()
    
    def _reset_zoom(self) -> None:
        if self._original_pixmap is None or self._original_pixmap.isNull():
            return
        
        scroll_width = self._scroll_area.width() - 20
        scroll_height = self._scroll_area.height() - 20
        
        if scroll_width > 0 and scroll_height > 0:
            width_ratio = scroll_width / self._original_pixmap.width()
            height_ratio = scroll_height / self._original_pixmap.height()
            self._zoom_factor = min(width_ratio, height_ratio, 1.0)
        else:
            self._zoom_factor = 0.5
        
        self._update_image()
    
    def set_machine(
        self, 
        states: list, 
        transitions: dict
    ) -> None:
        pass
