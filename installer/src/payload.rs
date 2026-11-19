//! The installer payload: a zip appended to the installer executable, found through a trailer.
//!
//! Layout of an installer file:  [stub program][zip payload][payload length: u64 LE][b"ANIMASFX"]
//! Shared by the console stub (sfx.rs) and the Windows GUI stub (installer-gui), which includes this
//! file with #[path]. Keep it to the API subset that zip 0.6 and 2.x have in common.

use std::env;
use std::fs::{self, File};
use std::io::{self, BufReader, Read, Seek, SeekFrom};
use std::path::{Path, PathBuf};

use zip::ZipArchive;

pub const MAGIC: &[u8; 8] = b"ANIMASFX";
pub const TRAILER: u64 = 16;
pub const DEFAULT_FOLDER: &str = "Animas Ember";
/// Never overwritten on update: this is where the player's saves and settings live.
pub const KEEP_DIR: &str = "data";
/// Payload entry holding the path of the launcher, relative to the install folder.
pub const LAUNCH_ENTRY: &str = ".launch";

/// A read-only, seekable window onto the payload bytes at the end of this executable.
pub struct Section {
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

pub type Payload = ZipArchive<BufReader<Section>>;

pub fn open_payload() -> Result<Payload, String> {
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
    ZipArchive::new(BufReader::new(section)).map_err(|e| format!("the installer is damaged ({e}). Please download it again."))
}

/// (number of files, total uncompressed bytes)
pub fn totals(zip: &mut Payload) -> Result<(u32, u64), String> {
    let (mut files, mut bytes) = (0u32, 0u64);
    for i in 0..zip.len() {
        let e = zip.by_index(i).map_err(|e| e.to_string())?;
        if !e.is_dir() {
            files += 1;
            bytes += e.size();
        }
    }
    Ok((files, bytes))
}

pub fn launch_entry(zip: &mut Payload) -> Option<String> {
    let mut entry = zip.by_name(LAUNCH_ENTRY).ok()?;
    let mut text = String::new();
    entry.read_to_string(&mut text).ok()?;
    let text = text.trim().to_string();
    (!text.is_empty()).then_some(text)
}

/// By default, a "Animas Ember" folder next to the installer.
pub fn default_dir() -> PathBuf {
    env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|d| d.join(DEFAULT_FOLDER)))
        .unwrap_or_else(|| PathBuf::from(DEFAULT_FOLDER))
}

#[derive(Debug, Default, Clone)]
pub struct Summary {
    pub written: u32,
    /// Files in the data folder that already existed and were left alone.
    pub kept: u32,
    /// Other existing files left alone because overwriting was turned off.
    pub skipped: u32,
    /// The launcher's path relative to the install folder, if the payload names one.
    pub launch: Option<String>,
}

/// Extracts everything into `dir`. `progress(bytes_done, current_file)` is called after each file;
/// return false from it to cancel. Unsafe paths (absolute, "..") are skipped; the data folder is never overwritten.
pub fn extract(
    zip: &mut Payload,
    dir: &Path,
    overwrite: bool,
    progress: &mut dyn FnMut(u64, &str) -> bool,
) -> Result<Summary, String> {
    let mut sum = Summary { launch: launch_entry(zip), ..Default::default() };
    let mut done = 0u64;
    fs::create_dir_all(dir).map_err(|e| format!("cannot create {}: {e}", dir.display()))?;
    for i in 0..zip.len() {
        let mut entry = zip.by_index(i).map_err(|e| format!("entry {i}: {e}"))?;
        // enclosed_name() rejects absolute paths and ".." escapes (zip-slip).
        let Some(rel) = entry.enclosed_name().map(|p| p.to_path_buf()) else { continue };
        let out = dir.join(&rel);
        if entry.is_dir() {
            fs::create_dir_all(&out).map_err(|e| format!("cannot create {}: {e}", out.display()))?;
            continue;
        }
        if let Some(parent) = out.parent() {
            fs::create_dir_all(parent).map_err(|e| format!("cannot create {}: {e}", parent.display()))?;
        }
        let size = entry.size();
        let exists = out.exists();
        if rel.starts_with(KEEP_DIR) && exists {
            sum.kept += 1;
        } else if !overwrite && exists {
            sum.skipped += 1;
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
            sum.written += 1;
        }
        done += size;
        if !progress(done, &rel.to_string_lossy()) {
            return Err("cancelled".into());
        }
    }
    Ok(sum)
}
