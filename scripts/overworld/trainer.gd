class_name Trainer
extends NPC
## A trainer who spots you along their line of sight, walks up, and challenges you.
## Battles arrive in a later update: for now the challenge shows their team and counts as a win.

@export var trainer_id := ""      ## unique; used to remember that you beat them
@export var sight_range := 4      ## how many tiles ahead they can see
@export var defeated_lines: Array[String] = ["You beat me fair and square!"]
## Each entry: {anima = "Snuffle", level = 5}
var team: Array[Dictionary] = []


func trainer_name() -> String:
	return CharacterRoster.display_name(look)


func is_defeated() -> bool:
	return GameState.get_flag("beat_" + trainer_id)


func _tile_delta(player: Player) -> Vector2i:
	return player.get_tile() - Player.world_to_tile(position)


## True if the player stands in front of us within sight_range with nothing solid in between.
func can_see(player: Player) -> bool:
	if is_defeated():
		return false
	var dir := Vector2i(Facing.to_vector(facing))
	var delta := _tile_delta(player)
	var dist := 0
	if dir.x != 0 and delta.y == 0 and signi(delta.x) == dir.x:
		dist = absi(delta.x)
	elif dir.y != 0 and delta.x == 0 and signi(delta.y) == dir.y:
		dist = absi(delta.y)
	if dist < 1 or dist > sight_range:
		return false
	var from := global_position + Vector2(dir) * 8.0
	var query := PhysicsRayQueryParameters2D.create(from, player.global_position, 1, [get_rid()])
	return get_world_2d().direct_space_state.intersect_ray(query).is_empty()


## Exclaim, walk up to the player, talk, and "battle".
func challenge(player: Player) -> void:
	GameState.input_locked = true
	var dir := Facing.to_vector(facing)
	_look.show_frame(dir)
	await _exclaim()
	var tiles := maxi(absi(_tile_delta(player).x), absi(_tile_delta(player).y)) - 1
	for i in tiles:
		_look.show_frame(dir, 1 + (i % 2))
		var tween := create_tween()
		tween.tween_property(self, "position", position + dir * Player.TILE, 0.18)
		await tween.finished
	_look.show_frame(dir)
	player.face(-dir)
	await _run_battle()


func interact(player_facing: Vector2) -> void:
	_look.show_frame(-player_facing)
	if is_defeated():
		await Dialogue.say(defeated_lines)
	else:
		await _run_battle()


func _run_battle() -> void:
	await Dialogue.say(dialogue)
	await Encounters.trainer_battle(self)
	GameState.set_flag("beat_" + trainer_id)


func _exclaim() -> void:
	var bubble := Sprite2D.new()
	bubble.texture = _bubble_texture()
	bubble.position = Vector2(0, -13)
	bubble.z_index = 10
	add_child(bubble)
	await get_tree().create_timer(0.6).timeout
	bubble.queue_free()


static func _bubble_texture() -> ImageTexture:
	var img := Image.create(7, 10, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	img.fill_rect(Rect2i(0, 0, 7, 8), Color("221a2c"))
	img.fill_rect(Rect2i(1, 1, 5, 6), Color.WHITE)
	img.fill_rect(Rect2i(3, 2, 1, 3), Color("d8402c"))
	img.set_pixel(3, 6, Color("d8402c"))
	img.fill_rect(Rect2i(3, 8, 1, 2), Color("221a2c"))
	return ImageTexture.create_from_image(img)
