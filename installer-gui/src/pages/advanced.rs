use crate::theme::note;
use crate::{Setup, WizardPage, APP_NAME};
use eframe::egui::{self, Color32, RichText};

pub fn render(app: &mut Setup, ui: &mut egui::Ui, ctx: &egui::Context) {
    ui.label(RichText::new("Installation Options").size(22.0).color(Color32::BLACK));
    ui.add_space(12.0);

    ui.checkbox(&mut app.overwrite_existing, RichText::new("Overwrite existing game files in the folder").size(12.5));
    ui.checkbox(&mut app.launch_after, RichText::new(format!("Start {APP_NAME} when finished")).size(12.5));
    ui.checkbox(&mut app.open_folder_after, RichText::new("Open the folder when finished").size(12.5));

    ui.add_space(18.0);
    ui.label(RichText::new("Destination folder").size(12.5).color(Color32::BLACK));
    ui.add_space(4.0);

    ui.horizontal(|ui| {
        #[cfg(windows)]
        let width = ui.available_width() - 88.0;
        #[cfg(not(windows))]
        let width = ui.available_width();
        ui.add_sized([width, 24.0], egui::TextEdit::singleline(&mut app.extract_dir));
        #[cfg(windows)]
        if ui.add_sized([80.0, 24.0], egui::Button::new("Browse")).clicked() {
            if let Some(folder) = rfd::FileDialog::new().pick_folder() {
                app.extract_dir = folder.to_string_lossy().to_string();
            }
        }
    });
    note(ui, "Portable install: no administrator privileges needed.");
    note(ui, "Installing over an older version keeps your data folder (saves and settings).");

    ui.with_layout(egui::Layout::bottom_up(egui::Align::LEFT), |ui| {
        ui.horizontal(|ui| {
            if ui.add_sized([82.0, 26.0], egui::Button::new("Back")).clicked() {
                app.page = WizardPage::Welcome;
            }
            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                if ui.add_sized([82.0, 26.0], egui::Button::new("Cancel")).clicked() {
                    ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                }
                ui.add_space(6.0);
                if ui.add_sized([82.0, 26.0], egui::Button::new("Install")).clicked() {
                    app.start_extract(ctx);
                }
            });
        });
    });
}
