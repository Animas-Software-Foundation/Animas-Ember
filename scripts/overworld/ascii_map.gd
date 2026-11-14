class_name AsciiMap
extends Node2D
## Builds a playable map at runtime from ASCII rows, using assets/tilesets/tiles.tres.
## Subclasses fill in the data in _setup(). For bigger maps, paint a TileMapLayer in
## the editor instead; Player, NPC, and Warp work the same either way.

const TILE_SET: TileSet = preload("res://assets/tilesets/tiles.tres")
const PLAYER_SCENE: PackedScene = preload("res://scenes/player.tscn")
const NPC_SCENE: PackedScene = preload("res://scenes/npc.tscn")
const VIEW_SIZE := Vector2(240, 160)

## Character -> atlas coordinates in tiles.png.
const LEGEND := {
	".": Vector2i(0, 0), ",": Vector2i(1, 0), "f": Vector2i(2, 0), "g": Vector2i(3, 0),
	"p": Vector2i(4, 0), "s": Vector2i(5, 0), "w": Vector2i(6, 0),
	"T": Vector2i(0, 1), "b": Vector2i(1, 1), "F": Vector2i(2, 1), "S": Vector2i(3, 1),
	"#": Vector2i(4, 1), "_": Vector2i(5, 1), "c": Vector2i(6, 1), "R": Vector2i(7, 1),
	"r": Vector2i(0, 2), "H": Vector2i(1, 2), "W": Vector2i(2, 2), "D": Vector2i(3, 2),
	"m": Vector2i(4, 2), "C": Vector2i(5, 2), "B": Vector2i(6, 2), "L": Vector2i(7, 2),
}

# Filled in by subclasses.
var rows: PackedStringArray = []
var start_tile := Vector2i.ZERO
var start_facing: Facing.Dir = Facing.Dir.DOWN
var intro: Array[String] = []
## {tile: Vector2i, lines: Array, facing: Facing.Dir, body: Color, hair: Color, hidden: bool}
var npc_defs: Array[Dictionary] = []
## {tile: Vector2i, scene: String, to_tile: Vector2i, facing: Facing.Dir}
var warp_defs: Array[Dictionary] = []

var _layer: TileMapLayer


func _setup() -> void:
	pass


func _ready() -> void:
	_setup()
	_build_tiles()
	_build_warps()
	_build_npcs()
	_spawn_player()
	if not intro.is_empty() and not GameState.get_flag("intro_shown"):
		GameState.set_flag("intro_shown")
		Dialogue.say(intro)


func _build_tiles() -> void:
	_layer = TileMapLayer.new()
	_layer.name = "Ground"
	_layer.tile_set = TILE_SET
	add_child(_layer)
	for y in rows.size():
		var row: String = rows[y]
		for x in row.length():
			var key := row[x]
			if LEGEND.has(key):
				_layer.set_cell(Vector2i(x, y), 0, LEGEND[key])
			else:
				push_warning("Unknown map character '%s' at (%d, %d)" % [key, x, y])


func _build_warps() -> void:
	for def in warp_defs:
		var warp := Warp.new()
		warp.position = Player.tile_to_world(def.tile)
		warp.target_scene = def.scene
		warp.target_tile = def.to_tile
		warp.target_facing = def.facing
		add_child(warp)


func _build_npcs() -> void:
	for def in npc_defs:
		var npc: NPC = NPC_SCENE.instantiate()
		npc.position = Player.tile_to_world(def.tile)
		npc.dialogue.assign(def.lines)
		npc.facing = def.get("facing", Facing.Dir.DOWN)
		npc.body_color = def.get("body", npc.body_color)
		npc.hair_color = def.get("hair", npc.hair_color)
		if def.get("hidden", false):  # invisible talk-trigger, e.g. for a sign tile
			npc.visible = false
			npc.turn_to_face_player = false
		add_child(npc)


func _spawn_player() -> void:
	var player: Player = PLAYER_SCENE.instantiate()
	player.position = Player.tile_to_world(start_tile)
	player.facing = Facing.to_vector(start_facing)
	add_child(player)

	# Keep the camera inside the map; centre maps smaller than the screen.
	var map_px := Vector2(rows[0].length(), rows.size()) * Player.TILE
	var pad := Vector2(maxf((VIEW_SIZE.x - map_px.x) / 2.0, 0.0), maxf((VIEW_SIZE.y - map_px.y) / 2.0, 0.0))
	var cam: Camera2D = player.get_node("Camera2D")
	cam.limit_left = int(-pad.x)
	cam.limit_top = int(-pad.y)
	cam.limit_right = int(map_px.x + pad.x)
	cam.limit_bottom = int(map_px.y + pad.y)

	player.stepped.connect(_on_player_stepped)


func _on_player_stepped(tile: Vector2i) -> void:
	var data := _layer.get_cell_tile_data(tile)
	if data != null and data.get_custom_data("tall_grass") and randf() < 0.2:
		Dialogue.say(["A wild creature appeared!", "(Battles arrive in Phase 4.)"])
