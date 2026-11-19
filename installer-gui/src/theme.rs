use eframe::egui::{self, Color32, FontId, Pos2, Rect, RichText, Rounding, Sense, Stroke, TextureHandle, Vec2};

pub const LINK: Color32 = Color32::from_rgb(190, 80, 14);
pub const HOVER_BG: Color32 = Color32::from_rgb(254, 242, 230);
pub const SUBTEXT_GRAY: Color32 = Color32::from_rgb(100, 100, 100);
pub const SIDEBAR_BG: Color32 = Color32::from_rgb(29, 26, 43);
pub const EMBER: Color32 = Color32::from_rgb(224, 112, 26);
pub const RED: Color32 = Color32::from_rgb(200, 60, 50);
pub const GOLD: Color32 = Color32::from_rgb(244, 200, 56);

pub fn visuals() -> egui::Visuals {
    let mut v = egui::Visuals::light();
    v.selection.bg_fill = EMBER;
    v.hyperlink_color = LINK;
    v
}

pub fn draw_sidebar(ui: &mut egui::Ui, icon: Option<&TextureHandle>) {
    let rect = ui.available_rect_before_wrap();
    let painter = ui.painter();
    painter.rect_filled(rect, Rounding::ZERO, SIDEBAR_BG);

    // Top-left ember accent
    painter.rect_filled(
        Rect::from_min_size(Pos2::new(rect.left() - 15.0, rect.top() - 15.0), Vec2::new(135.0, 95.0)),
        Rounding::same(18.0),
        EMBER,
    );
    painter.rect_filled(
        Rect::from_min_size(Pos2::new(rect.left() - 15.0, rect.top() + 52.0), Vec2::new(60.0, 40.0)),
        Rounding::same(14.0),
        RED,
    );

    // The game icon in the middle, with hard pixel edges
    if let Some(tex) = icon {
        let size = 96.0;
        let r = Rect::from_center_size(Pos2::new(rect.center().x, rect.top() + 160.0), Vec2::splat(size));
        painter.image(tex.id(), r, Rect::from_min_max(Pos2::ZERO, Pos2::new(1.0, 1.0)), Color32::WHITE);
    }

    // Bottom-right gold accent (kept clear of the text)
    painter.rect_filled(
        Rect::from_min_size(Pos2::new(rect.left() + 100.0, rect.bottom() - 70.0), Vec2::new(90.0, 100.0)),
        Rounding::same(18.0),
        GOLD,
    );

    let light = Color32::from_rgb(240, 235, 250);
    painter.text(Pos2::new(rect.left() + 16.0, rect.bottom() - 54.0), egui::Align2::LEFT_BOTTOM, "Animas", FontId::proportional(20.0), light);
    painter.text(Pos2::new(rect.left() + 16.0, rect.bottom() - 30.0), egui::Align2::LEFT_BOTTOM, "Ember", FontId::proportional(22.0), GOLD);
    painter.text(Pos2::new(rect.left() + 16.0, rect.bottom() - 12.0), egui::Align2::LEFT_BOTTOM, format!("v{}", crate::VERSION), FontId::proportional(12.0), Color32::from_rgb(170, 164, 195));

    painter.line_segment([rect.right_top(), rect.right_bottom()], Stroke::new(1.0_f32, Color32::from_rgb(225, 225, 225)));
}

pub fn action_link_block(ui: &mut egui::Ui, title: &str, lines: &[&str]) -> bool {
    let desired_size = Vec2::new(ui.available_width(), 26.0 + (lines.len() as f32 * 16.0));
    let (rect, response) = ui.allocate_exact_size(desired_size, Sense::click());

    if response.hovered() {
        ui.painter().rect_filled(rect, Rounding::same(4.0), HOVER_BG);
        ui.ctx().set_cursor_icon(egui::CursorIcon::PointingHand);
    }

    let painter = ui.painter();
    // A drawn chevron: the default font has no arrow glyph.
    let c = Pos2::new(rect.left() + 12.0, rect.top() + 14.0);
    let stroke = Stroke::new(2.0_f32, LINK);
    painter.line_segment([c + Vec2::new(-3.0, -5.0), c + Vec2::new(2.0, 0.0)], stroke);
    painter.line_segment([c + Vec2::new(2.0, 0.0), c + Vec2::new(-3.0, 5.0)], stroke);
    painter.text(
        Pos2::new(rect.left() + 26.0, rect.top() + 4.0),
        egui::Align2::LEFT_TOP,
        title,
        FontId::proportional(16.5),
        LINK,
    );
    for (i, line) in lines.iter().enumerate() {
        painter.text(
            Pos2::new(rect.left() + 26.0, rect.top() + 26.0 + (i as f32 * 15.0)),
            egui::Align2::LEFT_TOP,
            *line,
            FontId::proportional(12.0),
            LINK,
        );
    }
    response.clicked()
}

pub fn note(ui: &mut egui::Ui, text: &str) {
    ui.label(RichText::new(text).size(11.5).color(SUBTEXT_GRAY));
}
