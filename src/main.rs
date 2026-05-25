use clap::{Parser, Subcommand};
use anyhow::Result;
use std::path::PathBuf;

mod config;
mod xmlrpc_client;

#[derive(Parser)]
#[command(name = "moin-cli")]
#[command(about = "A Rust CLI for MoinMoin wiki servers via XML-RPC with MCP server support")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initial setup and authentication for MoinMoin wiki
    Auth,
    
    /// Get a page's content or history
    Get {
        /// Name of the page to get
        pagename: String,
        
        /// Wiki server alias to use
        #[arg(short, long)]
        server: Option<String>,
        
        /// Specific revision/version of the page
        #[arg(short, long)]
        version: Option<i32>,
        
        /// Show page revision history
        #[arg(long)]
        history: bool,
        
        /// Suppress status messages
        #[arg(short, long)]
        quiet: bool,
    },
    
    /// Update a page's content
    Put {
        /// Name of the page to update
        pagename: String,
        
        /// Content to put on the page
        content: Option<String>,
        
        /// File to read content from
        #[arg(short, long)]
        file: Option<PathBuf>,
        
        /// Wiki server alias to use
        #[arg(short, long)]
        server: Option<String>,
    },
    
    /// List all pages on the wiki
    List {
        /// Wiki server alias to use
        #[arg(short, long)]
        server: Option<String>,
    },
    
    /// Search for pages containing the query text
    Search {
        /// Search query
        query: String,
        
        /// Wiki server alias to use
        #[arg(short, long)]
        server: Option<String>,
    },
    
    /// Show pages changed in the last N days
    Recent {
        /// Number of days to look back (default: 7)
        #[arg(short, long, default_value_t = 7)]
        days: i32,
        
        /// Wiki server alias to use
        #[arg(short, long)]
        server: Option<String>,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Auth => {
            auth_command().await?;
        },
        Commands::Get { pagename, server, version, history, quiet } => {
            get_command(pagename, server, version, history, quiet).await?;
        },
        Commands::Put { pagename, content, file, server } => {
            put_command(pagename, content, file, server).await?;
        },
        Commands::List { server } => {
            list_command(server).await?;
        },
        Commands::Search { query, server } => {
            search_command(query, server).await?;
        },
        Commands::Recent { days, server } => {
            recent_command(days, server).await?;
        },
    }
    
    Ok(())
}

async fn auth_command() -> Result<()> {
    use dialoguer::{Input, Password};
    use crate::config::{Config, Settings, ServerConfig, save_config};
    use crate::xmlrpc_client::WikiRPCClient;
    
    println!("MoinMoin Wiki Authentication Setup");
    
    // Prompt for configuration
    let alias: String = Input::new()
        .with_prompt("Enter wiki name/alias")
        .interact_text()?;
    
    let url: String = Input::new()
        .with_prompt("Enter wiki server URL")
        .interact_text()?;
    
    let username: String = Input::new()
        .with_prompt("Enter wiki username")
        .interact_text()?;
    
    let password: String = Password::new()
        .with_prompt("Enter wiki password")
        .interact()?;
    
    // Create client and get token
    let endpoint = format!("{}/?action=xmlrpc2", url);
    let client = WikiRPCClient::new(endpoint, None);
    let token = client.get_auth_token(&username, &password).await?;
    
    // Create proper config structure
    let config = Config {
        settings: Settings {
            default_server: alias.clone(),
        },
        servers: {
            let mut servers = std::collections::HashMap::new();
            servers.insert(alias.clone(), ServerConfig {
                name: alias.clone(),
                url: url.clone(),
                username: username.clone(),
                access_token: Some(token),
            });
            servers
        },
    };
    
    save_config(&config)?;
    println!("Configuration saved successfully");
    Ok(())
}

async fn get_command(pagename: String, server: Option<String>, version: Option<i32>, history: bool, _quiet: bool) -> Result<()> {
    use crate::xmlrpc_client::WikiRPCClient;
    
    let client = match WikiRPCClient::from_config(server) {
        Ok(client) => client,
        Err(e) => {
            eprintln!("Error loading configuration: {}", e);
            eprintln!("Please run 'moin-cli auth' to set up your wiki connection first.");
            return Err(e);
        }
    };
    
    if history {
        let revisions = client.get_page_history(&pagename).await
            .map_err(|e| anyhow::anyhow!("Failed to get page history: {}", e))?;
        if revisions.is_empty() {
            println!("No history found for {}", pagename);
            return Ok(());
        }
        
        // Print header
        println!("{:<6} {:<20} {:<15} {}", "REV", "DATE", "AUTHOR", "COMMENT");
        println!("{}", "-".repeat(60));
        
        for rev in revisions {
            let v = rev.get("version").unwrap_or(&"N/A".to_string()).clone();
            let d = rev.get("lastModified").unwrap_or(&"N/A".to_string()).clone();
            let a = rev.get("author").unwrap_or(&"N/A".to_string()).clone();
            let c = rev.get("comment").unwrap_or(&"".to_string()).clone();
            println!("{:<6} {:<20} {:<15} {}", v, d, a, c);
        }
    } else {
        let content = client.get_page(&pagename, version).await
            .map_err(|e| anyhow::anyhow!("Failed to get page: {}", e))?;
        println!("{}", content);
    }
    
    Ok(())
}

async fn put_command(pagename: String, content: Option<String>, file: Option<PathBuf>, server: Option<String>) -> Result<()> {
    use crate::xmlrpc_client::WikiRPCClient;
    
    let mut final_content = content.unwrap_or_default();
    
    // Read from file if provided
    if let Some(file_path) = file {
        let mut file = std::fs::File::open(file_path)?;
        let mut buffer = String::new();
        std::io::Read::read_to_string(&mut file, &mut buffer)?;
        final_content = buffer;
    } else if final_content.is_empty() {
        // Read from stdin if no content and no file provided
        let mut buffer = String::new();
        std::io::Read::read_to_string(&mut std::io::stdin(), &mut buffer)?;
        final_content = buffer;
    }
    
    let client = WikiRPCClient::from_config(server)
        .map_err(|e| anyhow::anyhow!("Failed to load configuration: {}. Please run 'moin-cli auth' first.", e))?;
    
    let success = client.put_page(&pagename, &final_content).await
        .map_err(|e| anyhow::anyhow!("Failed to update page: {}", e))?;
    
    if success {
        println!("Successfully updated {}", pagename);
    } else {
        eprintln!("Failed to update {}", pagename);
    }
    
    Ok(())
}

async fn list_command(server: Option<String>) -> Result<()> {
    use crate::xmlrpc_client::WikiRPCClient;
    
    let client = WikiRPCClient::from_config(server)
        .map_err(|e| anyhow::anyhow!("Failed to load configuration: {}. Please run 'moin-cli auth' first.", e))?;
    
    let pages = client.get_all_pages().await
        .map_err(|e| anyhow::anyhow!("Failed to get pages: {}", e))?;
    
    for page in pages {
        println!("{}", page);
    }
    
    Ok(())
}

async fn search_command(query: String, server: Option<String>) -> Result<()> {
    use crate::xmlrpc_client::WikiRPCClient;
    
    let client = WikiRPCClient::from_config(server)
        .map_err(|e| anyhow::anyhow!("Failed to load configuration: {}. Please run 'moin-cli auth' first.", e))?;
    
    let results = client.search_pages(&query).await
        .map_err(|e| anyhow::anyhow!("Failed to search pages: {}", e))?;
    
    for page in results {
        println!("{}", page);
    }
    
    Ok(())
}

async fn recent_command(days: i32, server: Option<String>) -> Result<()> {
    use crate::xmlrpc_client::WikiRPCClient;
    
    let client = WikiRPCClient::from_config(server)
        .map_err(|e| anyhow::anyhow!("Failed to load configuration: {}. Please run 'moin-cli auth' first.", e))?;
    
    let pages = client.get_recent_changes(days).await
        .map_err(|e| anyhow::anyhow!("Failed to get recent changes: {}", e))?;
    
    if pages.is_empty() {
        println!("No changes in the last {} days", days);
        return Ok(());
    }
    
    for page in pages {
        println!("{}", page);
    }
    
    Ok(())
}
