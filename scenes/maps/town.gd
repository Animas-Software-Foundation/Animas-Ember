extends AsciiMap


func _setup() -> void:
	rows = PackedStringArray([
		"TTTTTTTTTTTTTTTTTTTTTTTT",
		"T..,..f.....,.....gggg.T",
		"T.....RRRR.........ggg.T",
		"T.f...RRRR...,.....ggg.T",
		"T.....HWHH...........g.T",
		"T.....HDHH......b......T",
		"T,....pp..............,T",
		"T.....pppppppppppppp..sT",
		"T..f..pp......S.......sT",
		"T.....pp........ff..wwwT",
		"T..,..pp..g.g.......wwwT",
		"T.....pp..ggg.....,.wwwT",
		"T.....pp..ggg..........T",
		"T.....pp..............bT",
		"T.....pp...............T",
		"TTTTTTTTTTTTTTTTTTTTTTTT",
	])
	start_tile = Vector2i(7, 6)
	start_facing = Facing.Dir.UP
	intro = ["Welcome to Animas: Ember!", "Arrows to walk, Enter to talk. Try the house!"]
	npc_defs = [
		{tile = Vector2i(10, 6), lines = ["Nice day for an adventure!", "The path east leads to Route 1... someday."]},
		{tile = Vector2i(9, 11), facing = Facing.Dir.RIGHT, body = Color("d0884a"), hair = Color("222222"),
			lines = ["Wild creatures hide in the tall grass.", "Walk through it and see what happens!"]},
		{tile = Vector2i(14, 8), hidden = true, lines = ["Welcome to Pixel Town!", "Population: you."]},
	]
	warp_defs = [
		{tile = Vector2i(7, 5), scene = "res://scenes/maps/house.tscn", to_tile = Vector2i(4, 6), facing = Facing.Dir.UP},
	]
