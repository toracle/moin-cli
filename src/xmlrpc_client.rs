use anyhow::Result;
use std::collections::HashMap;

#[derive(Debug)]
pub struct WikiRPCClient {
    endpoint: String,
    _alias: Option<String>,
    token: Option<String>,
}

/// Convert an xmlrpc::Value to a String representation, handling common types.
fn value_to_string(value: &xmlrpc::Value) -> String {
    match value {
        xmlrpc::Value::String(s) => s.clone(),
        xmlrpc::Value::Int(i) => i.to_string(),
        xmlrpc::Value::Int64(i) => i.to_string(),
        xmlrpc::Value::Bool(b) => b.to_string(),
        xmlrpc::Value::Double(d) => d.to_string(),
        xmlrpc::Value::DateTime(dt) => format!("{}", dt),
        _ => format!("{:?}", value),
    }
}

/// Extract the method result from a multicall response.
///
/// The multicall response is an array where each element is either:
/// - `Value::Array([actual_value])` on success
/// - `Value::Struct({"faultCode": ..., "faultString": ...})` on fault
///
/// We extract the result at `index` (typically 1 for the actual method call).
fn extract_multicall_result(multicall_result: xmlrpc::Value, index: usize) -> Result<xmlrpc::Value> {
    match multicall_result {
        xmlrpc::Value::Array(ref arr) => {
            if arr.len() <= index {
                return Err(anyhow::anyhow!(
                    "Multicall response has {} elements, expected at least {}",
                    arr.len(),
                    index + 1
                ));
            }
            let element = &arr[index];
            match element {
                // Success: wrapped as [result]
                xmlrpc::Value::Array(inner) => {
                    if inner.is_empty() {
                        Ok(xmlrpc::Value::Nil)
                    } else {
                        Ok(inner[0].clone())
                    }
                }
                // Fault: struct with faultCode and faultString
                xmlrpc::Value::Struct(map) => {
                    let fault_code = map
                        .get("faultCode")
                        .and_then(|v| v.as_i32())
                        .unwrap_or(-1);
                    let fault_string = map
                        .get("faultString")
                        .and_then(|v| v.as_str())
                        .unwrap_or("Unknown fault");
                    Err(anyhow::anyhow!(
                        "XML-RPC Fault {}: {}",
                        fault_code,
                        fault_string
                    ))
                }
                other => Err(anyhow::anyhow!(
                    "Unexpected multicall element type: {:?}",
                    other
                )),
            }
        }
        other => Err(anyhow::anyhow!(
            "Expected array from multicall, got: {:?}",
            other
        )),
    }
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
            .and_then(|a| config.servers.get(a))
            .ok_or_else(|| anyhow::anyhow!("Server not found in configuration"))?;

        let endpoint = format!("{}/?action=xmlrpc2", server_config.url);
        let token = server_config.access_token.clone();

        Ok(Self { endpoint, _alias: alias, token })
    }

    /// Make an XML-RPC call, bundling with applyAuthToken via system.multicall
    /// when a token is present. This ensures auth and the method execute in a
    /// single HTTP request so that the MoinMoin session applies correctly.
    async fn make_xmlrpc_call(&self, method: &str, params: Vec<xmlrpc::Value>) -> Result<xmlrpc::Value> {
        use xmlrpc::Request;

        let method = method.to_string();
        let endpoint = self.endpoint.clone();
        let token = self.token.clone();

        tokio::task::spawn_blocking(move || {
            if let Some(token) = token {
                // Bundle applyAuthToken + actual method in a single system.multicall request
                let auth_req = Request::new("applyAuthToken").arg(token);

                let mut actual_req = Request::new(&method);
                for param in params {
                    actual_req = actual_req.arg(param);
                }

                let multicall = Request::new_multicall([&auth_req, &actual_req]);
                let multicall_result = multicall
                    .call_url(&endpoint)
                    .map_err(|e| format_xmlrpc_error(&e, &endpoint))?;

                // Extract the second result (index 1) which is our actual method call
                extract_multicall_result(multicall_result, 1)
            } else {
                // No token — send the request directly
                let mut request = Request::new(&method);
                for param in params {
                    request = request.arg(param);
                }
                request
                    .call_url(&endpoint)
                    .map_err(|e| format_xmlrpc_error(&e, &endpoint))
            }
        }).await?
    }

    pub async fn get_page(&self, pagename: &str, revision: Option<i32>) -> Result<String> {
        let method = if revision.is_some() {
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
        use chrono::{Utc, Datelike, Timelike};
        use iso8601::{DateTime as IsoDateTime, Date as IsoDate, Time as IsoTime};

        // Use a date ~10 years ago to get all history
        let since = Utc::now() - chrono::Duration::days(3650);
        let naive = since.naive_utc();
        let iso_dt = IsoDateTime {
            date: IsoDate::YMD {
                year: naive.year(),
                month: naive.month(),
                day: naive.day(),
            },
            time: IsoTime {
                hour: naive.hour(),
                minute: naive.minute(),
                second: naive.second(),
                millisecond: 0,
                tz_offset_hours: 0,
                tz_offset_minutes: 0,
            },
        };

        let params = vec![
            xmlrpc::Value::DateTime(iso_dt),
            xmlrpc::Value::Array(vec![xmlrpc::Value::String(pagename.to_string())]),
        ];

        let result = self.make_xmlrpc_call("getRecentChangesWithAttributes", params).await?;

        // Response is [[history_entries_for_page1], ...]. Since we pass one pagename,
        // take result[0] which is the history list for that page.
        match result {
            xmlrpc::Value::Array(outer) => {
                // outer[0] is the history list for our single page
                let history_arr = if let Some(xmlrpc::Value::Array(inner)) = outer.into_iter().next() {
                    inner
                } else {
                    return Ok(Vec::new());
                };

                let mut history = Vec::new();
                for item in history_arr {
                    if let xmlrpc::Value::Struct(struct_val) = item {
                        let mut entry = HashMap::new();
                        for (key, value) in struct_val {
                            entry.insert(key, value_to_string(&value));
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

        // MoinMoin returns [(pagename, context_html), ...] — an array of 2-element arrays.
        // Extract the first element (pagename) from each inner array.
        match result {
            xmlrpc::Value::Array(arr) => {
                let mut results = Vec::new();
                for item in arr {
                    if let xmlrpc::Value::Array(inner) = item {
                        // inner[0] is the pagename, inner[1] is the context HTML
                        if let Some(xmlrpc::Value::String(page)) = inner.into_iter().next() {
                            results.push(page);
                        }
                    }
                }
                Ok(results)
            },
            _ => Err(anyhow::anyhow!("Unexpected response format for searchPages")),
        }
    }

    pub async fn get_recent_changes(&self, days: i32) -> Result<Vec<HashMap<String, String>>> {
        use chrono::{Utc, Datelike, Timelike};
        use iso8601::{DateTime as IsoDateTime, Date as IsoDate, Time as IsoTime};

        let since = Utc::now() - chrono::Duration::days(days as i64);
        let naive = since.naive_utc();
        let iso_dt = IsoDateTime {
            date: IsoDate::YMD {
                year: naive.year(),
                month: naive.month(),
                day: naive.day(),
            },
            time: IsoTime {
                hour: naive.hour(),
                minute: naive.minute(),
                second: naive.second(),
                millisecond: 0,
                tz_offset_hours: 0,
                tz_offset_minutes: 0,
            },
        };
        let params = vec![xmlrpc::Value::DateTime(iso_dt)];
        let result = self.make_xmlrpc_call("getRecentChanges", params).await?;

        // MoinMoin returns [{name, lastModified, author, version}, ...]
        // Return all fields as HashMap<String, String>, converting non-string values.
        match result {
            xmlrpc::Value::Array(arr) => {
                let mut changes = Vec::new();
                for item in arr {
                    if let xmlrpc::Value::Struct(struct_val) = item {
                        let mut entry = HashMap::new();
                        for (key, value) in struct_val {
                            entry.insert(key, value_to_string(&value));
                        }
                        changes.push(entry);
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
