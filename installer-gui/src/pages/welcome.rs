use crate::theme::action_link_block;
use crate::{Setup, WizardPage, APP_NAME, VERSION};
use eframe::egui::{self, Color32, RichText};

pub fn render(app: &mut Setup, ui: &mut egui::Ui, ctx: &egui::Context) {
    let bits = if cfg!(target_pointer_width = "64") { "64-bit" } else { "32-bit" };
    ui.label(RichText::new(format!("Install {APP_NAME} {VERSION} ({bits})")).size(22.0).color(Color32::BLACK));
    ui.add_space(6.0);
    ui.label(
        RichText::new(
            "Choose Install now to unpack the game into the folder below, or Customize to pick a different one. \
             Your saves and settings stay in a data folder inside it. Nothing is written to AppData or the registry.",
        )
        .size(12.5)
        .color(Color32::from_rgb(40, 40, 40)),
    );
    ui.add_space(22.0);

    let path_preview = app.extract_dir.clone();
    if action_link_block(ui, "Install now", &[&path_preview, "Portable: no registry changes and no administrator rights needed"]) {
        app.start_extract(ctx);
    }
    ui.add_space(16.0);
    if action_link_block(ui, "Customize installation", &["Choose the folder and installation options"]) {
        app.page = WizardPage::Customize;
    }

    ui.with_layout(egui::Layout::bottom_up(egui::Align::LEFT), |ui| {
        ui.horizontal(|ui| {
            ui.checkbox(&mut app.launch_after, RichText::new(format!("Start {APP_NAME} when finished")).size(12.5));
            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                if ui.add_sized([82.0, 26.0], egui::Button::new("Cancel")).clicked() {
                    ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                }
            });
        });
    });
}
