class_name PlaceholderSprite
## Draws a simple 16x16 person so the game is playable before real sprites exist.
## Call from a CanvasItem's _draw(); the node origin is the tile centre.

const SKIN := Color("f0c8a0")
const LEGS := Color("2a2a30")
const EYE := Color("222222")


static func draw_person(ci: CanvasItem, dir: Vector2, body: Color, hair: Color) -> void:
	var o := Vector2(-8, -8)
	ci.draw_rect(Rect2(o + Vector2(4, 13), Vector2(3, 3)), LEGS)
	ci.draw_rect(Rect2(o + Vector2(9, 13), Vector2(3, 3)), LEGS)
	ci.draw_rect(Rect2(o + Vector2(3, 7), Vector2(10, 6)), body)
	ci.draw_rect(Rect2(o + Vector2(4, 1), Vector2(8, 7)), SKIN)
	var hair_h := 7.0 if dir == Vector2.UP else 3.0
	ci.draw_rect(Rect2(o + Vector2(4, 0), Vector2(8, hair_h)), hair)
	if dir == Vector2.DOWN:
		ci.draw_rect(Rect2(o + Vector2(5, 5), Vector2(1, 2)), EYE)
		ci.draw_rect(Rect2(o + Vector2(10, 5), Vector2(1, 2)), EYE)
	elif dir == Vector2.LEFT:
		ci.draw_rect(Rect2(o + Vector2(5, 5), Vector2(1, 2)), EYE)
	elif dir == Vector2.RIGHT:
		ci.draw_rect(Rect2(o + Vector2(10, 5), Vector2(1, 2)), EYE)
