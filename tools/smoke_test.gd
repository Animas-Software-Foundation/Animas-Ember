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


func _close_dialogue() -> void:
	for i in 40:
		if not _locked():
			return
		await _hold("ui_accept", 0.04)


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

	await _close_dialogue()

	# ---- Phase 2: roster, Animadex, encounters, trainers ----
	var roster = load("res://scripts/data/anima_roster.gd")
	_check("roster has 151 animas", roster.COUNT == 151 and roster.ANIMAS.size() == 151)
	var names := {}
	var evo_ok := true
	for a in roster.ANIMAS:
		names[a.name] = true
		if a.evolves_to > 0 and roster.ANIMAS[a.evolves_to - 1].family != a.family:
			evo_ok = false
	_check("all 151 anima names are unique", names.size() == 151)
	_check("evolution chains stay inside their family", evo_ok)
	_check("sprite atlas region for #151 is correct", roster.icon(151).region.position == Vector2(192, 288))
	var cast = load("res://scripts/data/character_roster.gd")
	_check("character roster has 31 unique looks", cast.CAST.size() == 31 and cast.call("row_of", "warden") == 30)

	var dex = root.get_node("AnimaDex")
	var menu = root.get_node("GameMenu")
	var sg = root.get_node("SaveGame")
	sg.delete_save()
	await _hold("ui_cancel", 0.05)
	_check("Esc opens the menu", menu.is_open and _locked())
	await _hold("ui_accept", 0.05)
	_check("the menu opens the Animadex", dex.is_open)
	await _hold("ui_down", 0.05)
	await _hold("ui_right", 0.05)
	_check("Animadex navigation moves the selection (1 + 1 + 10)", dex._sel == 12)
	await _hold("ui_cancel", 0.05)
	_check("closing the Animadex returns to the menu", not dex.is_open and menu.is_open and _locked())
	await _hold("ui_cancel", 0.05)
	_check("Esc closes the menu", not menu.is_open and not _locked())

	var gs = root.get_node("GameState")
	root.get_node("Encounters").wild(101, 3)
	await create_timer(0.1).timeout
	_check("wild encounter marks the anima as seen", gs.seen.has(101) and _locked())
	await _close_dialogue()
	_check("wild encounter finishes and unlocks input", not _locked())

	change_scene_to_file("res://scenes/maps/route1.tscn")
	await create_timer(0.8).timeout
	_check("Route 1 loads", current_scene.name == "Route1" and _player().get_tile() == Vector2i(1, 7))
	var trainer: Node = null
	for child in current_scene.get_children():
		if "trainer_id" in child and child.trainer_id == "netter_pim":
			trainer = child
	_check("Route 1 has its trainers", trainer != null)
	_player().position = Vector2(9, 8) * 16 + Vector2(8, 8)
	_player().stepped.emit(Vector2i(9, 8))
	await create_timer(0.1).timeout
	_check("trainer spots the player in their line of sight", _locked())
	for i in 150:
		if gs.get_flag("beat_netter_pim"):
			break
		await _hold("ui_accept", 0.04)
	_check("trainer walked up next to the player", Vector2i((trainer.position / 16.0).floor()) == Vector2i(9, 7))
	_check("trainer challenge finished and was remembered", gs.get_flag("beat_netter_pim"))
	await _close_dialogue()
	_player().stepped.emit(Vector2i(9, 8))
	await create_timer(0.3).timeout
	_check("a beaten trainer does not challenge again", not _locked())

	# ---- saving and continuing ----
	await _hold("ui_cancel", 0.05)
	await _hold("ui_down", 0.05)
	await _hold("ui_accept", 0.05)
	_check("menu > Save game writes the save file", sg.has_save())
	var data = JSON.parse_string(FileAccess.get_file_as_string(sg.SAVE_PATH))
	_check("the save records map, position, trainer wins and seen animas",
		data.map == "res://scenes/maps/route1.tscn" and int(data.tile[0]) == 9 and int(data.tile[1]) == 8 \
		and data.flags.has("beat_netter_pim") and data.seen.size() >= 1 and data.version == 1)
	await _hold("ui_cancel", 0.05)
	change_scene_to_file("res://scenes/maps/town.tscn")
	await create_timer(0.8).timeout
	gs.flags.clear()
	gs.seen.clear()
	sg.continue_game()
	await create_timer(1.6).timeout
	_check("Continue returns to the saved map and position", current_scene.name == "Route1" and _player().get_tile() == Vector2i(9, 8))
	_check("Continue restores trainer wins and seen animas", gs.get_flag("beat_netter_pim") and gs.seen.has(101))

	var bad = FileAccess.open(sg.SAVE_PATH, FileAccess.WRITE)
	bad.store_string("not json {")
	bad.close()
	_check("a damaged save is rejected and set aside, not crashed on", not sg.load_game() and not sg.has_save() and FileAccess.file_exists(sg.SAVE_PATH + ".corrupt"))
	sg.delete_save()
	_check("delete_save removes every save file", not sg.has_save() and not FileAccess.file_exists(sg.SAVE_PATH + ".corrupt"))

	await _hold("ui_cancel", 0.05)
	await _hold("ui_down", 0.05)
	await _hold("ui_down", 0.05)
	await _hold("ui_accept", 0.05)
	_check("New game asks for confirmation first", menu._confirm_new and menu.is_open and gs.get_flag("beat_netter_pim"))
	await _hold("ui_accept", 0.05)
	await create_timer(1.2).timeout
	_check("New game wipes progress and starts in the town", current_scene.name == "Town" and not gs.get_flag("beat_netter_pim") and gs.seen_count() == 0)
	await _close_dialogue()
	sg.delete_save()

	print("\nRESULT: %s" % ("ALL PASSED" if _fails == 0 else "%d FAILED" % _fails))
	quit(_fails)
