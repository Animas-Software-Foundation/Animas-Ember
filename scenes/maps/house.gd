extends AsciiMap


func _setup() -> void:
	rows = PackedStringArray([
		"##########",
		"#BBB__BBB#",
		"#________#",
		"#__cccc__#",
		"#__cccc__#",
		"#________#",
		"#________#",
		"####m#####",
	])
	start_tile = Vector2i(4, 6)
	start_facing = Facing.Dir.UP
	npc_defs = [
		{tile = Vector2i(2, 5), facing = Facing.Dir.RIGHT, body = Color("c0508a"), hair = Color("6a3a1a"),
			lines = ["Welcome to my house!", "Real maps can be painted in the editor, too."]},
	]
	warp_defs = [
		{tile = Vector2i(4, 7), scene = "res://scenes/maps/town.tscn", to_tile = Vector2i(7, 6), facing = Facing.Dir.DOWN},
	]
