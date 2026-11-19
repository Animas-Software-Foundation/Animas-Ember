extends CanvasLayer
## The pause menu (autoload: GameMenu). Esc, or the MENU button on touch screens.
## Up/Down: choose   Enter/A: select   Esc: close

const FONT_PATH := "res://assets/fonts/animas_pixel.fnt"
const ITEMS := ["Animadex", "Save game", "New game", "Resume"]
const START_MAP := "res://scenes/maps/town.tscn"
const START_TILE := Vector2i(7, 6)

var is_open := false
var _sel := 0
var _confirm_new := false
var _font: Font
var _root: ColorRect
var _highlight: ColorRect
var _rows: Array[Label] = []
var _info: Label
var _status: Label


func _ready() -> void:
	layer = 92
	_font = load(FONT_PATH)
	_root = ColorRect.new()
	_root.color = Color(0, 0, 0, 0.55)
	_root.visible = false
	add_child(_root)
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	var border := ColorRect.new()
	border.color = Color("3b3b3b")
	border.position = Vector2(62, 22)
	border.size = Vector2(116, 116)
	_root.add_child(border)
	var panel := ColorRect.new()
	panel.color = Color("1d1a2b")
	panel.position = Vector2(64, 24)
	panel.size = Vector2(112, 112)
	_root.add_child(panel)
	_highlight = ColorRect.new()
	_highlight.color = Color("e0701a")
	_highlight.size = Vector2(100, 13)
	_root.add_child(_highlight)
	_label("MENU", Vector2(72, 29), Vector2(96, 10))
	for i in ITEMS.size():
		_rows.append(_label("", Vector2(76, 46 + i * 15), Vector2(92, 10)))
	_info = _label("", Vector2(72, 108), Vector2(100, 10))
	_status = _label("", Vector2(72, 120), Vector2(100, 10))
	AnimaDex.closed.connect(_on_dex_closed)


func _label(text: String, pos: Vector2, size: Vector2) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.size = size
	l.add_theme_font_override("font", _font)
	l.add_theme_font_size_override("font_size", 9)
	_root.add_child(l)
	return l


func open() -> void:
	is_open = true
	GameState.input_locked = true
	_sel = 0
	_confirm_new = false
	_status.text = ""
	_refresh()
	_root.visible = true


func close() -> void:
	is_open = false
	_root.visible = false
	GameState.input_locked = false


func _unhandled_input(event: InputEvent) -> void:
	if not is_open:
		if event.is_action_pressed("ui_cancel") and not GameState.input_locked \
				and get_tree().get_first_node_in_group("player") != null:
			open()
			get_viewport().set_input_as_handled()
		return
	if not _root.visible:
		return  # the Animadex is showing and handles its own input
	get_viewport().set_input_as_handled()
	if event.is_action_pressed("ui_cancel"):
		close()
	elif event.is_action_pressed("ui_up"):
		_move(-1)
	elif event.is_action_pressed("ui_down"):
		_move(1)
	elif event.is_action_pressed("ui_accept"):
		_activate()


func _move(delta: int) -> void:
	_sel = (_sel + delta + ITEMS.size()) % ITEMS.size()
	_confirm_new = false
	_status.text = ""
	_refresh()


func _activate() -> void:
	match _sel:
		0:
			_root.visible = false
			AnimaDex.open()
		1:
			_status.text = "Game saved." if SaveGame.save() else "Could not save."
		2:
			if not _confirm_new:
				_confirm_new = true
				_status.text = "Erase everything?"
				_refresh()
			else:
				_new_game()
		3:
			close()


func _new_game() -> void:
	SaveGame.delete_save()
	GameState.reset()
	close()
	SceneTransition.change_scene(START_MAP, START_TILE, Vector2.UP)


func _on_dex_closed() -> void:
	if is_open:
		GameState.input_locked = true
		_root.visible = true
		_refresh()


func _refresh() -> void:
	for i in ITEMS.size():
		_rows[i].text = ITEMS[i] if not (i == 2 and _confirm_new) else "Press A to confirm"
	_highlight.position = Vector2(70, 45 + _sel * 15)
	var t := int(GameState.playtime)
	_info.text = "Time %d:%02d   Seen %d/%d" % [t / 3600, (t / 60) % 60, GameState.seen_count(), AnimaRoster.COUNT]
