class_name Facing
## Direction helpers shared by the player, NPCs, and warps.

enum Dir { DOWN, UP, LEFT, RIGHT }


static func to_vector(dir: Dir) -> Vector2:
	match dir:
		Dir.UP:
			return Vector2.UP
		Dir.LEFT:
			return Vector2.LEFT
		Dir.RIGHT:
			return Vector2.RIGHT
		_:
			return Vector2.DOWN


## "up" / "down" / "left" / "right" - used to build animation names like "walk_up".
static func to_name(v: Vector2) -> String:
	if v == Vector2.UP:
		return "up"
	if v == Vector2.LEFT:
		return "left"
	if v == Vector2.RIGHT:
		return "right"
	return "down"
