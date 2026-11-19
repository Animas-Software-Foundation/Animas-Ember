extends CanvasLayer
## On-screen D-pad and action button for touch devices (autoload: TouchControls).
## Hidden on desktop. Sends the same ui_* actions the keyboard does.

const FONT_PATH := "res://assets/fonts/animas_pixel.fnt"
const BUTTONS := [
	# [action, label, position, size]
	["ui_up", "^", Vector2(23, 89), Vector2(22, 22)],
	["ui_down", "v", Vector2(23, 133), Vector2(22, 22)],
	["ui_left", "<", Vector2(1, 111), Vector2(22, 22)],
	["ui_right", ">", Vector2(45, 111), Vector2(22, 22)],
	["ui_accept", "A", Vector2(206, 126), Vector2(30, 30)],
	["ui_cancel", "MENU", Vector2(196, 4), Vector2(40, 18)],
]


func _ready() -> void:
	layer = 80
	if not (DisplayServer.is_touchscreen_available() or OS.has_feature("mobile")):
		visible = false
		return
	for def in BUTTONS:
		_add_button(def[0], def[1], def[2], def[3])


func _add_button(action: String, label: String, pos: Vector2, size: Vector2) -> void:
	var b := Button.new()
	b.text = label
	b.position = pos
	b.custom_minimum_size = size
	b.size = size
	b.focus_mode = Control.FOCUS_NONE
	b.modulate = Color(1, 1, 1, 0.55)
	b.add_theme_font_override("font", load(FONT_PATH))
	b.add_theme_font_size_override("font_size", 9)
	b.button_down.connect(_send.bind(action, true))
	b.button_up.connect(_send.bind(action, false))
	add_child(b)


func _send(action: String, pressed: bool) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = pressed
	Input.parse_input_event(ev)
