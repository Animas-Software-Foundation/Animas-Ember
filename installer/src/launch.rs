//! Portable launcher for Animas: Ember.
//!
//! Godot keeps its `user://` data in AppData (Windows), ~/.local/share (Linux), or
//! ~/Library/Application Support (macOS), and creates that folder at startup. This launcher points
//! those locations at a `data` folder next to the game, then starts the game, so nothing is
//! written outside the install folder and the whole folder can be moved or copied.
//!
//! Layout:  <launcher>  bin/.entry (path of the game, relative to bin/)  bin/<game files>  data/
//! If `data` cannot be written (for example the game is in Program Files), the game just runs normally.

#![cfg_attr(windows, windows_subsystem = "windows")]

use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{self, Command};

#[cfg(windows)]
fn fail(msg: &str) -> ! {
    use std::os::windows::ffi::OsStrExt;
    fn wide(s: &str) -> Vec<u16> {
        std::ffi::OsStr::new(s).encode_wide().chain(Some(0)).collect()
    }
    #[link(name = "user32")]
    extern "system" {
        fn MessageBoxW(hwnd: *mut core::ffi::c_void, text: *const u16, caption: *const u16, kind: u32) -> i32;
    }
    // SAFETY: both strings are NUL-terminated and outlive the call.
    unsafe {
        MessageBoxW(core::ptr::null_mut(), wide(msg).as_ptr(), wide("Animas: Ember").as_ptr(), 0x10);
    }
    process::exit(1)
}

#[cfg(not(windows))]
fn fail(msg: &str) -> ! {
    eprintln!("Animas: Ember: {msg}");
    process::exit(1)
}

fn writable_dir(dir: &Path) -> bool {
    if fs::create_dir_all(dir).is_err() {
        return false;
    }
    let probe = dir.join(".write_test");
    let ok = fs::write(&probe, b"ok").is_ok();
    let _ = fs::remove_file(&probe);
    ok
}

/// Points every location Godot uses for user data at `data`.
fn redirect(cmd: &mut Command, data: &Path) {
    let sub = |name: &str| -> PathBuf {
        let p = data.join(name);
        let _ = fs::create_dir_all(&p);
        p
    };
    // Godot honors the XDG variables on Linux and on Windows.
    cmd.env("XDG_DATA_HOME", sub("share"))
        .env("XDG_CONFIG_HOME", sub("config"))
        .env("XDG_CACHE_HOME", sub("cache"));
    #[cfg(windows)]
    cmd.env("APPDATA", sub("roaming"));
    // macOS has no XDG support: Godot builds its paths from $HOME.
    #[cfg(target_os = "macos")]
    cmd.env("HOME", sub("home"));
    cmd.env("ANIMAS_PORTABLE", "1");
}

#[cfg(unix)]
fn launch(mut cmd: Command) -> ! {
    use std::os::unix::process::CommandExt;
    let err = cmd.exec(); // replaces this process; only returns on failure
    fail(&format!("could not start the game: {err}"))
}

#[cfg(not(unix))]
fn launch(mut cmd: Command) -> ! {
    match cmd.status() {
        Ok(status) => process::exit(status.code().unwrap_or(0)),
        Err(err) => fail(&format!("could not start the game: {err}")),
    }
}

fn main() {
    let exe = env::current_exe().unwrap_or_else(|_| PathBuf::from("."));
    let root = exe.parent().map(Path::to_path_buf).unwrap_or_else(|| PathBuf::from("."));
    let bin = root.join("bin");
    let entry = fs::read_to_string(bin.join(".entry")).unwrap_or_default();
    let entry = entry.trim();
    if entry.is_empty() {
        fail("The game files are missing (bin/.entry was not found).\nPlease reinstall the game.");
    }
    let game = bin.join(entry);
    if !game.is_file() {
        fail(&format!("The game executable is missing:\n{}\nPlease reinstall the game.", game.display()));
    }
    let mut cmd = Command::new(&game);
    cmd.args(env::args_os().skip(1)).current_dir(&bin);
    let data = root.join("data");
    if writable_dir(&data) {
        redirect(&mut cmd, &data);
    }
    launch(cmd)
}
