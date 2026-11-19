//! Animas: Ember graphical installer (the Windows setup.exe stub).
//!
//! A finished installer is this program followed by a zip payload and a trailer, built by
//! tools/package_portable.py (see installer/src/payload.rs). Run it for a small wizard, or use
//! --silent for unattended installs:  setup.exe --silent --dir "D:\Games\Animas Ember" --run

#![cfg_attr(all(not(debug_assertions), windows), windows_subsystem = "windows")]

#[allow(dead_code)]
#[path = "../../installer/src/payload.rs"]
mod payload;
mod pages;
mod theme;

use eframe::egui::{self, Color32};
use std::path::PathBuf;
use std::process::Command;
use std::sync::{Arc, Mutex};
use std::time::Duration;

pub const APP_NAME: &str = "Animas: Ember";
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
const ICON_RGBA: &[u8] = include_bytes!("../assets/icon16.rgba");

#[derive(PartialEq, Clone, Copy)]
pub enum WizardPage {
    Welcome,
    Customize,
    Extracting,
    Finished,
}

/// Shared between the UI thread and the extraction thread.
#[derive(Default)]
pub struct Progress {
    pub done: u64,
    pub total: u64,
    pub current: String,
    pub cancel: bool,
    pub result: Option<Result<payload::Summary, String>>,
}

pub struct Setup {
    pub page: WizardPage,
    pub launch_after: bool,
    pub open_folder_after: bool,
    pub overwrite_existing: bool,
    pub extract_dir: String,
    pub progress: Arc<Mutex<Progress>>,
    pub outcome: Option<Result<payload::Summary, String>>,
    pub icon: Option<egui::TextureHandle>,
}

impl Setup {
    fn new(dir: Option<PathBuf>) -> Self {
        let dir = dir.unwrap_or_else(payload::default_dir);
        let mut app = Self {
            page: WizardPage::Welcome,
            launch_after: true,
            open_folder_after: false,
            overwrite_existing: true,
            extract_dir: dir.to_string_lossy().to_string(),
            progress: Arc::new(Mutex::new(Progress::default())),
            outcome: None,
            icon: None,
        };
        // A bare stub has nothing to install: say so right away instead of failing later.
        if let Err(e) = payload::open_payload() {
            app.outcome = Some(Err(e));
            app.page = WizardPage::Finished;
        }
        app
    }

    pub fn start_extract(&mut self, ctx: &egui::Context) {
        self.page = WizardPage::Extracting;
        *self.progress.lock().unwrap() = Progress::default();
        let shared = self.progress.clone();
        let dir = PathBuf::from(&self.extract_dir);
        let overwrite = self.overwrite_existing;
        let ctx = ctx.clone();
        std::thread::spawn(move || {
            let result = run_extract(&shared, &dir, overwrite, &ctx);
            shared.lock().unwrap().result = Some(result);
            ctx.request_repaint();
        });
    }

    fn finish(&mut self, result: Result<payload::Summary, String>) {
        if let Ok(sum) = &result {
            if self.launch_after {
                if let Some(rel) = &sum.launch {
                    launch_game(&self.extract_dir, rel);
                }
            }
            if self.open_folder_after {
                open_folder(&self.extract_dir);
            }
        }
        self.outcome = Some(result);
        self.page = WizardPage::Finished;
    }
}

fn run_extract(shared: &Arc<Mutex<Progress>>, dir: &std::path::Path, overwrite: bool, ctx: &egui::Context) -> Result<payload::Summary, String> {
    let mut zip = payload::open_payload()?;
    let (_, total) = payload::totals(&mut zip)?;
    shared.lock().unwrap().total = total;
    payload::extract(&mut zip, dir, overwrite, &mut |done, name| {
        let mut p = shared.lock().unwrap();
        p.done = done;
        p.current = name.to_string();
        let keep_going = !p.cancel;
        drop(p);
        ctx.request_repaint();
        keep_going
    })
}

pub fn launch_game(dir: &str, rel: &str) {
    let _ = Command::new(PathBuf::from(dir).join(rel)).current_dir(dir).spawn();
}

pub fn open_folder(path: &str) {
    let opener = if cfg!(windows) { "explorer" } else if cfg!(target_os = "macos") { "open" } else { "xdg-open" };
    let _ = Command::new(opener).arg(path).spawn();
}

impl eframe::App for Setup {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        if self.icon.is_none() {
            let image = egui::ColorImage::from_rgba_unmultiplied([16, 16], ICON_RGBA);
            self.icon = Some(ctx.load_texture("icon", image, egui::TextureOptions::NEAREST));
        }
        if self.page == WizardPage::Extracting {
            let finished = self.progress.lock().unwrap().result.take();
            match finished {
                Some(result) => self.finish(result),
                None => ctx.request_repaint_after(Duration::from_millis(60)),
            }
        }

        egui::SidePanel::left("sidebar")
            .exact_width(165.0)
            .resizable(false)
            .frame(egui::Frame::none())
            .show(ctx, |ui| theme::draw_sidebar(ui, self.icon.as_ref()));

        egui::CentralPanel::default()
            .frame(egui::Frame::none().fill(Color32::WHITE).inner_margin(egui::Margin::symmetric(24.0, 18.0)))
            .show(ctx, |ui| match self.page {
                WizardPage::Welcome => pages::welcome::render(self, ui, ctx),
                WizardPage::Customize => pages::advanced::render(self, ui, ctx),
                WizardPage::Extracting => pages::status::render_installing(self, ui, ctx),
                WizardPage::Finished => pages::status::render_finished(self, ui, ctx),
            });
    }
}

// ---------------------------------------------------------------- command line

struct Cli {
    silent: bool,
    list: bool,
    run: bool,
    overwrite: bool,
    dir: Option<PathBuf>,
}

/// Ok(None): handled (--help / --version). Accepts --silent/--yes/-y/-s//S, --dir/-d//D=path.
fn parse_cli() -> Result<Option<Cli>, String> {
    let mut cli = Cli { silent: false, list: false, run: false, overwrite: true, dir: None };
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "-h" | "--help" | "/?" => {
                println!(
                    "{APP_NAME} setup {VERSION}\n\nUSAGE: setup [OPTIONS]\n\n  \
                     -s, --silent, --yes, /S   install without showing the wizard\n  \
                     -d, --dir <PATH>, /D=PATH install into PATH (default: a \"{}\" folder next to this file)\n  \
                     -r, --run                 start the game when finished\n  \
                         --no-overwrite        keep files that already exist\n  \
                     -l, --list                list the files inside this installer\n  \
                     -V, --version             print the version\n\n\
                     Your saves and settings live in the \"{}\" folder, which is never overwritten.",
                    payload::DEFAULT_FOLDER,
                    payload::KEEP_DIR
                );
                return Ok(None);
            }
            "-V" | "--version" => {
                println!("{VERSION}");
                return Ok(None);
            }
            "-s" | "--silent" | "-y" | "--yes" | "/S" | "/s" => cli.silent = true,
            "-r" | "--run" => cli.run = true,
            "-l" | "--list" => cli.list = true,
            "--no-overwrite" => cli.overwrite = false,
            "-d" | "--dir" => cli.dir = Some(PathBuf::from(args.next().ok_or("--dir needs a path")?)),
            other if other.starts_with("/D=") || other.starts_with("/d=") => cli.dir = Some(PathBuf::from(&other[3..])),
            other => return Err(format!("unknown option '{other}' (try --help)")),
        }
    }
    Ok(Some(cli))
}

/// --silent and --list: no window. Returns the process exit code.
fn run_cli(cli: Cli) -> i32 {
    let result = (|| -> Result<(), String> {
        let mut zip = payload::open_payload()?;
        if cli.list {
            for i in 0..zip.len() {
                let e = zip.by_index(i).map_err(|e| e.to_string())?;
                println!("{:>10}  {}", e.size(), e.name());
            }
            return Ok(());
        }
        let dir = cli.dir.clone().unwrap_or_else(payload::default_dir);
        println!("Installing to {}", dir.display());
        let sum = payload::extract(&mut zip, &dir, cli.overwrite, &mut |_, _| true)?;
        println!("Done: {} files installed{}.", sum.written, if sum.kept > 0 { format!(", {} user-data files kept", sum.kept) } else { String::new() });
        if cli.run {
            match &sum.launch {
                Some(rel) => launch_game(&dir.to_string_lossy(), rel),
                None => println!("(This installer does not say how to start the game, so it was not launched.)"),
            }
        }
        Ok(())
    })();
    match result {
        Ok(()) => 0,
        Err(e) => {
            eprintln!("\nError: {e}");
            1
        }
    }
}

fn main() -> eframe::Result<()> {
    let cli = match parse_cli() {
        Ok(Some(cli)) => cli,
        Ok(None) => return Ok(()),
        Err(e) => {
            eprintln!("Error: {e}");
            std::process::exit(2);
        }
    };
    if cli.silent || cli.list {
        std::process::exit(run_cli(cli));
    }

    // Window icon: the game icon, scaled up with hard pixel edges.
    let mut rgba = Vec::with_capacity(32 * 32 * 4);
    for y in 0..32 {
        for x in 0..32 {
            let i = ((y / 2) * 16 + x / 2) * 4;
            rgba.extend_from_slice(&ICON_RGBA[i..i + 4]);
        }
    }
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([610.0, 385.0])
            .with_resizable(false)
            .with_icon(egui::IconData { rgba, width: 32, height: 32 }),
        ..Default::default()
    };
    let bits = if cfg!(target_pointer_width = "64") { "64-bit" } else { "32-bit" };
    eframe::run_native(
        &format!("{APP_NAME} {VERSION} Setup ({bits})"),
        options,
        Box::new(move |cc| {
            cc.egui_ctx.set_visuals(theme::visuals());
            Ok(Box::new(Setup::new(cli.dir)))
        }),
    )
}
