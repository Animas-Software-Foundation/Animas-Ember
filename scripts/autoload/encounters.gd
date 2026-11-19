extends CanvasLayer
## Wild-anima and trainer encounter screens (autoload: Encounters).
## Battles arrive in a later update, so for now these show who you met and mark it in the Animadex.
## Usage: await Encounters.wild(Roster id, level)   /   await Encounters.trainer_battle(trainer)

const FONT_PATH := "res://assets/fonts/animas_pixel.fnt"

var _root: ColorRect
var _sprite: TextureRect
var _title: Label
var _team: Control


func _ready() -> void:
	layer = 85
	_root = ColorRect.new()
	_root.color = Color("1d1a2b")
	_root.visible = false
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_sprite = TextureRect.new()
	_sprite.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_sprite.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_root.add_child(_sprite)
	_title = Label.new()
	_title.add_theme_font_override("font", load(FONT_PATH))
	_title.add_theme_font_size_override("font_size", 9)
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.position = Vector2(0, 98)
	_title.size = Vector2(240, 10)
	_root.add_child(_title)
	_team = Control.new()
	_root.add_child(_team)


func wild(anima_id: int, level: int) -> void:
	var anima := AnimaRoster.get_anima(anima_id)
	GameState.mark_seen(anima_id)
	_team.visible = false
	_place_sprite(AnimaRoster.icon(anima_id), Vector2(72, 2), 96)
	_title.text = "%s   Lv %d" % [anima.name, level]
	_root.visible = true
	await Dialogue.say([
		"A wild %s appeared!" % anima.name,
		"It is a %s anima. (Battles arrive in a later update.)" % "/".join(anima.types),
	])
	_root.visible = false
	SaveGame.save()


func trainer_battle(trainer: Trainer) -> void:
	for child in _team.get_children():
		child.queue_free()
	_place_sprite(CharacterRoster.portrait(trainer.look), Vector2(88, 6), 64)
	_title.text = trainer.trainer_name()
	var count := trainer.team.size()
	var x0 := (240 - count * 36) / 2
	for i in count:
		var member: Dictionary = trainer.team[i]
		var id := AnimaRoster.id_of(member.anima)
		GameState.mark_seen(id)
		var icon := TextureRect.new()
		icon.texture = AnimaRoster.icon(id)
		icon.position = Vector2(x0 + i * 36 + 2, 70)
		icon.size = Vector2(32, 32)
		_team.add_child(icon)
	_team.visible = true
	_root.visible = true
	var lead: Dictionary = trainer.team[0] if count > 0 else {anima = "Animus", level = 1}
	await Dialogue.say([
		"%s sent out %s (Lv %d)!" % [trainer.trainer_name(), lead.anima, lead.level],
		"(Battles arrive in a later update. You win by default!)",
	])
	_root.visible = false
	SaveGame.save()


func _place_sprite(tex: Texture2D, pos: Vector2, size: float) -> void:
	_sprite.texture = tex
	_sprite.position = pos
	_sprite.size = Vector2(size, size)
