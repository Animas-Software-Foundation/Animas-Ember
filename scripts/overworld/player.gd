class_name Player
extends Node2D
## Grid-based overworld player, FireRed style:
##  - tap a direction to turn in place, hold it to walk
##  - one tile per step, tweened
##  - Enter / Space (ui_accept) interacts with whatever you're facing

## Emitted after every completed step. Phase 2+ can hook wild encounters,
## trainer line-of-sight, etc. onto this.
signal stepped(tile: Vector2i)

const TILE := 16

@export var move_time := 0.2   ## seconds per tile
@export var turn_delay := 0.1  ## pause after turning before you can walk
@export var look := "hero"  ## character id, see CharacterRoster

var facing := Vector2.DOWN
var moving := false
var _turn_timer := 0.0
var _walk_toggle := false

@onready var _ray: RayCast2D = $RayCast2D
@onready var _look: CharacterSprite = $Look


func _ready() -> void:
	_look.character = look
	if GameState.has_spawn:
		position = tile_to_world(GameState.spawn_tile)
		facing = GameState.spawn_facing
		GameState.has_spawn = false
	else:
		# Snap to the tile grid wherever you dropped the node in the editor.
		position = tile_to_world(world_to_tile(position))
	_play("idle")


static func tile_to_world(tile: Vector2i) -> Vector2:
	return Vector2(tile) * TILE + Vector2(TILE, TILE) / 2.0


static func world_to_tile(pos: Vector2) -> Vector2i:
	return Vector2i((pos / TILE).floor())


func get_tile() -> Vector2i:
	return world_to_tile(position)


func _physics_process(delta: float) -> void:
	if moving or GameState.input_locked:
		return
	if _turn_timer > 0.0:
		_turn_timer -= delta
		return

	if Input.is_action_just_pressed("ui_accept"):
		_interact()
		return

	var dir := _read_direction()
	if dir == Vector2.ZERO:
		return

	if dir != facing:
		# Turn first; walking starts if the key is still held afterwards.
		facing = dir
		_play("idle")
		_turn_timer = turn_delay
		return

	if _can_move(dir):
		_step(dir)


func _read_direction() -> Vector2:
	# One axis at a time, like the GBA games.
	if Input.is_action_pressed("ui_up"):
		return Vector2.UP
	if Input.is_action_pressed("ui_down"):
		return Vector2.DOWN
	if Input.is_action_pressed("ui_left"):
		return Vector2.LEFT
	if Input.is_action_pressed("ui_right"):
		return Vector2.RIGHT
	return Vector2.ZERO


func _can_move(dir: Vector2) -> bool:
	_ray.target_position = dir * TILE
	_ray.force_raycast_update()
	return not _ray.is_colliding()


func _step(dir: Vector2) -> void:
	moving = true
	_walk_toggle = not _walk_toggle
	_play("walk")

	var target := position + dir * TILE
	var tween := create_tween()
	tween.tween_property(self, "position", target, move_time)
	await tween.finished

	position = target
	moving = false
	stepped.emit(get_tile())

	if _check_warp():
		return
	if _read_direction() == Vector2.ZERO:
		_play("idle")


## Returns true if we just stepped onto a warp tile.
func _check_warp() -> bool:
	var tile := get_tile()
	for node in get_tree().get_nodes_in_group("warps"):
		var warp := node as Warp
		if warp != null and warp.get_tile() == tile:
			_play("idle")
			warp.activate()
			return true
	return false


func _interact() -> void:
	_ray.target_position = facing * TILE
	_ray.force_raycast_update()
	var target := _ray.get_collider()
	if target != null and target.has_method("interact"):
		target.interact(facing)


## Turns the player (used when a trainer challenges you).
func face(dir: Vector2) -> void:
	facing = dir
	_play("idle")


## kind: "idle" or "walk" (walking alternates the two step frames).
func _play(kind: String) -> void:
	_look.show_frame(facing, 0 if kind == "idle" else (1 if _walk_toggle else 2))
