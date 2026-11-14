extends CanvasLayer
## Typewriter dialogue box (autoload: Dialogue). Built in code, so no scene needed.
## Usage: await Dialogue.say(["Hello!", "Welcome to Pixel Town."])

signal _advance

const CHARS_PER_SECOND := 45.0
## Short delay before returning control, so the key press that closed the
## box can't immediately re-trigger an interaction.
const UNLOCK_DELAY := 0.12

var _panel: PanelContainer
var _label: Label
var _active := false
var _typing := false
var _elapsed := 0.0


func _ready() -> void:
	layer = 90

	_panel = PanelContainer.new()
	_panel.visible = false
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	_panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_panel.offset_left = 4
	_panel.offset_right = -4
	_panel.offset_top = -52
	_panel.offset_bottom = -4

	var style := StyleBoxFlat.new()
	style.bg_color = Color.WHITE
	style.border_color = Color("3b3b3b")
	style.set_border_width_all(2)
	style.set_corner_radius_all(3)
	style.set_content_margin_all(6)
	_panel.add_theme_stylebox_override("panel", style)

	_label = Label.new()
	_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_label.add_theme_color_override("font_color", Color("202020"))
	_label.add_theme_font_size_override("font_size", 10)
	_panel.add_child(_label)


func say(lines: Array) -> void:
	if _active:
		return
	_active = true
	GameState.input_locked = true
	_panel.visible = true

	for line in lines:
		_label.text = str(line)
		_label.visible_characters = 0
		_elapsed = 0.0
		_typing = true
		await _advance

	_panel.visible = false
	await get_tree().create_timer(UNLOCK_DELAY).timeout
	GameState.input_locked = false
	_active = false


func _process(delta: float) -> void:
	if not _typing:
		return
	_elapsed += delta
	_label.visible_characters = int(_elapsed * CHARS_PER_SECOND)
	if _label.visible_characters >= _label.text.length():
		_finish_typing()


func _unhandled_input(event: InputEvent) -> void:
	if not _active or not event.is_action_pressed("ui_accept"):
		return
	get_viewport().set_input_as_handled()
	if _typing:
		_finish_typing()  # first press: show the full line
	else:
		_advance.emit()   # second press: next line


func _finish_typing() -> void:
	_typing = false
	_label.visible_characters = -1
