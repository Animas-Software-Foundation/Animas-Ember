extends Node
## Saving and continuing (autoload: SaveGame).
##
## One save file, user://save.json. With the portable launcher that is <game folder>/data/...,
## so your progress travels with the game folder. It is saved automatically on map changes,
## after trainer wins and encounters, and when the window closes, or from the menu.
## On launch, the game continues from the save unless started with --new-game.

const SAVE_PATH := "user://save.json"
const FORMAT := 1

var _pending := {}


func _ready() -> void:
	# Load synchronously so the state is ready before the first map builds (no intro replay).
	if _should_continue() and load_game():
		_apply_pending.call_deferred()


func _should_continue() -> bool:
	var args := OS.get_cmdline_args()
	return not ("--new-game" in args or "--script" in args or "-s" in args)


func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)


func delete_save() -> void:
	for path in [SAVE_PATH, SAVE_PATH + ".tmp", SAVE_PATH + ".corrupt"]:
		if FileAccess.file_exists(path):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(path))


## Writes the save. Returns false if there is nothing to save yet or the file could not be written.
func save() -> bool:
	var player := get_tree().get_first_node_in_group("player")
	if player == null or GameState.current_map.is_empty():
		return false
	var tile: Vector2i = player.get_tile()
	var data := {
		"version": FORMAT,
		"game_version": ProjectSettings.get_setting("application/config/version", "0"),
		"saved_at": Time.get_unix_time_from_system(),
		"playtime": GameState.playtime,
		"map": GameState.current_map,
		"tile": [tile.x, tile.y],
		"facing": [player.facing.x, player.facing.y],
		"flags": GameState.flags,
		"seen": GameState.seen.keys(),
	}
	var tmp := SAVE_PATH + ".tmp"
	var file := FileAccess.open(tmp, FileAccess.WRITE)
	if file == null:
		push_warning("Could not write the save file: %s" % error_string(FileAccess.get_open_error()))
		return false
	file.store_string(JSON.stringify(data, "\t"))
	file.close()
	# Write-then-rename, so a crash mid-save can never leave a half-written save.
	return DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp), ProjectSettings.globalize_path(SAVE_PATH)) == OK


## Reads the save into GameState. Returns false (and sets a damaged file aside) if it cannot be used.
func load_game() -> bool:
	if not has_save():
		return false
	var json := JSON.new()  # (unlike JSON.parse_string, this does not print an engine error for bad files)
	var parsed: Variant = json.data if json.parse(FileAccess.get_file_as_string(SAVE_PATH)) == OK else null
	if not _valid(parsed):
		push_warning("The save file is damaged or from a newer version; keeping it as save.json.corrupt.")
		DirAccess.rename_absolute(ProjectSettings.globalize_path(SAVE_PATH), ProjectSettings.globalize_path(SAVE_PATH + ".corrupt"))
		return false
	GameState.flags = parsed.flags
	GameState.seen.clear()
	for id in parsed.seen:
		GameState.seen[int(id)] = true
	GameState.playtime = float(parsed.get("playtime", 0.0))
	_pending = {
		"map": parsed.map,
		"tile": Vector2i(int(parsed.tile[0]), int(parsed.tile[1])),
		"facing": Vector2(float(parsed.facing[0]), float(parsed.facing[1])),
	}
	return true


func _valid(d: Variant) -> bool:
	if typeof(d) != TYPE_DICTIONARY:
		return false
	for key in ["version", "map", "tile", "facing", "flags", "seen"]:
		if not d.has(key):
			return false
	return int(d.version) <= FORMAT and typeof(d.map) == TYPE_STRING and ResourceLoader.exists(d.map) \
		and typeof(d.tile) == TYPE_ARRAY and d.tile.size() == 2 and typeof(d.facing) == TYPE_ARRAY and d.facing.size() == 2 \
		and typeof(d.flags) == TYPE_DICTIONARY and typeof(d.seen) == TYPE_ARRAY


## Loads the save and puts the player where it says (used by the menu and by tests).
func continue_game() -> void:
	if load_game():
		await _apply_pending()


func _apply_pending() -> void:
	if _pending.is_empty():
		return
	await get_tree().process_frame
	await get_tree().process_frame
	var target: Dictionary = _pending
	_pending = {}
	var scene := get_tree().current_scene
	var player := get_tree().get_first_node_in_group("player")
	if scene != null and scene.scene_file_path == target.map and player != null:
		player.position = Player.tile_to_world(target.tile)
		player.face(target.facing)
	else:
		SceneTransition.change_scene(target.map, target.tile, target.facing)


func _notification(what: int) -> void:
	# Save when the window closes, and when a phone app goes to the background.
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_APPLICATION_PAUSED:
		save()
