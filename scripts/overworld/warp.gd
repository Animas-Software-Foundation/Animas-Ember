class_name Warp
extends Marker2D
## Place on a door / route-edge tile. Stepping onto it loads another map.
## The Player checks the "warps" group after every step.

@export_file("*.tscn") var target_scene := ""
## Tile coordinates (not pixels) where the player appears in the target map.
@export var target_tile := Vector2i.ZERO
@export var target_facing: Facing.Dir = Facing.Dir.DOWN


func _ready() -> void:
	add_to_group("warps")


func get_tile() -> Vector2i:
	return Player.world_to_tile(global_position)


func activate() -> void:
	if target_scene.is_empty():
		push_warning("Warp at %s has no target_scene set." % get_tile())
		return
	SceneTransition.change_scene(target_scene, target_tile, Facing.to_vector(target_facing))
