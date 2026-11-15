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
		{tile = Vector2i(2, 5), look = "mom", facing = Facing.Dir.RIGHT,
			lines = ["Welcome home! Be careful out there.", "Remember: your Animadex fills up as you meet new animas."]},
		{tile = Vector2i(6, 2), look = "professor", lines = ["I'm Professor Cinder. I study animas.", "151 species have been recorded. Can you meet them all?"]},
		{tile = Vector2i(7, 5), look = "student", facing = Facing.Dir.LEFT, lines = ["I'm taking notes for the Professor.", "Trainers on Route 1 will battle you on sight!"]},
	]
	warp_defs = [
		{tile = Vector2i(4, 7), scene = "res://scenes/maps/town.tscn", to_tile = Vector2i(7, 6), facing = Facing.Dir.DOWN},
	]
