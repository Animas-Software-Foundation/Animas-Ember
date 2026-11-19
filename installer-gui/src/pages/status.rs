use crate::theme::{note, SUBTEXT_GRAY};
use crate::{launch_game, open_folder, Setup};
use eframe::egui::{self, Color32, RichText};

pub fn render_installing(app: &mut Setup, ui: &mut egui::Ui, _ctx: &egui::Context) {
    let (done, total, current) = {
        let p = app.progress.lock().unwrap();
        (p.done, p.total, p.current.clone())
    };
    let fraction = if total == 0 { 0.0 } else { (done as f32 / total as f32).clamp(0.0, 1.0) };

    ui.label(RichText::new("Installing").size(22.0).color(Color32::BLACK));
    ui.add_space(20.0);
    ui.label("Unpacking the game files...");
    ui.add_space(8.0);
    ui.add(egui::ProgressBar::new(fraction).show_percentage());
    ui.add_space(6.0);
    note(ui, &current);

    ui.with_layout(egui::Layout::bottom_up(egui::Align::RIGHT), |ui| {
        if ui.add_sized([82.0, 26.0], egui::Button::new("Cancel")).clicked() {
            app.progress.lock().unwrap().cancel = true;
        }
    });
}

pub fn render_finished(app: &mut Setup, ui: &mut egui::Ui, ctx: &egui::Context) {
    let outcome = app.outcome.clone();
    match &outcome {
        Some(Ok(sum)) => {
            ui.label(RichText::new("Installation complete").size(22.0).color(Color32::BLACK));
            ui.add_space(10.0);
            ui.label(RichText::new("The game is installed and ready to play.").size(12.5));
            ui.add_space(12.0);
            let mut detail = format!("{} files installed to {}", sum.written, app.extract_dir);
            if sum.kept > 0 {
                detail += &format!("\n{} existing data files were kept (your saves and settings).", sum.kept);
            }
            if sum.skipped > 0 {
                detail += &format!("\n{} existing files were left alone.", sum.skipped);
            }
            ui.label(RichText::new(detail).size(12.0).color(SUBTEXT_GRAY));
        }
        Some(Err(err)) => {
            let cancelled = err == "cancelled";
            ui.label(RichText::new(if cancelled { "Installation cancelled" } else { "Installation failed" }).size(22.0).color(Color32::BLACK));
            ui.add_space(10.0);
            if !cancelled {
                let tidy = err.lines().map(|l| l.trim()).collect::<Vec<_>>().join("\n");
                let tidy = tidy[..1].to_uppercase() + &tidy[1..];
                ui.label(RichText::new(tidy).size(12.5).color(crate::theme::RED));
            }
            ui.add_space(12.0);
            note(ui, "Nothing else was changed on your computer.");
        }
        None => {}
    }

    ui.with_layout(egui::Layout::bottom_up(egui::Align::LEFT), |ui| {
        ui.horizontal(|ui| {
            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                if ui.add_sized([82.0, 26.0], egui::Button::new("Close")).clicked() {
                    ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                }
                if let Some(Ok(sum)) = &outcome {
                    ui.add_space(6.0);
                    if ui.add_sized([100.0, 26.0], egui::Button::new("Open Folder")).clicked() {
                        open_folder(&app.extract_dir);
                    }
                    if let Some(rel) = &sum.launch {
                        ui.add_space(6.0);
                        if ui.add_sized([82.0, 26.0], egui::Button::new("Play")).clicked() {
                            launch_game(&app.extract_dir, rel);
                        }
                    }
                }
            });
        });
    });
}
