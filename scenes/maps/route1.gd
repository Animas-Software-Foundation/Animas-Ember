extends AsciiMap


func _setup() -> void:
	rows = PackedStringArray([
		"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
		"T.ggggg....gggg.....ggggggg..T",
		"T.ggggg.T..ggfg.T...ggggggg..T",
		"T.ggggg..ggg,gg....Tggggggg..T",
		"T........gggggg........T.....T",
		"T.T.f..,.gg....T.....gggggb.TT",
		"T....T....T...,..f..,gggggg..T",
		"pppppppppppppppppppppppppppppT",
		"TppppppppppppppppppppppppppfpT",
		"T.,...b..,.T......T...f.,.T..T",
		"T..gggggg....ggggggb.ggggggg.T",
		"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
	])
	start_tile = Vector2i(1, 7)
	start_facing = Facing.Dir.RIGHT
	npc_defs = [
		{tile = Vector2i(14, 9), look = "hiker", facing = Facing.Dir.UP,
			lines = ["Hiking builds character. And sore legs.", "Trainers on this route will challenge you if you walk in front of them!"]},
		{tile = Vector2i(27, 6), hidden = true, lines = ["Route 1", "The road ends here for now. More of the world is coming soon!"]},
	]
	trainer_defs = [
		{tile = Vector2i(9, 5), look = "netter", id = "netter_pim", facing = Facing.Dir.DOWN, range = 4,
			lines = ["You walked right into my net! Let's battle!"], after = ["My bugs are the best... usually."],
			team = [{anima = "Fidget", level = 3}, {anima = "Sparkbug", level = 4}]},
		{tile = Vector2i(16, 10), look = "scout", id = "scout_nell", facing = Facing.Dir.UP, range = 4,
			lines = ["Scouts never miss a thing. Ready?"], after = ["Great teamwork. I'm taking notes."],
			team = [{anima = "Snuffle", level = 4}, {anima = "Sproutle", level = 5}]},
		{tile = Vector2i(24, 6), look = "camper", id = "camper_ty", facing = Facing.Dir.DOWN, range = 3,
			lines = ["I've been camping out here all week. Battle time!"], after = ["Time to go home and rest."],
			team = [{anima = "Cindle", level = 5}, {anima = "Zaplet", level = 5}]},
	]
	encounter_table = [
		{anima = "Fidget", min = 2, max = 4, weight = 25}, {anima = "Chirpa", min = 2, max = 4, weight = 20},
		{anima = "Snuffle", min = 3, max = 5, weight = 20}, {anima = "Nutkin", min = 3, max = 5, weight = 15},
		{anima = "Hopper", min = 4, max = 6, weight = 10}, {anima = "Puffling", min = 3, max = 5, weight = 10},
	]
	warp_defs = [
		{tile = Vector2i(0, 7), scene = "res://scenes/maps/town.tscn", to_tile = Vector2i(22, 7), facing = Facing.Dir.LEFT},
	]
