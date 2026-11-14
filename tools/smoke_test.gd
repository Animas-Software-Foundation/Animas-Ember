extends SceneTree
## Headless smoke test:  godot --headless --path . -s tools/smoke_test.gd
## Walks through a door, bumps a wall, and talks to an NPC.

var _fails := 0


func _initialize() -> void:
	_run()


func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  ") + label)
	if not ok:
		_fails += 1


func _locked() -> bool:
	return root.get_node("GameState").input_locked


func _player() -> Node:
	return current_scene.find_child("Player", true, false)


func _send(action: String, pressed: bool) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = pressed
	Input.parse_input_event(ev)


func _hold(action: String, secs: float) -> void:
	_send(action, true)
	await create_timer(secs).timeout
	_send(action, false)
	await create_timer(0.05).timeout


func _run() -> void:
	change_scene_to_file("res://scenes/maps/town.tscn")
	await create_timer(0.5).timeout
	_check("town loads, player at (7, 6)", _player() != null and _player().get_tile() == Vector2i(7, 6))
	_check("intro dialogue is showing", _locked())
	for i in 3:  # skip the intro: finish typing, then advance, twice
		await _hold("ui_accept", 0.05)
		await _hold("ui_accept", 0.05)
	await create_timer(0.3).timeout
	_check("dialogue closed, input unlocked", not _locked())

	await _hold("ui_up", 0.35)  # walk onto the door tile
	await create_timer(1.0).timeout
	_check("door warps into the house", current_scene.name == "House")
	_check("player spawns at (4, 6)", _player().get_tile() == Vector2i(4, 6))

	await _hold("ui_left", 1.5)  # should stop at the wall
	_check("wall blocks movement (stopped at x=1)", _player().get_tile().x == 1)

	await _hold("ui_up", 0.05)    # tap: turn up
	await create_timer(0.15).timeout
	await _hold("ui_up", 0.15)    # hold: one step to (1, 5)
	await create_timer(0.3).timeout
	_check("walked one tile up to (1, 5)", _player().get_tile() == Vector2i(1, 5))
	await _hold("ui_right", 0.05) # tap: turn right, now facing the NPC at (2, 5)
	await create_timer(0.15).timeout
	await _hold("ui_right", 0.02) # NPC tile is solid: stay put
	_check("NPC blocks movement (still at x=1)", _player().get_tile().x == 1)
	await _hold("ui_accept", 0.05)
	await create_timer(0.1).timeout
	_check("NPC dialogue opens", _locked())

	print("\nRESULT: %s" % ("ALL PASSED" if _fails == 0 else "%d FAILED" % _fails))
	quit(_fails)
