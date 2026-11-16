//! Animas: Ember self-extracting installer *stub*.
//!
//! A finished installer is this stub followed by a zip payload and a 16-byte trailer
//! (the payload length as a little-endian u64, then the magic bytes `ANIMASFX`).
//! `tools/package_portable.py` builds it. The stub finds its own payload, asks where to
//! install (portable: by default a folder next to the installer), extracts it, and can
//! launch the game. The `data` folder (saves and settings) is never overwritten.

use std::env;
use std::fs::{self, File};
use std::io::{self, BufReader, IsTerminal, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode};

use zip::ZipArchive;

const MAGIC: &[u8; 8] = b"ANIMASFX";
const TRAILER: u64 = 16;
const TITLE: &str = "Animas: Ember";
const DEFAULT_FOLDER: &str = "Animas Ember";
/// Never overwritten on update: this is where the player's saves and settings live.
const KEEP_DIR: &str = "data";
/// Payload entry holding the path of the launcher, relative to the install folder.
const LAUNCH_ENTRY: &str = ".launch";

/// A read-only, seekable window onto the payload bytes at the end of this executable.
struct Section {
    file: File,
    start: u64,
    len: u64,
    pos: u64,
}

impl Read for Section {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        let remaining = self.len.saturating_sub(self.pos);
        if remaining == 0 {
            return Ok(0);
        }
        let want = buf.len().min(remaining as usize);
        self.file.seek(SeekFrom::Start(self.start + self.pos))?;
        let got = self.file.read(&mut buf[..want])?;
        self.pos += got as u64;
        Ok(got)
    }
}

impl Seek for Section {
    fn seek(&mut self, to: SeekFrom) -> io::Result<u64> {
        let target = match to {
            SeekFrom::Start(n) => n as i128,
            SeekFrom::End(n) => self.len as i128 + n as i128,
            SeekFrom::Current(n) => self.pos as i128 + n as i128,
        };
        if target < 0 {
            return Err(io::Error::new(io::ErrorKind::InvalidInput, "seek before the start"));
        }
        self.pos = target as u64;
        Ok(self.pos)
    }
}

type Payload = ZipArchive<BufReader<Section>>;

fn open_payload() -> Result<Payload, String> {
    let exe = env::current_exe().map_err(|e| format!("cannot locate this program: {e}"))?;
    let mut file = File::open(&exe).map_err(|e| format!("cannot read {}: {e}", exe.display()))?;
    let size = file.metadata().map_err(|e| e.to_string())?.len();
    if size < TRAILER {
        return Err("this is a bare installer stub with no game attached".into());
    }
    file.seek(SeekFrom::End(-(TRAILER as i64))).map_err(|e| e.to_string())?;
    let mut trailer = [0u8; TRAILER as usize];
    file.read_exact(&mut trailer).map_err(|e| e.to_string())?;
    if &trailer[8..] != MAGIC {
        return Err("this is a bare installer stub with no game attached.\n       Build a real installer with tools/package_portable.py.".into());
    }
    let len = u64::from_le_bytes(trailer[..8].try_into().unwrap());
    if len == 0 || len > size - TRAILER {
        return Err("the installer is damaged (bad payload size). Please download it again.".into());
    }
    let section = Section { file, start: size - TRAILER - len, len, pos: 0 };
    ZipArchive::new(BufReader::new(section))
        .map_err(|e| format!("the installer is damaged ({e}). Please download it again."))
}

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
                     -d, --dir <PATH>  install into PATH (default: a \"{DEFAULT_FOLDER}\" folder next to this file)\n  \
                     -y, --yes         do not ask any questions; use the defaults\n  \
                     -r, --run         launch the game when the install finishes\n  \
                     -l, --list        list the files inside this installer and exit\n  \
                     -V, --version     print the version and exit\n  \
                     -h, --help        show this help\n\n\
                     Your saves and settings live in the \"{KEEP_DIR}\" folder, which is never overwritten.",
                    env!("CARGO_PKG_VERSION")
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

fn pause() {
    if cfg!(windows) {
        let _ = ask("\nPress Enter to close...");
    }
}

fn read_launch_entry(zip: &mut Payload) -> Option<String> {
    let mut entry = zip.by_name(LAUNCH_ENTRY).ok()?;
    let mut text = String::new();
    entry.read_to_string(&mut text).ok()?;
    let text = text.trim().to_string();
    (!text.is_empty()).then_some(text)
}

/// Extracts everything into `dir`. Returns (files written, files kept because they are user data).
fn extract(zip: &mut Payload, dir: &Path, total: u64) -> Result<(u32, u32), String> {
    let (mut written, mut kept, mut done, mut last) = (0u32, 0u32, 0u64, u64::MAX);
    for i in 0..zip.len() {
        let mut entry = zip.by_index(i).map_err(|e| format!("entry {i}: {e}"))?;
        // enclosed_name() rejects absolute paths and ".." escapes (zip-slip).
        let Some(rel) = entry.enclosed_name().map(Path::to_path_buf) else { continue };
        let out = dir.join(&rel);
        if entry.is_dir() {
            fs::create_dir_all(&out).map_err(|e| format!("cannot create {}: {e}", out.display()))?;
            continue;
        }
        if let Some(parent) = out.parent() {
            fs::create_dir_all(parent).map_err(|e| format!("cannot create {}: {e}", parent.display()))?;
        }
        let size = entry.size();
        if rel.starts_with(KEEP_DIR) && out.exists() {
            kept += 1;
        } else {
            let mut file = File::create(&out).map_err(|e| {
                format!("cannot write {}: {e}\n       (If the game is running, close it and try again.)", out.display())
            })?;
            io::copy(&mut entry, &mut file).map_err(|e| format!("{}: {e}", rel.display()))?;
            #[cfg(unix)]
            if let Some(mode) = entry.unix_mode() {
                use std::os::unix::fs::PermissionsExt;
                let _ = fs::set_permissions(&out, fs::Permissions::from_mode(mode & 0o7777));
            }
            written += 1;
        }
        done += size;
        let pct = if total == 0 { 100 } else { done * 100 / total };
        if pct != last {
            last = pct;
            let filled = (pct * 30 / 100) as usize;
            print!("\r  [{}{}] {pct:>3}%", "#".repeat(filled), "-".repeat(30 - filled));
            let _ = io::stdout().flush();
        }
    }
    println!();
    Ok((written, kept))
}

fn run() -> Result<(), String> {
    let Some(opts) = parse_args()? else { return Ok(()) };
    let mut zip = open_payload()?;

    let mut total = 0u64;
    let mut files = 0u32;
    for i in 0..zip.len() {
        let e = zip.by_index(i).map_err(|e| e.to_string())?;
        if !e.is_dir() {
            total += e.size();
            files += 1;
        }
    }
    if opts.list {
        for i in 0..zip.len() {
            let e = zip.by_index(i).map_err(|e| e.to_string())?;
            println!("{:>10}  {}", e.size(), e.name());
        }
        return Ok(());
    }

    let interactive = !opts.yes && io::stdin().is_terminal();
    println!("{TITLE} installer {}\n  {files} files, {} once installed\n", env!("CARGO_PKG_VERSION"), human(total));

    let default_dir = env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|d| d.join(DEFAULT_FOLDER)))
        .unwrap_or_else(|| PathBuf::from(DEFAULT_FOLDER));
    let dir = match opts.dir {
        Some(d) => d,
        None if interactive => {
            let answer = ask(&format!("Install folder [{}]: ", default_dir.display()));
            if answer.is_empty() { default_dir } else { PathBuf::from(answer) }
        }
        None => default_dir,
    };
    if dir.join(KEEP_DIR).is_dir() {
        println!("Updating the existing install. Your \"{KEEP_DIR}\" folder (saves and settings) is kept.");
    }
    println!("Installing to {}", dir.display());
    fs::create_dir_all(&dir).map_err(|e| format!("cannot create {}: {e}", dir.display()))?;

    let launch = read_launch_entry(&mut zip);
    let (written, kept) = extract(&mut zip, &dir, total)?;
    println!("Done: {written} files installed{}.", if kept > 0 { format!(", {kept} user-data files kept") } else { String::new() });

    let mut start = opts.run;
    if interactive && !start {
        start = !ask(&format!("Launch {TITLE} now? [Y/n] ")).to_lowercase().starts_with('n');
    }
    if start {
        match launch {
            Some(rel) => {
                Command::new(dir.join(&rel)).current_dir(&dir).spawn().map_err(|e| format!("could not start the game: {e}"))?;
            }
            None => println!("(This installer does not say how to start the game, so it was not launched.)"),
        }
    } else {
        println!("\nTo play, run the \"{}\" launcher in that folder.", launch.as_deref().unwrap_or("game"));
    }
    if interactive {
        pause();
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(msg) => {
            eprintln!("\nError: {msg}");
            if io::stdin().is_terminal() {
                pause();
            }
            ExitCode::from(1)
        }
    }
}
