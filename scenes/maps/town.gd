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
		"T.....pppppppppppppppppp",
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
		{tile = Vector2i(10, 6), look = "kid_boy", lines = ["Nice day for an adventure!", "The path east leads to Route 1. Watch out for trainers!"]},
		{tile = Vector2i(9, 11), look = "gardener", facing = Facing.Dir.RIGHT,
			lines = ["Wild animas hide in the tall grass.", "Walk through it and see who shows up!"]},
		{tile = Vector2i(16, 3), look = "elder", facing = Facing.Dir.LEFT,
			lines = ["Welcome to Pixel Town, young one.", "There are 151 animas out there. Press Esc to open your Animadex and see them all."]},
		{tile = Vector2i(2, 9), look = "granny", facing = Facing.Dir.RIGHT,
			lines = ["When I was young, I only knew of a handful of animas.", "Now they say there are 151 species!"]},
		{tile = Vector2i(12, 4), look = "shopkeeper", lines = ["The shop is still being built.", "Come back in a later update!"]},
		{tile = Vector2i(18, 10), look = "fisher", facing = Facing.Dir.RIGHT,
			lines = ["The fish aren't biting today.", "Maybe I should try the pond over there."]},
		{tile = Vector2i(14, 8), hidden = true, lines = ["Welcome to Pixel Town!", "Route 1 is to the east."]},
	]
	encounter_table = [
		{anima = "Nutkin", min = 2, max = 4, weight = 30}, {anima = "Chirpa", min = 2, max = 4, weight = 30},
		{anima = "Snuffle", min = 2, max = 4, weight = 25}, {anima = "Tadgle", min = 2, max = 3, weight = 15},
	]
	warp_defs = [
		{tile = Vector2i(23, 7), scene = "res://scenes/maps/route1.tscn", to_tile = Vector2i(1, 7), facing = Facing.Dir.RIGHT},
		{tile = Vector2i(7, 5), scene = "res://scenes/maps/house.tscn", to_tile = Vector2i(4, 6), facing = Facing.Dir.UP},
	]
