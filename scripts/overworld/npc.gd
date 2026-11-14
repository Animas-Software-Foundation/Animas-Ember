class_name NPC
extends StaticBody2D
## A talkable NPC. Needs a CollisionShape2D (16x16) so the player's ray hits it.
## Optional: an AnimatedSprite2D child with idle_down / idle_up / idle_left / idle_right.

@export var dialogue: Array[String] = ["Hello there!"]
@export var facing: Facing.Dir = Facing.Dir.DOWN
@export var turn_to_face_player := true
@export var body_color := Color("4a7bd0")  ## placeholder look, used when there is no sprite
@export var hair_color := Color("3a2a1a")

var _dir := Vector2.DOWN

@onready var _sprite: AnimatedSprite2D = get_node_or_null("AnimatedSprite2D")


func _ready() -> void:
	position = Player.tile_to_world(Player.world_to_tile(position))
	_play_idle(Facing.to_vector(facing))


## Called by the Player when you press the action key while facing this NPC.
func interact(player_facing: Vector2) -> void:
	if turn_to_face_player:
		_play_idle(-player_facing)
	await Dialogue.say(dialogue)


func _draw() -> void:
	if _sprite == null or _sprite.sprite_frames == null:
		PlaceholderSprite.draw_person(self, _dir, body_color, hair_color)


func _play_idle(dir: Vector2) -> void:
	_dir = dir
	queue_redraw()
	if _sprite == null or _sprite.sprite_frames == null:
		return
	var anim := "idle_%s" % Facing.to_name(dir)
	if _sprite.sprite_frames.has_animation(anim):
		_sprite.play(anim)
