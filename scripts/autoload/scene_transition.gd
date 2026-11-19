extends CanvasLayer
## Fade-to-black scene changes (autoload: SceneTransition).
## Usage: SceneTransition.change_scene("res://scenes/maps/route_1.tscn", Vector2i(5, 12))

var _rect: ColorRect
var _busy := false


func _ready() -> void:
	layer = 100
	_rect = ColorRect.new()
	_rect.color = Color.BLACK
	_rect.modulate.a = 0.0
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_rect)
	_rect.set_anchors_preset(Control.PRESET_FULL_RECT)


func change_scene(path: String, tile: Vector2i, facing := Vector2.DOWN, duration := 0.25) -> void:
	if _busy:
		return
	_busy = true
	GameState.input_locked = true
	GameState.has_spawn = true
	GameState.spawn_tile = tile
	GameState.spawn_facing = facing

	await _fade_to(1.0, duration)
	get_tree().change_scene_to_file(path)
	# Give the new scene a couple of frames to run _ready().
	await get_tree().process_frame
	await get_tree().process_frame
	await _fade_to(0.0, duration)

	GameState.input_locked = false
	_busy = false
	SaveGame.save()


func _fade_to(alpha: float, duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_rect, "modulate:a", alpha, duration)
	await tween.finished
