class_name CharacterSprite
extends Sprite2D
## Draws one character from assets/characters/characters.png (see CharacterRoster).
## Set `character` to an id such as "hero" or "gardener", then call show_frame().

@export var character := "hero":
	set(value):
		character = value
		_refresh()

var _facing := Vector2.DOWN
var _anim := 0


func _ready() -> void:
	texture = load(CharacterRoster.ATLAS_PATH)
	hframes = CharacterRoster.FRAMES_PER_ROW
	vframes = CharacterRoster.CAST.size()
	_refresh()


## anim: 0 idle, 1 and 2 walking.
func show_frame(facing: Vector2, anim := 0) -> void:
	_facing = facing
	_anim = anim
	_refresh()


func _refresh() -> void:
	if texture == null:
		return
	frame = CharacterRoster.row_of(character) * hframes + Facing.index_of(_facing) * 3 + _anim
