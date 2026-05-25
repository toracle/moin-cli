use anyhow::Result;
use std::collections::HashMap;

#[derive(Debug)]
pub struct WikiRPCClient {
    endpoint: String,
    _alias: Option<String>,
    token: Option<String>,
}

impl WikiRPCClient {
    pub fn new(endpoint: String, alias: Option<String>) -> Self {
        Self { endpoint, _alias: alias, token: None }
    }
    
    pub fn from_config(alias: Option<String>) -> Result<Self> {
        use crate::config::load_config;
        
        // Try to load config, but don't fail if it doesn't exist
        let config = match load_config() {
            Ok(config) => config,
            Err(_) => {
                // No config exists yet, return a client that will prompt for auth
                let endpoint = "http://localhost:8080/?action=xmlrpc2".to_string();
                return Ok(Self::new(endpoint, alias));
            }
        };
        
        // Determine which server to use
        let server_alias = alias.clone().or_else(|| {
            Some(config.settings.default_server.clone())
        });
        
        let server_config = server_alias
            .as_ref()
            .and_then(|alias| config.servers.get(alias))
            .ok_or_else(|| anyhow::anyhow!("Server not found in configuration"))?;
            
        let endpoint = format!("{}/?action=xmlrpc2", server_config.url);
        let token = server_config.access_token.clone();
        
        Ok(Self { endpoint, _alias: alias, token })
    }
    
    async fn make_xmlrpc_call(&self, method: &str, params: Vec<xmlrpc::Value>) -> Result<xmlrpc::Value> {
        use xmlrpc::Request;
        
        let method = method.to_string();
        let endpoint = self.endpoint.clone();
        let token = self.token.clone();
        
        // Use the xmlrpc crate's built-in HTTP transport
        // Note: This uses blocking reqwest internally, but we're in an async context
        // We'll spawn a blocking task for this
        let result = tokio::task::spawn_blocking(move || {
            // Build the XML-RPC request with parameters
            let mut request = Request::new(&method);
            for param in params {
                request = request.arg(param);
            }
            
            // If we have a token, we need to call applyAuthToken first
            // For MoinMoin, we need to call applyAuthToken as a separate request
            if let Some(token) = token {
                // First apply the auth token
                let apply_token_req = Request::new("applyAuthToken").arg(token);
                apply_token_req.call_url(&endpoint)
                    .map_err(|e| format_xmlrpc_error(&e, &endpoint))?;
                
                // Then make our actual request
                request.call_url(&endpoint)
                    .map_err(|e| format_xmlrpc_error(&e, &endpoint))
            } else {
                request.call_url(&endpoint)
                    .map_err(|e| format_xmlrpc_error(&e, &endpoint))
            }
        }).await?;
        
        result
    }
    
    pub async fn get_page(&self, pagename: &str, revision: Option<i32>) -> Result<String> {
        let method = if let Some(_rev) = revision {
            "getPageVersion"
        } else {
            "getPage"
        };
        
        let params = if let Some(rev) = revision {
            vec![
                xmlrpc::Value::String(pagename.to_string()),
                xmlrpc::Value::Int(rev),
            ]
        } else {
            vec![xmlrpc::Value::String(pagename.to_string())]
        };
        
        let result = self.make_xmlrpc_call(method, params).await?;
        
        match result {
            xmlrpc::Value::String(content) => Ok(content),
            _ => Err(anyhow::anyhow!("Unexpected response format for getPage")),
        }
    }
    
    pub async fn get_page_history(&self, pagename: &str) -> Result<Vec<HashMap<String, String>>> {
        let params = vec![
            xmlrpc::Value::String(pagename.to_string()),
        ];
        
        let result = self.make_xmlrpc_call("getRecentChangesWithAttributes", params).await?;
        
        match result {
            xmlrpc::Value::Array(arr) => {
                let mut history = Vec::new();
                for item in arr {
                    if let xmlrpc::Value::Struct(struct_val) = item {
                        let mut entry = HashMap::new();
                        for (key, value) in struct_val {
                            if let xmlrpc::Value::String(s) = value {
                                entry.insert(key, s);
                            }
                        }
                        history.push(entry);
                    }
                }
                Ok(history)
            },
            _ => Ok(Vec::new()),
        }
    }
    
    pub async fn get_auth_token(&self, username: &str, password: &str) -> Result<String> {
        let params = vec![
            xmlrpc::Value::String(username.to_string()),
            xmlrpc::Value::String(password.to_string()),
        ];
        
        let result = self.make_xmlrpc_call("getAuthToken", params).await?;
        
        match result {
            xmlrpc::Value::String(token) => Ok(token),
            _ => Err(anyhow::anyhow!("Unexpected response format for getAuthToken")),
        }
    }
    
    pub async fn get_all_pages(&self) -> Result<Vec<String>> {
        let params = vec![];
        let result = self.make_xmlrpc_call("getAllPages", params).await?;
        
        match result {
            xmlrpc::Value::Array(arr) => {
                let mut pages = Vec::new();
                for item in arr {
                    if let xmlrpc::Value::String(page) = item {
                        pages.push(page);
                    }
                }
                Ok(pages)
            },
            _ => Err(anyhow::anyhow!("Unexpected response format for getAllPages")),
        }
    }
    
    pub async fn search_pages(&self, query: &str) -> Result<Vec<String>> {
        let params = vec![xmlrpc::Value::String(query.to_string())];
        let result = self.make_xmlrpc_call("searchPages", params).await?;
        
        match result {
            xmlrpc::Value::Array(arr) => {
                let mut results = Vec::new();
                for item in arr {
                    if let xmlrpc::Value::String(page) = item {
                        results.push(page);
                    }
                }
                Ok(results)
            },
            _ => Err(anyhow::anyhow!("Unexpected response format for searchPages")),
        }
    }
    
    pub async fn get_recent_changes(&self, days: i32) -> Result<Vec<String>> {
        use chrono::{Utc, Duration};
        
        let since = Utc::now() - Duration::days(days as i64);
        let params = vec![xmlrpc::Value::String(since.to_rfc3339())];
        let result = self.make_xmlrpc_call("getRecentChanges", params).await?;
        
        match result {
            xmlrpc::Value::Array(arr) => {
                let mut changes = Vec::new();
                for item in arr {
                    if let xmlrpc::Value::String(page) = item {
                        changes.push(page);
                    } else if let xmlrpc::Value::Struct(struct_val) = item {
                        if let Some(xmlrpc::Value::String(page)) = struct_val.get("name") {
                            changes.push(page.clone());
                        }
                    }
                }
                Ok(changes)
            },
            _ => Err(anyhow::anyhow!("Unexpected response format for getRecentChanges")),
        }
    }
    
    pub async fn put_page(&self, pagename: &str, content: &str) -> Result<bool> {
        let params = vec![
            xmlrpc::Value::String(pagename.to_string()),
            xmlrpc::Value::String(content.to_string()),
        ];
        
        let result = self.make_xmlrpc_call("putPage", params).await?;
        
        match result {
            xmlrpc::Value::Bool(success) => Ok(success),
            _ => Err(anyhow::anyhow!("Unexpected response format for putPage")),
        }
    }
}

/// Format XML-RPC errors into user-friendly messages
fn format_xmlrpc_error(error: &xmlrpc::Error, endpoint: &str) -> anyhow::Error {
    let error_string = format!("{}", error);
    
    // Check if it's a fault
    if let Some(fault) = error.fault() {
        return anyhow::anyhow!("XML-RPC Fault {}: {}", fault.fault_code, fault.fault_string);
    }
    
    // Check for common transport errors in the string representation
    if error_string.contains("Connection refused") || error_string.contains("connect error") || error_string.contains("Connection reset") {
        anyhow::anyhow!(
            "Could not connect to wiki server at {}\nPlease check that your MoinMoin server is running and the URL is correct.",
            endpoint
        )
    } else if error_string.contains("404") || error_string.contains("Not Found") {
        anyhow::anyhow!(
            "The wiki server at {} does not support XML-RPC or the endpoint is incorrect.\nPlease check your server configuration.",
            endpoint
        )
    } else if error_string.contains("timeout") || error_string.contains("timed out") {
        anyhow::anyhow!(
            "Connection to wiki server at {} timed out.\nPlease check your network connection and try again.",
            endpoint
        )
    } else {
        anyhow::anyhow!("Failed to connect to wiki server at {}: {}", endpoint, error_string)
    }
}
