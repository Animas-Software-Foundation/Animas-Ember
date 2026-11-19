extends CanvasLayer
## The Animadex: browse all 151 animas (autoload: AnimaDex).
## Open it from the menu (Esc, or the MENU button on touch screens).
## Up/Down: move   Left/Right: jump 10   Enter/A: switch Stats <-> Info   Esc: close

const FONT_PATH := "res://assets/fonts/animas_pixel.fnt"
const ROWS := 10
const STAT_NAMES := ["HP", "ATK", "DEF", "SPD", "SPC"]

signal closed

var is_open := false
var _sel := 1
var _page := 0
var _font: Font
var _root: ColorRect
var _row_labels: Array[Label] = []
var _highlight: ColorRect
var _count: Label
var _sprite: TextureRect
var _no: Label
var _name: Label
var _types: Label
var _size: Label
var _stat_names: Array[Label] = []
var _stat_bars: Array[ColorRect] = []
var _stat_vals: Array[Label] = []
var _info: Label


func _ready() -> void:
	layer = 95
	_font = load(FONT_PATH)
	_root = ColorRect.new()
	_root.color = Color("1d1a2b")
	_root.visible = false
	add_child(_root)
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_label("ANIMADEX", Vector2(6, 2))
	_count = _label("", Vector2(150, 2), Vector2(84, 10))
	_count.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_highlight = ColorRect.new()
	_highlight.color = Color("e0701a")
	_highlight.size = Vector2(102, 12)
	_root.add_child(_highlight)
	for i in ROWS:
		_row_labels.append(_label("", Vector2(6, 14 + i * 12 + 1), Vector2(98, 10)))
	_sprite = TextureRect.new()
	_sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_sprite.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_sprite.position = Vector2(110, 14)
	_sprite.size = Vector2(64, 64)
	_root.add_child(_sprite)
	_no = _label("", Vector2(178, 14), Vector2(58, 10))
	_types = _label("", Vector2(178, 26), Vector2(58, 20))
	_size = _label("", Vector2(178, 54), Vector2(58, 20))
	_name = _label("", Vector2(110, 78), Vector2(126, 10))
	for i in STAT_NAMES.size():
		var y := 90 + i * 12
		var l := _label(STAT_NAMES[i], Vector2(110, y), Vector2(26, 10))
		_stat_names.append(l)
		var bar := ColorRect.new()
		bar.color = Color("f08a24")
		bar.position = Vector2(138, y + 2)
		bar.size = Vector2(4, 5)
		_root.add_child(bar)
		_stat_bars.append(bar)
		_stat_vals.append(_label("", Vector2(206, y), Vector2(30, 10)))
	_info = _label("", Vector2(110, 90), Vector2(126, 70))
	_info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART


func _label(text: String, pos: Vector2, size := Vector2.ZERO) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	if size != Vector2.ZERO:
		l.size = size
	l.add_theme_font_override("font", _font)
	l.add_theme_font_size_override("font_size", 9)
	l.add_theme_constant_override("line_spacing", 0)
	_root.add_child(l)
	return l


func open() -> void:
	is_open = true
	GameState.input_locked = true
	_page = 0
	_refresh()
	_root.visible = true


func close() -> void:
	is_open = false
	_root.visible = false
	GameState.input_locked = false
	closed.emit()


func _unhandled_input(event: InputEvent) -> void:
	if not is_open:
		return
	get_viewport().set_input_as_handled()
	if event.is_action_pressed("ui_cancel"):
		close()
	elif event.is_action_pressed("ui_accept"):
		_page = 1 - _page
		_refresh()
	elif event.is_action_pressed("ui_up", true):
		_move(-1)
	elif event.is_action_pressed("ui_down", true):
		_move(1)
	elif event.is_action_pressed("ui_left", true):
		_move(-10)
	elif event.is_action_pressed("ui_right", true):
		_move(10)


func _move(delta: int) -> void:
	_sel = clampi(_sel + delta, 1, AnimaRoster.COUNT)
	_refresh()


func _refresh() -> void:
	var top := clampi(_sel - ROWS / 2, 1, AnimaRoster.COUNT - ROWS + 1)
	for i in ROWS:
		var id := top + i
		var a := AnimaRoster.get_anima(id)
		_row_labels[i].text = "%03d %s" % [id, a.name]
		_row_labels[i].modulate = Color.WHITE if GameState.seen.has(id) else Color(1, 1, 1, 0.55)
		if id == _sel:
			_highlight.position = Vector2(4, 14 + i * 12)
	_count.text = "Seen %d/%d" % [GameState.seen_count(), AnimaRoster.COUNT]
	var cur := AnimaRoster.get_anima(_sel)
	_sprite.texture = AnimaRoster.icon(_sel)
	_no.text = "No.%03d" % _sel
	_name.text = cur.name
	_size.text = "Ht %.1fm\nWt %.1fkg" % [cur.height, cur.weight]
	_types.text = "\n".join(cur.types)
	_info.visible = _page == 1
	for i in STAT_NAMES.size():
		var shown := _page == 0
		_stat_bars[i].visible = shown
		_stat_vals[i].visible = shown
		_stat_names[i].visible = shown
		var v: int = cur.stats[i]
		_stat_bars[i].size.x = maxf(2.0, v / 160.0 * 62.0)
		_stat_vals[i].text = str(v)
	if _page == 1:
		var evo := ""
		if cur.evolves_to > 0:
			evo = "\nNext: %s Lv %d" % [AnimaRoster.get_anima(cur.evolves_to).name, cur.evolve_level]
		_info.text = cur.dex + evo
