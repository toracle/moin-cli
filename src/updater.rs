use anyhow::{Context, Result};
use serde::Deserialize;
use std::env;
use std::fs;
#[cfg(unix)]
use std::fs::Permissions;
#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};

use crate::{VERSION, REPO_URL};

/// GitHub release information
#[derive(Debug, Deserialize)]
pub struct GitHubRelease {
    pub tag_name: String,
    #[allow(dead_code)]
    pub name: String,
    pub assets: Vec<ReleaseAsset>,
}

#[derive(Debug, Deserialize)]
pub struct ReleaseAsset {
    pub name: String,
    pub browser_download_url: String,
}

/// Check for available updates from GitHub
pub async fn check_for_updates() -> Result<Option<GitHubRelease>> {
    let client = reqwest::Client::new();
    
    // Get the latest release from GitHub
    let releases_url = format!("{}/releases/latest", REPO_URL);
    
    let response = client
        .get(&releases_url)
        .header("Accept", "application/vnd.github.v3+json")
        .header("User-Agent", "moin-cli/0.1.0")
        .send()
        .await
        .context("Failed to fetch latest release from GitHub")?;
    
    // Check for redirects (302) - means no latest release
    if response.status() == reqwest::StatusCode::FOUND ||
       response.status() == reqwest::StatusCode::SEE_OTHER ||
       response.status() == reqwest::StatusCode::MOVED_PERMANENTLY {
        // Redirect to /releases means no latest release exists
        return Ok(None);
    }
    
    if !response.status().is_success() {
        // If 404, there might be no releases yet
        if response.status() == reqwest::StatusCode::NOT_FOUND ||
           response.status() == reqwest::StatusCode::NOT_ACCEPTABLE {
            return Ok(None);
        }
        return Err(anyhow::anyhow!(
            "GitHub API error: {}", 
            response.status()
        ));
    }
    
    let release: GitHubRelease = response
        .json()
        .await
        .context("Failed to parse release JSON")?;
    
    // Compare versions
    let latest_version = release.tag_name.trim_start_matches('v');
    let current_version = VERSION.trim_start_matches('v');
    
    if version_compare(latest_version, current_version) > 0 {
        Ok(Some(release))
    } else {
        Ok(None)
    }
}

/// Compare two version strings
/// Returns 1 if a > b, -1 if a < b, 0 if equal
pub fn version_compare(a: &str, b: &str) -> i32 {
    let a_parts: Vec<u32> = a
        .split('.')
        .filter_map(|s| s.parse().ok())
        .collect();
    let b_parts: Vec<u32> = b
        .split('.')
        .filter_map(|s| s.parse().ok())
        .collect();
    
    let max_len = a_parts.len().max(b_parts.len());
    
    for i in 0..max_len {
        let a_val = a_parts.get(i).copied().unwrap_or(0);
        let b_val = b_parts.get(i).copied().unwrap_or(0);
        
        match a_val.cmp(&b_val) {
            std::cmp::Ordering::Greater => return 1,
            std::cmp::Ordering::Less => return -1,
            std::cmp::Ordering::Equal => continue,
        }
    }
    
    0
}

/// Get the appropriate download URL for the current platform
pub fn get_platform_download_url(release: &GitHubRelease) -> Result<String> {
    let target = get_target_triplet()?;
    let arch = env::consts::ARCH;
    let os = env::consts::OS;
    
    // Try to find matching asset
    for asset in &release.assets {
        let name = asset.name.to_lowercase();
        
        // Check for platform-specific binary
        if name.contains(&target.to_lowercase()) ||
           name.contains("universal") ||
           name.contains("static") {
            
            // Check for common binary extensions
            if name.ends_with(".tar.gz") || 
               name.ends_with(".tgz") || 
               name.ends_with(".zip") ||
               name.contains("moin-cli") {
                return Ok(asset.browser_download_url.clone());
            }
        }
    }
    
    // Fallback: try common patterns
    for asset in &release.assets {
        let name = asset.name.to_lowercase();
        
        if (os == "linux" && (name.contains("linux") || name.contains("gnu"))) ||
           (os == "windows" && (name.contains("windows") || name.contains("msvc") || name.ends_with(".exe"))) ||
           (os == "macos" && (name.contains("macos") || name.contains("darwin") || name.contains("apple"))) {
            
            if name.ends_with(".tar.gz") || 
               name.ends_with(".tgz") || 
               name.ends_with(".zip") ||
               name.ends_with(".exe") ||
               name.contains("moin-cli") {
                return Ok(asset.browser_download_url.clone());
            }
        }
    }
    
    // Last resort: return any asset URL
    if !release.assets.is_empty() {
        return Ok(release.assets[0].browser_download_url.clone());
    }
    
    Err(anyhow::anyhow!(
        "No downloadable assets found for platform: {} on {}/{}",
        target,
        arch,
        os
    ))
}

/// Download a file from a URL using streaming for memory efficiency
pub async fn download_file(url: &str, dest: &Path) -> Result<()> {
    let client = reqwest::Client::new();
    
    let mut response = client
        .get(url)
        .header("User-Agent", "moin-cli/0.1.0")
        .send()
        .await
        .context("Failed to start download")?;
    
    if !response.status().is_success() {
        return Err(anyhow::anyhow!(
            "Failed to download: HTTP {}", 
            response.status()
        ));
    }
    
    // Create parent directories if needed
    if let Some(parent) = dest.parent() {
        tokio::fs::create_dir_all(parent)
            .await
            .context("Failed to create destination directory")?;
    }
    
    let mut file = tokio::fs::File::create(dest)
        .await
        .with_context(|| format!("Failed to create file: {:?}", dest))?;
    
    // Stream the download to avoid loading entire file into memory
    while let Some(chunk) = response
        .chunk()
        .await
        .context("Failed to read download chunk")?
    {
        tokio::io::AsyncWriteExt::write_all(&mut file, &chunk)
            .await
            .context("Failed to write download chunk to file")?;
    }
    
    Ok(())
}

/// Extract a tar.gz file
#[cfg(unix)]
fn extract_tar_gz(tarball_path: &Path, dest_dir: &Path) -> Result<PathBuf> {
    use std::process::Command;
    
    if !dest_dir.exists() {
        fs::create_dir_all(dest_dir)
            .context("Failed to create temp directory")?;
    }
    
    let output = Command::new("tar")
        .arg("-xzf")
        .arg(tarball_path)
        .arg("-C")
        .arg(dest_dir)
        .output()
        .context("Failed to execute tar")?;
    
    if !output.status.success() {
        return Err(anyhow::anyhow!(
            "tar extraction failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    
    // Find the extracted binary
    for entry in walkdir::WalkDir::new(dest_dir) {
        let entry = entry?;
        let path = entry.path();
        
        if path.is_file() && path.file_name() == Some(std::ffi::OsStr::new("moin-cli")) {
            return Ok(path.to_path_buf());
        }
    }
    
    Err(anyhow::anyhow!("Binary not found in archive"))
}

/// Perform self-update to the latest version
pub async fn perform_self_update(release: &GitHubRelease) -> Result<()> {
    use dialoguer::Confirm;
    
    let download_url = get_platform_download_url(release)?;
    println!("Downloading update from: {}", download_url);
    
    // Create temporary directory for download
    let temp_dir = tempfile::tempdir()
        .context("Failed to create temporary directory")?;
    let temp_path = temp_dir.path();
    
    // Determine filename from URL
    let filename = download_url.split('/').last()
        .unwrap_or("moin-cli.tar.gz");
    let download_path = temp_path.join(filename);
    
    // Download the file
    download_file(&download_url, &download_path).await?;
    println!("Download complete");
    
    // Extract based on file type
    let extracted_binary = if filename.ends_with(".tar.gz") || filename.ends_with(".tgz") {
        #[cfg(unix)]
        {
            extract_tar_gz(&download_path, temp_path)?
        }
        #[cfg(not(unix))]
        {
            return Err(anyhow::anyhow!("tar.gz extraction not supported on this platform"));
        }
    } else if filename.ends_with(".zip") {
        #[cfg(unix)]
        {
            extract_zip(&download_path, temp_path)?
        }
        #[cfg(not(unix))]
        {
            extract_zip(&download_path, temp_path)?
        }
    } else if filename.ends_with(".exe") {
        download_path
    } else {
        download_path
    };
    
    println!("Binary extracted to: {:?}", extracted_binary);
    
    // Ask for confirmation before replacing
    if !Confirm::new()
        .with_prompt(format!(
            "Replace current moin-cli with v{}?",
            release.tag_name
        ))
        .default(true)
        .interact()?
    {
        println!("Update cancelled");
        return Ok(());
    }
    
    // Get current executable path
    let current_exe = env::current_exe()
        .context("Failed to get current executable path")?;
    
    // Make backup of current binary
    let backup_path = current_exe.with_extension("bak");
    fs::copy(&current_exe, &backup_path)
        .context("Failed to create backup of current binary")?;
    println!("Backup created at: {:?}", backup_path);
    
    // Replace current binary with new one
    fs::copy(&extracted_binary, &current_exe)
        .context("Failed to replace current binary")?;
    
    // Set executable permissions on Unix
    #[cfg(unix)]
    {
        let perms = Permissions::from_mode(0o755);
        if let Err(e) = fs::set_permissions(&current_exe, perms) {
            eprintln!("Warning: Failed to set executable permissions: {}", e);
        }
    }
    
    println!("Successfully updated to version {}", release.tag_name);
    
    // Clean up temp directory (will be auto-deleted when temp_dir is dropped)
    // But we can try to clean up backup if update was successful
    fs::remove_file(backup_path)
        .ok(); // Ignore errors
    
    Ok(())
}

/// Extract a zip file
fn extract_zip(zip_path: &Path, dest_dir: &Path) -> Result<PathBuf> {
    use std::process::Command;
    
    if !dest_dir.exists() {
        fs::create_dir_all(dest_dir)
            .context("Failed to create temp directory")?;
    }
    
    // Try unzip command first
    let output = Command::new("unzip")
        .arg("-o")
        .arg(zip_path)
        .arg("-d")
        .arg(dest_dir)
        .output();
    
    let output = match output {
        Ok(o) => o,
        Err(_) => {
            // Try using 7z utility
            Command::new("7z")
                .arg("x")
                .arg(zip_path)
                .arg("-o")
                .arg(dest_dir)
                .output()
                .context("Failed to execute 7z")?
        }
    };
    
    if !output.status.success() {
        return Err(anyhow::anyhow!(
            "Zip extraction failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    
    // Find the extracted binary
    for entry in walkdir::WalkDir::new(dest_dir) {
        let entry = entry?;
        let path = entry.path();
        
        let file_name = path.file_name().unwrap_or_default();
        let file_name_str = file_name.to_string_lossy();
        
        if path.is_file() && (file_name_str == "moin-cli" || file_name_str == "moin-cli.exe") {
            return Ok(path.to_path_buf());
        }
    }
    
    Err(anyhow::anyhow!("Binary not found in zip archive"))
}

/// Get the target triplet for the current platform
pub fn get_target_triplet() -> Result<String> {
    // Try to get from environment variables first
    if let Ok(target) = env::var("CARGO_CFG_TARGET_TRIPLE") {
        return Ok(target);
    }
    
    // Build target triplet based on platform
    let arch = env::consts::ARCH;
    let os = env::consts::OS;
    
    let target = match (arch, os) {
        ("x86_64", "linux") => "x86_64-unknown-linux-gnu",
        ("x86_64", "windows") => "x86_64-pc-windows-msvc",
        ("x86_64", "macos") => "x86_64-apple-darwin",
        ("aarch64", "linux") => "aarch64-unknown-linux-gnu",
        ("aarch64", "macos") => "aarch64-apple-darwin",
        ("arm", "linux") => "arm-unknown-linux-gnueabi",
        ("arm64", "macos") => "aarch64-apple-darwin",
        _ => return Err(anyhow::anyhow!(
            "Unsupported platform: {}/{}", 
            arch, 
            os
        )),
    };
    
    Ok(target.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_version_compare() {
        assert_eq!(version_compare("1.0.0", "1.0.0"), 0);
        assert_eq!(version_compare("1.0.1", "1.0.0"), 1);
        assert_eq!(version_compare("1.0.0", "1.0.1"), -1);
        assert_eq!(version_compare("2.0.0", "1.9.9"), 1);
        assert_eq!(version_compare("1.9.9", "2.0.0"), -1);
        assert_eq!(version_compare("1.0", "1.0.0"), 0);
        assert_eq!(version_compare("1", "1.0.0"), 0);
    }
}
