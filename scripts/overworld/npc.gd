class_name NPC
extends StaticBody2D
## A talkable NPC with its own look (a character id from CharacterRoster).
## Needs a CollisionShape2D (16x16) so the player's ray hits it.

@export var dialogue: Array[String] = ["Hello there!"]
@export var facing: Facing.Dir = Facing.Dir.DOWN
@export var turn_to_face_player := true
@export var look := "kid_boy"  ## character id, see CharacterRoster

@onready var _look: CharacterSprite = $Look


func _ready() -> void:
	position = Player.tile_to_world(Player.world_to_tile(position))
	_look.character = look
	_look.show_frame(Facing.to_vector(facing))


## Called by the Player when you press the action key while facing this NPC.
func interact(player_facing: Vector2) -> void:
	if turn_to_face_player:
		_look.show_frame(-player_facing)
	await Dialogue.say(dialogue)
