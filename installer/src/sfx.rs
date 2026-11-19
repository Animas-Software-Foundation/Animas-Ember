//! Animas: Ember self-extracting installer *stub* (console version, used on Linux and macOS).
//!
//! A finished installer is this stub followed by a zip payload and a 16-byte trailer (see payload.rs).
//! `tools/package_portable.py` builds it. The stub finds its own payload, asks where to install
//! (portable: by default a folder next to the installer), extracts it, and can launch the game.
//! The `data` folder (saves and settings) is never overwritten. On Windows the installer is the
//! graphical one in installer-gui/ instead.

mod payload;

use std::env;
use std::io::{self, IsTerminal, Write};
use std::path::PathBuf;
use std::process::{Command, ExitCode};

const TITLE: &str = "Animas: Ember";

struct Options {
    dir: Option<PathBuf>,
    yes: bool,
    run: bool,
    list: bool,
}

fn parse_args() -> Result<Option<Options>, String> {
    let mut o = Options { dir: None, yes: false, run: false, list: false };
    let mut args = env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "-h" | "--help" => {
                println!(
                    "{TITLE} installer {}\n\n\
                     USAGE: installer [OPTIONS]\n\n\
                     OPTIONS:\n  \
                     -d, --dir <PATH>  install into PATH (default: a \"{}\" folder next to this file)\n  \
                     -y, --yes         do not ask any questions; use the defaults\n  \
                     -r, --run         launch the game when the install finishes\n  \
                     -l, --list        list the files inside this installer and exit\n  \
                     -V, --version     print the version and exit\n  \
                     -h, --help        show this help\n\n\
                     Your saves and settings live in the \"{}\" folder, which is never overwritten.",
                    env!("CARGO_PKG_VERSION"),
                    payload::DEFAULT_FOLDER,
                    payload::KEEP_DIR
                );
                return Ok(None);
            }
            "-V" | "--version" => {
                println!("{}", env!("CARGO_PKG_VERSION"));
                return Ok(None);
            }
            "-d" | "--dir" => o.dir = Some(PathBuf::from(args.next().ok_or("--dir needs a path")?)),
            "-y" | "--yes" => o.yes = true,
            "-r" | "--run" => o.run = true,
            "-l" | "--list" => o.list = true,
            other => return Err(format!("unknown option '{other}' (try --help)")),
        }
    }
    Ok(Some(o))
}

fn human(bytes: u64) -> String {
    let mb = bytes as f64 / 1_048_576.0;
    if mb >= 1.0 { format!("{mb:.1} MB") } else { format!("{:.0} KB", bytes as f64 / 1024.0) }
}

fn ask(prompt: &str) -> String {
    print!("{prompt}");
    let _ = io::stdout().flush();
    let mut line = String::new();
    let _ = io::stdin().read_line(&mut line);
    line.trim().trim_matches('"').to_string()
}

fn run() -> Result<(), String> {
    let Some(opts) = parse_args()? else { return Ok(()) };
    let mut zip = payload::open_payload()?;
    let (files, total) = payload::totals(&mut zip)?;
    if opts.list {
        for i in 0..zip.len() {
            let e = zip.by_index(i).map_err(|e| e.to_string())?;
            println!("{:>10}  {}", e.size(), e.name());
        }
        return Ok(());
    }

    let interactive = !opts.yes && io::stdin().is_terminal();
    println!("{TITLE} installer {}\n  {files} files, {} once installed\n", env!("CARGO_PKG_VERSION"), human(total));

    let default_dir = payload::default_dir();
    let dir = match opts.dir {
        Some(d) => d,
        None if interactive => {
            let answer = ask(&format!("Install folder [{}]: ", default_dir.display()));
            if answer.is_empty() { default_dir } else { PathBuf::from(answer) }
        }
        None => default_dir,
    };
    if dir.join(payload::KEEP_DIR).is_dir() {
        println!("Updating the existing install. Your \"{}\" folder (saves and settings) is kept.", payload::KEEP_DIR);
    }
    println!("Installing to {}", dir.display());

    let mut last = u64::MAX;
    let sum = payload::extract(&mut zip, &dir, true, &mut |done, _| {
        let pct = if total == 0 { 100 } else { done * 100 / total };
        if pct != last {
            last = pct;
            let filled = (pct * 30 / 100) as usize;
            print!("\r  [{}{}] {pct:>3}%", "#".repeat(filled), "-".repeat(30 - filled));
            let _ = io::stdout().flush();
        }
        true
    })?;
    println!();
    println!("Done: {} files installed{}.", sum.written, if sum.kept > 0 { format!(", {} user-data files kept", sum.kept) } else { String::new() });

    let mut start = opts.run;
    if interactive && !start {
        start = !ask(&format!("Launch {TITLE} now? [Y/n] ")).to_lowercase().starts_with('n');
    }
    if start {
        match &sum.launch {
            Some(rel) => {
                Command::new(dir.join(rel)).current_dir(&dir).spawn().map_err(|e| format!("could not start the game: {e}"))?;
            }
            None => println!("(This installer does not say how to start the game, so it was not launched.)"),
        }
    } else {
        println!("\nTo play, run the \"{}\" launcher in that folder.", sum.launch.as_deref().unwrap_or("game"));
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(msg) => {
            eprintln!("\nError: {msg}");
            ExitCode::from(1)
        }
    }
}
