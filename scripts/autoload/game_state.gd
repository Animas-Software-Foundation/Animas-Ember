extends Node
## Global game state (autoload: GameState).
## Later phases will add the party, inventory, and save/load here.

## True while a dialogue, menu, or transition owns the input.
var input_locked := false

## Where the player should appear after the next scene change.
var has_spawn := false
var spawn_tile := Vector2i.ZERO
var spawn_facing := Vector2.DOWN

## Story flags, e.g. "got_starter", "beat_gym_1".
var flags: Dictionary = {}


func set_flag(flag_name: String, value := true) -> void:
	flags[flag_name] = value


func get_flag(flag_name: String) -> bool:
	return flags.get(flag_name, false)


## Animas you have met (id -> true). Fills the Animadex.
var seen: Dictionary = {}


func mark_seen(anima_id: int) -> void:
	seen[anima_id] = true


func seen_count() -> int:
	return seen.size()


## Seconds played; saved and restored by SaveGame.
var playtime := 0.0
## Scene file of the map the player is in (set by AsciiMap); saved by SaveGame.
var current_map := ""


func _process(delta: float) -> void:
	playtime += delta


## Back to a brand-new game (used by "New game" in the menu).
func reset() -> void:
	flags.clear()
	seen.clear()
	playtime = 0.0
	has_spawn = false
	input_locked = false
